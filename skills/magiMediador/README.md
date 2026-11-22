# magiMediador — Mediador Central (`RITSUKO-0`) del Sistema MAGI

## 1. Propósito General
`magiMediador` es la skill orquestadora de nivel superior del plugin **MAGI Decision System**. Define el contrato operativo de **RITSUKO-0**, quien encuadra dilemas complejos, coordina la deliberación en dos rondas entre los tres núcleos (`MELCHIOR-1`, `BALTHAZAR-2`, `CASPER-3`), modera el careo de evidencia cruzada y consolida el veredicto por mayoría (`2/3`).

## 2. Arquitectura y Componibilidad
- **Nivel:** Orquestador (`Workbench / Pipeline`).
- **Nodos Subordinados:**
  - `melchiorIngeniera` (`MELCHIOR-1` — Lente Científica/Ingeniera)
  - `balthazarMadre` (`BALTHAZAR-2` — Lente Protectora/Madre)
  - `casperMujer` (`CASPER-3` — Lente Intuitiva/Mujer)
- **Simetría de Herramientas (`ALL_MAGI_TOOLS`):** Los 3 nodos cuentan con acceso idéntico a las 9 herramientas del sistema, diferenciándose por su lente cognitiva.
- **Modos de Ejecución:**
  - **Modo A (MCP + SDK):** Invocación de `deliberar_con_magi` en `mcp_server.py` (`engine/magi_mediator.py`).
  - **Modo B (IDE Nativo):** Despacho paralelo de subagentes (`melchior-ingeniera`, `balthazar-madre`, `casper-mujer`) con `Model: "flash"` e invocación de herramientas vía `ejecutar_herramienta_magi`.

## 3. Especificación de Entradas y Salidas
- **Entradas:**
  - `dilema` (texto obligatorio): Decisión técnica, arquitectónica, financiera o estratégica a evaluar.
  - `contexto` (texto opcional): Restricciones de presupuesto, plazos, tamaño de equipo o antecedentes.
- **Salida:**
  - **Dossier Ejecutivo MAGI** en formato Markdown con: resolución de quórum (`2/3`), encuadre de `RITSUKO-0`, tabla comparativa Ronda 1 vs. Ronda 2 con evidencia de `ALL_MAGI_TOOLS`, síntesis del careo y plan de acción condicionado.

## 4. Ejemplo de Uso
```text
/magiMediador ¿Debemos migrar nuestro backend monolítico a microservicios este trimestre con un equipo de 4 desarrolladores y lanzamiento comercial en 10 semanas?
```

## 5. Auditoría de Seguridad (ClawScan)
- **Escáner:** `@openclaw/clawscan` (`--scanner clawscan-static`).
- **Resultado:** `0 CRITICAL`, `0 HIGH`.
- **Notas:** Skill puramente declarativa en Markdown; no contiene ejecución arbitraria de procesos, tuberías hacia shell ni exfiltración de variables sensibles.
