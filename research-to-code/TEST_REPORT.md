# Informe de pruebas: research-to-code

La Skill soporta artículos, libros, documentación, PDFs locales, tesis, informes y especificaciones técnicas. Esta revisión añade el protocolo de aceptación matemática *test-first* sin alterar la portabilidad entre agentes.

## Resultado

| Suite | Ejecutadas y aprobadas | Omitidas |
|---|---:|---:|
| `skill_scripts_and_mutation` | 35 | 0 |
| `attention_1706_03762v7` | 14 | 0 |
| `local_specification` | 6 | 0 |
| `math_translation` | 10 | 0 |
| `frameworks_pytorch_tensorflow` | 9 | 11 |
| `sparsemax_1602_02068v2` | 16 | 3 |

**Total de pruebas distintas: 90 ejecutadas y aprobadas, 14 omitidas.**

Las auditorías estructurales repiten algunos tests de los ejemplos, y no se cuentan dos veces.

## Verificación matemática test-first

- `SKILL.md` ordena registrar antes del código un microcaso discriminante y su prueba de aceptación independiente, sin extender este requisito a cada helper.
- `references/rigorous-testing.md` incluye protocolo, plantilla, limitaciones de diferencias finitas y manejo de oráculos ambiguos.
- `scripts/numeric_checks.py` incorpora `check_gradient`, que compara una derivada analítica independiente con diferencias centrales en dos pasos y devuelve el desacuerdo entre estimaciones.
- `examples/math_patterns/tests/test_math_patterns.py` comprueba gradiente analítico de esperanza ponderada y una mutación real de media sin ponderar.
- `evals/evals.json` incorpora escenarios 11 y 12 y `evals/test-first-rubric.md` exige trazas temporales fiables para afirmar orden test-first. Se añadieron regresiones estructurales, pero no se ha observado ningún agente ejecutando estos escenarios.

## Portabilidad y nuevas fuentes

- La misma Skill se instala para Codex y OpenCode en `.agents/skills/research-to-code`, y para Claude Code en `.claude/skills/research-to-code`. La ruta específica de OpenCode también está soportada.
- El generador utiliza `implementation_spec.json` (esquema 2.0) y admite URL, identificador general (p. ej. DOI o ISBN) o ruta a documento local; no requiere ninguna plataforma editorial.
- El caso `examples/local_specification` prueba un contrato matemático extraído de `SPECIFICATION.md` con cálculo manual, referencia por bucles, vectorización y tests adversarios.
- Se probaron rutas de instalación, reemplazo seguro, metadatos de Skill y ejecución del auditor de fuentes generalizadas.

## Limitaciones

- Las 14 pruebas de TensorFlow no se han ejecutado; TensorFlow no está disponible en este entorno.
- No hay ejecución end-to-end de Codex, OpenCode o Claude Code: solo instalación, lectura de metadatos y tests de código.
- Verificar estos ejemplos no garantiza traducir correctamente cualquier documento ni reproduce los resultados experimentales de un artículo.
- `test_report.json` conserva comandos, versiones y resultados observados.

## Repetición

```bash
python scripts/run_self_tests.py
python -m unittest discover -s tests -v
python scripts/audit_project.py --project examples/local_specification --run-tests --strict
```
