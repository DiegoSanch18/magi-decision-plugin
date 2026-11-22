# melchiorIngeniera — Nodo `MELCHIOR-1` (La Ingeniera / Científica)

## 1. Propósito General
`melchiorIngeniera` define la lente cognitiva del nodo **MELCHIOR-1** dentro del Sistema MAGI. Aunque dispone del arsenal simétrico completo de 9 herramientas (`ALL_MAGI_TOOLS`), su evaluación prioriza la verdad matemática, el cálculo de ROI, las métricas de Google Sheets y la viabilidad técnica de la infraestructura.

## 2. Arquitectura y Herramientas (`ALL_MAGI_TOOLS`)
- **Nivel:** Atómico / Especialista Deliberativo (`subagent: true`).
- **Herramientas Primarias de su Lente:**
  - `leer_metricas_sheet(rango, spreadsheet_id)`
  - `calcular_viabilidad_y_roi(costo_estimado, retorno_esperado, horas_esfuerzo)`
  - `inspeccionar_recursos_tecnicos(ruta_proyecto)`
- **Herramientas Simétricas Adicionales:** Acceso completo a las 6 herramientas restantes de riesgos/normativa y estrategia/propósito para verificación cruzada en Ronda 1 y Ronda 2.

## 3. Especificación de Entradas y Salidas
- **Entrada:** Brief neutral de decisión en Ronda 1 o Dossier de Careo con pregunta dirigida de `RITSUKO-0` en Ronda 2.
- **Salida:** Objeto JSON estructurado conforme a `DictamenNodo` (`nodo`, `lente_cognitiva`, `voto`, `evidencia_herramientas`, `argumento_clave`, `objecion_o_condicion`).

## 4. Auditoría de Seguridad (ClawScan)
- **Escáner:** `@openclaw/clawscan` (`--scanner clawscan-static`).
- **Resultado:** `0 CRITICAL`, `0 HIGH`.
- **Notas:** Especificación limpia en Markdown sin patrones de riesgo estático.
