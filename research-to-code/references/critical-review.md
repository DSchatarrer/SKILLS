# Protocolo de revisión crítica y antifalsos positivos

No se trata de repetir mentalmente un mismo cálculo, sino de obtener *evidencias contrastables*.

## Antes del código: hipótesis alternativas

Para toda ecuación crítica:
1. ¿Qué significa literalmente la notación y qué no define el paper?
2. ¿Hay una lectura igualmente plausible (eje, signo, transpuesta, normalizador, distribución)?
3. ¿Qué microcaso haría que ambas lecturas diesen salidas diferentes?
4. ¿Qué dato o apéndice permite elegir entre ellas?
5. Si no hay evidencia, ¿quedará la ambigüedad documentada en vez de disimulada?

## Al escribir tests: busca falsaciones

- Cambia el eje de sumatorio: ¿el test falla?
- Elimina un escalado, una máscara o un término del gradiente: ¿el test falla?
- Sustituye pesos de esperanza por uniforme: ¿se detecta?
- Permuta dos ejes en una operación tensorial: ¿se detecta en shapes no cuadrados?
- Compara datos de validación con entrenamiento filtrado: ¿se descubre?
- Desactiva control de aleatoriedad: ¿reporta varianza en vez de inventar determinismo?
- ¿Hay al menos una prueba que no use la misma implementación interna como oráculo?

## Auditoría de coincidencias sospechosas

Una métrica coincidente por azar puede ocultar bugs. Exige:
- Escalas y denominadores comparables, no solo un número semejante.
- Igual protocolo y definiciones de métricas.
- Baselines y ablations de componentes esenciales.
- Resultados con al menos los puntos críticos del método, no solo una puntuación.
- Ejecución reproducible desde configuración y seed declaradas.

## Informe sin maquillaje

Usa estas etiquetas: `OBSERVADO`, `FUENTE`, `INFERENCIA`, `HIPÓTESIS`, `BLOQUEO`.

- `OBSERVADO`: comando ejecutado y salida guardada.
- `FUENTE`: afirmación del artículo, con ubicación exacta.
- `INFERENCIA`: deducción razonada pero no literalmente afirmada.
- `HIPÓTESIS`: no corroborada; necesita test o aclaración.
- `BLOQUEO`: el dato o infraestructura falta; impide una conclusión.

**No falsifiques ejecución**, no fabriques resultados, no interpretes una compilación sin errores como validación matemática, no vendas test unitario como reproducción de resultados.
