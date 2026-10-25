# Especificación local: esperanza discreta ponderada

**Tipo:** especificación didáctica para las pruebas de la Skill. **Revisión:** 1.0. **Licencia:** CC0, texto creado dentro de este proyecto. No es una publicación externa.

## Sección 1: contrato matemático

Sea `x` un vector real finito de longitud `n` y `p` un vector de probabilidades de longitud `n`. Se requiere `n >= 1`, `p_i >= 0`, `sum(p) = 1` y valores finitos.

La esperanza discreta es `E_p[x] = sum_{i=0}^{n-1} p_i * x_i`, un escalar real.

Caso verificable: `x=[2,10]`, `p=[0.9,0.1]`; salida `2.8` (NO `6`, que sería la media sin ponderar).

## Sección 2: implementación y validación

Implementar una referencia mediante bucles y una versión vectorizada independiente. Rechazar valores no finitos, formas incompatibles, probabilidades negativas o pesos no normalizados. No confundir una prueba del operador con una reproducción experimental.
