# Tipos de fuente y trazabilidad

**La fuente no determina si la Skill se activa; la tarea de implementar y verificar sí.** Aceptar artículos de revistas, conferencias, preprints, libros, tesis, manuales, notas de clase, documentación oficial, PDFs, informes técnicos, estándares, especificaciones internas y archivos locales. Una solicitud solo informativa (p. ej., fecha de publicación) no requiere esta Skill.

| Fuente | Identificar | Precaución principal |
|---|---|---|
| Artículo de revista o congreso | DOI, publicación, versión, erratas, apéndice | Texto aceptado vs preliminar, corrigendas |
| Preprint | ID propio, revisión, fecha, versión | Cambios entre versiones y diferencias con la publicada |
| Libro o capítulo | ISBN, edición, capítulo y página | Erratas, cambios de notación según edición |
| Tesis o informe | Autor, institución, fecha, páginas, archivo | Métodos no validados ni replicados |
| Manual/documentación | URL y versión de API o software, sección | Documentación mutable y semántica dependiente de versión |
| Norma/especificación | Organismo, número y revisión, sección | Requisitos normativos vs ejemplos ilustrativos |
| PDF local o texto aportado | Ruta, hash si procede, página/sección y revisión | Acceso limitado, transcripción/OCR y derechos de autor |

## Regla de evidencia

1. Guardar `source.type`, `source.title` y al menos un origen (`url`, `local_path` o `identifier`). No marcar `source.primary_source` verificado sin leer el material.
2. Localizar la ecuación, pseudocódigo o procedimiento; si no existe, registrar que el código es una *propuesta* y no una traducción literal.
3. Documentar valores, unidades, índices, ejes, restricciones y supuestos. Contrastar redondeos, convenciones de notación y reglas de dominio.
4. Distinguir teoría, resultados de tests y reproducción empírica; no afirmar equivalencia por mera coincidencia en algunos ejemplos.
5. Cuando la fuente sea mutable, fijar fecha, revisión, commit o copia comprobada. Respetar confidencialidad/licencia en fuentes internas.
