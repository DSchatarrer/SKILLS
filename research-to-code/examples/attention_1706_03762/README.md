# Ejemplo evaluable de artículo real: arXiv:1706.03762v7

Se implementa únicamente el operador de atención de la ecuación (1) del paper. Requiere NumPy. Uso local y sin descargar archivos:

```bash
cd examples/attention_1706_03762
python -m unittest discover -s tests -v
```

Para probar en consola:

```python
import numpy as np
from attention import scaled_dot_product_attention
Q = np.array([[1., 0.]])
K = np.array([[1., 0.], [0., 1.]])
V = np.array([[10.], [20.]])
print(scaled_dot_product_attention(Q, K, V))
```

El operador permite una máscara booleana (`True`=posición permitida), y rechaza filas sin ninguna posición permitida para evitar pesos indeterminados. Se incluye una referencia lenta por bucles, usada para verificación cruzada. **No reproduce la arquitectura completa ni las métricas del paper**.
