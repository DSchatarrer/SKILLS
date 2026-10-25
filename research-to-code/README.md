# Skill: research-to-code

**Portable para Codex, OpenCode y Claude Code**. Una única Skill conforme al formato de Agent Skills (`SKILL.md` con `name` y `description`, más `references/`, `scripts/` y `examples/`). Lee críticamente artículos, libros, tesis, estándares, documentación, especificaciones y PDFs locales; traduce matemáticas a código comprobable y verifica NumPy, PyTorch y TensorFlow cuando están disponibles.

## Instalar en los tres agentes

Extrae el ZIP completo. Desde la carpeta `research-to-code/` extraída, ejecuta:

```bash
# En Windows y Linux/macOS, sustituye /ruta/al/repositorio por tu proyecto.
python scripts/install_skill.py --target all --scope project --project-root /ruta/al/repositorio
```

Este comando crea **dos copias idénticas** que cubren los **tres** runtimes:

- **Codex y OpenCode:** `<proyecto>/.agents/skills/research-to-code/`
- **Claude Code:** `<proyecto>/.claude/skills/research-to-code/`

OpenCode reconoce la ruta de Codex `.agents/skills`, por eso no se crea otra copia en `.opencode/skills` con el mismo ID. Esta compatibilidad de rutas procede de la documentación oficial de los clientes; no depende de que estén instalados en la máquina al ejecutar el instalador.

Para utilizarla en **todos tus proyectos**, desde la carpeta de la Skill:

```bash
python scripts/install_skill.py --target all --scope user
```

Para instalar **solo un agente**, sustituye `all` por `codex`, `opencode` o `claude`. OpenCode, instalado individualmente, usa `.opencode/skills/` por proyecto o `~/.config/opencode/skills/` en el usuario. `--dry-run` muestra las rutas sin escribir; `--force` permite actualizar una instalación anterior. **No ejecutes la instalación por proyecto dentro de la carpeta fuente de la Skill:** indica el proyecto destino con `--project-root` o usa `--scope user`.

Para **Windows PowerShell** puedes pasar el directorio del repositorio entre comillas:

```powershell
python .\scripts\install_skill.py --target all --scope project --project-root "C:\ruta\a\mi-proyecto"
```

Para **Claude.ai web**, la instalación es distinta a Claude Code: se puede necesitar cargar el ZIP desde la interfaz, si el plan y la función lo permiten. La prueba de rutas de Claude Code no verifica la plataforma web.

Consulta `references/agent-compatibility.md` para rutas y limitaciones. El instalador no descarga nada, no instala dependencias y no se conecta a servidores.

## Ejecutar pruebas de este paquete

Desde la carpeta raíz de la Skill:

```bash
python scripts/run_self_tests.py
python -m unittest discover -s tests -v
python scripts/audit_project.py --project examples/attention_1706_03762 --run-tests --strict
(cd examples/math_patterns && python -m unittest discover -s tests -v)
```

Requisitos para el ejemplo: Python >= 3.10 y NumPy >= 1.24. Los ejemplos de `examples/frameworks` requieren PyTorch o TensorFlow según la suite seleccionada (dependencias opcionales). El creador y la auditoría estructural usan solo biblioteca estándar. No acceden a la red.

## Inicializar un proyecto real

```bash
python scripts/init_project.py --root ./mi-implementacion --title "Método técnico" --source-type documentation --source-url https://example.org/method --version rev-1
```

Un proyecto nuevo comienza **sin verificar**. Completa su `implementation_spec.json` con evidencia de la fuente original y añade código/tests; de lo contrario la auditoría marcará errores deliberadamente.

**Seguridad**: `audit_project.py --run-tests` ejecuta tests del proyecto local. Úsalo solo con proyectos de confianza, nunca directamente sobre repositorios de origen desconocido.

**Limitación de validación**: el paquete sí incluye pruebas automáticas de sus scripts y del ejemplo matemático; las pruebas de activación y uso *real* por Codex, OpenCode y Claude Code requieren ejecutar cada agente con permisos para cargar Skills. Se incluyen escenarios en `evals/evals.json`, pero no se atribuye ningún resultado de benchmark que no haya sido observado.

Documentación y procedencia: `references/sources.md`.

En **Windows PowerShell**, puedes ejecutar `python scripts/run_self_tests.py` desde la carpeta extraída; no depende de `bash`.

## PyTorch y TensorFlow

Incluye código específico de ambos frameworks en `examples/frameworks/framework_ops.py`, junto con equivalencias matemáticas documentadas en `references/pytorch-tensorflow.md`. Las funciones separadas de atención y sumatorios usan tensores nativos para conservar derivadas.

```bash
cd examples/frameworks
python -m unittest discover -s tests -v
```

TensorFlow/PyTorch no se instalan por defecto ni se necesitan para el núcleo NumPy. Si alguno falta, `unittest` marca `skipped` y el informe diferencia explícitamente pruebas ejecutadas de pruebas omitidas.

## Ejemplos de verificación científica

El catálogo `references/benchmark-catalog.md` propone ejemplos de dificultad creciente procedentes de artículos y de otros tipos de fuente. Hay un segundo caso completo de verificación de componentes: **Sparsemax**, en un artículo científico, en `examples/sparsemax_1602_02068/`.

```bash
cd examples/sparsemax_1602_02068
python -m unittest discover -s tests -v
```

Incluye tres implementaciones nativas, oráculos independientes (bisección y SciPy SLSQP), pruebas de jacobiano/autodiff, invariantes matemáticas y mutaciones erróneas. TensorFlow no se declara verificado si no se ha ejecutado. El script general `python scripts/run_self_tests.py` también ejecuta este nuevo caso, y realiza una auditoría estricta.

## Fuentes admitidas y metadatos

**No está limitada a ninguna plataforma de publicación.** Acepta DOI, ISBN, URL, ruta a PDF/documento local, identificador de informe o especificación, junto con la revisión o edición. El generador y auditor trabajan con `implementation_spec.json` (esquema 2.0, objeto `source`), sin exigir un identificador concreto. Consulta `references/source-types.md`.

```bash
# Especificación local
python scripts/init_project.py --root ./mi-metodo --title "Rotación 2D" --source-type specification --source-path docs/rotacion.pdf

# Libro, tercera edición
python scripts/init_project.py --root ./mi-libro --title "Método del capítulo 7" --source-type book --source-id ISBN-EXAMPLE --version edicion-3
```

El archivo generado comienza en estado **NO EVALUADO**; completar la fuente y aportar pruebas antes de reclamar reproducibilidad.

## Caso real de prueba sin plataforma editorial

`examples/local_specification/` contiene una especificación Markdown local, su implementación NumPy, tests adversarios y manifiesto de procedencia verificable. Se audita en cada ejecución del test runner.

## Si ya tenías la Skill antigua

La Skill ahora se instala con el nuevo nombre `research-to-code`. Las carpetas de una versión anterior pueden permanecer en el equipo y cargar instrucciones duplicadas. Tras comprobar que esta versión funciona, elimina manualmente la instalación anterior correspondiente desde `.agents/skills/`, `.claude/skills/` o `.opencode/skills/`. El instalador **no borra automáticamente** otras Skills por seguridad.
