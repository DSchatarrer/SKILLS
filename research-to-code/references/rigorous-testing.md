# Pirámide de tests para implementación científica

## 0. Protocolo test-first para componentes matemáticos críticos

El objetivo no es conseguir tests verdes, sino **fijar de antemano predicciones falsables** que no dependan del código que se va a juzgar. Se aplica por ecuación o componente crítico, no a cada función auxiliar.

1. **Derivar**. Partir del contrato matemático y escoger un microcaso pequeño, asimétrico y discriminante. Calcular sin ejecutar la implementación objetivo una salida esperada manual o analítica, con dimensiones, unidades y supuestos. Identificar una implementación incorrecta plausible que debería dar otro resultado.
2. **Registrar**. Escribir primero el test de aceptación con **entradas literales y salida esperada independiente**, tolerancia justificada y comentario con la derivación/fuente. Se puede ejecutar y observar un error de importación o función ausente; eso no es un fracaso del protocolo. No declarar una ejecución si no ocurrió.
3. **Implementar**. Crear referencia transparente y versión eficiente después. Mantener las expectativas fijadas: si el oráculo era erróneo, documentar qué evidencia lo corrige antes de actualizarlo. No editar el esperado únicamente para que el código pase.
4. **Contrastar**. Ejecutar tests, añadir invariantes, variantes de shape, casos adversarios y comparación de backends; un test que pasa solo acota la evidencia al conjunto observado.
5. **Refutar**. Introducir temporalmente una mutación plausible (cambiar eje, signo, normalizador, máscara...) y observar al menos un fallo pertinente; restaurar el código antes de entregar.

**Independencia**: una segunda función que comparte el cálculo defectuoso, un snapshot de salida de la implementación, o tests creados cambiando valores hasta que pasen **no son oráculos independientes**. Preferir derivación analítica, cálculo manual con operaciones elementales, propiedades demostrables o algoritmos distintos. Si el cálculo manual también depende de una interpretación ambigua de la fuente, construir primero un caso que discrimine lecturas y dejar la ambigüedad explícita si no se puede resolver.

### Ejemplo mínimo reproducible (antes de implementar)

Para `f(x,p)=Σᵢ pᵢxᵢ`, con `x=[2,10]` y `p=[0.9,0.1]`, el cálculo manual fija `f=2.8`, no `6.0` (media uniforme). Respecto de `x`, si `p` es constante, `∂f/∂x=[0.9,0.1]`.

```python
import unittest
import numpy as np
from method import weighted_expectation  # pendiente de implementar

class ContractTests(unittest.TestCase):
    def test_hand_calculated_value(self):
        self.assertAlmostEqual(weighted_expectation([2., 10.], [.9, .1]), 2.8)

    def test_numeric_gradient_against_analytic_oracle(self):
        from numeric_checks import check_gradient  # util ubicado en scripts/
        p = np.array([.9, .1], dtype=np.float64)
        check_gradient(
            lambda x: float(weighted_expectation(x, p)),
            np.array([2., 10.], dtype=np.float64),
            expected_gradient=p,
        )
```

Este bloque es una **plantilla**, no un test directamente ejecutable en su ubicación actual: `method` debe implementarse en el proyecto, y `numeric_checks` debe estar disponible en el `PYTHONPATH` mediante la ruta absoluta de `scripts/` de la Skill o una copia revisada del utilitario. Consulta también `examples/math_patterns/tests/test_math_patterns.py` para tests ejecutables que siguen estas predicciones.

Cuando no es posible obtener un valor numérico exacto, prepara antes de implementar propiedades invariantes o metamórficas y detalla qué errores podrían quedar sin detectar. El historial de creación de tests, si el agente/runtime lo expone, se evalúa con `evals/test-first-rubric.md`; **no puede deducirse retrospectivamente** de un árbol de archivos final.

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
- Diferencias finitas centrales: `(f(x+h)-f(x-h))/(2h)` para funciones escalares suaves y vectores pequeños. Comprobar sensibilidad a al menos dos valores de `h` y contrastar con una derivada analítica independiente cuando exista (`scripts/numeric_checks.py`, función `check_gradient`). Una coincidencia en uno o varios pasos no certifica diferenciabilidad ni corrección matemática global. En puntos no diferenciables, operaciones discretas, funciones no deterministas sin control del ruido o derivadas numéricamente mal condicionadas, documentar el límite y elegir otra evidencia.
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
