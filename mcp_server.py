"""Servidor FastMCP (`mcp_server.py`) del Sistema MAGI para Google Antigravity IDE.

Expone dos herramientas MCP complementarias:
1. `deliberar_con_magi` (Modo A): Orquesta una deliberación completa del Sistema MAGI
   (RITSUKO-0 + MELCHIOR-1, BALTHAZAR-2, CASPER-3) mediante el motor `engine.magi_mediator`.
2. `ejecutar_herramienta_magi` (Modo B): Permite a los subagentes nativos de Antigravity
   (`melchior-ingeniera`, `balthazar-madre`, `casper-mujer`) ejecutar sus herramientas
   exclusivas de dominio verificando `NODE_ALLOWED_TOOLS` y registrando la auditoría
   en `TRAZA_HERRAMIENTAS`.
"""

from typing import Any

try:
    from mcp.server.fastmcp import FastMCP  # type: ignore
except ModuleNotFoundError:
    from mcp.server.mcpserver import MCPServer as FastMCP  # type: ignore

from engine.magi_mediator import (
    NODE_ALLOWED_TOOLS,
    TRAZA_HERRAMIENTAS,
    ejecutar_deliberacion_magi,
    normalizar_nombre_nodo,
    validar_aislamiento_herramienta,
)
from tools import ALL_MAGI_TOOLS, MAGI_TOOL_REGISTRY

mcp = FastMCP("magi-decision-system")


@mcp.tool()
async def deliberar_con_magi(dilema: str, contexto: str = "") -> dict[str, Any]:
    """Orquesta una deliberación completa del Sistema MAGI (Melchior, Balthazar, Casper + Mediador Ritsuko)."""
    veredicto = await ejecutar_deliberacion_magi(dilema=dilema, contexto=contexto)
    return {
        "veredicto_markdown": veredicto,
        "auditoria_herramientas_usadas": list(TRAZA_HERRAMIENTAS),
    }


@mcp.tool()
async def ejecutar_herramienta_magi(
    nombre_herramienta: str,
    argumentos: dict[str, Any] | None = None,
    nodo: str = "",
) -> dict[str, Any]:
    """Ejecuta una herramienta del Sistema MAGI validando el aislamiento de dominio por `nodo` y registrando su traza."""
    fn = MAGI_TOOL_REGISTRY.get(nombre_herramienta)
    if fn is None:
        return {
            "error": f"Herramienta '{nombre_herramienta}' no encontrada en el catálogo MAGI.",
            "herramientas_disponibles": [t.__name__ for t in ALL_MAGI_TOOLS],
        }

    if nodo and nodo.strip():
        valido, motivo = validar_aislamiento_herramienta(nodo, nombre_herramienta)
        if not valido:
            return {
                "error": motivo,
                "aislamiento_violado": True,
                "nodo": nodo,
                "herramienta": nombre_herramienta,
                "herramientas_permitidas_nodo": sorted(
                    NODE_ALLOWED_TOOLS.get(normalizar_nombre_nodo(nodo), set())
                ),
            }

    kwargs = argumentos or {}
    nodo_registrado = normalizar_nombre_nodo(nodo) if (nodo and nodo.strip()) else "directo"
    try:
        resultado = fn(**kwargs)
        TRAZA_HERRAMIENTAS.append(
            {
                "herramienta": nombre_herramienta,
                "args": kwargs,
                "nodo": nodo_registrado,
                "agente": nodo or "directo",
                "aislamiento_valido": True,
            }
        )
        return {
            "herramienta": nombre_herramienta,
            "nodo": nodo_registrado,
            "aislamiento_valido": True,
            "argumentos": kwargs,
            "resultado": resultado,
            "total_trazas_sesion": len(TRAZA_HERRAMIENTAS),
        }
    except Exception as exc:
        return {
            "error": f"Error al ejecutar '{nombre_herramienta}': {exc}",
            "herramienta": nombre_herramienta,
            "nodo": nodo_registrado,
            "argumentos": kwargs,
        }


if __name__ == "__main__":
    mcp.run()
