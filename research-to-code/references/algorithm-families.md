# Estrategias según el tipo de investigación

## ML supervisado / redes neuronales

- Separar arquitectura, inicialización, loss, optimizador, scheduler y lógica del experimento.
- Calcular tensor shapes y máscaras por capa; tests del `forward`, `backward`, batch size 1 y tamaños variables.
- Verificar gradientes en doble precisión si la función es diferenciable.
- Detectar leakage; estadísticas de normalización solo desde training; elegir checkpoint desde validation, nunca test.
- Replicar el protocolo antes de cambiar la arquitectura y hacer ablations.

## Probabilidad y estadística

- Distinguir variables aleatorias, densidades, masas, estimadores y realizaciones observadas.
- Comprobar normalización, soporte, independencia condicionada, parametrización de dispersión (varianza vs desviación estándar).
- Para Monte Carlo, fijar generador por ejecución, error estándar/CI y convergencia con tamaño muestral.
- Evaluar sesgo del estimador, cobertura e identificación; no asumir correlación = causalidad.

## Optimización convexa/no convexa

- Registrar objetivo, factibilidad, restricciones, inicialización, dominio, gradientes/Jacobianos y stopping criterion.
- Para casos convexos, contrastar KKT/solución analítica cuando se pueda; para no convexos, semillas y sensibilidad a inicializaciones.
- Comprobar que el algoritmo mejora el objetivo sin violar restricciones; inspeccionar divergencia y condiciones numéricas.
- No llamar óptimo global a una solución local sin evidencia.

## Métodos numéricos, EDO/EDP

- Consistencia, estabilidad, convergencia y orden empírico con reducción de paso/malla.
- Verificar condiciones iniciales y de contorno, unidades, discretización de derivadas, tratamiento de discontinuidades.
- Comparar con problema manufacturado de solución conocida; estimar error de discretización y tolerancia de integrador.
- Evaluar conservación de energía/masa si la matemática lo exige.

## Procesado de señal / visión

- Diferenciar convolución y correlación; especificar orden de canales y stride/padding/dilatación.
- Dominios Fourier y espacial: normalizaciones FFT, frecuencia discreta, límites, ventanas y aliasing.
- Confirmar geometría, interpolación, muestreo, escalas y unidades de métricas.

## Causalidad / experimentos aleatorios

- Explicitar estimando, tratamiento, outcome, DAG o supuestos de identificación, positividad, SUTVA si aplica.
- Detectar selección, confusión, variables posteriores al tratamiento y leakage.
- Comparar con ejemplos sintéticos con efecto causal verdadero conocido; reportar sensibilidad a supuestos.

## Aprendizaje por refuerzo / control

- Fijar convención de episodios, retorno descontado, terminal/truncado, reward scaling y exploración.
- Testear Bellman en MDP minúsculo resoluble analíticamente.
- Reportar seeds, curva de recompensa, número de episodios y variabilidad; comparar bajo iguales presupuestos.

## Artículos teóricos puros

- No forzar a programar un teorema sin objeto algorítmico. Se pueden crear pruebas computacionales ilustrativas, ejemplos/casos límite y verificación simbólica si corresponden, pero no sustituyen una demostración.
- Identificar hipótesis y comprobar contraejemplos fuera del dominio; no presentar evidencia numérica como prueba formal.
