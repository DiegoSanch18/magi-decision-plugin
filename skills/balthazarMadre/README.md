# balthazarMadre — Nodo `BALTHAZAR-2` (La Madre / Núcleo de Preservación)

## 1. Propósito General
`balthazarMadre` define la lente cognitiva del nodo **BALTHAZAR-2** dentro del Sistema MAGI. Con acceso simétrico a las 9 herramientas de `ALL_MAGI_TOOLS`, su misión es proteger la continuidad del sistema, auditar políticas en Google Drive, verificar límites operativos en `constraints.yaml` y prevenir fallos irreversibles mediante análisis FMEA.

## 2. Arquitectura y Herramientas (`ALL_MAGI_TOOLS`)
- **Nivel:** Atómico / Especialista Deliberativo (`subagent: true`).
- **Herramientas Primarias de su Lente:**
  - `buscar_y_leer_doc_drive(consulta)`
  - `auditar_riesgos_y_fallos(escenario, impacto_1_a_10, reversibilidad)`
  - `verificar_limites_y_restricciones(ruta_config)`
- **Herramientas Simétricas Adicionales:** Acceso completo a las 6 herramientas restantes de ingeniería/finanzas y propósito/factor humano para contrastar riesgos frente a retornos y carga de equipo.

## 3. Especificación de Entradas y Salidas
- **Entrada:** Brief neutral de decisión en Ronda 1 o Dossier de Careo con pregunta dirigida de `RITSUKO-0` en Ronda 2.
- **Salida:** Objeto JSON estructurado conforme a `DictamenNodo` (`nodo`, `lente_cognitiva`, `voto`, `evidencia_herramientas`, `argumento_clave`, `objecion_o_condicion`).

## 4. Auditoría de Seguridad (ClawScan)
- **Escáner:** `@openclaw/clawscan` (`--scanner clawscan-static`).
- **Resultado:** `0 CRITICAL`, `0 HIGH`.
- **Notas:** Especificación limpia en Markdown sin patrones de riesgo estático.
