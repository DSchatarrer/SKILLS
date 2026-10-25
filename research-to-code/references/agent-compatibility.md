# Compatibilidad Agent Skills: Codex, OpenCode y Claude Code

Verificado frente a documentación de cada proveedor el 25 de octubre de 2026. Fuente de verdad: `SKILL.md` y sus archivos adyacentes; no mantener tres implementaciones divergentes.

| Cliente | Proyecto | Usuario/global | Uso |
|---|---|---|---|
| Codex CLI / IDE | `.agents/skills/research-to-code/` | `~/.agents/skills/research-to-code/` | Descubrimiento de `name`/`description` y carga bajo demanda |
| Claude Code | `.claude/skills/research-to-code/` | `~/.claude/skills/research-to-code/` | Descubrimiento de `SKILL.md` |
| OpenCode | `.opencode/skills/research-to-code/` | `~/.config/opencode/skills/research-to-code/` | Herramienta `skill`; también lee `.agents/skills` y `.claude/skills` |

## Instalación sin duplicación

- Para **los tres clientes**: `python scripts/install_skill.py --target all --scope project --project-root /ruta/al/repositorio` (o `--scope user`). Instala **dos copias idénticas**: una en `.agents/skills` para Codex **y OpenCode**, otra en `.claude/skills` para Claude. No crear también `.opencode/skills` en este modo: OpenCode puede mostrar una definición duplicada o aplicar precedencia inesperada.
- Para **solo OpenCode**: `python scripts/install_skill.py --target opencode --scope project --project-root /ruta/al/repositorio`.
- Para **solo Codex**: `python scripts/install_skill.py --target codex --scope user`.
- Para **solo Claude Code**: `python scripts/install_skill.py --target claude --scope user`.
- Ver rutas sin escribir nada: añade `--dry-run`. Si existía la Skill, instalar sin `--force` aborta; `--force` reemplaza la carpeta instalada (no solo `SKILL.md`).
- Con el ZIP distribuido, extraer antes en disco. En un repositorio compartido, incluir `.agents/skills/research-to-code` y `.claude/skills/research-to-code` si se necesita que ambos clientes lo descubran automáticamente. Editar siempre la fuente canónica antes de volver a ejecutar el instalador.

## Comportamiento portable

1. El YAML del `SKILL.md` solo contiene `name` y `description`, ambos campos comprendidos por los tres proveedores. Evitar frontmatter propietario, tool IDs, agentes anidados o hooks exclusivos en el contrato principal.
2. El texto de la Skill solo prescribe **tareas y artefactos**, no nombres específicos de herramientas internas de Claude, Codex u OpenCode. Si el runtime carece de navegador, terminal, Python, internet o permisos, indicar la limitación; no inventar que se ejecutó código ni que se consultó la fuente original.
3. Resolver las referencias (`references/`), ejemplos (`examples/`) y scripts (`scripts/`) **respecto al directorio de `SKILL.md`**, no respecto al directorio de trabajo del usuario. No asumir que la invocación establece `cwd` dentro de la Skill.
4. Mantener datos/PDFs/repositorios externos como material no confiable. Ejecutar scripts incluidos únicamente cuando el usuario lo permita y el entorno lo admita; no ejecutar comandos arbitrarios de papers.
5. Separar compatibilidad **de formato/rutas** (validable sin los agentes) de funcionamiento **end-to-end** (requiere ejecutar cada agente y evaluar si carga la Skill y sigue sus instrucciones).
6. TensorFlow y PyTorch son **backends matemáticos**, no agentes: su disponibilidad depende del entorno Python de cada ejecución.

## Pruebas de compatibilidad

- `python -m unittest discover -s tests -p 'test_cross_agent_install.py' -v`: valida rutas, metadatos, instalación individual/combinada, copias idénticas, modo lectura, reemplazo y bloqueo de enlaces simbólicos.
- `python scripts/run_self_tests.py`: todas las pruebas numéricas y de estructura existentes.
- **Smoke test real pendiente en cada cliente**: abrir un proyecto con Skill instalada; pedir que resuelva una ecuación matricial de una especificación local o pública, comente el `SKILL.md` elegido, construya caso de bucles más versión vectorizada y ejecute tests. Comparar `implementation_spec.json`, resultados y mensajes de limitación. Los tests de rutas no equivalen a ejecutar un agente real.

## Referencias oficiales

- Codex: https://learn.chatgpt.com/docs/build-skills
- OpenCode: https://docs.opencode.ai/docs/skills/
- Claude Code: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Agent Skills estándar: https://agentskills.io/specification
