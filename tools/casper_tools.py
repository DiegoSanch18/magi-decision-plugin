import os
from pathlib import Path


def consultar_bitacora_local(palabra_clave: str = "", subcarpeta: str = "notas") -> dict:
    """Lee archivos Markdown locales (VISION.md, bitácoras, retrospectivas) para evaluar coherencia estratégica."""
    base = Path(os.getenv("MAGI_WORKSPACE_DIR", ".")) / subcarpeta
    if not base.exists():
        return {"error": f"No existe el directorio {base}"}

    notas = []
    for md in sorted(base.rglob("*.md")):
        contenido = md.read_text(encoding="utf-8")
        if not palabra_clave or palabra_clave.lower() in contenido.lower():
            notas.append({"archivo": md.name, "extracto": contenido[:3000]})

    return {"archivos_encontrados": len(notas), "notas": notas[:4]}


def medir_costo_oportunidad(alternativa_actual: str, ventana_tiempo_meses: int) -> dict:
    """Evalúa la urgencia estratégica y el costo de postergar una decisión."""
    urgencia = "ALTA" if ventana_tiempo_meses <= 3 else "MEDIA" if ventana_tiempo_meses <= 9 else "BAJA"
    return {
        "alternativa_status_quo": alternativa_actual,
        "ventana_meses": ventana_tiempo_meses,
        "urgencia_estrategica": urgencia,
        "lectura": "Ventana crítica de oportunidad; postergar equivale a renunciar." if urgencia == "ALTA" else "Margen disponible para preparación.",
    }


def analizar_impacto_humano(contexto_equipo_o_usuario: str) -> dict:
    """Estructura el impacto en motivación, aprendizaje y energía vital."""
    return {
        "contexto_analizado": contexto_equipo_o_usuario,
        "eje_evaluado": "Alineación con propósito, autonomía y crecimiento sostenido",
    }


CASPER_TOOLS = [consultar_bitacora_local, medir_costo_oportunidad, analizar_impacto_humano]
