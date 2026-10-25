# Caso de prueba independiente de plataformas de publicación

La fuente es el fichero **local** `SPECIFICATION.md`; no tiene URL ni DOI. Las dos implementaciones se contrastan con un cálculo manual conocido, propiedades matemáticas e inputs adversarios.

```bash
cd examples/local_specification
python -m unittest discover -s tests -v
```

La cobertura solo verifica el operador descrito por esta especificación didáctica; no representa un experimento científico ni una publicación externa.
