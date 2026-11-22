"""CLI de ejecución de herramientas MAGI con validación de aislamiento por nodo (Modo B).

Uso:
    python -m tools.cli --list
    python -m tools.cli --node melchior-ingeniera calcular_viabilidad_y_roi --json-args '{"costo_estimado": 1000, "retorno_esperado": 1500, "horas_esfuerzo": 20}'
"""

import argparse
import inspect
import json
import sys
from typing import Any

from tools import ALL_MAGI_TOOLS, MAGI_TOOL_REGISTRY
from engine.magi_mediator import (
    NODE_ALLOWED_TOOLS,
    normalizar_nombre_nodo,
    validar_aislamiento_herramienta,
)


def _dominio_de_herramienta(nombre_fn: str) -> str:
    for nodo, permitidas in NODE_ALLOWED_TOOLS.items():
        if nombre_fn in permitidas:
            return nodo
    return "compartido"


def listar_herramientas() -> dict[str, Any]:
    catalogo = []
    for fn in ALL_MAGI_TOOLS:
        sig = inspect.signature(fn)
        parametros = {
            k: {
                "tipo": getattr(v.annotation, "__name__", str(v.annotation)),
                "default": None if v.default is inspect.Parameter.empty else v.default,
                "requerido": v.default is inspect.Parameter.empty,
            }
            for k, v in sig.parameters.items()
        }
        catalogo.append(
            {
                "nombre": fn.__name__,
                "nodo_exclusivo": _dominio_de_herramienta(fn.__name__),
                "descripcion": (fn.__doc__ or "").strip(),
                "parametros": parametros,
            }
        )
    return {
        "total_herramientas": len(catalogo),
        "aislamiento_por_nodo": {k: sorted(v) for k, v in NODE_ALLOWED_TOOLS.items()},
        "herramientas": catalogo,
    }


def ejecutar_cli(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        prog="python -m tools.cli",
        description="Ejecuta herramientas del Sistema MAGI respetando el aislamiento de dominio por nodo (`--node`).",
    )
    parser.add_argument(
        "tool_name",
        nargs="?",
        help="Nombre de la herramienta MAGI a ejecutar.",
    )
    parser.add_argument(
        "--node",
        default="",
        help="Identificador del nodo que invoca la herramienta (`melchior-ingeniera`, `balthazar-madre`, `casper-mujer`).",
    )
    parser.add_argument(
        "--json-args",
        default="{}",
        help="Objeto JSON con los argumentos de la herramienta.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Lista las 9 herramientas disponibles y su asignación exclusiva por nodo.",
    )

    args = parser.parse_args(argv)

    if args.list:
        print(json.dumps(listar_herramientas(), ensure_ascii=False, indent=2))
        return 0

    if not args.tool_name:
        parser.error("Debes especificar `tool_name` o usar `--list`.")

    fn = MAGI_TOOL_REGISTRY.get(args.tool_name)
    if fn is None:
        error_payload = {
            "error": f"Herramienta desconocida: '{args.tool_name}'",
            "herramientas_disponibles": list(MAGI_TOOL_REGISTRY.keys()),
        }
        print(json.dumps(error_payload, ensure_ascii=False, indent=2))
        return 1

    if args.node:
        valido, motivo = validar_aislamiento_herramienta(args.node, args.tool_name)
        if not valido:
            isolation_payload = {
                "error": motivo,
                "aislamiento_violado": True,
                "nodo": args.node,
                "herramienta": args.tool_name,
            }
            print(json.dumps(isolation_payload, ensure_ascii=False, indent=2))
            return 1

    try:
        parsed_kwargs = json.loads(args.json_args) if args.json_args else {}
        if not isinstance(parsed_kwargs, dict):
            raise ValueError("--json-args debe ser un objeto JSON (dict).")
    except Exception as exc:
        print(
            json.dumps(
                {"error": f"JSON inválido en --json-args: {exc}"},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    try:
        resultado = fn(**parsed_kwargs)
        nodo_tag = normalizar_nombre_nodo(args.node) if args.node else "directo"
        salida = {
            "herramienta": args.tool_name,
            "nodo": nodo_tag,
            "aislamiento_valido": True,
            "argumentos": parsed_kwargs,
            "resultado": resultado,
        }
        print(json.dumps(salida, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(
            json.dumps(
                {"error": f"Error ejecutando '{args.tool_name}': {exc}"},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1


if __name__ == "__main__":
    sys.exit(ejecutar_cli())
