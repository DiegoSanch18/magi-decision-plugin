"""Suite de pruebas de integración del Sistema MAGI (`magi-decision-plugin`).

Verifica:
1. Capacidades simétricas (`ALL_MAGI_TOOLS` = 9 herramientas) en los 3 subagentes
   (`melchior-ingeniera`, `balthazar-madre`, `casper-mujer`) y en el Mediador
   (`LocalAgentConfig`), con lentes cognitivas diferenciadas.
2. Funcionamiento del hook `@post_tool_call` (`auditar_llamada_herramienta`) y
   registro en `TRAZA_HERRAMIENTAS`.
3. Ejecución de las 9 herramientas de dominio (incluyendo mocks de Google Sheets y
   Google Drive, manejo de errores sin credenciales, lectura de `constraints.yaml`
   y `notas/VISION.md`).
4. CLI `tools/cli.py` para Modo B (listado, invocación JSON y manejo de errores).
5. Servidor FastMCP `mcp_server.py` (`ejecutar_herramienta_magi` y `deliberar_con_magi`).
"""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any
import pytest

import tools
from tools import (
    ALL_MAGI_TOOLS,
    MELCHIOR_TOOLS,
    BALTHAZAR_TOOLS,
    CASPER_TOOLS,
    MAGI_TOOL_REGISTRY,
    leer_metricas_sheet,
    calcular_viabilidad_y_roi,
    inspeccionar_recursos_tecnicos,
    buscar_y_leer_doc_drive,
    auditar_riesgos_y_fallos,
    verificar_limites_y_restricciones,
    consultar_bitacora_local,
    medir_costo_oportunidad,
    analizar_impacto_humano,
)
from tools.cli import ejecutar_cli, listar_herramientas
from engine.magi_mediator import (
    DictamenNodo,
    LocalAgentConfig,
    TRAZA_HERRAMIENTAS,
    auditar_llamada_herramienta,
    crear_subagentes_magi,
    ejecutar_deliberacion_magi,
    leer_skill_body,
)
from mcp_server import deliberar_con_magi, ejecutar_herramienta_magi


EXPECTED_9_TOOL_NAMES = [
    "leer_metricas_sheet",
    "calcular_viabilidad_y_roi",
    "inspeccionar_recursos_tecnicos",
    "buscar_y_leer_doc_drive",
    "auditar_riesgos_y_fallos",
    "verificar_limites_y_restricciones",
    "consultar_bitacora_local",
    "medir_costo_oportunidad",
    "analizar_impacto_humano",
]


def test_symmetric_all_magi_tools_export() -> None:
    """Verifica que ALL_MAGI_TOOLS contenga exactamente las 9 herramientas de los 3 dominios."""
    assert len(MELCHIOR_TOOLS) == 3
    assert len(BALTHAZAR_TOOLS) == 3
    assert len(CASPER_TOOLS) == 3
    assert len(ALL_MAGI_TOOLS) == 9
    assert [fn.__name__ for fn in ALL_MAGI_TOOLS] == EXPECTED_9_TOOL_NAMES
    assert set(MAGI_TOOL_REGISTRY.keys()) == set(EXPECTED_9_TOOL_NAMES)


def test_subagents_have_symmetric_tools_and_distinct_cognitive_lenses() -> None:
    """Verifica que los 3 nodos MAGI tengan exactamente las mismas 9 herramientas y lentes distintas."""
    subagentes = crear_subagentes_magi()
    assert len(subagentes) == 3

    nombres = [s.name for s in subagentes]
    assert nombres == ["melchior-ingeniera", "balthazar-madre", "casper-mujer"]

    for sub in subagentes:
        tool_names = [fn.__name__ for fn in sub.tools]
        assert tool_names == EXPECTED_9_TOOL_NAMES, (
            f"El subagente {sub.name} debe poseer las 9 herramientas simétricas de ALL_MAGI_TOOLS"
        )
        assert len(sub.system_instructions.strip()) > 20

    # Sus instrucciones y descripciones deben diferir según su lente cognitiva
    instrucciones = {s.system_instructions for s in subagentes}
    descripciones = {s.description for s in subagentes}
    assert len(instrucciones) == 3
    assert len(descripciones) == 3

    # Verifica también la configuración del agente padre (RITSUKO-0)
    config_padre = LocalAgentConfig(
        model="gemini-3.8-flash",
        system_instructions=leer_skill_body(".agents/skills/magi-mediador"),
        skills_paths=[".agents/skills/magi-mediador"],
        tools=list(ALL_MAGI_TOOLS),
        subagents=subagentes,
        hooks=[auditar_llamada_herramienta],
    )
    assert [fn.__name__ for fn in config_padre.tools] == EXPECTED_9_TOOL_NAMES
    assert len(config_padre.subagents) == 3


def test_dictamen_nodo_pydantic_schema() -> None:
    """Verifica el contrato de salida estructurada DictamenNodo."""
    dictamen = DictamenNodo(
        nodo="MELCHIOR-1",
        lente_cognitiva="Ingeniera / Científica",
        voto="A FAVOR",
        evidencia_herramientas=["ROI=50.0%", "Beneficio neto=9000.0 USD"],
        argumento_clave="Retorno positivo respaldado por métricas.",
        objecion_o_condicion="Mantener cobertura de tests > 90%.",
    )
    assert dictamen.nodo == "MELCHIOR-1"
    assert dictamen.voto == "A FAVOR"
    assert len(dictamen.evidencia_herramientas) == 2


@pytest.mark.asyncio
async def test_post_tool_call_hook_populates_traza() -> None:
    """Verifica que el hook @post_tool_call registre herramienta, argumentos y agente."""
    TRAZA_HERRAMIENTAS.clear()

    @dataclass
    class DummyEvent:
        tool_name: str
        tool_args: dict[str, Any]
        agent_name: str = "MELCHIOR-1"

    ev = DummyEvent(
        tool_name="calcular_viabilidad_y_roi",
        tool_args={"costo_estimado": 1000.0, "retorno_esperado": 1800.0, "horas_esfuerzo": 40},
        agent_name="MELCHIOR-1",
    )
    returned = await auditar_llamada_herramienta(ev)
    assert returned is ev
    assert len(TRAZA_HERRAMIENTAS) == 1
    assert TRAZA_HERRAMIENTAS[0]["herramienta"] == "calcular_viabilidad_y_roi"
    assert TRAZA_HERRAMIENTAS[0]["args"]["costo_estimado"] == 1000.0
    assert TRAZA_HERRAMIENTAS[0]["agente"] == "MELCHIOR-1"


def test_melchior_domain_tools_and_mocked_sheets(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifica las 3 herramientas cuantitativas/técnicas (ROI, inspección técnica y Google Sheets)."""
    # 1. calcular_viabilidad_y_roi
    viable = calcular_viabilidad_y_roi(costo_estimado=10000.0, retorno_esperado=15000.0, horas_esfuerzo=100)
    assert viable["roi_porcentaje"] == 50.0
    assert viable["beneficio_neto"] == 5000.0
    assert viable["retorno_por_hora"] == 50.0
    assert viable["viable_cuantitativamente"] is True

    no_viable = calcular_viabilidad_y_roi(costo_estimado=10000.0, retorno_esperado=10500.0, horas_esfuerzo=100)
    assert no_viable["roi_porcentaje"] == 5.0
    assert no_viable["viable_cuantitativamente"] is False

    # 2. inspeccionar_recursos_tecnicos
    project_root = str(Path(__file__).resolve().parent.parent)
    infra = inspeccionar_recursos_tecnicos(ruta_proyecto=project_root)
    assert "pyproject.toml" in infra["archivos_infraestructura"]
    assert infra["archivos_python"] >= 5
    assert infra["diagnostico"] == "Base técnica detectada"

    # 3a. leer_metricas_sheet sin credenciales -> error controlado
    monkeypatch.delenv("MAGI_MELCHIOR_SHEET_ID", raising=False)
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    err_sheet = leer_metricas_sheet()
    assert "error" in err_sheet

    # 3b. leer_metricas_sheet con mock de gspread y Credentials
    monkeypatch.setenv("MAGI_MELCHIOR_SHEET_ID", "sheet_test_123")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "dummy_creds.json")

    class FakeSheet1:
        def get(self, rango: str) -> list[list[str]]:
            assert rango == "A1:C3"
            return [
                ["Metrica", "Valor", "Estado"],
                ["Presupuesto", "25000", "Aprobado"],
                ["BurnRate", "4200", "Normal"],
            ]

    class FakeSpreadsheet:
        sheet1 = FakeSheet1()

    class FakeClient:
        def open_by_key(self, key: str) -> FakeSpreadsheet:
            assert key == "sheet_test_123"
            return FakeSpreadsheet()

    monkeypatch.setattr(
        tools.melchior_tools.Credentials,
        "from_service_account_file",
        lambda path, scopes: "fake_creds",
    )
    monkeypatch.setattr(
        tools.melchior_tools.gspread,
        "authorize",
        lambda creds: FakeClient(),
    )

    ok_sheet = leer_metricas_sheet(rango="A1:C3")
    assert ok_sheet["total_filas"] == 2
    assert ok_sheet["datos"][0]["Metrica"] == "Presupuesto"
    assert ok_sheet["datos"][0]["Valor"] == "25000"


def test_balthazar_domain_tools_and_mocked_drive(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifica las 3 herramientas de preservación/riesgo (FMEA, constraints.yaml y Google Drive)."""
    # 1. auditar_riesgos_y_fallos
    critico = auditar_riesgos_y_fallos("Migración big-bang sin rollback", impacto_1_a_10=9, reversibilidad="Baja")
    assert critico["alerta_critica"] is True
    assert critico["dictamen_preventivo"] == "Requiere plan de contingencia obligatorio"

    acotado = auditar_riesgos_y_fallos("Canary deployment con feature flag", impacto_1_a_10=5, reversibilidad="Alta")
    assert acotado["alerta_critica"] is False
    assert acotado["dictamen_preventivo"] == "Riesgo acotable"

    # 2. verificar_limites_y_restricciones
    project_root = Path(__file__).resolve().parent.parent
    limites = verificar_limites_y_restricciones(str(project_root / "constraints.yaml"))
    assert "restricciones" in limites
    assert "tope_trimestral_usd" in limites["restricciones"]

    inexistente = verificar_limites_y_restricciones("no_existe_constraints.yaml")
    assert "mensaje" in inexistente

    # 3a. buscar_y_leer_doc_drive sin credenciales -> error controlado
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    err_drive = buscar_y_leer_doc_drive("SLA")
    assert "error" in err_drive

    # 3b. buscar_y_leer_doc_drive con mock de Drive API v3
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "dummy_creds.json")
    monkeypatch.setenv("MAGI_BALTHAZAR_DRIVE_FOLDER_ID", "folder_999")

    class FakeRequest:
        def __init__(self, payload: Any) -> None:
            self._payload = payload

        def execute(self) -> Any:
            return self._payload

    class FakeFilesResource:
        def list(self, q: str, pageSize: int, fields: str) -> FakeRequest:
            assert "SLA" in q
            assert "folder_999" in q
            return FakeRequest(
                {
                    "files": [
                        {
                            "id": "doc_1",
                            "name": "Contrato_SLA_Produccion",
                            "mimeType": "application/vnd.google-apps.document",
                        }
                    ]
                }
            )

        def export(self, fileId: str, mimeType: str) -> FakeRequest:
            assert fileId == "doc_1"
            assert mimeType == "text/plain"
            return FakeRequest(b"Clausula 4: Disponibilidad minima garantizada 99.9%.")

    class FakeDriveService:
        def files(self) -> FakeFilesResource:
            return FakeFilesResource()

    monkeypatch.setattr(
        tools.balthazar_tools.Credentials,
        "from_service_account_file",
        lambda path, scopes: "fake_creds",
    )
    monkeypatch.setattr(
        tools.balthazar_tools,
        "build",
        lambda service, version, credentials: FakeDriveService(),
    )

    ok_drive = buscar_y_leer_doc_drive("SLA")
    assert ok_drive["coincidencias"] == 1
    assert ok_drive["documentos"][0]["documento"] == "Contrato_SLA_Produccion"
    assert "99.9%" in ok_drive["documentos"][0]["contenido"]


def test_casper_domain_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifica las 3 herramientas estratégicas/humanas (VISION.md, costo de oportunidad e impacto humano)."""
    project_root = str(Path(__file__).resolve().parent.parent)
    monkeypatch.setenv("MAGI_WORKSPACE_DIR", project_root)

    # 1. consultar_bitacora_local
    bitacora = consultar_bitacora_local(palabra_clave="lanzamiento", subcarpeta="notas")
    assert bitacora["archivos_encontrados"] >= 1
    assert any(n["archivo"] == "VISION.md" for n in bitacora["notas"])

    # 2. medir_costo_oportunidad
    urgente = medir_costo_oportunidad("Mantener monolito actual", ventana_tiempo_meses=2)
    assert urgente["urgencia_estrategica"] == "ALTA"

    medio = medir_costo_oportunidad("Postergar refactor", ventana_tiempo_meses=6)
    assert medio["urgencia_estrategica"] == "MEDIA"

    bajo = medir_costo_oportunidad("Reescritura cosmética", ventana_tiempo_meses=12)
    assert bajo["urgencia_estrategica"] == "BAJA"

    # 3. analizar_impacto_humano
    impacto = analizar_impacto_humano("Equipo de 4 devs a 10 semanas del lanzamiento")
    assert "Alineación con propósito" in impacto["eje_evaluado"]


def test_cli_tool_runner(capsys: pytest.CaptureFixture[str]) -> None:
    """Verifica el ejecutor CLI `python -m tools.cli` para Modo B."""
    catalogo = listar_herramientas()
    assert catalogo["total_herramientas"] == 9

    rc_list = ejecutar_cli(["--list"])
    assert rc_list == 0
    out_list = json.loads(capsys.readouterr().out)
    assert out_list["total_herramientas"] == 9

    rc_call = ejecutar_cli(
        [
            "calcular_viabilidad_y_roi",
            "--json-args",
            '{"costo_estimado": 5000, "retorno_esperado": 8000, "horas_esfuerzo": 60}',
        ]
    )
    assert rc_call == 0
    out_call = json.loads(capsys.readouterr().out)
    assert out_call["herramienta"] == "calcular_viabilidad_y_roi"
    assert out_call["resultado"]["roi_porcentaje"] == 60.0
    assert out_call["resultado"]["viable_cuantitativamente"] is True

    rc_err = ejecutar_cli(["herramienta_inexistente"])
    assert rc_err == 1
    out_err = json.loads(capsys.readouterr().out)
    assert "error" in out_err


@pytest.mark.asyncio
async def test_mcp_server_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifica las herramientas expuestas por `mcp_server.py` (Modo A y Modo B)."""
    project_root = str(Path(__file__).resolve().parent.parent)
    monkeypatch.setenv("MAGI_WORKSPACE_DIR", project_root)
    TRAZA_HERRAMIENTAS.clear()

    # Modo B: ejecutar_herramienta_magi
    res_tool = await ejecutar_herramienta_magi(
        nombre_herramienta="auditar_riesgos_y_fallos",
        argumentos={"escenario": "Corte de base de datos", "impacto_1_a_10": 9, "reversibilidad": "baja"},
        nodo="MELCHIOR-1",
    )
    assert res_tool["herramienta"] == "auditar_riesgos_y_fallos"
    assert res_tool["nodo"] == "MELCHIOR-1"
    assert res_tool["resultado"]["alerta_critica"] is True
    assert len(TRAZA_HERRAMIENTAS) == 1
    assert TRAZA_HERRAMIENTAS[0]["agente"] == "MELCHIOR-1"

    # Modo A: deliberar_con_magi
    res_delib = await deliberar_con_magi(
        dilema="¿Debemos migrar nuestro backend monolítico a microservicios este trimestre?",
        contexto="Equipo de 4 desarrolladores, presupuesto ajustado y lanzamiento comercial en 10 semanas.",
    )
    assert "Veredicto del Sistema MAGI" in res_delib["veredicto_markdown"]
    assert "MELCHIOR-1" in res_delib["veredicto_markdown"]
    assert "BALTHAZAR-2" in res_delib["veredicto_markdown"]
    assert "CASPER-3" in res_delib["veredicto_markdown"]
    assert len(res_delib["auditoria_herramientas_usadas"]) >= 6
