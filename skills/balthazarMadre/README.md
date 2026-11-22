# balthazarMadre — Nodo `BALTHAZAR-2` (La Madre / Núcleo de Preservación)

## 1. Propósito General
`balthazarMadre` define el contrato operativo y de aislamiento de dominio del nodo **BALTHAZAR-2** dentro del Sistema MAGI. Su misión es proteger la continuidad del sistema, auditar políticas en Google Drive, verificar límites operativos en `constraints.yaml` y prevenir fallos irreversibles mediante análisis FMEA, sin verse sesgada en Ronda 1 por promesas de ROI o entusiasmo estratégico.

## 2. Arquitectura y Herramientas Exclusivas (`BALTHAZAR_TOOLS`)
- **Nivel:** Atómico / Especialista Deliberativo (`subagent: true`).
- **Subconjunto Exclusivo Autorizado (`nodo="balthazar-madre"`):**
  - `buscar_y_leer_doc_drive(consulta)`
  - `auditar_riesgos_y_fallos(escenario, impacto_1_a_10, reversibilidad)`
  - `verificar_limites_y_restricciones(ruta_config)`
- **Aislamiento Forzado:** El motor (`validar_aislamiento_herramienta`) bloquea cualquier intento de `balthazar-madre` de ejecutar herramientas pertenecientes a `MELCHIOR_TOOLS` o `CASPER_TOOLS`.

## 3. Especificación de Entradas y Salidas
- **Entrada:** Brief neutral de decisión en Ronda 1 o Dossier de Careo con evidencia cruzada y pregunta dirigida de `RITSUKO-0` en Ronda 2.
- **Salida:** Objeto JSON estructurado conforme a `DictamenNodo` (`nodo`, `lente_cognitiva`, `voto`, `evidencia_herramientas`, `argumento_clave`, `objecion_o_condicion`).

## 4. Auditoría de Seguridad (ClawScan)
- **Escáner:** `@openclaw/clawscan` (`--scanner clawscan-static`).
- **Resultado:** `0 CRITICAL`, `0 HIGH`.
- **Notas:** Especificación limpia en Markdown sin patrones de riesgo estático.
