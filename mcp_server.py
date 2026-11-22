"""Servidor FastMCP (`mcp_server.py`) del Sistema MAGI para Google Antigravity IDE.

Expone dos herramientas MCP complementarias:
1. `deliberar_con_magi` (Modo A): Orquesta una deliberación completa del Sistema MAGI
   (RITSUKO-0 + MELCHIOR-1, BALTHAZAR-2, CASPER-3) mediante el motor `engine.magi_mediator`.
2. `ejecutar_herramienta_magi` (Modo B): Permite a cualquiera de los subagentes nativos
   de Antigravity (`melchior-ingeniera`, `balthazar-madre`, `casper-mujer`) o al Mediador
   invocar simétricamente cualquiera de las 9 herramientas de `ALL_MAGI_TOOLS`,
   registrando la auditoría en `TRAZA_HERRAMIENTAS`.
"""

from dataclasses import dataclass
from typing import Any

try:
    from mcp.server.fastmcp import FastMCP  # type: ignore
except ModuleNotFoundError:
    from mcp.server.mcpserver import MCPServer as FastMCP  # type: ignore
from engine.magi_mediator import (
    TRAZA_HERRAMIENTAS,
    auditar_llamada_herramienta,
    ejecutar_deliberacion_magi,
)
from tools import ALL_MAGI_TOOLS, MAGI_TOOL_REGISTRY

mcp = FastMCP("magi-decision-system")


@dataclass
class _MCPToolEvent:
    tool_name: str
    tool_args: dict[str, Any]
    agent_name: str = "mcp-client"


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
    """Ejecuta cualquiera de las 9 herramientas simétricas de `ALL_MAGI_TOOLS` y registra su traza de auditoría."""
    fn = MAGI_TOOL_REGISTRY.get(nombre_herramienta)
    if fn is None:
        return {
            "error": f"Herramienta '{nombre_herramienta}' no encontrada en ALL_MAGI_TOOLS.",
            "herramientas_disponibles": [t.__name__ for t in ALL_MAGI_TOOLS],
        }

    kwargs = argumentos or {}
    try:
        resultado = fn(**kwargs)
        evento = _MCPToolEvent(
            tool_name=nombre_herramienta,
            tool_args=kwargs,
            agent_name=nodo or "mcp-node",
        )
        await auditar_llamada_herramienta(evento)
        return {
            "herramienta": nombre_herramienta,
            "nodo": nodo or "simetrico",
            "argumentos": kwargs,
            "resultado": resultado,
            "total_trazas_sesion": len(TRAZA_HERRAMIENTAS),
        }
    except Exception as exc:
        return {
            "error": f"Error al ejecutar '{nombre_herramienta}': {exc}",
            "herramienta": nombre_herramienta,
            "argumentos": kwargs,
        }


if __name__ == "__main__":
    mcp.run()
