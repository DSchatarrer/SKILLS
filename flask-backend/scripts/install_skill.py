#!/usr/bin/env python3
"""Install the canonical Flask skill for Codex and/or OpenCode (stdlib only).

Default `both` places a SINGLE copy in .agents/skills/flask-backend, a location
that BOTH agents discover. Use `opencode` only to request a native OpenCode path.
Does not contact the network, modify agent configs or execute external commands.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

SKILL_NAME = "flask-backend"
SKILL_ROOT = Path(__file__).resolve().parents[1]


def destinations(target: str, scope: str, root: Path) -> dict[str, Path]:
    """Resolve paths; `both` deliberately uses a shared directory."""
    if target not in {"both", "codex", "opencode"}:
        raise ValueError("target debe ser both, codex u opencode")
    if scope not in {"project", "user"}:
        raise ValueError("scope debe ser project o user")
    root = root.expanduser().resolve()
    shared = root / ".agents" / "skills" / SKILL_NAME
    native = (root / ".opencode" / "skills" / SKILL_NAME if scope == "project"
              else root / ".config" / "opencode" / "skills" / SKILL_NAME)
    return {("codex-y-opencode" if target == "both" else target):
            shared if target in {"both", "codex"} else native}


def validate_skill(root: Path) -> None:
    import re
    manifest = root / "SKILL.md"
    if not manifest.is_file():
        raise ValueError(f"SKILL.md no encontrado: {manifest}")
    body = manifest.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", body, re.DOTALL)
    if not match:
        raise ValueError("Falta frontmatter YAML delimitado por ---")
    meta = match.group(1)
    name = re.search(r"(?m)^name:\s*([a-z0-9-]+)\s*$", meta)
    description = re.search(r"(?m)^description:\s*(.+)$", meta)
    if not name or name.group(1) != SKILL_NAME or root.name != SKILL_NAME:
        raise ValueError("El nombre del manifiesto no coincide con el directorio")
    if not description or not 1 <= len(description.group(1).strip()) <= 1024:
        raise ValueError("description debe contener entre 1 y 1024 caracteres")
    if not (root / "references" / "repo-map.md").is_file():
        raise ValueError("Falta el mapa de referencia")


def _reject_symlinks(path: Path) -> None:
    # Avoid modifying symlinks at the target path and its existing ancestors.
    for current in (path, *path.parents):
        if current.is_symlink():
            raise ValueError(f"Destino enlazado simbólicamente; se rechaza: {current}")


def install(*, target: str = "both", scope: str = "project", root: Path | None = None,
            force: bool = False, dry_run: bool = False,
            source: Path = SKILL_ROOT) -> dict[str, object]:
    """Return exact destinations. Existing installs are never overwritten implicitly."""
    validate_skill(source)
    base = root if root is not None else (Path.cwd() if scope == "project" else Path.home())
    paths = destinations(target, scope, base)
    source = source.resolve()
    for dest in paths.values():
        _reject_symlinks(dest)
        if dest.resolve() == source or dest.resolve().is_relative_to(source):
            raise ValueError("El destino está dentro de la skill original")
        if dest.exists() and not force:
            raise FileExistsError(f"Ya existe {dest}. Usar --force para reemplazarla.")
        if dest.exists() and not dest.is_dir():
            raise FileExistsError(f"El destino no es directorio: {dest}")
    report: dict[str, object] = {
        "target": target, "scope": scope, "dry_run": dry_run,
        "paths": {k: str(v) for k, v in paths.items()}, "installed": [],
        "open_code_uses_shared_codex_path": target in {"both", "codex"},
    }
    if dry_run:
        return report
    for agent, dest in paths.items():
        dest.parent.mkdir(parents=True, exist_ok=True)
        # Stage on same filesystem to make final renames atomic when possible.
        with tempfile.TemporaryDirectory(prefix=".skill-stage-", dir=dest.parent) as staging:
            staged = Path(staging) / SKILL_NAME
            shutil.copytree(source, staged, symlinks=False,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache", ".DS_Store"))
            validate_skill(staged)
            if dest.exists():
                backup = Path(staging) / "previous-installation"
                dest.rename(backup)
                try:
                    staged.rename(dest)
                except BaseException:
                    backup.rename(dest)
                    raise
            else:
                staged.rename(dest)
        report["installed"].append(agent)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=["both", "codex", "opencode"], default="both")
    parser.add_argument("--scope", choices=["project", "user"], default="project")
    parser.add_argument("--project-root", type=Path,
                        help="Raíz del proyecto (predeterminada: directorio actual)")
    parser.add_argument("--home", type=Path, help="Directorio personal (para pruebas/portabilidad)")
    parser.add_argument("--force", action="store_true", help="Reemplazar instalación existente")
    parser.add_argument("--dry-run", action="store_true", help="Mostrar destinos sin escribir")
    args = parser.parse_args(argv)
    base = (args.project_root if args.scope == "project" else args.home)
    try:
        print(json.dumps(install(target=args.target, scope=args.scope, root=base,
                                 force=args.force, dry_run=args.dry_run),
                         ensure_ascii=False, indent=2))
    except (ValueError, OSError) as exc:
        print(f"No se instaló: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
