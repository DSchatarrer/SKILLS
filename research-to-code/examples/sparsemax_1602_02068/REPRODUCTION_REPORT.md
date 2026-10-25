# Informe de verificación: Sparsemax (arXiv:1602.02068v2)

- Fuente: https://arxiv.org/html/1602.02068v2 (consultada 2026-10-25), Sec. 2, Eqs. (2), (3), (4), (6) y (12), Proposición 2.
- Alcance verificado: evaluación del operador y derivadas en regiones con soporte fijo, NumPy y PyTorch CPU.
- Implementaciones: `sparsemax.py` (nativas NumPy, PyTorch, TensorFlow). Las versiones vectorizadas se contrastan con bisección de umbral independiente y con el optimizador SLSQP de SciPy para la definición como argmin.
- Comprobaciones matemáticas: pertenencia al simplex, ceros exactos, invariancia aditiva y bajo permutación, caso binario hard-sigmoid, jacobiano por diferencias finitas y `gradcheck` de PyTorch.
- Casos adversarios: eje de normalización equivocado y sustitución silenciosa por softmax, ambos detectados; caso no diferenciable de cambio de soporte separado de gradcheck.
- Limitaciones: no hay entrenamiento del modelo, pérdidas (Eq.20), datasets, comparación de tablas, GPU ni prueba TensorFlow si no está instalada.
- Grado de evidencia: **componente_verificado** en NumPy/PyTorch; TensorFlow **pendiente de ejecutar**. Auditoría estructural no certifica fidelidad al paper completo.

Consulta el resumen numérico de la versión empaquetada en `../../TEST_REPORT.md` y los logs JSON en `../../test_report.json`.
