# Prueba real de arXiv:1602.02068v2 (Sparsemax)

Fuente primaria: [HTML del artículo, sección 2](https://arxiv.org/html/1602.02068v2#S2) / [Ficha arXiv](https://arxiv.org/abs/1602.02068).

**Alcance**: operador `sparsemax` en el último eje (Eqs. 2, 3, 4; Algoritmo 1), y jacobiano analítico para un vector (Eq. 12). Implementado en NumPy, PyTorch y TensorFlow como funciones distintas. **No** se implementa la pérdida `sparsemax loss` (Eq. 20), las arquitecturas ni los experimentos de clasificación del artículo.

**Traza matemática**:

- Eq. 2, proyección euclídea al simplex: `numpy_sparsemax`, `torch_sparsemax`, `tensorflow_sparsemax`. Contraste con minimización acotada SciPy SLSQP en `test_constrained_optimization_eq2`.
- Eqs. 3-4 y Alg. 1, ordenación, soporte, tau: mismas tres funciones; contraste con `sparsemax_bisection_reference` (búsqueda numérica, independiente de ordenación).
- Prop. 2, invariancia a traslación y permutación: `test_translation_invariance`, `test_permutation_invariance`.
- Eq. 6, hard sigmoid binaria: `test_binary_hard_sigmoid_eq6`.
- Eq. 12, jacobiano: `sparsemax_jacobian_reference` y tests de diferencias finitas, `torch.autograd.functional.jacobian`, `torch.autograd.gradcheck`; TensorFlow `GradientTape` si está disponible.

## Ejecución

```bash
cd examples/sparsemax_1602_02068
python -m unittest discover -s tests -v
```

Bibliotecas: NumPy obligatoria; SciPy, PyTorch y TensorFlow opcionales para sus respectivas suites. Ausencias se marcan como `skipped`; nunca se presentan como tests aprobados.

**Advertencia crítica:** `sparsemax` es diferenciable a trozos. En cambios de conjunto soporte, los gradientes unilaterales pueden diferir; se excluyen dichos puntos de `gradcheck`. Al principio de la prueba se eligió accidentalmente un punto de frontera en PyTorch y `gradcheck` falló. Reemplazar dicho punto por uno estrictamente interior permitió verificar el jacobiano sin cambiar el algoritmo. Se mantiene un test explícito que confirma la no diferenciabilidad de la frontera.
