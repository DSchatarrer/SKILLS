# Pirámide de tests para implementación científica

## 1. Sintaxis y ejecución

- Importación sin side effects, ejecución de ejemplo pequeño, dependencias y versiones.
- No convertir el éxito de importación en validación matemática.

## 2. Contrato matemático

- Shapes exactos, escalas y unidades, dtype/dispositivo, máscaras y ejes.
- Casos calculables a mano: elementos individuales, ceros, identidades, simetrías.
- Entradas ilegales: arrays con shapes incompatibles, pesos negativos, denominador 0, matrices singulares.

## 3. Dos algoritmos independientes

- Referencia mediante bucles pequeños vs vectorización `einsum`/matmul.
- Solución cerrada vs método iterativo cuando se conoce una.
- Implementación externa fiable vs derivada propia (registrar versiones y posibles convenciones distintas).
- Evitar oráculos circulares: comparar dos wrappers de la misma implementación no da evidencia independiente.

## 4. Propiedades e invariantes

- Conservación de masa/probabilidad, normalización, monotonía, límites de una función.
- Invarianza de permutación conjunta de claves-valores en atención sin positional encoding.
- Simetría en matrices cuando así lo impone la teoría.
- Cambiar seed, lote y orden cuando la propiedad exige invariancia.
- Tests metamórficos: cambiar entrada con transformación que debería preservar o transformar predictiblemente salida.

## 5. Precisión y gradientes

- `np.testing.assert_allclose` con tolerancias según rango/dtype/método. Evitar `atol` grande que tape errores en 0.
- Diferencias finitas centrales: `(f(x+h)-f(x-h))/(2h)` para funciones suaves y vectores pequeños. Comprobar sensibilidad a `h`.
- En PyTorch, `torch.autograd.gradcheck` con entradas dobles y condición de diferenciabilidad; gradientes analíticos vs numéricos. En TensorFlow, `tf.GradientTape` comparado con diferencias centrales (float64) y, si aplica, test separado bajo `tf.function`.
- NaN/Inf, overflow en softmax/logsumexp, números muy pequeños y condicionamiento.

## 6. Estadística

- Stochastic: evaluar varias seeds; estimar incertidumbre e intervalo de confianza apropiado.
- No usar un test t sin atender independencia, normalidad, autocorrelación, múltiples comparaciones.
- Pruebas estadísticas ruidosas requieren más corridas y umbrales predefinidos, no elegir tras observar.

## 7. Reproducción real

- Entrenar/evaluar con splits documentados, mismo preprocesado, métricas y versión de librerías.
- Comparación con tablas del artículo, errores por seed, baselines/ablaciones y sensibilidad a hiperparámetros.
- Error de métrica no se reduce a un test que pasa. Reportar diferencias aunque el sentido sea favorable.

## 8. Tests negativos / mutantes

Para demostrar que un test detecta errores, introduce temporalmente una implementación errónea (p. ej. elimina `1/sqrt(d_k)` o mezcla ejes) y verifica que el test **falla**; nunca distribuyas la mutación como implementación definitiva.

## 9. Matriz de evidencias

| Nivel | Exigencia mínima |
|---|---|
| `no_evaluado` | No se ejecutaron pruebas |
| `tests_unitarios` | Unitarias ejecutadas y reportadas |
| `componente_verificado` | Unitarias + referencia independiente + propiedades, con trazabilidad |
| `reproduccion_parcial` | Algún experimento en datos comparables y resultados con diferencias explicadas |
| `reproduccion_experimental` | Experimentos centrales, protocolos equivalentes y comparación cuantitativa documentada |

Esta escala es interna a la Skill, no una certificación científica ni un estándar oficial de Anthropic.

## 10. Estado por backend

Reporta versiones detectadas y los contadores **ejecutados, aprobados, fallidos y omitidos** por separado. Los tests omitidos por falta de TensorFlow, CUDA o PyTorch **no demuestran soporte verificado**. Una biblioteca se considera respaldada por pruebas solo cuando se ha importado y ejecutado en un entorno compatible. No compares framework A con framework B como único oráculo; utiliza también bucles escalares, invariantes o solución analítica.
