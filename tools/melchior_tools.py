import os
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials

SCOPES_SHEETS = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def leer_metricas_sheet(rango: str = "A1:F30", spreadsheet_id: str = "") -> dict:
    """Lee un rango de celdas desde Google Sheets para análisis financiero o de métricas."""
    sheet_id = spreadsheet_id or os.getenv("MAGI_MELCHIOR_SHEET_ID", "")
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

    if not sheet_id or not creds_path:
        return {"error": "Configura MAGI_MELCHIOR_SHEET_ID y GOOGLE_APPLICATION_CREDENTIALS en .env"}

    try:
        creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES_SHEETS)
        cliente = gspread.authorize(creds)
        hoja = cliente.open_by_key(sheet_id).sheet1
        valores = hoja.get(rango)
        if not valores:
            return {"registros": [], "mensaje": "Rango vacío en la hoja de cálculo."}
        encabezados, filas = valores[0], valores[1:]
        return {
            "fuente": f"Google Sheet ({sheet_id})",
            "total_filas": len(filas),
            "datos": [dict(zip(encabezados, fila)) for fila in filas],
        }
    except Exception as exc:
        return {"error": f"Error leyendo Google Sheets: {exc}"}


def calcular_viabilidad_y_roi(costo_estimado: float, retorno_esperado: float, horas_esfuerzo: int) -> dict:
    """Calcula ROI porcentual, beneficio neto y retorno por hora invertida."""
    roi = ((retorno_esperado - costo_estimado) / costo_estimado * 100) if costo_estimado > 0 else 0.0
    valor_hora = (retorno_esperado - costo_estimado) / horas_esfuerzo if horas_esfuerzo > 0 else 0.0
    return {
        "roi_porcentaje": round(roi, 2),
        "beneficio_neto": round(retorno_esperado - costo_estimado, 2),
        "retorno_por_hora": round(valor_hora, 2),
        "viable_cuantitativamente": roi >= 15.0 and valor_hora > 0,
    }


def inspeccionar_recursos_tecnicos(ruta_proyecto: str = ".") -> dict:
    """Inspecciona infraestructura y archivos técnicos en el workspace local."""
    raiz = Path(ruta_proyecto)
    infra = [
        p.name for p in raiz.glob("*")
        if p.name in {"pyproject.toml", "package.json", "Dockerfile", "docker-compose.yml", "requirements.txt"}
    ]
    return {
        "archivos_infraestructura": sorted(infra),
        "archivos_python": len(list(raiz.rglob("*.py"))),
        "diagnostico": "Base técnica detectada" if infra else "Sin archivos de infraestructura base",
    }


MELCHIOR_TOOLS = [leer_metricas_sheet, calcular_viabilidad_y_roi, inspeccionar_recursos_tecnicos]
