# Traducciones matemáticas ejecutables

Ejemplos independientes del paper concreto:

- `y_i = Σ_j A_ij x_j` → bucle y `np.einsum('ij,j->i',...)`.
- `E_p[X] = Σ_i p_i x_i` → producto ponderado, no media simple salvo uniforme.
- `h_{t+1}=A h_t + B x_t` → recurrencia `for`, con `h_0` explícito.

Ejecutar desde este directorio: `python -m unittest discover -s tests -v`.

Los ejemplos demuestran traducciones generales, NO validan por sí mismos ninguna publicación arXiv.
