"""Suite de pruebas de integración del Sistema MAGI (`magi-decision-plugin`).

Verifica:
1. Aislamiento estricto de herramientas por dominio en los 3 subagentes:
   - `melchior-ingeniera`: `MELCHIOR_TOOLS` (3 herramientas cuantitativas/técnicas)
   - `balthazar-madre`: `BALTHAZAR_TOOLS` (3 herramientas normativas/riesgo)
   - `casper-mujer`: `CASPER_TOOLS` (3 herramientas estratégicas/humanas)
   con intersección vacía entre nodos, mientras que el agente padre (`RITSUKO-0` /
   `LocalAgentConfig`) registra las 9 herramientas (`ALL_MAGI_TOOLS`).
2. Validación de aislamiento (`NODE_ALLOWED_TOOLS` y `validar_aislamiento_herramienta`),
   permitiendo llamadas de dominio propio y bloqueando invocaciones cruzadas en
   `mcp_server.py` (`ejecutar_herramienta_magi`) y `tools/cli.py --node`.
3. Funcionamiento del hook `@post_tool_call` (`auditar_llamada_herramienta`) y
   registro en `TRAZA_HERRAMIENTAS`.
4. Ejecución de las 9 herramientas de dominio (incluyendo mocks de Google Sheets y
   Google Drive, manejo de errores sin credenciales, lectura de `constraints.yaml`
   y `notas/VISION.md`).
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
    NODE_ALLOWED_TOOLS,
    TRAZA_HERRAMIENTAS,
    auditar_llamada_herramienta,
    crear_subagentes_magi,
    ejecutar_deliberacion_magi,
    leer_skill_body,
    validar_aislamiento_herramienta,
)
from mcp_server import deliberar_con_magi, ejecutar_herramienta_magi


EXPECTED_MELCHIOR_NAMES = [
    "leer_metricas_sheet",
    "calcular_viabilidad_y_roi",
    "inspeccionar_recursos_tecnicos",
]
EXPECTED_BALTHAZAR_NAMES = [
    "buscar_y_leer_doc_drive",
    "auditar_riesgos_y_fallos",
    "verificar_limites_y_restricciones",
]
EXPECTED_CASPER_NAMES = [
    "consultar_bitacora_local",
    "medir_costo_oportunidad",
    "analizar_impacto_humano",
]
EXPECTED_9_TOOL_NAMES = (
    EXPECTED_MELCHIOR_NAMES + EXPECTED_BALTHAZAR_NAMES + EXPECTED_CASPER_NAMES
)


def test_tool_catalog_and_node_allowed_tools_mapping() -> None:
    """Verifica el catálogo de 9 herramientas y el mapa de aislamiento NODE_ALLOWED_TOOLS."""
    assert len(MELCHIOR_TOOLS) == 3
    assert len(BALTHAZAR_TOOLS) == 3
    assert len(CASPER_TOOLS) == 3
    assert len(ALL_MAGI_TOOLS) == 9
    assert [fn.__name__ for fn in ALL_MAGI_TOOLS] == EXPECTED_9_TOOL_NAMES
    assert set(MAGI_TOOL_REGISTRY.keys()) == set(EXPECTED_9_TOOL_NAMES)

    assert NODE_ALLOWED_TOOLS["melchior-ingeniera"] == set(EXPECTED_MELCHIOR_NAMES)
    assert NODE_ALLOWED_TOOLS["balthazar-madre"] == set(EXPECTED_BALTHAZAR_NAMES)
    assert NODE_ALLOWED_TOOLS["casper-mujer"] == set(EXPECTED_CASPER_NAMES)


def test_subagents_have_isolated_domain_tools_and_parent_has_all() -> None:
    """Verifica que cada SubagentConfig reciba SOLO sus 3 herramientas exclusivas sin solapamiento, y el padre las 9."""
    subagentes = crear_subagentes_magi()
    assert len(subagentes) == 3

    por_nombre = {s.name: [fn.__name__ for fn in s.tools] for s in subagentes}
    assert por_nombre["melchior-ingeniera"] == EXPECTED_MELCHIOR_NAMES
    assert por_nombre["balthazar-madre"] == EXPECTED_BALTHAZAR_NAMES
    assert por_nombre["casper-mujer"] == EXPECTED_CASPER_NAMES

    # Intersección estrictamente vacía entre los 3 nodos
    set_melchior = set(por_nombre["melchior-ingeniera"])
    set_balthazar = set(por_nombre["balthazar-madre"])
    set_casper = set(por_nombre["casper-mujer"])
    assert set_melchior.isdisjoint(set_balthazar)
    assert set_melchior.isdisjoint(set_casper)
    assert set_balthazar.isdisjoint(set_casper)

    # El agente padre (RITSUKO-0 / LocalAgentConfig) registra la unión completa (9 herramientas)
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


def test_validar_aislamiento_herramienta_helper() -> None:
    """Verifica que validar_aislamiento_herramienta autorice herramientas propias y bloquee cruzadas."""
    ok_m, _ = validar_aislamiento_herramienta("melchior-ingeniera", "calcular_viabilidad_y_roi")
    assert ok_m is True

    ok_b, _ = validar_aislamiento_herramienta("BALTHAZAR-2", "auditar_riesgos_y_fallos")
    assert ok_b is True

    ok_c, _ = validar_aislamiento_herramienta("casper-mujer", "consultar_bitacora_local")
    assert ok_c is True

    # Cruces prohibidos
    cross_mb, msg_mb = validar_aislamiento_herramienta("melchior-ingeniera", "buscar_y_leer_doc_drive")
    assert cross_mb is False
    assert "Violación de aislamiento" in msg_mb

    cross_bc, msg_bc = validar_aislamiento_herramienta("balthazar-madre", "medir_costo_oportunidad")
    assert cross_bc is False
    assert "Violación de aislamiento" in msg_bc

    cross_cm, msg_cm = validar_aislamiento_herramienta("casper-mujer", "leer_metricas_sheet")
    assert cross_cm is False
    assert "Violación de aislamiento" in msg_cm

    # Nodo inexistente
    unknown, msg_unk = validar_aislamiento_herramienta("nodo-fantasma", "calcular_viabilidad_y_roi")
    assert unknown is False
    assert "Nodo desconocido" in msg_unk


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
    """Verifica que el hook @post_tool_call registre herramienta, argumentos, nodo y aislamiento_valido."""
    TRAZA_HERRAMIENTAS.clear()

    @dataclass
    class DummyEvent:
        tool_name: str
        tool_args: dict[str, Any]
        agent_name: str = "melchior-ingeniera"

    ev = DummyEvent(
        tool_name="calcular_viabilidad_y_roi",
        tool_args={"costo_estimado": 1000.0, "retorno_esperado": 1800.0, "horas_esfuerzo": 40},
        agent_name="melchior-ingeniera",
    )
    returned = await auditar_llamada_herramienta(ev)
    assert returned is ev
    assert len(TRAZA_HERRAMIENTAS) == 1
    assert TRAZA_HERRAMIENTAS[0]["herramienta"] == "calcular_viabilidad_y_roi"
    assert TRAZA_HERRAMIENTAS[0]["args"]["costo_estimado"] == 1000.0
    assert TRAZA_HERRAMIENTAS[0]["nodo"] == "melchior-ingeniera"
    assert TRAZA_HERRAMIENTAS[0]["aislamiento_valido"] is True


def test_melchior_domain_tools_and_mocked_sheets(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifica las 3 herramientas cuantitativas/técnicas (ROI, inspección técnica y Google Sheets)."""
    viable = calcular_viabilidad_y_roi(costo_estimado=10000.0, retorno_esperado=15000.0, horas_esfuerzo=100)
    assert viable["roi_porcentaje"] == 50.0
    assert viable["beneficio_neto"] == 5000.0
    assert viable["retorno_por_hora"] == 50.0
    assert viable["viable_cuantitativamente"] is True

    no_viable = calcular_viabilidad_y_roi(costo_estimado=10000.0, retorno_esperado=10500.0, horas_esfuerzo=100)
    assert no_viable["roi_porcentaje"] == 5.0
    assert no_viable["viable_cuantitativamente"] is False

    project_root = str(Path(__file__).resolve().parent.parent)
    infra = inspeccionar_recursos_tecnicos(ruta_proyecto=project_root)
    assert "pyproject.toml" in infra["archivos_infraestructura"]
    assert infra["archivos_python"] >= 5
    assert infra["diagnostico"] == "Base técnica detectada"

    monkeypatch.delenv("MAGI_MELCHIOR_SHEET_ID", raising=False)
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    err_sheet = leer_metricas_sheet()
    assert "error" in err_sheet

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
    critico = auditar_riesgos_y_fallos("Migración big-bang sin rollback", impacto_1_a_10=9, reversibilidad="Baja")
    assert critico["alerta_critica"] is True
    assert critico["dictamen_preventivo"] == "Requiere plan de contingencia obligatorio"

    acotado = auditar_riesgos_y_fallos("Canary deployment con feature flag", impacto_1_a_10=5, reversibilidad="Alta")
    assert acotado["alerta_critica"] is False
    assert acotado["dictamen_preventivo"] == "Riesgo acotable"

    project_root = Path(__file__).resolve().parent.parent
    limites = verificar_limites_y_restricciones(str(project_root / "constraints.yaml"))
    assert "restricciones" in limites
    assert "tope_trimestral_usd" in limites["restricciones"]

    inexistente = verificar_limites_y_restricciones("no_existe_constraints.yaml")
    assert "mensaje" in inexistente

    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    err_drive = buscar_y_leer_doc_drive("SLA")
    assert "error" in err_drive

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

    bitacora = consultar_bitacora_local(palabra_clave="lanzamiento", subcarpeta="notas")
    assert bitacora["archivos_encontrados"] >= 1
    assert any(n["archivo"] == "VISION.md" for n in bitacora["notas"])

    urgente = medir_costo_oportunidad("Mantener monolito actual", ventana_tiempo_meses=2)
    assert urgente["urgencia_estrategica"] == "ALTA"

    medio = medir_costo_oportunidad("Postergar refactor", ventana_tiempo_meses=6)
    assert medio["urgencia_estrategica"] == "MEDIA"

    bajo = medir_costo_oportunidad("Reescritura cosmética", ventana_tiempo_meses=12)
    assert bajo["urgencia_estrategica"] == "BAJA"

    impacto = analizar_impacto_humano("Equipo de 4 devs a 10 semanas del lanzamiento")
    assert "Alineación con propósito" in impacto["eje_evaluado"]


def test_cli_tool_runner_and_node_isolation(capsys: pytest.CaptureFixture[str]) -> None:
    """Verifica el ejecutor CLI `python -m tools.cli` con y sin `--node` (aislamiento de dominio)."""
    catalogo = listar_herramientas()
    assert catalogo["total_herramientas"] == 9
    assert "aislamiento_por_nodo" in catalogo

    rc_list = ejecutar_cli(["--list"])
    assert rc_list == 0
    out_list = json.loads(capsys.readouterr().out)
    assert out_list["total_herramientas"] == 9

    # Invocación válida con --node melchior-ingeniera sobre su propia herramienta
    rc_ok = ejecutar_cli(
        [
            "--node",
            "melchior-ingeniera",
            "calcular_viabilidad_y_roi",
            "--json-args",
            '{"costo_estimado": 5000, "retorno_esperado": 8000, "horas_esfuerzo": 60}',
        ]
    )
    assert rc_ok == 0
    out_ok = json.loads(capsys.readouterr().out)
    assert out_ok["herramienta"] == "calcular_viabilidad_y_roi"
    assert out_ok["nodo"] == "melchior-ingeniera"
    assert out_ok["aislamiento_valido"] is True
    assert out_ok["resultado"]["roi_porcentaje"] == 60.0

    # Invocación cruzada prohibida: melchior-ingeniera intentando usar herramienta de balthazar-madre
    rc_violation = ejecutar_cli(
        [
            "--node",
            "melchior-ingeniera",
            "auditar_riesgos_y_fallos",
            "--json-args",
            '{"escenario": "Fallo", "impacto_1_a_10": 9, "reversibilidad": "baja"}',
        ]
    )
    assert rc_violation == 1
    out_violation = json.loads(capsys.readouterr().out)
    assert out_violation["aislamiento_violado"] is True
    assert out_violation["nodo"] == "melchior-ingeniera"
    assert out_violation["herramienta"] == "auditar_riesgos_y_fallos"

    # Herramienta inexistente
    rc_err = ejecutar_cli(["herramienta_inexistente"])
    assert rc_err == 1
    out_err = json.loads(capsys.readouterr().out)
    assert "error" in out_err


@pytest.mark.asyncio
async def test_mcp_server_tools_and_isolation(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifica `mcp_server.py`: llamadas válidas por nodo, rechazo de llamadas cruzadas y deliberación completa."""
    project_root = str(Path(__file__).resolve().parent.parent)
    monkeypatch.setenv("MAGI_WORKSPACE_DIR", project_root)
    TRAZA_HERRAMIENTAS.clear()

    # 1. Llamada válida: BALTHAZAR-2 ejecutando su propia herramienta `auditar_riesgos_y_fallos`
    res_ok = await ejecutar_herramienta_magi(
        nombre_herramienta="auditar_riesgos_y_fallos",
        argumentos={"escenario": "Corte de base de datos", "impacto_1_a_10": 9, "reversibilidad": "baja"},
        nodo="balthazar-madre",
    )
    assert res_ok["herramienta"] == "auditar_riesgos_y_fallos"
    assert res_ok["nodo"] == "balthazar-madre"
    assert res_ok["aislamiento_valido"] is True
    assert res_ok["resultado"]["alerta_critica"] is True
    assert len(TRAZA_HERRAMIENTAS) == 1
    assert TRAZA_HERRAMIENTAS[0]["nodo"] == "balthazar-madre"
    assert TRAZA_HERRAMIENTAS[0]["aislamiento_valido"] is True

    # 2. Llamada cruzada rechazada: MELCHIOR-1 intentando ejecutar `auditar_riesgos_y_fallos` (de Balthazar)
    res_blocked = await ejecutar_herramienta_magi(
        nombre_herramienta="auditar_riesgos_y_fallos",
        argumentos={"escenario": "Corte de base de datos", "impacto_1_a_10": 9, "reversibilidad": "baja"},
        nodo="melchior-ingeniera",
    )
    assert "error" in res_blocked
    assert res_blocked["aislamiento_violado"] is True
    assert res_blocked["nodo"] == "melchior-ingeniera"
    assert len(TRAZA_HERRAMIENTAS) == 1  # No debe haberse ejecutado ni agregado a la traza

    # 3. Modo A: deliberar_con_magi
    res_delib = await deliberar_con_magi(
        dilema="¿Debemos migrar nuestro backend monolítico a microservicios este trimestre?",
        contexto="Equipo de 4 desarrolladores, presupuesto ajustado y lanzamiento comercial en 10 semanas.",
    )
    assert "Veredicto del Sistema MAGI" in res_delib["veredicto_markdown"]
    assert "MELCHIOR-1" in res_delib["veredicto_markdown"]
    assert "BALTHAZAR-2" in res_delib["veredicto_markdown"]
    assert "CASPER-3" in res_delib["veredicto_markdown"]
    assert len(res_delib["auditoria_herramientas_usadas"]) >= 6
    assert all(t["aislamiento_valido"] is True for t in res_delib["auditoria_herramientas_usadas"])
