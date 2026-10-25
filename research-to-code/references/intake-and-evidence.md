# Análisis de fuente, procedencia y evidencia

## Antes de implementar

1. Identificar el tipo de fuente, título, responsables, DOI/ISBN/URL/ruta local, revisión o edición y fecha de acceso; no exigir un tipo de identificador específico.
2. Revisar erratas, anexos, revisiones y páginas relevantes. Comparar HTML y PDF, o transcripción y documento escaneado, cuando difieran en notación.
3. Buscar en el artículo y materiales de autores: pseudocódigo, código oficial, modelos, pesos, datasets, configuración de entrenamiento, evaluación, tablas de resultados y bibliografía.
4. Para software de terceros, registrar commit/hash, licencia, dependencia y procedencia. No ejecutar repositorios sin inspección/permiso.
5. Extraer tabla de afirmaciones con ubicación precisa, nivel: `textual`, `inferida`, `hipótesis`, `no_verificada`.
6. Establecer alcance realista y restricciones de acceso/cómputo antes del plan experimental.

## Hoja de lectura crítica

| Campo | Pregunta | Evidencia |
|---|---|---|
| Contribución | ¿Cuál es la novedad frente a baselines? | sección/página |
| Definiciones | ¿Qué significa cada símbolo, parámetro e índice? | definición literal |
| Algoritmo | ¿Qué pasos ordenados y criterios de parada? | algoritmo/ecuación |
| Optimización | ¿Se minimiza o maximiza, con qué restricciones? | sección |
| Estadística | ¿Qué variables/densidades/distribuciones? | ecuación |
| Datos | ¿Qué split, filtraciones y preprocesamiento? | tabla/apéndice |
| Métrica | ¿Cómo se computa exactamente? | texto/código |
| Resultados | ¿Qué cifras, errores, desviaciones y seeds? | tabla |
| Supuestos | ¿Qué condiciones exige la teoría? | teorema/apéndice |
| Disponibilidad | ¿Son accesibles datos, código y recursos? | URLs verificadas |

## Regla de oro de la incertidumbre

- Si falta el orden de ejes: nunca inferir silenciosamente `(batch, seq, dim)`.
- Si el artículo escribe `E[X]` sin distribución: documentar la distribución supuesta antes de muestrear.
- Si presenta curvas sin cifras: no afirmar coincidencia cuantitativa al comparar a ojo.
- Si código del autor difiere del PDF: conservar ambas versiones y reportar cuál se reprodujo.
- Si hay varias revisiones o ediciones: evitar mezclar fórmulas o resultados sin anotar de qué versión procede cada uno.

## Formato de cita en implementación

`tipo=documentation | titulo=Manual de referencia | version=rev-4 | seccion=3.2.1 | ecuacion=1 | interpretacion=literal | fuente=https://example.org/manual#3-2-1`

No se requiere redistribuir el material fuente ni su código para guardar trazabilidad. Respeta los derechos de autor y licencias.
