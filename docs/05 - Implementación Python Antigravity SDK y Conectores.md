# Implementación con Google Antigravity SDK (`google-antigravity`) y Conectores Simétricos

Este documento contiene el código Python completo para ejecutar el **Sistema MAGI + Mediador (`RITSUKO-0`)** utilizando las primitivas de `google-antigravity` (`Agent`, `LocalAgentConfig`, `types.SubagentConfig`, `@post_tool_call`) y `FastMCP`, garantizando **capacidades simétricas (`ALL_MAGI_TOOLS`)** en los 3 nodos deliberativos con **lentes cognitivas diferenciadas**, así como soporte dual para **Modo A (FastMCP + SDK)** y **Modo B (Orquestación Nativa en Antigravity IDE)**.

---

## 1. Herramientas Cuantitativas y Técnicas (`tools/melchior_tools.py`)

```python
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
        "archivos_infraestructura": infra,
        "archivos_python": len(list(raiz.rglob("*.py"))),
        "diagnostico": "Base técnica detectada" if infra else "Sin archivos de infraestructura base",
    }

MELCHIOR_TOOLS = [leer_metricas_sheet, calcular_viabilidad_y_roi, inspeccionar_recursos_tecnicos]
```

---

## 2. Herramientas Normativas y de Riesgo (`tools/balthazar_tools.py`)

```python
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
                texto = drive.files().export(
                    fileId=archivo["id"], mimeType="text/plain"
                ).execute().decode("utf-8")
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
        return {"mensaje": f"No existe {ruta_config}; aplicar criterios conservadores por defecto."}
    return {"archivo": ruta_config, "restricciones": archivo.read_text(encoding="utf-8")[:3000]}

BALTHAZAR_TOOLS = [buscar_y_leer_doc_drive, auditar_riesgos_y_fallos, verificar_limites_y_restricciones]
```

---

## 3. Herramientas Estratégicas y de Factor Humano (`tools/casper_tools.py`)

```python
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
```

---

## 4. Orquestador Principal con Capacidades Simétricas (`engine/magi_mediator.py`)

> **Principio de Simetría (`ALL_MAGI_TOOLS`):** Tanto el agente mediador padre (`LocalAgentConfig`) como los tres subagentes (`MELCHIOR-1`, `BALTHAZAR-2`, `CASPER-3`) reciben el arsenal completo `ALL_MAGI_TOOLS = MELCHIOR_TOOLS + BALTHAZAR_TOOLS + CASPER_TOOLS`. La diferenciación radica exclusivamente en su `description` y `system_instructions` (lente cognitiva).

```python
import asyncio
from pathlib import Path
from pydantic import BaseModel
from google.antigravity import Agent, LocalAgentConfig, types
from google.antigravity.hooks import post_tool_call

from tools import ALL_MAGI_TOOLS

class DictamenNodo(BaseModel):
    nodo: str
    lente_cognitiva: str
    voto: str                      # "A FAVOR" o "EN CONTRA"
    evidencia_herramientas: list[str]
    argumento_clave: str
    objecion_o_condicion: str

def leer_skill_body(skill_dir: str) -> str:
    texto = (Path(skill_dir) / "SKILL.md").read_text(encoding="utf-8")
    return texto.split("---", 2)[2].strip() if texto.startswith("---") else texto

# Hook de observabilidad para auditar qué herramienta invocó cada nodo
TRAZA_HERRAMIENTAS: list[dict] = []

@post_tool_call
async def auditar_llamada_herramienta(event):
    TRAZA_HERRAMIENTAS.append({
        "herramienta": event.tool_name,
        "args": event.tool_args,
    })
    return event

def crear_subagentes_magi() -> list[types.SubagentConfig]:
    return [
        types.SubagentConfig(
            name="melchior-ingeniera",
            description="MELCHIOR-1 (Lente Ingeniera/Científica): Evalúa lógica, métricas en Google Sheets, ROI y viabilidad técnica usando ALL_MAGI_TOOLS.",
            system_instructions=leer_skill_body(".agents/skills/melchior-ingeniera"),
            tools=list(ALL_MAGI_TOOLS),
        ),
        types.SubagentConfig(
            name="balthazar-madre",
            description="BALTHAZAR-2 (Lente Madre/Preservación): Evalúa seguridad, documentos en Google Drive, riesgos FMEA y límites en constraints.yaml usando ALL_MAGI_TOOLS.",
            system_instructions=leer_skill_body(".agents/skills/balthazar-madre"),
            tools=list(ALL_MAGI_TOOLS),
        ),
        types.SubagentConfig(
            name="casper-mujer",
            description="CASPER-3 (Lente Mujer/Propósito): Evalúa visión en VISION.md, costo de oportunidad y factor humano usando ALL_MAGI_TOOLS.",
            system_instructions=leer_skill_body(".agents/skills/casper-mujer"),
            tools=list(ALL_MAGI_TOOLS),
        ),
    ]

async def ejecutar_deliberacion_magi(dilema: str, contexto: str = "") -> str:
    """Ejecuta el ciclo completo: Mediador -> Ronda 1 Paralela -> Careo Ronda 2 -> Veredicto 2/3."""
    TRAZA_HERRAMIENTAS.clear()

    config_mediador = LocalAgentConfig(
        model="gemini-3.8-flash",
        system_instructions=leer_skill_body(".agents/skills/magi-mediador"),
        skills_paths=[".agents/skills/magi-mediador"],
        tools=list(ALL_MAGI_TOOLS),
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
        "exigiendo que cada uno use el arsenal simétrico ALL_MAGI_TOOLS desde su lente cognitiva y devuelva su DictamenNodo en JSON.\n"
        "3. Analiza las fricciones entre sus evidencias, formula una pregunta de careo dirigida a cada uno "
        "y ejecútalos en Ronda 2 para que confirmen o modifiquen su voto.\n"
        "4. Emite el Veredicto Final MAGI con el marcador de quórum (2/3) y el plan de acción."
    )

    async with Agent(config_mediador) as mediador:
        respuesta = await mediador.chat(prompt_deliberacion)
        veredicto = await respuesta.text()

    return veredicto
```

---

## 5. Servidor MCP Dual (`mcp_server.py`) para Antigravity App / IDE

Expone tanto `deliberar_con_magi` (Modo A — ciclo completo por SDK) como `ejecutar_herramienta_magi` (Modo B — ejecución directa de cualquiera de las 9 herramientas de `ALL_MAGI_TOOLS` por subagentes nativos con registro en `TRAZA_HERRAMIENTAS`):

```python
from mcp.server.fastmcp import FastMCP
from engine.magi_mediator import ejecutar_deliberacion_magi, TRAZA_HERRAMIENTAS
from tools import TOOL_REGISTRY

mcp = FastMCP("magi-decision-system")

@mcp.tool()
async def deliberar_con_magi(dilema: str, contexto: str = "") -> dict:
    """Orquesta una deliberación completa del Sistema MAGI (Melchior, Balthazar, Casper + Mediador Ritsuko)."""
    veredicto = await ejecutar_deliberacion_magi(dilema=dilema, contexto=contexto)
    return {
        "veredicto_markdown": veredicto,
        "auditoria_herramientas_usadas": list(TRAZA_HERRAMIENTAS),
    }

@mcp.tool()
async def ejecutar_herramienta_magi(nombre_herramienta: str, argumentos: dict | None = None) -> dict:
    """Ejecuta cualquiera de las 9 herramientas simétricas de ALL_MAGI_TOOLS y registra la llamada en TRAZA_HERRAMIENTAS."""
    fn = TOOL_REGISTRY.get(nombre_herramienta)
    if fn is None:
        return {"error": f"Herramienta desconocida: {nombre_herramienta}"}
    args = argumentos or {}
    resultado = fn(**args)
    TRAZA_HERRAMIENTAS.append({"herramienta": nombre_herramienta, "args": args})
    return {"herramienta": nombre_herramienta, "resultado": resultado}

if __name__ == "__main__":
    mcp.run()
```
