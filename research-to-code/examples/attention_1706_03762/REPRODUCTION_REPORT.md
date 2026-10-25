# Informe acotado: atención escalada

Fuente: Vaswani et al., *Attention Is All You Need*, arXiv:1706.03762v7, sección 3.2.1, ecuación (1). URL: https://arxiv.org/html/1706.03762v7

**Alcance**: implementación autónoma de `softmax(QKᵀ/√dk)V`, referencia independiente por bucles y pruebas deterministas. Se añade máscara booleana como extensión de API con convención explícita. **No** se implementa el Transformer completo, no se entrena ni se replican los BLEU del artículo.

- Ecuación 1 → `attention.py:scaled_dot_product_attention`.
- Oráculo matemático → `attention.py:attention_reference_loops`.
- Tests → `tests/test_attention.py`: valor cerrado, producto y escala, shapes, normalización, máscara, causalidad, invariancia, estabilidad, lotes, entradas inválidas.
- Ejecutar desde este directorio: `python -m unittest discover -s tests -v`.
- Auditoría desde la raíz de la Skill: `python scripts/audit_project.py --project examples/attention_1706_03762 --run-tests --strict`.

**Interpretación**: las pruebas verifican propiedades de este componente dentro del dominio admitido. La conclusión **no** demuestra equivalencia de un Transformer ni validez de experimentos de traducción.
