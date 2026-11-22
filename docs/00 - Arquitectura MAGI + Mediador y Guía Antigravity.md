# Sistema MAGI + Mediador Central (`RITSUKO-0`) para Google Antigravity

Este paquete contiene la especificación completa y lista para implementar de un **sistema multi-agente de toma de decisiones** inspirado en *Neon Genesis Evangelion*, construido sobre el **Google Antigravity SDK (`google-antigravity`)**, **FastMCP** y el estándar abierto de **Agent Skills (`SKILL.md`)**.

---

## 1. Arquitectura de 4 Agentes: Capacidades Simétricas (`ALL_MAGI_TOOLS`) y Lentes Cognitivas

A diferencia de un debate plano entre tres agentes, la incorporación de un **Mediador Central (`RITSUKO-0`)** evita cámaras de eco y dirige el careo antes de emitir el veredicto por mayoría (`2/3`). Los **3 Nodos Deliberativos (`MELCHIOR-1`, `BALTHAZAR-2`, `CASPER-3`)** poseen **exactamente las mismas capacidades operativas y acceso al arsenal completo de 9 herramientas (`ALL_MAGI_TOOLS`)**, diferenciándose exclusivamente por su **lente cognitiva y filosófica**:

```text
                        ┌──────────────────────────────────┐
                        │     USUARIO / ANTIGRAVITY IDE    │
                        │  Comando: /magiMediador o MCP    │
                        └─────────────────┬────────────────┘
                                          │ Dilema bruto
                                          ▼
                        ┌──────────────────────────────────┐
                        │      RITSUKO-0 (MEDIADOR)        │
                        │  • Encuadra y desambigua dilema  │
                        │  • Orquesta Ronda 1 y Ronda 2    │
                        │  • Formula careo y cierra quórum │
                        └───┬─────────────┬────────────┬───┘
                            │             │            │
         ┌──────────────────┘             │            └──────────────────┐
         ▼                                ▼                               ▼
┌─────────────────┐              ┌─────────────────┐              ┌─────────────────┐
│   MELCHIOR-1    │              │   BALTHAZAR-2   │              │    CASPER-3     │
│  (La Ingeniera) │              │   (La Madre)    │              │   (La Mujer)    │
├─────────────────┤              ├─────────────────┤              ├─────────────────┤
│ • Lente: Lógica,│              │ • Lente: Riesgo,│              │ • Lente: Visión,│
│   ROI y Técnica │              │   FMEA y Límites│              │   Timing/Humano │
│ • ALL_MAGI_TOOLS│              │ • ALL_MAGI_TOOLS│              │ • ALL_MAGI_TOOLS│
└─────────────────┘              └─────────────────┘              └─────────────────┘
```

### Ciclo de Deliberación en 4 Fases y Ejecución Dual (Modo A y Modo B)
- **Modo A (FastMCP + Antigravity SDK):** Mediante la herramienta MCP `deliberar_con_magi(dilema, contexto)`, que instancia `LocalAgentConfig` y los 3 `SubagentConfig` con `tools=ALL_MAGI_TOOLS` y el hook `@post_tool_call`.
- **Modo B (Orquestación Nativa en Antigravity IDE):** Mediante `/magiMediador`, donde el coordinador invoca a los subagentes declarativos (`melchior-ingeniera`, `balthazar-madre`, `casper-mujer`) con `Model: "flash"`, quienes ejecutan cualquiera de las 9 herramientas vía MCP `ejecutar_herramienta_magi` o CLI `python -m tools.cli`.

1. **Fase 0 — Encuadre (Mediador):** `RITSUKO-0` limpia el dilema del usuario, identifica variables faltantes y redacta un *Brief Neutral* para que los 3 nodos evalúen exactamente el mismo problema.
2. **Fase 1 — Investigación Aislada (Ronda 1 en Paralelo):** Los 3 subagentes se ejecutan de forma concurrente sin verse entre sí. Cada uno consulta el arsenal simétrico `ALL_MAGI_TOOLS` (Sheets, ROI, infraestructura, Drive, FMEA, `constraints.yaml`, `VISION.md`, costo de oportunidad e impacto humano) desde su lente cognitiva y emite su dictamen inicial (`DictamenNodo`).
3. **Fase 2 — Careo Moderado (Mediador → Ronda 2):** `RITSUKO-0` analiza las contradicciones entre los hallazgos (ej. *Melchior muestra ROI positivo en Sheets, pero Balthazar encontró un límite contractual en Drive/`constraints.yaml`*) y envía **preguntas cruzadas dirigidas** a cada nodo para una segunda ronda de réplica.
4. **Fase 3 — Veredicto y Quórum (`2/3`):** El Mediador contabiliza los votos definitivos, registra si hubo cambios de postura entre rondas, sintetiza las condiciones obligatorias de mitigación y entrega el **Dossier Ejecutivo MAGI**.

---

## 2. Estructura de Archivos del Proyecto (`C:\git\magi-decision-plugin`)

```text
magi-decision-plugin/
├── plugin.json                           # Manifiesto del plugin nativo Antigravity
├── mcp_config.json                       # Configuración Stdio fija (.venv\Scripts\python.exe)
├── README.md                             # Documentación general del repositorio y plugin
├── .env.example                          # Plantilla de credenciales y IDs de Sheets/Drive
├── constraints.yaml                      # Restricciones operativas, presupuestarias y de SLA
├── pyproject.toml                        # Dependencias (google-antigravity, gspread, mcp, etc.)
├── mcp_server.py                         # Servidor FastMCP (deliberar_con_magi + ejecutar_herramienta_magi)
├── assets/
│   └── logo.svg                          # Ícono vectorial de los 3 monolitos MAGI + RITSUKO-0
├── engine/
│   └── magi_mediator.py                  # Orquestador principal con Antigravity SDK
├── tools/
│   ├── __init__.py                       # Exporta ALL_MAGI_TOOLS (las 9 herramientas)
│   ├── melchior_tools.py                 # Conector Google Sheets + cálculos financieros e infra
│   ├── balthazar_tools.py                # Conector Google Drive + auditoría FMEA y constraints
│   ├── casper_tools.py                   # Conector Markdown local + costo de oportunidad y humano
│   └── cli.py                            # Interfaz CLI para invocación desde Modo B
├── notas/
│   └── VISION.md                         # Bitácora estratégica leída desde ALL_MAGI_TOOLS
├── agents/                               # Subagentes declarativos del plugin (model: flash)
│   ├── melchior-ingeniera.md
│   ├── balthazar-madre.md
│   └── casper-mujer.md
├── skills/                               # Skills nativas en camelCase con documentación dual
│   ├── magiMediador/                     # SKILL.md + README.md
│   ├── melchiorIngeniera/                # SKILL.md + README.md
│   ├── balthazarMadre/                   # SKILL.md + README.md
│   └── casperMujer/                      # SKILL.md + README.md
└── .agents/
    └── skills/                           # Espejo kebab-case para compatibilidad SDK
        ├── magi-mediador/SKILL.md
        ├── melchior-ingeniera/SKILL.md
        ├── balthazar-madre/SKILL.md
        └── casper-mujer/SKILL.md
```

---

## 3. Instalación y Configuración de Entorno

### Paso 1: Instalar el entorno virtual, SDK y conectores
```bash
pip install google-antigravity pydantic gspread google-auth google-api-python-client mcp pyyaml
```

### Paso 2: Configurar `.env`
```env
# Autenticación Antigravity SDK / Gemini
GEMINI_API_KEY="tu_api_key_aqui"

# Credenciales de Google Cloud (Service Account en modo solo lectura)
GOOGLE_APPLICATION_CREDENTIALS="/ruta/segura/service-account.json"

# Fuentes de datos consultables desde ALL_MAGI_TOOLS
MAGI_MELCHIOR_SHEET_ID="1A2B3C4D5E6F7G8H9I0J"
MAGI_BALTHAZAR_DRIVE_FOLDER_ID="1ISoLiSI2_dc6TuNQ44pFaNnKnyZZP0Ic"
MAGI_WORKSPACE_DIR="."
```

> **Importante:** Comparte tanto tu hoja de cálculo de Google Sheets como la carpeta de Google Drive con el correo `...@...iam.gserviceaccount.com` de tu Service Account en modo **Lector**.
