# Estructura de `implementation_spec.json` (esquema 2.0)

Una fuente puede ser un artículo de revista o congreso, preprint, libro, tesis, informe, documentación, especificación o archivo local. No depende de ningún proveedor de publicaciones.

```bash
python scripts/init_project.py --root ./experimento --title "Algoritmo de mi manual" --source-type documentation --source-url https://example.org/method --version rev-2
python scripts/init_project.py --root ./experimento-local --title "Algoritmo del PDF" --source-type specification --source-path docs/spec.pdf
python scripts/init_project.py --root ./libro --title "Capítulo 7" --source-type book --source-id ISBN-12345 --version edicion-3
```

- `source.type`: `article`, `preprint`, `conference_paper`, `book`, `thesis`, `technical_report`, `documentation`, `specification`, `notebook` u `other`.
- `source.title`: título exacto comprobado.
- `source.url`, `source.local_path`, `source.identifier`: al menos una referencia persistente; identificador puede ser DOI, ISBN, ID del documento, etc.
- `source.version`: edición, revisión, versión o commit según corresponda, sin exigir un formato concreto.
- `source.version_verified`: verdadero solo tras comprobar la edición contra la fuente.
- `source.primary_source`: enlace o ubicación exacta de la sección realmente consultada; inicialmente `null` hasta verificación.
- `source.source_accessed_at`: fecha de consulta; `source.license_reviewed`: revisión de licencia.
- `scope`: delimita componente, algoritmo, sistema completo o reproducción experimental.
- `equations`: contratos matemáticos con localización en fuente, símbolos, formas, hipótesis, código y tests.
- `experiments`: ejecución real, nunca afirmaciones basadas solo en pruebas unitarias.
- `environment`: bibliotecas, versiones, hardware, RNG/semillas.
- `unknowns`: detalles que impiden asegurar equivalencia o reproducción.
- `evidence.claim_level`: `no_evaluado`, `tests_unitarios`, `componente_verificado`, `reproduccion_parcial`, `reproduccion_experimental`.

Ejemplo de contrato:

```json
{
  "id": "ecuacion_1",
  "source_section": "Capítulo 2, §4, ecuación 3",
  "expression": "y_i = sum_j A_ij x_j",
  "symbols": {"A": "matriz real n×m", "x": "vector real m"},
  "assumptions": ["m > 0"],
  "input_shapes": {"A":"(n,m)","x":"(m,)"},
  "output_shape": "(n,)",
  "implementation": "src/method.py",
  "reference_implementation": "src/method_reference.py",
  "test_file": "tests/test_method.py",
  "status": "unverified"
}
```

El auditor revisa estructura, rutas y consistencia de afirmaciones, pero no prueba matemáticamente la equivalencia. Las pruebas de ambos códigos deben ser independientes en lo posible. Estados: `unverified`, `unit_tested`, `verified`, `blocked`.
