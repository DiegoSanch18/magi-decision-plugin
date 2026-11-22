# casperMujer — Nodo `CASPER-3` (La Mujer / Intuición y Propósito Vital)

## 1. Propósito General
`casperMujer` define la lente cognitiva del nodo **CASPER-3** dentro del Sistema MAGI. Con acceso simétrico a las 9 herramientas de `ALL_MAGI_TOOLS`, evalúa cada decisión a través de la coherencia con la visión estratégica (`notas/VISION.md`), el costo de oportunidad de postergar la acción y el impacto en la motivación y propósito del equipo humano.

## 2. Arquitectura y Herramientas (`ALL_MAGI_TOOLS`)
- **Nivel:** Atómico / Especialista Deliberativo (`subagent: true`).
- **Herramientas Primarias de su Lente:**
  - `consultar_bitacora_local(palabra_clave, subcarpeta)`
  - `medir_costo_oportunidad(alternativa_actual, ventana_tiempo_meses)`
  - `analizar_impacto_humano(contexto_equipo_o_usuario)`
- **Herramientas Simétricas Adicionales:** Acceso completo a las 6 herramientas restantes de ingeniería/finanzas y riesgos/cumplimiento para evaluar si el potencial estratégico compensa el esfuerzo técnico y las restricciones operativas.

## 3. Especificación de Entradas y Salidas
- **Entrada:** Brief neutral de decisión en Ronda 1 o Dossier de Careo con pregunta dirigida de `RITSUKO-0` en Ronda 2.
- **Salida:** Objeto JSON estructurado conforme a `DictamenNodo` (`nodo`, `lente_cognitiva`, `voto`, `evidencia_herramientas`, `argumento_clave`, `objecion_o_condicion`).

## 4. Auditoría de Seguridad (ClawScan)
- **Escáner:** `@openclaw/clawscan` (`--scanner clawscan-static`).
- **Resultado:** `0 CRITICAL`, `0 HIGH`.
- **Notas:** Especificación limpia en Markdown sin patrones de riesgo estático.
