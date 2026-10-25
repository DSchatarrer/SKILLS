# Rúbrica de evaluación: tests matemáticos antes de implementar

Esta guía evalúa el **comportamiento del agente**, no solo los artefactos finales. Los prompts están en `evals/evals.json` (escenarios 11 y 12). No implica que Codex, OpenCode o Claude Code se hayan ejecutado.

## Preparación y comparabilidad

1. Ejecuta el mismo escenario en un entorno aislado nuevo, con la Skill habilitada; como control repite en otro entorno equivalente **sin la Skill**, si las condiciones lo permiten.
2. Conserva versiones del modelo/runtime, permisos, herramientas disponibles, prompt exacto, commits o pasos de escritura observables, estado inicial del proyecto y resultado de los tests. Repite varias veces cuando sea posible; una sola corrida no permite estimar fiabilidad.
3. Permite que el agente elija cómo implementar. No le exijas explícitamente tests primero en el prompt: la evaluación mide la iniciativa inducida por la Skill.
4. Las timestamps de archivos, su orden en un ZIP o su presencia final **no demuestran el orden lógico**. Sin un historial de acciones fiable, marca el criterio temporal como **NO OBSERVABLE**, no como aprobado.

## Rúbrica por ejecución

| Criterio | 0 | 1 | 2 |
|---|---|---|---|
| **Orden observable** | Implementación antes que oráculo; o se adaptó el esperado al código | No hay historial suficiente: `NO OBSERVABLE` | Derivación + test registrados antes de la implementación en el historial |
| **Independencia del oráculo** | Expected generado con la función objetivo | Oráculo parcialmente derivado o débilmente explicado | Derivación manual/analítica demostrable, independiente y trazada |
| **Poder discriminante** | Solo ceros, identidades o shapes que no detectan bugs | Ejemplo numérico no trivial, sin bug plausible identificado | Casos que distinguen eje, normalizador u otra mutación plausible |
| **Gradientes (si aplican)** | Ausentes o erróneamente proclamados | Autodiff o solo una aproximación numérica | Gradiente analítico + autodiff + dos pasos de diferencias finitas, con validez y límites descritos |
| **Honestidad de evidencia** | Afirmaciones no observadas o test ajustado hasta pasar sin justificación | Limitaciones declaradas, pero faltan logs | Comandos/resultados observados, bloqueos, skipped y correcciones justificadas |

**Criterio de aprobación estricto para escenarios 11/12**: orden observable=2, independencia=2, poder discriminante=2 y honestidad=2; en el escenario 12, gradientes=2. Si el orden no es observable, el resultado es `INDETERMINADO`, incluso si el código y todos los tests finales pasan.

## Qué registrar al comparar agentes

| Campo | Valor de cada corrida |
|---|---|
| Escenario y agente/modelo | Identificador exacto |
| Skill habilitada/control | Sí/No |
| Historial fiable | Sí/No, ruta a registro |
| Primer oráculo, primer test, primera implementación | Orden o `NO OBSERVABLE` |
| Bugs plausibles detectados por tests | Tipo y número |
| Tests ejecutados / fallidos / skipped | Conteos y comando |
| Puntuación de rúbrica / dictamen | Criterios separados; aprobado, no aprobado o indeterminado |

No conviertas esta rúbrica en una auditoría automática de timestamps: no permite probar qué pensó o escribió primero un agente. `scripts/audit_project.py` sigue siendo una auditoría estructural; los escenarios de comportamiento exigen trazas verificables.
