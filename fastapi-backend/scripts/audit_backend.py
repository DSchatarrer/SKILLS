#!/usr/bin/env python3
"""Static, read-only inventory for a FastAPI backend. Does NOT execute source code.

Usage: python scripts/audit_backend.py --root /path/to/backend_async --format json
Findings are heuristic prompts for manual review, not proof of exploitability.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head", "trace"}


def _lit_string(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _keywords(node: ast.Call) -> dict[str, ast.AST]:
    return {kv.arg: kv.value for kv in node.keywords if kv.arg is not None}


def _contains_name(node: ast.AST, name: str) -> bool:
    return any(isinstance(child, ast.Name) and child.id == name for child in ast.walk(node))


def audit(root: Path) -> dict:
    root = root.expanduser().resolve()
    source = root / "src" if (root / "src").is_dir() else root
    if not source.is_dir():
        raise ValueError(f"No existe el directorio: {root}")
    endpoints: list[dict] = []
    parse_errors: list[dict] = []
    warnings: list[dict] = []
    files = 0
    for path in sorted(source.rglob("*.py")):
        if path.is_symlink():
            continue
        try:
            if path.stat().st_size > 2_000_000:
                warnings.append({"path": path.relative_to(root).as_posix(),
                                 "finding": "Archivo >2 MB omitido"})
                continue
            source_text = path.read_text(encoding="utf-8-sig")
            tree = ast.parse(source_text, filename=str(path))
        except (OSError, UnicodeError, SyntaxError) as error:
            parse_errors.append({"path": path.relative_to(root).as_posix(),
                                 "error": type(error).__name__ + ": " + str(error)})
            continue
        files += 1
        relpath = path.relative_to(root).as_posix()
        routers = {}
        for node in tree.body:
            if (isinstance(node, (ast.Assign, ast.AnnAssign))
                    and isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Name)
                    and node.value.func.id == "APIRouter"):
                name = None
                if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                    name = node.targets[0].id
                if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                    name = node.target.id
                if name:
                    kwargs = _keywords(node.value)
                    dependencies = kwargs.get("dependencies")
                    routers[name] = {"prefix": _lit_string(kwargs.get("prefix")) or "",
                                     "has_role_dependency": bool(dependencies is not None and
                                                                 _contains_name(dependencies, "require_roles"))}
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for dec in node.decorator_list:
                if (not isinstance(dec, ast.Call) or not isinstance(dec.func, ast.Attribute)
                        or not isinstance(dec.func.value, ast.Name)
                        or dec.func.attr not in HTTP_METHODS
                        or dec.func.value.id not in routers):
                    continue
                router = routers[dec.func.value.id]
                route_suffix = _lit_string(dec.args[0]) if dec.args else ""
                if route_suffix is None:
                    route_suffix = "<dynamic>"
                full_path = router["prefix"] + (route_suffix if route_suffix.startswith("/") else "/" + route_suffix)
                endpoint = {"method": dec.func.attr.upper(), "path": full_path,
                            "handler": node.name, "file": relpath, "line": node.lineno,
                            "router_has_role_dependency": router["has_role_dependency"],
                            "handler_mentions_role_dependency": _contains_name(node, "require_roles")
                            or _contains_name(dec, "require_roles"),
                            "declares_response_model": "response_model" in _keywords(dec)}
                endpoints.append(endpoint)
                if ("alta-usuario" in full_path and not endpoint["router_has_role_dependency"]
                        and not endpoint["handler_mentions_role_dependency"]):
                    warnings.append({"path": relpath, "line": node.lineno,
                                     "finding": "ALTA USUARIO: no se observa require_roles en router/handler; verificar todas las dependencias y autorización efectiva"})
        # Snapshot-specific review hint: API key in query string.
        if relpath.endswith("core/security.py") and "def require_secret" in source_text and "Query(" in source_text:
            warnings.append({"path": relpath,
                             "finding": "API key por Query: revisar exposición en logs y migrar nuevos usos a headers"})
    return {"root": str(root), "python_files_parsed": files, "endpoints": endpoints,
            "warnings": warnings, "parse_errors": parse_errors,
            "limitations": "AST estático: no evalúa include_router anidados, Depends indirectas, settings, mounts ni la seguridad efectiva."}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = audit(args.root)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    print("Raíz:", result["root"], "| Python analizados:", result["python_files_parsed"])
    for e in result["endpoints"]:
        print(f"  {e['method']:6} {e['path']:36} {e['file']}:{e['line']}")
    for warning in result["warnings"]:
        print("REVISAR:", warning["path"], "-", warning["finding"])
    for error in result["parse_errors"]:
        print("ERROR AL LEER:", error["path"], "-", error["error"])
    print("Limitación:", result["limitations"])
    return 0 if not result["parse_errors"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
