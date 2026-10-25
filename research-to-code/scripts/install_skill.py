#!/usr/bin/env python3
"""Install the ONE canonical Agent Skill into Codex, Claude Code and/or OpenCode.

No external dependencies, downloads, shell commands, or hidden host configuration.
The agent-specific differences are discovery paths ONLY; content stays identical.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "research-to-code"
TARGETS = ("codex", "opencode", "claude")


def discover_paths(*, target: str, scope: str, project_root: Path | None = None,
                   home: Path | None = None) -> dict[str, Path]:
    """Return platform-specific paths. 'all' installs 2 copies, not 3.

    OpenCode natively discovers Codex's .agents/skills path, so creating both
    .agents and .opencode copies of the same skill can cause duplicate IDs.
    """
    if target not in (*TARGETS, "all"):
        raise ValueError("Unknown target")
    if scope not in ("project", "user"):
        raise ValueError("Unknown scope")
    if scope == "project":
        root = (project_root or Path.cwd()).expanduser().resolve()
        mapping = {
            "codex": root / ".agents" / "skills" / SKILL_NAME,
            "claude": root / ".claude" / "skills" / SKILL_NAME,
            "opencode": root / ".opencode" / "skills" / SKILL_NAME,
        }
    else:
        root = (home or Path.home()).expanduser().resolve()
        mapping = {
            "codex": root / ".agents" / "skills" / SKILL_NAME,
            "claude": root / ".claude" / "skills" / SKILL_NAME,
            "opencode": root / ".config" / "opencode" / "skills" / SKILL_NAME,
        }
    if target == "all":
        # OpenCode reads '.agents/skills' at both project and user scope.
        return {key: mapping[key] for key in ("codex", "claude")}
    return {target: mapping[target]}


def validate_source(root: Path = SKILL_ROOT) -> None:
    path = root / "SKILL.md"
    if not path.is_file():
        raise ValueError(f"Missing {path}")
    content = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", content, re.S)
    if not match:
        raise ValueError("SKILL.md requires YAML frontmatter")
    header = match.group(1)
    if not re.search(r"(?m)^name:\s*" + SKILL_NAME + r"\s*$", header):
        raise ValueError("Skill frontmatter name and directory name must match")
    desc = re.search(r"(?m)^description:\s*(.*)$", header)
    if not desc or not 1 <= len(desc.group(1).strip()) <= 1024:
        raise ValueError("Description must be between 1 and 1024 characters")


def install(*, target: str, scope: str, project_root: Path | None = None,
            home: Path | None = None, force: bool = False,
            dry_run: bool = False, skill_root: Path = SKILL_ROOT) -> dict:
    validate_source(skill_root)
    destinations = discover_paths(target=target, scope=scope, project_root=project_root, home=home)
    result = {"target": target, "scope": scope, "dry_run": dry_run,
              "installed": [], "paths": {k: str(v) for k, v in destinations.items()},
              "opencode_also_discovers_codex_path": target == "all"}
    for agent, destination in destinations.items():
        if destination.is_symlink():
            raise FileExistsError(f"Refusing to replace a symlink: {destination}")
        if destination.exists() and not force:
            raise FileExistsError(f"Already exists: {destination} (use --force to replace)")
        if destination.exists() and not destination.is_dir():
            raise FileExistsError(f"Not a directory: {destination}")
        # Guard against recursion when trying to install inside the source itself.
        if destination == skill_root.resolve() or destination.is_relative_to(skill_root.resolve()):
            raise ValueError("Destination is inside source skill directory. Use --project-root PROJECT or --scope user")
    if dry_run:
        return result
    for agent, destination in destinations.items():
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="_skill_stage_", dir=destination.parent) as staging:
            incoming = Path(staging) / SKILL_NAME
            shutil.copytree(skill_root, incoming, symlinks=False, ignore=shutil.ignore_patterns(
                "__pycache__", "*.pyc", ".pytest_cache", ".DS_Store", ".git"))
            validate_source(incoming)
            if destination.exists():
                # A replacement is staged and validated before removing old files.
                backup = Path(staging) / (SKILL_NAME + "-backup")
                destination.rename(backup)
                try:
                    incoming.rename(destination)
                except BaseException:
                    backup.rename(destination)
                    raise
            else:
                incoming.rename(destination)
        result["installed"].append(agent)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=(*TARGETS, "all"), default="all",
                        help="all installs Codex+Claude paths; OpenCode reads the Codex path")
    parser.add_argument("--scope", choices=("user", "project"), default="project")
    parser.add_argument("--project-root", type=Path, default=None,
                        help="Project path; default current working directory")
    parser.add_argument("--force", action="store_true", help="Replace existing skill directories")
    parser.add_argument("--dry-run", action="store_true", help="Print destinations without writing")
    args = parser.parse_args(argv)
    try:
        result = install(target=args.target, scope=args.scope, project_root=args.project_root,
                         force=args.force, dry_run=args.dry_run)
    except (OSError, ValueError) as error:
        print(f"Installation failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
