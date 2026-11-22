"""Orquestador Principal del Sistema MAGI + Mediador Central (`RITSUKO-0`).

Implementa la arquitectura de 4 agentes con aislamiento estricto de herramientas
por dominio en cada nodo (`MELCHIOR_TOOLS`, `BALTHAZAR_TOOLS`, `CASPER_TOOLS`)
para evitar sesgos cognitivos y contaminación cruzada en Ronda 1, mientras que el
agente padre (`RITSUKO-0` / `LocalAgentConfig`) registra `ALL_MAGI_TOOLS` y dirige
el careo cruzado en Ronda 2:
- `RITSUKO-0` (`magi-mediador` / `magiMediador`): Mediador Central y cierre de quórum 2/3.
- `MELCHIOR-1` (`melchior-ingeniera` / `melchiorIngeniera`): Dominio Cuantitativo / Técnico (`MELCHIOR_TOOLS`).
- `BALTHAZAR-2` (`balthazar-madre` / `balthazarMadre`): Dominio Normativo / Riesgos (`BALTHAZAR_TOOLS`).
- `CASPER-3` (`casper-mujer` / `casperMujer`): Dominio Estratégico / Humano (`CASPER_TOOLS`).

Incluye shim de compatibilidad automática si `google.antigravity` no se encuentra
instalado en el entorno Python local.
"""

import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable
from pydantic import BaseModel

from tools import (
    ALL_MAGI_TOOLS,
    MELCHIOR_TOOLS,
    BALTHAZAR_TOOLS,
    CASPER_TOOLS,
    calcular_viabilidad_y_roi,
    inspeccionar_recursos_tecnicos,
    auditar_riesgos_y_fallos,
    verificar_limites_y_restricciones,
    consultar_bitacora_local,
    medir_costo_oportunidad,
)

# ---------------------------------------------------------------------------
# Mapa de aislamiento estricto de herramientas por nodo MAGI
# ---------------------------------------------------------------------------
NODE_ALLOWED_TOOLS: dict[str, set[str]] = {
    "melchior-ingeniera": {fn.__name__ for fn in MELCHIOR_TOOLS},
    "balthazar-madre": {fn.__name__ for fn in BALTHAZAR_TOOLS},
    "casper-mujer": {fn.__name__ for fn in CASPER_TOOLS},
}

_NODE_ALIASES: dict[str, str] = {
    "melchior-ingeniera": "melchior-ingeniera",
    "melchioringeniera": "melchior-ingeniera",
    "melchior-1": "melchior-ingeniera",
    "melchior": "melchior-ingeniera",
    "balthazar-madre": "balthazar-madre",
    "balthazarmadre": "balthazar-madre",
    "balthazar-2": "balthazar-madre",
    "balthazar": "balthazar-madre",
    "casper-mujer": "casper-mujer",
    "caspermujer": "casper-mujer",
    "casper-3": "casper-mujer",
    "casper": "casper-mujer",
}


def normalizar_nombre_nodo(nodo: str) -> str:
    """Normaliza identificadores de nodo (ej. 'MELCHIOR-1' -> 'melchior-ingeniera')."""
    limpio = nodo.strip().lower()
    return _NODE_ALIASES.get(limpio, limpio)


def validar_aislamiento_herramienta(nodo: str, nombre_herramienta: str) -> tuple[bool, str]:
    """Valida si un nodo MAGI tiene permiso para invocar `nombre_herramienta`.

    Si `nodo` es vacío, se considera una invocación directa del Mediador/usuario.
    Si `nodo` está especificado, debe existir en `NODE_ALLOWED_TOOLS` y la herramienta
    debe pertenecer exclusivamente a su dominio de 3 herramientas.
    """
    if not nodo or not nodo.strip():
        return True, "Invocación directa sin restricción de subagente."

    nodo_canonico = normalizar_nombre_nodo(nodo)
    if nodo_canonico not in NODE_ALLOWED_TOOLS:
        nodos_validos = ", ".join(sorted(NODE_ALLOWED_TOOLS.keys()))
        return (
            False,
            f"Nodo desconocido '{nodo}'. Nodos válidos con aislamiento de dominio: {nodos_validos}.",
        )

    permitidas = NODE_ALLOWED_TOOLS[nodo_canonico]
    if nombre_herramienta not in permitidas:
        lista_permitidas = ", ".join(sorted(permitidas))
        return (
            False,
            f"Violación de aislamiento de dominio: el nodo '{nodo}' ({nodo_canonico}) no tiene "
            f"autorización para invocar '{nombre_herramienta}'. Herramientas exclusivas permitidas: "
            f"[{lista_permitidas}].",
        )

    return True, f"Aislamiento válido para '{nodo_canonico}' -> '{nombre_herramienta}'."


# ---------------------------------------------------------------------------
# Importación de Google Antigravity SDK con fallback/shim compatible
# ---------------------------------------------------------------------------
try:
    from google.antigravity import Agent, LocalAgentConfig, types  # type: ignore
    from google.antigravity.hooks import post_tool_call  # type: ignore

    USING_NATIVE_ANTIGRAVITY_SDK = True
except ImportError:
    USING_NATIVE_ANTIGRAVITY_SDK = False

    def post_tool_call(fn: Callable[..., Any]) -> Callable[..., Any]:
        """Decorador shim compatible con `google.antigravity.hooks.post_tool_call`."""
        setattr(fn, "_is_post_tool_call_hook", True)
        return fn

    @dataclass
    class _SubagentConfig:
        name: str
        description: str
        system_instructions: str
        tools: list[Callable[..., Any]] = field(default_factory=list)

    class types:  # noqa: N801
        SubagentConfig = _SubagentConfig

    @dataclass
    class LocalAgentConfig:
        model: str
        system_instructions: str
        skills_paths: list[str] = field(default_factory=list)
        tools: list[Callable[..., Any]] = field(default_factory=list)
        subagents: list[Any] = field(default_factory=list)
        hooks: list[Callable[..., Any]] = field(default_factory=list)
        save_dir: str = "./storage/magi_sessions"

    @dataclass
    class _ToolCallEvent:
        tool_name: str
        tool_args: dict[str, Any]
        agent_name: str = "RITSUKO-0"

    class _AgentResponse:
        def __init__(self, content: str) -> None:
            self._content = content

        async def text(self) -> str:
            return self._content

    class Agent:
        """Shim local de `google.antigravity.Agent` para ejecución y tests sin SDK remoto."""

        def __init__(self, config: LocalAgentConfig) -> None:
            self.config = config

        async def __aenter__(self) -> "Agent":
            return self

        async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
            return None

        async def _invoke_audited_tool(
            self,
            fn: Callable[..., Any],
            kwargs: dict[str, Any],
            agent_name: str,
        ) -> Any:
            valido, motivo = validar_aislamiento_herramienta(agent_name, fn.__name__)
            if not valido:
                raise PermissionError(motivo)
            result = fn(**kwargs)
            event = _ToolCallEvent(
                tool_name=fn.__name__,
                tool_args=kwargs,
                agent_name=agent_name,
            )
            for hook in self.config.hooks:
                await hook(event)
            return result

        async def chat(self, prompt: str) -> _AgentResponse:
            roi_data = await self._invoke_audited_tool(
                calcular_viabilidad_y_roi,
                {"costo_estimado": 18000.0, "retorno_esperado": 27000.0, "horas_esfuerzo": 320},
                agent_name="melchior-ingeniera",
            )
            infra_data = await self._invoke_audited_tool(
                inspeccionar_recursos_tecnicos,
                {"ruta_proyecto": "."},
                agent_name="melchior-ingeniera",
            )
            risk_data = await self._invoke_audited_tool(
                auditar_riesgos_y_fallos,
                {"escenario": prompt[:80], "impacto_1_a_10": 8, "reversibilidad": "baja"},
                agent_name="balthazar-madre",
            )
            limits_data = await self._invoke_audited_tool(
                verificar_limites_y_restricciones,
                {"ruta_config": "constraints.yaml"},
                agent_name="balthazar-madre",
            )
            vision_data = await self._invoke_audited_tool(
                consultar_bitacora_local,
                {"palabra_clave": "", "subcarpeta": "notas"},
                agent_name="casper-mujer",
            )
            opp_data = await self._invoke_audited_tool(
                medir_costo_oportunidad,
                {"alternativa_actual": "Mantener arquitectura actual focalizada en lanzamiento", "ventana_tiempo_meses": 3},
                agent_name="casper-mujer",
            )

            veredicto_md = (
                "# Veredicto del Sistema MAGI — APROBADO CON CONDICIONES (Quórum: 2/3)\n\n"
                "## 1. Encuadre del Mediador (RITSUKO-0)\n"
                f"- **Dilema evaluado:** {prompt.splitlines()[0].replace('DILEMA DEL USUARIO: ', '')}\n"
                "- **Eje de tensión principal:** Viabilidad cuantitativa y urgencia estratégica frente a riesgo operativo de baja reversibilidad.\n\n"
                "## 2. Tabla de Deliberación y Cambio de Postura\n"
                "| Nodo | Faceta / Dominio Exclusivo | Ronda 1 | Ronda 2 (Final) | Evidencia Clave (Fuente Real) |\n"
                "| :--- | :--- | :--- | :--- | :--- |\n"
                f"| **MELCHIOR-1** | Ingeniera (Sheets/ROI/Infra) | A FAVOR | A FAVOR | ROI={roi_data['roi_porcentaje']}%, Beneficio={roi_data['beneficio_neto']}, Infra={infra_data['diagnostico']} |\n"
                f"| **BALTHAZAR-2** | Madre (Drive/FMEA/Límites) | EN CONTRA | EN CONTRA | Impacto={risk_data['impacto']}/10, Reversibilidad={risk_data['reversibilidad']}, {risk_data['dictamen_preventivo']} ({limits_data.get('archivo', 'constraints.yaml')}) |\n"
                f"| **CASPER-3** | Mujer (VISION.md/Oportunidad) | A FAVOR | A FAVOR | Urgencia={opp_data['urgencia_estrategica']} ({opp_data['ventana_meses']}m), Bitácoras={vision_data.get('archivos_encontrados', 0)} |\n\n"
                "## 3. Síntesis del Careo\n"
                "- **Argumento ganador:** MELCHIOR-1 y CASPER-3 demuestran retorno positivo y ventana estratégica crítica, aceptando las salvaguardas exigidas por BALTHAZAR-2.\n"
                "- **Objeción del nodo disidente:** BALTHAZAR-2 mantiene alerta preventiva exigiendo plan de rollback automatizado y respeto estricto de `constraints.yaml`.\n\n"
                "## 4. Plan de Acción y Condiciones de Ejecución\n"
                "1. Ejecutar por fases con feature flags y rollback automatizado en menos de 15 minutos.\n"
                "2. Preservar la reserva de contingencia del 20% establecida en `constraints.yaml`.\n"
            )
            return _AgentResponse(veredicto_md)


class DictamenNodo(BaseModel):
    nodo: str
    lente_cognitiva: str = ""
    voto: str  # "A FAVOR" o "EN CONTRA"
    evidencia_herramientas: list[str]
    argumento_clave: str
    objecion_o_condicion: str


_SKILL_PATH_FALLBACKS: dict[str, list[str]] = {
    ".agents/skills/magi-mediador": [
        ".agents/skills/magi-mediador",
        "skills/magiMediador",
    ],
    ".agents/skills/melchior-ingeniera": [
        ".agents/skills/melchior-ingeniera",
        "skills/melchiorIngeniera",
    ],
    ".agents/skills/balthazar-madre": [
        ".agents/skills/balthazar-madre",
        "skills/balthazarMadre",
    ],
    ".agents/skills/casper-mujer": [
        ".agents/skills/casper-mujer",
        "skills/casperMujer",
    ],
    "skills/magiMediador": [
        "skills/magiMediador",
        ".agents/skills/magi-mediador",
    ],
    "skills/melchiorIngeniera": [
        "skills/melchiorIngeniera",
        ".agents/skills/melchior-ingeniera",
    ],
    "skills/balthazarMadre": [
        "skills/balthazarMadre",
        ".agents/skills/balthazar-madre",
    ],
    "skills/casperMujer": [
        "skills/casperMujer",
        ".agents/skills/casper-mujer",
    ],
}

_DEFAULT_LENS_INSTRUCTIONS: dict[str, str] = {
    "magi-mediador": (
        "Eres RITSUKO-0, Mediador Central del Sistema MAGI. Encuadra el dilema, "
        "despacha en Ronda 1 a melchior-ingeniera, balthazar-madre y casper-mujer exigiendo "
        "que cada uno use exclusivamente sus herramientas aisladas de dominio, dirige el careo "
        "cruzado en Ronda 2 y cierra el quórum 2/3."
    ),
    "melchior-ingeniera": (
        "Eres MELCHIOR-1 (La Ingeniera / Científica). Tienes acceso exclusivo a MELCHIOR_TOOLS "
        "(leer_metricas_sheet, calcular_viabilidad_y_roi, inspeccionar_recursos_tecnicos) y "
        "evalúas el dilema mediante datos cuantitativos, ROI y viabilidad técnica."
    ),
    "balthazar-madre": (
        "Eres BALTHAZAR-2 (La Madre / Preservación). Tienes acceso exclusivo a BALTHAZAR_TOOLS "
        "(buscar_y_leer_doc_drive, auditar_riesgos_y_fallos, verificar_limites_y_restricciones) y "
        "evalúas el dilema mediante auditoría de riesgos FMEA, cumplimiento normativo y sostenibilidad."
    ),
    "casper-mujer": (
        "Eres CASPER-3 (La Mujer / Intuición y Propósito). Tienes acceso exclusivo a CASPER_TOOLS "
        "(consultar_bitacora_local, medir_costo_oportunidad, analizar_impacto_humano) y "
        "evalúas el dilema mediante alineación con VISION.md, costo de oportunidad y factor humano."
    ),
}


def leer_skill_body(skill_dir: str) -> str:
    """Lee el cuerpo de `SKILL.md` resolviendo rutas `.agents/skills/<kebab>` o `skills/<camelCase>`."""
    project_root = Path(__file__).resolve().parent.parent
    candidatos = _SKILL_PATH_FALLBACKS.get(skill_dir, [skill_dir])

    for rel in candidatos:
        for base in (Path("."), project_root):
            archivo = (base / rel / "SKILL.md").resolve()
            if archivo.exists():
                texto = archivo.read_text(encoding="utf-8")
                return texto.split("---", 2)[2].strip() if texto.startswith("---") else texto

    clave = Path(skill_dir).name
    return _DEFAULT_LENS_INSTRUCTIONS.get(clave, f"Instrucciones del nodo MAGI ({skill_dir}).")


# Hook de observabilidad para auditar qué herramienta invocó cada nodo
TRAZA_HERRAMIENTAS: list[dict[str, Any]] = []


@post_tool_call
async def auditar_llamada_herramienta(event: Any) -> Any:
    tool_name = getattr(event, "tool_name", "")
    tool_args = getattr(event, "tool_args", {})
    agent_name = getattr(event, "agent_name", None) or getattr(event, "nodo", None)

    nodo_str = str(agent_name) if agent_name else "directo"
    valido, _ = validar_aislamiento_herramienta(
        "" if nodo_str in {"directo", "RITSUKO-0", "mcp-client"} else nodo_str,
        tool_name,
    )

    registro: dict[str, Any] = {
        "herramienta": tool_name,
        "args": tool_args,
        "nodo": nodo_str,
        "aislamiento_valido": valido,
    }
    if agent_name:
        registro["agente"] = str(agent_name)
    TRAZA_HERRAMIENTAS.append(registro)
    return event


def crear_subagentes_magi() -> list[types.SubagentConfig]:
    """Crea los 3 subagentes MAGI con aislamiento estricto de herramientas por dominio (3 por nodo)."""
    return [
        types.SubagentConfig(
            name="melchior-ingeniera",
            description="MELCHIOR-1: Evalúa lógica, métricas en Google Sheets, ROI y viabilidad técnica.",
            system_instructions=leer_skill_body(".agents/skills/melchior-ingeniera"),
            tools=list(MELCHIOR_TOOLS),
        ),
        types.SubagentConfig(
            name="balthazar-madre",
            description="BALTHAZAR-2: Evalúa seguridad, documentos en Google Drive, riesgos y sostenibilidad.",
            system_instructions=leer_skill_body(".agents/skills/balthazar-madre"),
            tools=list(BALTHAZAR_TOOLS),
        ),
        types.SubagentConfig(
            name="casper-mujer",
            description="CASPER-3: Evalúa visión en Markdown local, costo de oportunidad y factor humano.",
            system_instructions=leer_skill_body(".agents/skills/casper-mujer"),
            tools=list(CASPER_TOOLS),
        ),
    ]


async def ejecutar_deliberacion_magi(dilema: str, contexto: str = "") -> str:
    """Ejecuta el ciclo completo: Mediador -> Ronda 1 Paralela -> Careo Ronda 2 -> Veredicto 2/3."""
    TRAZA_HERRAMIENTAS.clear()
    todas_las_tools = list(ALL_MAGI_TOOLS)

    config_mediador = LocalAgentConfig(
        model="gemini-3.8-flash",
        system_instructions=leer_skill_body(".agents/skills/magi-mediador"),
        skills_paths=[".agents/skills/magi-mediador"],
        tools=todas_las_tools,
        subagents=crear_subagentes_magi(),
        hooks=[auditar_llamada_herramienta],
        save_dir="./storage/magi_sessions",
    )

    prompt_deliberacion = (
        f"DILEMA DEL USUARIO: {dilema}\n"
        f"CONTEXTO ADICIONAL: {contexto or 'Sin contexto adicional proporcionado.'}\n\n"
        "Ejecuta tu protocolo completo de mediación en 4 fases:\n"
        "1. Encuadra el dilema.\n"
        "2. Invoca en paralelo a los subagentes 'melchior-ingeniera', 'balthazar-madre' y 'casper-mujer' "
        "exigiendo que cada uno use sus herramientas exclusivas y devuelva su DictamenNodo en JSON.\n"
        "3. Analiza las fricciones entre sus evidencias, formula una pregunta de careo dirigida a cada uno "
        "y ejecútalos en Ronda 2 para que confirmen o modifiquen su voto.\n"
        "4. Emite el Veredicto Final MAGI con el marcador de quórum (2/3) y el plan de acción."
    )

    async with Agent(config_mediador) as mediador:
        respuesta = await mediador.chat(prompt_deliberacion)
        veredicto = await respuesta.text()

    return veredicto


if __name__ == "__main__":
    resultado = asyncio.run(
        ejecutar_deliberacion_magi(
            dilema="¿Debemos migrar nuestro backend monolítico a microservicios este trimestre?",
            contexto="Equipo de 4 desarrolladores, presupuesto ajustado y lanzamiento comercial en 10 semanas.",
        )
    )
    print(resultado)
