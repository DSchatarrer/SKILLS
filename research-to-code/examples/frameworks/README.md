# Equivalencias NumPy / PyTorch / TensorFlow

Ejemplos didácticos independientes de frameworks para la ecuación (1) del paper arXiv:1706.03762v7, **no** el Transformer completo.

- `framework_ops.py`: `torch_attention`, `tensorflow_attention`, `torch_indexed_sum`, `tensorflow_indexed_sum`.
- `tests/test_frameworks.py`: compara cada framework con una referencia NumPy implementada mediante bucles escalares; comprueba máscara booleana `True=permitido`, invariantes, shapes, precisión `float64`, gradientes y mutación de la escala. Para PyTorch contrasta también con `torch.nn.functional.scaled_dot_product_attention`. TensorFlow se contrasta además en `tf.function`.
- No se entrenan modelos ni se reproducen métricas experimentales.

## Ejecutar

```bash
python -m pip install numpy torch  # o instala PyTorch según tu hardware y la guía oficial
cd examples/frameworks
python -m unittest discover -s tests -v
```

Para TensorFlow, instala `tensorflow` en un entorno compatible con tu Python/SO según las instrucciones oficiales de TensorFlow. TensorFlow y PyTorch son **opcionales**, no se instala ninguno al ejecutar la Skill.

⚠️ Un test `skipped` **no demuestra corrección**. Consulta `test_report.json` para saber qué se probó en cada entorno.
