import os
from pathlib import Path
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES_DRIVE = ["https://www.googleapis.com/auth/drive.readonly"]


def buscar_y_leer_doc_drive(consulta: str) -> dict:
    """Busca documentos en Google Drive y extrae su texto para auditar límites o políticas."""
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    folder_id = os.getenv("MAGI_BALTHAZAR_DRIVE_FOLDER_ID", "")

    if not creds_path:
        return {"error": "Configura GOOGLE_APPLICATION_CREDENTIALS en .env"}

    try:
        creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES_DRIVE)
        drive = build("drive", "v3", credentials=creds)
        filtro_carpeta = f"and '{folder_id}' in parents " if folder_id else ""
        query = f"name contains '{consulta}' {filtro_carpeta}and trashed = false"

        archivos = drive.files().list(
            q=query, pageSize=3, fields="files(id, name, mimeType)"
        ).execute().get("files", [])

        extractos = []
        for archivo in archivos:
            if archivo["mimeType"] == "application/vnd.google-apps.document":
                raw_export = drive.files().export(
                    fileId=archivo["id"], mimeType="text/plain"
                ).execute()
                texto = raw_export.decode("utf-8") if isinstance(raw_export, (bytes, bytearray)) else str(raw_export)
                extractos.append({"documento": archivo["name"], "contenido": texto[:3500]})

        return {"coincidencias": len(extractos), "documentos": extractos}
    except Exception as exc:
        return {"error": f"Error consultando Google Drive: {exc}"}


def auditar_riesgos_y_fallos(escenario: str, impacto_1_a_10: int, reversibilidad: str) -> dict:
    """Evalúa severidad del peor escenario y nivel de reversibilidad ('alta', 'media', 'baja')."""
    rev = reversibilidad.strip().lower()
    riesgo_critico = impacto_1_a_10 >= 8 and rev == "baja"
    return {
        "escenario_evaluado": escenario,
        "impacto": impacto_1_a_10,
        "reversibilidad": rev,
        "alerta_critica": riesgo_critico,
        "dictamen_preventivo": "Requiere plan de contingencia obligatorio" if riesgo_critico else "Riesgo acotable",
    }


def verificar_limites_y_restricciones(ruta_config: str = "constraints.yaml") -> dict:
    """Lee restricciones locales documentadas en el proyecto."""
    archivo = Path(ruta_config)
    if not archivo.exists():
        base_env = Path(os.getenv("MAGI_WORKSPACE_DIR", ".")) / ruta_config
        if base_env.exists():
            archivo = base_env
        else:
            return {"mensaje": f"No existe {ruta_config}; aplicar criterios conservadores por defecto."}
    return {"archivo": str(ruta_config), "restricciones": archivo.read_text(encoding="utf-8")[:3000]}


BALTHAZAR_TOOLS = [buscar_y_leer_doc_drive, auditar_riesgos_y_fallos, verificar_limites_y_restricciones]
