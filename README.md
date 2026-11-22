# MAGI Decision System + Mediador Central (`RITSUKO-0`)

Plugin nativo y servidor MCP para **Google Antigravity** que implementa un sistema multi-agente de deliberación y toma de decisiones inspirado en *Neon Genesis Evangelion*, construido sobre **Google Antigravity SDK (`google-antigravity`)**, **Agent Skills (`SKILL.md`)** y **FastMCP**.

---

## 1. Arquitectura de Aislamiento Estricto de Dominio y Síntesis en el Mediador

El Sistema MAGI opera con **4 agentes**: un Mediador Central (`RITSUKO-0`) que no vota y dirige el proceso, y **3 Nodos Deliberativos** (`MELCHIOR-1`, `BALTHAZAR-2`, `CASPER-3`) con **aislamiento estricto de herramientas y fuentes de datos por dominio (`MELCHIOR_TOOLS`, `BALTHAZAR_TOOLS`, `CASPER_TOOLS`)**.

### ¿Por qué Aislamiento Estricto por Nodo?
En la **Ronda 1 (Investigación Aislada)**, cada nodo accede **exclusivamente** a las 3 herramientas de su dominio. Esto elimina el ruido inter-dominio y evita el sesgo de confirmación o contaminación cognitiva (por ejemplo, impide que `MELCHIOR-1` suavice un cálculo de ROI negativo por simpatía con `VISION.md`, o que `CASPER-3` autocensure una apuesta estratégica por leer antes de tiempo una matriz conservadora de riesgos). La traducción y confrontación de evidencia asimétrica ocurre **exclusivamente a través de `RITSUKO-0` en la Ronda 2 (Careo Moderado)**:

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
                        │  • Fase 1: Despacha Ronda 1 aislada    │
                        │  • Fase 2: Cruza evidencia (Ronda 2)   │
                        │  • Fase 3: Cierra quórum 2/3 + Dossier │
                        └───┬───────────────┬────────────────┬───┘
                            │               │                │
         ┌──────────────────┘               │                └──────────────────┐
         ▼                                  ▼                                   ▼
┌─────────────────────┐            ┌─────────────────────┐            ┌─────────────────────┐
│     MELCHIOR-1      │            │     BALTHAZAR-2     │            │      CASPER-3       │
│   (La Ingeniera)    │            │     (La Madre)      │            │     (La Mujer)      │
├─────────────────────┤            ├─────────────────────┤            ├─────────────────────┤
│ • Dominio Exclusivo:│            │ • Dominio Exclusivo:│            │ • Dominio Exclusivo:│
│   MELCHIOR_TOOLS (3)│            │   BALTHAZAR_TOOLS(3)│            │   CASPER_TOOLS (3)  │
│ • Google Sheets,    │            │ • Google Drive,     │            │ • VISION.md local,  │
│   ROI e Infra       │            │   FMEA y Constraints│            │   Timing y Humano   │
│ • Thinking: HIGH    │            │ • Thinking: MED     │            │ • Thinking: LOW     │
└─────────────────────┘            └─────────────────────┘            └─────────────────────┘
```

### Matriz de Herramientas Exclusivas por Nodo (`NODE_ALLOWED_TOOLS`)

| Nodo Exclusivo | Subconjunto | Herramienta | Propósito |
| :--- | :--- | :--- | :--- |
| **`MELCHIOR-1`** (`melchior-ingeniera`) | `MELCHIOR_TOOLS` | `leer_metricas_sheet(rango, spreadsheet_id)` | Lee KPIs, presupuestos y métricas reales desde Google Sheets (`spreadsheets.readonly`). |
| **`MELCHIOR-1`** (`melchior-ingeniera`) | `MELCHIOR_TOOLS` | `calcular_viabilidad_y_roi(costo_estimado, retorno_esperado, horas_esfuerzo)` | Calcula ROI porcentual, beneficio neto, retorno por hora y viabilidad (`ROI >= 15%`). |
| **`MELCHIOR-1`** (`melchior-ingeniera`) | `MELCHIOR_TOOLS` | `inspeccionar_recursos_tecnicos(ruta_proyecto)` | Audita archivos de infraestructura (`pyproject.toml`, `Dockerfile`, etc.) y módulos Python del workspace. |
| **`BALTHAZAR-2`** (`balthazar-madre`) | `BALTHAZAR_TOOLS` | `buscar_y_leer_doc_drive(consulta)` | Busca y exporta documentos normativos, contratos y políticas en Google Drive (`drive.readonly`). |
| **`BALTHAZAR-2`** (`balthazar-madre`) | `BALTHAZAR_TOOLS` | `auditar_riesgos_y_fallos(escenario, impacto_1_a_10, reversibilidad)` | Evalúa severidad FMEA, radio de impacto (*blast radius*) y alerta crítica (`impacto >= 8` y reversibilidad `baja`). |
| **`BALTHAZAR-2`** (`balthazar-madre`) | `BALTHAZAR_TOOLS` | `verificar_limites_y_restricciones(ruta_config)` | Inspecciona topes presupuestarios, SLAs y restricciones operativas en `constraints.yaml`. |
| **`CASPER-3`** (`casper-mujer`) | `CASPER_TOOLS` | `consultar_bitacora_local(palabra_clave, subcarpeta)` | Lee bitácoras estratégicas y propósito en Markdown local (`notas/VISION.md`). |
| **`CASPER-3`** (`casper-mujer`) | `CASPER_TOOLS` | `medir_costo_oportunidad(alternativa_actual, ventana_tiempo_meses)` | Determina urgencia estratégica (`ALTA <= 3m`, `MEDIA <= 9m`, `BAJA > 9m`) y costo de postergar. |
| **`CASPER-3`** (`casper-mujer`) | `CASPER_TOOLS` | `analizar_impacto_humano(contexto_equipo_o_usuario)` | Estructura el impacto sobre motivación, autonomía, aprendizaje y desgaste del equipo. |

> **Nota del Antigravity SDK:** El agente padre (`LocalAgentConfig` de `RITSUKO-0`) registra la unión de las 9 herramientas (`ALL_MAGI_TOOLS`) como requisito del runtime del SDK para habilitar el despacho a subagentes, mientras que cada `SubagentConfig` recibe únicamente su lista aislada de 3 herramientas (`MELCHIOR_TOOLS`, `BALTHAZAR_TOOLS` o `CASPER_TOOLS`).

---

## 2. Ejecución Dual: Modo A (FastMCP + SDK) y Modo B (Nativo en Antigravity IDE)

El plugin soporta dos modalidades de ejecución con cumplimiento forzado del aislamiento por nodo (`validar_aislamiento_herramienta`):

### Modo A — Servidor MCP (`deliberar_con_magi` vía Antigravity SDK)
- Expuesto por `mcp_server.py` (`FastMCP("magi-decision-system")`).
- La herramienta MCP `deliberar_con_magi(dilema, contexto)` instancia `LocalAgentConfig` y los 3 `SubagentConfig` en `engine/magi_mediator.py`, asignando a cada nodo únicamente sus 3 herramientas exclusivas y auditando cada invocación mediante el hook `@post_tool_call` (`auditar_llamada_herramienta`) en `TRAZA_HERRAMIENTAS`.

### Modo B — Orquestación Nativa en Antigravity IDE (`/magiMediador`)
- Al invocar `/magiMediador`, el agente principal asume el rol de **RITSUKO-0** y coordina directamente a los subagentes declarativos (`melchior-ingeniera`, `balthazar-madre`, `casper-mujer`) definidos en `agents/` y `skills/`.
- Cada subagente invoca únicamente sus 3 herramientas autorizadas identificando su nodo (`nodo="<nombre-nodo>"` o `--node <nombre-nodo>`), siendo bloqueada cualquier llamada cruzada fuera de su dominio:
  1. Vía MCP: `ejecutar_herramienta_magi(nombre_herramienta, argumentos, nodo="melchior-ingeniera")`, o
  2. Vía CLI local: `python -m tools.cli --node melchior-ingeniera <nombre_herramienta> --json-args '{...}'`.

---

## 3. Estructura del Proyecto y Plugin

```text
magi-decision-plugin/
├── plugin.json                           # Manifiesto oficial del plugin Antigravity
├── mcp_config.json                       # Configuración Stdio fija hacia .venv\Scripts\python.exe
├── mcp_server.py                         # Servidor FastMCP (deliberar_con_magi + ejecutar_herramienta_magi con guardián de nodo)
├── pyproject.toml                        # Configuración de paquete y dependencias Python
├── .env.example                          # Plantilla de variables de entorno
├── constraints.yaml                      # Límites operativos, presupuestarios y regulatorios (Balthazar-2)
├── assets/
│   └── logo.svg                          # Ícono vectorial de los 3 monolitos MAGI + RITSUKO-0
├── notas/
│   └── VISION.md                         # Bitácora de visión estratégica (Casper-3)
├── tools/
│   ├── __init__.py                       # Exporta MELCHIOR_TOOLS, BALTHAZAR_TOOLS, CASPER_TOOLS y ALL_MAGI_TOOLS
│   ├── melchior_tools.py                 # Herramientas exclusivas de Melchior-1 (Sheets, ROI, Infra)
│   ├── balthazar_tools.py                # Herramientas exclusivas de Balthazar-2 (Drive, FMEA, Constraints)
│   ├── casper_tools.py                   # Herramientas exclusivas de Casper-3 (VISION.md, Costo Oportunidad, Humano)
│   └── cli.py                            # Runner CLI con validación de aislamiento (--node)
├── engine/
│   ├── __init__.py
│   └── magi_mediator.py                  # Orquestador SDK con aislamiento por SubagentConfig y NODE_ALLOWED_TOOLS
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
    └── test_magi_integration.py          # Suite pytest de integración, aislamiento por dominio y hooks
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
