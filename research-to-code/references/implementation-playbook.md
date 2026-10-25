# De una fuente técnica a una base de código revisable

## Estructura recomendada para cualquier fuente

```text
research-project/
  implementation_spec.json               # Procedencia, alcance, contratos
  README.md                     # Qué sí y no reproduce
  requirements.txt              # Dependencias con versiones para el proyecto concreto
  src/                          # Referencias simples y código optimizado
  tests/                        # Tests deterministas y adversarios
  configs/                      # Hiperparámetros y seeds
  experiments/                  # Scripts de entrenamiento/evaluación
  results/                      # Métricas reales y logs con procedencia
  REPRODUCTION_REPORT.md        # Evidencia y límites
```

## Flujo en cuatro capas

1. **Matemática**: definiciones, axiomas, hipótesis, variables e índices. Ficha con referencia al original.
2. **Referencia**: función simple, sin optimizaciones o trucos; valida entradas, shapes y dominio.
3. **Optimizada**: NumPy primero para fórmulas aisladas; PyTorch/TensorFlow/JAX cuando sean necesarios gradientes, aceleración o ecosistemas concretos. No añadas librerías sin motivo.
4. **Sistema experimental**: carga, preprocesado, splits, entrenamiento, evaluación, CI/logs y regeneración.

## Decisiones explícitas

- Modelo determinista: fixtures, tolerancia por dtype y pruebas metamórficas.
- Probabilístico: seeds controladas, generador local, distribución exacta, estimadores e intervalos de confianza.
- Optimización: función objetivo y restricciones, signo y scheduling, inicialización, convergencia, tolerancia.
- ML: orden de operadores, normalización, entrenamiento vs evaluación, máscara, padding, fuga de datos, propagación de gradientes.
- Métodos numéricos: orden de aproximación, estabilidad, error de discretización, condiciones iniciales/de contorno y paso temporal.
- Teoría: implementar las afirmaciones constructivas solo cuando proceda; un teorema no requiere simulación si no hay método ejecutable.
- Código del autor: utilizar como contraste, registrar diferencias y no copiar licencias incompatibles.

## Reglas para código fiable

- Funciones pequeñas, tipadas si procede; docstrings que indiquen matemáticas, shapes, unidades y restricciones.
- Errores diagnósticos para inputs inválidos; no convertir NaN a 0 ni corregir datos silenciosamente.
- Parámetros nombrados, configuraciones serializables, librerías versionadas, ejecutar desde cero.
- Versionar pruebas y guardar semillas, hash/URL de datos, revisión de la fuente y commit del código, plataforma y comandos.
- Priorizar recursos disponibles: smoke test CPU pequeño, luego benchmark; no prometer entrenamientos masivos.
- Aislamiento: `python -m venv .venv`; instalar dependencias necesarias localmente tras revisar licencias/seguridad.
- Evitar redes durante pruebas unitarias. Las descargas deben ser una etapa opcional, visible y controlada.

## Plantilla de registro de decisión

```markdown
- Fuente: fuente/versión __, pág./sección __, ecuación __
- Ecuación literal: ...
- Interpretación: ...
- Ambigüedad: ...
- Decisión tomada: ...
- Alternativa rechazada: ...
- Evidencia: ...
- Prueba que la diferencia: ...
- Estado: literal / aproximación / por verificar
```
