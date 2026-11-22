# MAGI Decision System + Mediador Central (`RITSUKO-0`)

Plugin nativo y servidor MCP para **Google Antigravity** que implementa un sistema multi-agente de deliberación y toma de decisiones inspirado en *Neon Genesis Evangelion*, construido sobre **Google Antigravity SDK (`google-antigravity`)**, **Agent Skills (`SKILL.md`)** y **FastMCP**.

---

## 1. Arquitectura de Capacidades Simétricas y Lentes Cognitivas Diferenciadas

El Sistema MAGI opera con **4 agentes**: un Mediador Central (`RITSUKO-0`) que no vota y dirige el proceso, y **3 Nodos Deliberativos** (`MELCHIOR-1`, `BALTHAZAR-2`, `CASPER-3`) que cuentan con **capacidades de herramientas 100% simétricas (`ALL_MAGI_TOOLS`)**, diferenciándose exclusivamente por su **lente cognitiva y filosófica**:

```text
                        ┌────────────────────────────────────────┐
                        │        USUARIO / ANTIGRAVITY IDE       │
                        │   Comando: /magiMediador o MCP Tool    │
                        └───────────────────┬────────────────────┘
                                            │ Dilema bruto
                                            ▼
                        ┌────────────────────────────────────────┐
                        │          RITSUKO-0 (MEDIADOR)          │
                        │  • Fase 0: Encuadra dilema binario     │
                        │  • Fase 1: Despacha Ronda 1 paralela   │
                        │  • Fase 2: Formula careo (Ronda 2)     │
                        │  • Fase 3: Cierra quórum 2/3 + Dossier │
                        └───┬───────────────┬────────────────┬───┘
                            │               │                │
         ┌──────────────────┘               │                └──────────────────┐
         ▼                                  ▼                                   ▼
┌─────────────────────┐            ┌─────────────────────┐            ┌─────────────────────┐
│     MELCHIOR-1      │            │     BALTHAZAR-2     │            │      CASPER-3       │
│   (La Ingeniera)    │            │     (La Madre)      │            │     (La Mujer)      │
├─────────────────────┤            ├─────────────────────┤            ├─────────────────────┤
│ • Lente: Empírica,  │            │ • Lente: Protectora,│            │ • Lente: Estratégica│
│   lógica, ROI y     │            │   continuidad, FMEA │            │   propósito, timing │
│   viabilidad técnica│            │   y cumplimiento    │            │   y factor humano   │
│ • Arsenal Simétrico:│            │ • Arsenal Simétrico:│            │ • Arsenal Simétrico:│
│   ALL_MAGI_TOOLS (9)│            │   ALL_MAGI_TOOLS (9)│            │   ALL_MAGI_TOOLS (9)│
└─────────────────────┘            └─────────────────────┘            └─────────────────────┘
```

### Arsenal Simétrico Completo (`ALL_MAGI_TOOLS` — 9 Herramientas)

Todos los nodos (`MELCHIOR-1`, `BALTHAZAR-2`, `CASPER-3`) pueden invocar cualquiera de las 9 herramientas del sistema para auditar la realidad desde su respectiva lente cognitiva:

| Dominio | Herramienta | Propósito |
| :--- | :--- | :--- |
| **Cuantitativo y Técnico** | `leer_metricas_sheet(rango, spreadsheet_id)` | Lee KPIs, presupuestos y métricas reales desde Google Sheets (`spreadsheets.readonly`). |
| **Cuantitativo y Técnico** | `calcular_viabilidad_y_roi(costo_estimado, retorno_esperado, horas_esfuerzo)` | Calcula ROI porcentual, beneficio neto, retorno por hora y viabilidad (`ROI >= 15%`). |
| **Cuantitativo y Técnico** | `inspeccionar_recursos_tecnicos(ruta_proyecto)` | Audita archivos de infraestructura (`pyproject.toml`, `Dockerfile`, etc.) y módulos Python del workspace. |
| **Normativo y Riesgos** | `buscar_y_leer_doc_drive(consulta)` | Busca y exporta documentos normativos, contratos y políticas en Google Drive (`drive.readonly`). |
| **Normativo y Riesgos** | `auditar_riesgos_y_fallos(escenario, impacto_1_a_10, reversibilidad)` | Evalúa severidad FMEA, radio de impacto (*blast radius*) y alerta crítica (`impacto >= 8` y reversibilidad `baja`). |
| **Normativo y Riesgos** | `verificar_limites_y_restricciones(ruta_config)` | Inspecciona topes presupuestarios, SLAs y restricciones operativas en `constraints.yaml`. |
| **Estratégico y Humano** | `consultar_bitacora_local(palabra_clave, subcarpeta)` | Lee bitácoras estratégicas y propósito en Markdown local (`notas/VISION.md`). |
| **Estratégico y Humano** | `medir_costo_oportunidad(alternativa_actual, ventana_tiempo_meses)` | Determina urgencia estratégica (`ALTA <= 3m`, `MEDIA <= 9m`, `BAJA > 9m`) y costo de postergar. |
| **Estratégico y Humano** | `analizar_impacto_humano(contexto_equipo_o_usuario)` | Estructura el impacto sobre motivación, autonomía, aprendizaje y desgaste del equipo. |

---

## 2. Ejecución Dual: Modo A (FastMCP + SDK) y Modo B (Nativo en Antigravity IDE)

El plugin soporta dos modalidades de ejecución complementarias:

### Modo A — Servidor MCP (`deliberar_con_magi` vía Antigravity SDK)
- Expuesto por `mcp_server.py` (`FastMCP("magi-decision-system")`).
- La herramienta MCP `deliberar_con_magi(dilema, contexto)` instancia `LocalAgentConfig` y los 3 `SubagentConfig` en `engine/magi_mediator.py`, asignando `ALL_MAGI_TOOLS` a todos los nodos y registrando cada invocación mediante el hook `@post_tool_call` (`auditar_llamada_herramienta`) en `TRAZA_HERRAMIENTAS`.

### Modo B — Orquestación Nativa en Antigravity IDE (`/magiMediador`)
- Al invocar `/magiMediador`, el agente principal asume el rol de **RITSUKO-0** y coordina directamente a los subagentes declarativos (`melchior-ingeniera`, `balthazar-madre`, `casper-mujer`) definidos en `agents/` y `skills/`.
- Cada nodo ejecuta cualquiera de las 9 herramientas de `ALL_MAGI_TOOLS` a través de:
  1. La herramienta MCP `ejecutar_herramienta_magi(nombre_herramienta, argumentos)` del servidor `magi-decision-system`, o
  2. La interfaz CLI local: `python -m tools.cli <nombre_herramienta> --json-args '{...}'`.

---

## 3. Estructura del Proyecto y Plugin

```text
magi-decision-plugin/
├── plugin.json                           # Manifiesto oficial del plugin Antigravity
├── mcp_config.json                       # Configuración Stdio fija hacia .venv\Scripts\python.exe
├── mcp_server.py                         # Servidor FastMCP (deliberar_con_magi + ejecutar_herramienta_magi)
├── pyproject.toml                        # Configuración de paquete y dependencias Python
├── .env.example                          # Plantilla de variables de entorno
├── constraints.yaml                      # Límites operativos, presupuestarios y regulatorios
├── assets/
│   └── logo.svg                          # Ícono vectorial de los 3 monolitos MAGI + RITSUKO-0
├── notas/
│   └── VISION.md                         # Bitácora de visión estratégica y objetivos a largo plazo
├── tools/
│   ├── __init__.py                       # Exporta ALL_MAGI_TOOLS (las 9 herramientas)
│   ├── melchior_tools.py                 # Herramientas cuantitativas, Sheets y ROI
│   ├── balthazar_tools.py                # Herramientas normativas, Drive, FMEA y constraints
│   ├── casper_tools.py                   # Herramientas estratégicas, VISION.md y factor humano
│   └── cli.py                            # Runner CLI para invocación desde subagentes nativos
├── engine/
│   ├── __init__.py
│   └── magi_mediator.py                  # Orquestador SDK con capacidades simétricas y hook @post_tool_call
├── agents/
│   ├── melchior-ingeniera.md             # Subagente declarativo MELCHIOR-1 (model: flash)
│   ├── balthazar-madre.md                # Subagente declarativo BALTHAZAR-2 (model: flash)
│   └── casper-mujer.md                   # Subagente declarativo CASPER-3 (model: flash)
├── skills/
│   ├── magiMediador/                     # Skill orquestadora RITSUKO-0 (SKILL.md + README.md)
│   ├── melchiorIngeniera/                # Skill nodo MELCHIOR-1 (SKILL.md + README.md)
│   ├── balthazarMadre/                   # Skill nodo BALTHAZAR-2 (SKILL.md + README.md)
│   └── casperMujer/                      # Skill nodo CASPER-3 (SKILL.md + README.md)
├── .agents/
│   └── skills/                           # Espejo kebab-case para compatibilidad directa con el SDK
│       ├── magi-mediador/SKILL.md
│       ├── melchior-ingeniera/SKILL.md
│       ├── balthazar-madre/SKILL.md
│       └── casper-mujer/SKILL.md
├── docs/                                 # Especificaciones arquitectónicas de referencia (00 a 05)
└── tests/
    └── test_magi_integration.py          # Suite pytest de integración, simetría y hooks
```

---

## 4. Configuración e Instalación

### 1. Entorno Virtual y Dependencias
```powershell
cd C:\git\magi-decision-plugin
python -m venv .venv
.\.venv\Scripts\pip install -e ".[dev]"
```

### 2. Variables de Entorno (`.env`)
Copia `.env.example` a `.env` y configura tus credenciales (Google Sheets y Drive operan en modo **estrictamente solo lectura**):
```env
GEMINI_API_KEY="tu_api_key_aqui"
GOOGLE_APPLICATION_CREDENTIALS="C:/ruta/segura/service-account.json"
MAGI_MELCHIOR_SHEET_ID="1A2B3C4D5E6F7G8H9I0J"
MAGI_BALTHAZAR_DRIVE_FOLDER_ID="1ISoLiSI2_dc6TuNQ44pFaNnKnyZZP0Ic"
MAGI_WORKSPACE_DIR="C:/git/magi-decision-plugin"
```

### 3. Pruebas Automatizadas y Auditoría ClawScan
```powershell
.\.venv\Scripts\pytest tests/test_magi_integration.py -v
clawscan.cmd C:\git\magi-decision-plugin\skills\magiMediador --scanner clawscan-static --output C:\git\magi-decision-plugin\clawscan-results\magiMediador.json
```
