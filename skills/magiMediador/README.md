# magiMediador — Mediador Central (`RITSUKO-0`) del Sistema MAGI

## 1. Propósito General
`magiMediador` es la skill orquestadora de nivel superior del plugin **MAGI Decision System**. Define el contrato operativo de **RITSUKO-0**, quien encuadra dilemas complejos, coordina la deliberación en dos rondas entre los tres núcleos (`MELCHIOR-1`, `BALTHAZAR-2`, `CASPER-3`) bajo **aislamiento estricto de herramientas por dominio** en Ronda 1, sintetiza y confronta la evidencia asimétrica en el careo de Ronda 2 y consolida el veredicto por mayoría (`2/3`).

## 2. Arquitectura y Aislamiento de Dominio
- **Nivel:** Orquestador (`Workbench / Pipeline`).
- **Nodos Subordinados y Subconjuntos Exclusivos (`NODE_ALLOWED_TOOLS`):**
  - `melchiorIngeniera` (`MELCHIOR-1` — `MELCHIOR_TOOLS`: Google Sheets, ROI, Infraestructura)
  - `balthazarMadre` (`BALTHAZAR-2` — `BALTHAZAR_TOOLS`: Google Drive, FMEA, `constraints.yaml`)
  - `casperMujer` (`CASPER-3` — `CASPER_TOOLS`: `notas/VISION.md`, Costo de Oportunidad, Impacto Humano)
- **Justificación del Aislamiento:** Evita sesgos cognitivos y contaminación cruzada en Ronda 1; sólo `RITSUKO-0` cruza los hallazgos entre dominios al formular el careo de Ronda 2.
- **Modos de Ejecución:**
  - **Modo A (MCP + SDK):** Invocación de `deliberar_con_magi` en `mcp_server.py` (`engine/magi_mediator.py`).
  - **Modo B (IDE Nativo):** Despacho paralelo de subagentes (`melchior-ingeniera`, `balthazar-madre`, `casper-mujer`) con `Model: "flash"` e invocación de herramientas validada por nodo (`ejecutar_herramienta_magi(..., nodo=...)`).

## 3. Especificación de Entradas y Salidas
- **Entradas:**
  - `dilema` (texto obligatorio): Decisión técnica, arquitectónica, financiera o estratégica a evaluar.
  - `contexto` (texto opcional): Restricciones de presupuesto, plazos, tamaño de equipo o antecedentes.
- **Salida:**
  - **Dossier Ejecutivo MAGI** en formato Markdown con: resolución de quórum (`2/3`), encuadre de `RITSUKO-0`, tabla comparativa Ronda 1 vs. Ronda 2 con evidencia aislada por dominio, síntesis del careo y plan de acción condicionado.

## 4. Ejemplo de Uso
```text
/magiMediador ¿Debemos migrar nuestro backend monolítico a microservicios este trimestre con un equipo de 4 desarrolladores y lanzamiento comercial en 10 semanas?
```

## 5. Auditoría de Seguridad (ClawScan)
- **Escáner:** `@openclaw/clawscan` (`--scanner clawscan-static`).
- **Resultado:** `0 CRITICAL`, `0 HIGH`.
- **Notas:** Skill puramente declarativa en Markdown; no contiene ejecución arbitraria de procesos, tuberías hacia shell ni exfiltración de variables sensibles.
