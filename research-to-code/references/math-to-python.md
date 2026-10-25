# Traducción rigurosa de matemáticas a Python

**No hay correspondencia sintáctica universal.** Identifica primero dominio, dimensiones, índices libres/reducidos, supuestos y si la igualdad es exacta, numérica o estadística. Para cada ecuación incluye: expresión, tabla de símbolos y shapes, referencia lenta, versión eficiente, prueba de equivalencia y condiciones límite.

## Diccionario de patrones

| Matemática | Traducción candidata | Atención a |
|---|---|---|
| `Σ_{i=1}^n x_i` | `sum(x)` o `np.sum(x, axis=...)` | El eje reducido, límites y array vacío |
| `Σ_j A_ij B_jk` | `A @ B` / `np.einsum('ij,jk->ik', A, B)` | Shapes `(m,n)@(n,p)`; queda `(m,p)` |
| `Π_i x_i` | `np.prod(x, axis=...)` | Under/overflow; log-producto si aplicable |
| `A^T` | `A.T` / `np.swapaxes(A,-1,-2)` | `.T` invierte todos los ejes en nD |
| `x·y` | `np.dot(x,y)` / `np.sum(x*y,axis=-1)` | Shapes y producto hermítico en complejos |
| `||x||_2` | `np.linalg.norm(x,axis=-1)` | Normas escalares vs por lote |
| `argmax_i x_i` | `np.argmax(x,axis=...)` | Índice base 0 y empates |
| `1{condición}` | `np.where(cond,1,0)` | Booleanos y broadcasting |
| `softmax(x)_i` | `exp(x_i-max(x))/sum(exp(x-max(x)))` | Estabilidad, eje correcto, máscara total |
| `log Σ exp(x_i)` | `scipy.special.logsumexp(x,axis=...)` | Overflow al usar forma ingenua |
| `E_p[f(X)]` discreta | `np.sum(p*f(x),axis=...)` | `p≥0`, `sum(p)=1`, soporte |
| `E_p[f(X)]` por muestreo | `mean(f(sample))` | Estimador + incertidumbre, no igualdad exacta |
| `∫_a^b f(x)dx` | `scipy.integrate.quad` / `trapezoid` | Cuadratura + tolerancia y singularidades |
| `dx/dt = f(t,x)` | `scipy.integrate.solve_ivp` | Método y errores; Euler es aproximación |
| `x_{t+1}=f(x_t,θ)` | `for t in range(T): ...` o `scan` | Inicialización, orden y truncación |
| `∇_θ L` | derivada analítica, `torch.autograd.grad` o `tf.GradientTape` | `requires_grad` / `tape.watch`, gradiente y grafo |
| `θ←θ−η∇L` | paso de descenso de gradiente | Minimización; signo, tasa y update |
| `argmin_θ f(θ)` | búsqueda discreta o optimizador | Restricciones, óptimo local, tolerancias |
| `P(A|B)` | `P(A∩B)/P(B)` | `P(B)>0`; densidades ≠ probabilidades |
| `a*b` convolución | `np.convolve` / `scipy.signal.convolve` | Padding, stride, convolución vs correlación |
| `O(·)` complejidad | análisis asintótico | No se implementa como operación matemática |

## Ejemplo 1: sumatorio → bucle → vectorizado

Ecuación: `y_i = Σ_{j=1}^m A_{ij} x_j`. Shapes `A:(n,m)`, `x:(m,)`, `y:(n,)`.

```python
import numpy as np

def reference(A, x):
    n, m = A.shape
    assert x.shape == (m,)
    return np.array([sum(A[i, j] * x[j] for j in range(m)) for i in range(n)])

def fast(A, x):
    return A @ x

A = np.array([[1., 2.], [3., 4.]])
x = np.array([5., 6.])
np.testing.assert_allclose(reference(A, x), fast(A, x))
```

**Pregunta clave**: si el sumatorio solo reduce `j`, `i` queda libre. Un `np.sum(A*x)` indiscriminado aplana índices y destruye el shape.

## Ejemplo 2: esperanza matemática ≠ media siempre

Para `E_p[X] = Σ_i p_i x_i`:

```python
x = np.array([2., 10.])
p = np.array([0.9, 0.1])
assert np.all(p >= 0) and np.isclose(p.sum(), 1)
expected = np.dot(p, x)  # 2.8, no 6.0
```

Una media simple solo es equivalente con probabilidades uniformes o con muestras representativas bajo condiciones estadísticas especificadas.

## Ejemplo 3: recurrencia temporal

`h_t = tanh(W h_{t-1} + U x_t + b)` necesita orden temporal explícito; no se sustituye automáticamente por un producto matricial único. Para `t=1..T`:

```python
h = h0.copy()
for t in range(T):
    h = np.tanh(W @ h + U @ x[t] + b)
```

## Ejemplo 4: contracción de tensores

`C_{bik} = Σ_j A_{bij} B_{bjk}`: `np.einsum('bij,bjk->bik', A, B)`; también `A @ B` si coinciden lotes. Comparar contra bucles anidados y comprobar no mezclar dimensión `b` con `j`.

## Diagnósticos de errores frecuentes

- Off-by-one: matemáticas `i=1..n` vs Python `range(n)`, y si hay término `i=0`.
- Variables libres o índices mudos: repetir un índice en `einsum` implica contracción, salvo salida explícita.
- Denominadores o normalizadores incorrectos (`n` vs `n-1`, media vs suma, `sqrt(d_k)`).
- Softmax sobre el eje de características en lugar del eje de claves.
- `sum` de tensores multidimensionales vs `np.sum` con eje explícito.
- Error de tipos: enteros, float32, float64, complejo, overflow, underflow, NaN.
- Gradiente: orientación columna/fila, transpuestas y signo; gradcheck con float64.
- Monte Carlo: reportar error estándar o CI; no confundir estimador con esperanza teórica.
- Criterios de parada: tolerancia, número máximo de pasos y casos no convergentes.
- Convenciones: métrica, normalización, unidades físicas, tiempo continuo vs discreto, zero-based indexing.

## Estrategia de comprobación

1. Resuelve manualmente un caso con 2–3 elementos.
2. Ejecuta la versión explícita de referencia sobre entradas deterministas.
3. Ejecuta la vectorizada sobre las mismas entradas.
4. Contrasta con `np.testing.assert_allclose` y tolerancias justificadas.
5. Prueba shape, boundary, inputs inválidos, gran escala numérica y propiedades (linealidad, simetría, invariancia, etc.).
6. Si hay derivadas, compara autodiff con diferencias centrales solo en puntos suaves y float64. Evita usar diferencias finitas como oráculo en discontinuidades.

Fuentes: https://numpy.org/doc/stable/reference/generated/numpy.einsum.html ; https://docs.pytorch.org/docs/stable/generated/torch.autograd.gradcheck.html


## Equivalencias de frameworks

Para PyTorch/TensorFlow (sumatorios, `einsum`, atención, gradientes, máscaras y recurrencias), consulta **[pytorch-tensorflow.md](pytorch-tensorflow.md)** y `examples/frameworks/`; valida siempre `axis`/`dim`, shape, tipo, precisión y semántica de máscara. Una instrucción en NumPy **no es** implementación TensorFlow/PyTorch salvo portar y probar.
