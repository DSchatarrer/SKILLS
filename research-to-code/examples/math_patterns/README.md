# Traducciones matemáticas ejecutables

Ejemplos independientes del paper concreto:

- `y_i = Σ_j A_ij x_j` → bucle y `np.einsum('ij,j->i',...)`.
- `E_p[X] = Σ_i p_i x_i` → producto ponderado, no media simple salvo uniforme.
- `h_{t+1}=A h_t + B x_t` → recurrencia `for`, con `h_0` explícito.

Ejecutar desde este directorio: `python -m unittest discover -s tests -v`.

Los ejemplos demuestran traducciones generales, NO validan por sí mismos ninguna publicación arXiv.

## Caso de aceptación independiente

Para `x=[2,10]`, `p=[0.9,0.1]`, el resultado calculado a mano es `2.8` y el gradiente analítico respecto de `x` es `[0.9,0.1]`. Esos son los valores esperados del test, **no** salidas capturadas de la función. `tests/test_math_patterns.py` contrasta ambos, con diferencias finitas centrales de dos pasos, y enseña qué defecto de una media uniforme quedaría expuesto.

Este ejemplo ilustra **cómo fijar** oráculos antes de codificar, pero la existencia de los archivos finales no demuestra el orden histórico en que fueron escritos. Para evaluar esa conducta en un agente real se requiere la traza descrita en `evals/test-first-rubric.md` (desde la raíz de la Skill).
