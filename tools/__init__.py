"""Arsenal completo y simétrico de herramientas del Sistema MAGI (`ALL_MAGI_TOOLS`).

Todos los nodos del Sistema MAGI (`MELCHIOR-1`, `BALTHAZAR-2`, `CASPER-3`) y el
Mediador Central (`RITSUKO-0`) disponen de acceso simétrico a las 9 herramientas
de los tres dominios (cuantitativo/técnico, normativo/riesgos, estratégico/humano),
diferenciándose exclusivamente por su lente cognitiva de evaluación.
"""

from tools.melchior_tools import (
    SCOPES_SHEETS,
    MELCHIOR_TOOLS,
    leer_metricas_sheet,
    calcular_viabilidad_y_roi,
    inspeccionar_recursos_tecnicos,
)
from tools.balthazar_tools import (
    SCOPES_DRIVE,
    BALTHAZAR_TOOLS,
    buscar_y_leer_doc_drive,
    auditar_riesgos_y_fallos,
    verificar_limites_y_restricciones,
)
from tools.casper_tools import (
    CASPER_TOOLS,
    consultar_bitacora_local,
    medir_costo_oportunidad,
    analizar_impacto_humano,
)

ALL_MAGI_TOOLS = MELCHIOR_TOOLS + BALTHAZAR_TOOLS + CASPER_TOOLS

MAGI_TOOL_REGISTRY = {fn.__name__: fn for fn in ALL_MAGI_TOOLS}

__all__ = [
    "SCOPES_SHEETS",
    "SCOPES_DRIVE",
    "MELCHIOR_TOOLS",
    "BALTHAZAR_TOOLS",
    "CASPER_TOOLS",
    "ALL_MAGI_TOOLS",
    "MAGI_TOOL_REGISTRY",
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
