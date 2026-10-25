# Catálogo de casos de prueba para evaluar implementaciones científicas

Los siguientes son **artículos reales**. Niveles de dificultad estimados **para implementar el componente indicado**, no los papers completos. Versión a fijar antes de iniciar un nuevo caso. La prueba de `Sparsemax` está implementada; los demás son propuestas (salvo la atención del Transformer existente).

| Orden | Artículo | arXiv | Nivel | Componente a traducir | Qué intentar refutar/probar |
|---|---|---|---|---|---|
| 1 | Layer Normalization (Ba et al., 2016) | https://arxiv.org/abs/1607.06450 | Baja | media, varianza, reescalado y traslación por última dimensión | ejes correctos, comparación con torch.nn.LayerNorm/tf.keras.layers.LayerNormalization con mismo epsilon, batch-size 1, gradiente, varianza sesgada |
| 2 | Adam: A Method for Stochastic Optimization (Kingma y Ba, 2014) | https://arxiv.org/abs/1412.6980 | Baja-media | actualización por momentos con corrección de sesgo | primeros pasos manuales, eps dentro/fuera de raíz, convergencia en cuadrática, reinicio de estado y variantes del optimizador |
| 3 | From Softmax to Sparsemax (Martins y Astudillo, 2016) | https://arxiv.org/abs/1602.02068 | Media | proyección al simplex y jacobiano por soporte | comparación con bisección y optimización restringida, sum=1, invariancias, estabilidad y no diferenciabilidad de frontera. **Ya implementado, pruebas reales** |
| 4 | Fourier Features Let Networks Learn High Frequency Functions (Tancik et al., 2020) | https://arxiv.org/abs/2006.10739 | Media | mapeo senoidal de Fourier, funciones periódicas y modelo de regresión sintético | shapes, escala 2pi, reproducibilidad con B fijo, grafo gradiente, generalización sin afirmar reproducción de benchmarks |
| 5 | RoFormer: Enhanced Transformer with Rotary Position Embedding (Su et al., 2021) | https://arxiv.org/abs/2104.09864 | Media-alta | pares de dimensiones, matrices de rotación y dot product con posición relativa | invariancia de norma, convención de pares, signo de ángulos, propiedad relativa, formas (batch,heads,seq,d) |
| 6 | Neural Ordinary Differential Equations (Chen et al., 2018; revisar v6, 2026) | https://arxiv.org/abs/1806.07366 | Alta | solver ODE, gradiente adjunto y tolerancias | resolver ODE contra solución analítica; RK4 vs solver adaptativo, gradientes, costo y sensibilidad a tolerancias |
| 7 | Attention Is All You Need (Vaswani et al., 2017) | https://arxiv.org/abs/1706.03762 | Media-alta | atención escalada Eq. 1 | scaling sqrt(d_k), máscara, softmax sobre eje correcto, gradientes y variantes multihead. **Ya implementado solo Eq.1** |

## Protocolo de evaluación cruzada por artículo

Para cualquier benchmark, crear `implementation_spec.json` con versión y secciones; traducir primero contrato de shapes, índices y supuestos; crear un oráculo matemático independiente de la implementación vectorizada; probar NumPy y PyTorch/TensorFlow si están instalados; ejecutar checks negativos deliberados; declarar los experimentos grandes y las pruebas omitidas explícitamente. No equiparar igualdad en un caso sintético con reproducción de resultados de investigación.

Fuentes primarias consultadas para estos ejemplos: artículos enlazados y HTML para Sparsemax, https://arxiv.org/html/1602.02068v2, y Layer Normalization, https://arxiv.org/html/1607.06450v1. Para Neural ODE, arXiv mostraba una revisión v6 de 9 oct 2026: registrar versión para evitar cambios de ecuaciones sin advertirlo.

## Casos agnósticos de repositorio o plataforma

| Tipo de fuente | Ejercicio | Error deliberado que se debe detectar |
|---|---|---|
| Manual técnico de una API | Contracción tensorial definida mediante índices | Eje de reducción equivocado |
| Libro de álgebra lineal | Resolver un sistema triangular mediante sustitución hacia delante | Índice off-by-one y división por diagonal cero |
| Especificación interna en Markdown o PDF | Media ponderada o actualización recursiva | Confundir pesos con promedio simple; indexar mal el primer paso |
| Tesis o informe metodológico | Estimador estadístico con supuestos | Sesgo por denominador incorrecto y error en intervalos |

Estos cuatro casos no exigen ningún servidor de preprints ni identificador especial. La entrada puede ser una ruta local, URL, ISBN, DOI o documento aportado por el usuario.
