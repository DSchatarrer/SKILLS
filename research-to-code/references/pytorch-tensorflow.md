# Implementar y verificar papers con PyTorch y TensorFlow

**Objetivo**: traducir la misma ecuación a código idiomático de cada backend; conservar shapes, índices, precisión y gradientes. No basta cambiar imports. La tabla da correspondencias candidatas, no identidades universales.

| Matemática | NumPy / Python (referencia) | PyTorch | TensorFlow |
|---|---|---|---|
| `y_i=Σ_j A_ij x_j` | `A@x` / bucles | `torch.einsum('ij,j->i',A,x)` | `tf.einsum('ij,j->i',A,x)` |
| `Σ_j x_ij` | `np.sum(x,axis=-1)` | `torch.sum(x,dim=-1)` | `tf.reduce_sum(x,axis=-1)` |
| `C_bik=Σ_j A_bij B_bjk` | `np.einsum('bij,bjk->bik',A,B)` | `torch.einsum('bij,bjk->bik',A,B)` | `tf.einsum('bij,bjk->bik',A,B)` |
| `AB` | `A@B` | `torch.matmul(A,B)` | `tf.linalg.matmul(A,B)` |
| `A^T` (últimos ejes) | `np.swapaxes(A,-1,-2)` | `A.transpose(-2,-1)` | `tf.linalg.matrix_transpose(A)` |
| `softmax(x)_i` | `exp(x-max)/Σ exp(...)` | `torch.softmax(x,dim=-1)` | `tf.nn.softmax(x,axis=-1)` |
| `E_p[f(X)]` discreta | `np.sum(p*f,axis=...)` | `torch.sum(p*f,dim=...)` | `tf.reduce_sum(p*f,axis=...)` |
| `log Σ_i exp(x_i)` | `scipy.special.logsumexp` | `torch.logsumexp(x,dim=-1)` | `tf.reduce_logsumexp(x,axis=-1)` |
| `∇_θ L` | derivada / diferencias finitas | `torch.autograd.grad(L,theta)` | `tape.gradient(L,theta)` |
| `θ ← θ−η∇L` | actualización explícita | `optimizer.step()` con `zero_grad()` | `optimizer.apply_gradients(...)` |
| `h_{t+1}=f(h_t,x_t)` | bucle Python | bucle conservando autograd, `torch.scan` solo si API disponible | `tf.scan`, `tf.while_loop` o bucle eager |
| `1{cond}` | `np.where(cond,a,b)` | `torch.where(cond,a,b)` | `tf.where(cond,a,b)` |
| `mean(x)` | `np.mean(x)` | `torch.mean(x)` | `tf.reduce_mean(x)` |

## Contrato antes de seleccionar framework

1. Fija dimensión, unidad y dtype por símbolo; identifica índices libres y contraídos, ejes de reducción y batch.
2. Implementa referencia simple en Python/NumPy **independiente** de la función del framework.
3. Implementa operaciones nativas conservando el grafo de gradientes. No uses `.detach()`, `.item()`, `.numpy()`, conversiones a lista ni `np.array` dentro del cálculo diferenciable; sus usos en validación eager o tests pueden ser aceptables, pero impiden tracing o gradientes si aparecen en el camino activo.
4. Comprueba equivalencia con float64 primero; después prueba float32, dispositivos, mixed precision y `tf.function` o compilación cuando se requieran. Registrar tolerancias según dtype/backend y diferencias de kernels.
5. Con `mask` bool de atención, declara expresamente `True=permitido` (como `torch.nn.functional.scaled_dot_product_attention`) o `True=bloqueado` (otras APIs pueden invertir el significado). Prueba filas completamente enmascaradas y que las probabilidades de las claves prohibidas sean cero.
6. En el TensorFlow de modo grafo usa `tf.shape(x)` para dimensiones dinámicas en vez de `int(x.shape[d])`; con `tf.GradientTape` recuerda observar constantes (`tape.watch(x)`) o utilizar `tf.Variable`.
7. Para PyTorch usa `requires_grad_(True)`, `torch.autograd.gradcheck` con float64 y evita `torch.no_grad()` en el forward cuya derivada se evalúa. Gradientes finitos no bastan: comparar gradiente correcto con diferencias centrales cuando es suave.
8. Si el paper requiere entrenar, documenta `tf.keras`/`torch.nn.Module`, optimizador, loss reduction (`mean` vs `sum`), inicialización, seeds, normalización, métricas, estado del modelo, checkpoints y dataset/splits. Una demostración de Eq.1 no reproduce entrenamiento.
9. `tf.function`/tracing y operaciones in-place requieren tests separados: el comportamiento de ejecución eager no demuestra que compilen ni que conserven gradientes en modo grafo.

## Ejemplos verificables

`examples/frameworks/framework_ops.py`: `torch_indexed_sum`, `tensorflow_indexed_sum`, `torch_attention`, `tensorflow_attention` para la Eq.1 de arXiv:1706.03762v7. `examples/frameworks/tests/test_frameworks.py` compara con oracle de bucles NumPy; además `gradcheck`, `GradientTape`, máscaras y una mutación con escalado incorrecto. Los tests `skip` por dependencia ausente NO cuentan como ejecutados.

```
cd examples/frameworks
python -m unittest discover -s tests -v
```

Fuentes: [PyTorch gradcheck](https://docs.pytorch.org/docs/stable/generated/torch.autograd.gradcheck.html), [PyTorch SDPA](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html), [TensorFlow autodiff](https://www.tensorflow.org/guide/autodiff), [TensorFlow softmax](https://www.tensorflow.org/api_docs/python/tf/nn/softmax).
