# Fuentes contrastadas para el diseño de la Skill

Consultadas el 25-10-2026. Los enlaces son referencias informativas, no dependencias de runtime.

1. Anthropic, Agent Skills overview: https://platform.claude.com/docs/es/agents-and-tools/agent-skills/overview
2. Anthropic, Skill authoring best practices: https://platform.claude.com/docs/es/agents-and-tools/agent-skills/best-practices
3. Anthropic, skill-creator (ejemplo mantenido por el proveedor): https://github.com/anthropics/skills/tree/main/skills/skill-creator
4. Anthropic, skills repository: https://github.com/anthropics/skills
5. NumPy, einsum: https://numpy.org/doc/stable/reference/generated/numpy.einsum.html
6. PyTorch, gradcheck: https://docs.pytorch.org/docs/stable/generated/torch.autograd.gradcheck.html
7. NeurIPS, Paper Checklist: https://neurips.cc/public/guides/PaperChecklist
8. scikit-learn, cross-validation y preprocesado: https://scikit-learn.org/stable/modules/cross_validation.html
9. Vaswani et al. (2017), Attention Is All You Need, versión 7: https://arxiv.org/html/1706.03762v7 ; historial https://arxiv.org/abs/1706.03762

7. TensorFlow, autodiferenciación: https://www.tensorflow.org/guide/autodiff
8. TensorFlow, softmax: https://www.tensorflow.org/api_docs/python/tf/nn/softmax
9. PyTorch, atención escalada y convenciones de máscara: https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html
10. TensorFlow, operaciones de tensores: https://www.tensorflow.org/api_docs/python/tf/einsum

## Compatibilidad entre agentes (consultas 25-10-2026)

- Codex / OpenAI: https://learn.chatgpt.com/docs/build-skills ; https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md
- OpenCode: https://docs.opencode.ai/docs/skills/
- Claude Code: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Estándar: https://agentskills.io/specification

La compatibilidad de estructura y rutas es diferente de la validación de activación y respuesta de cada CLI/IDE en una sesión real.
