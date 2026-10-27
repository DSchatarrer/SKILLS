#!/usr/bin/env python3
"""Inventario AST de un backend Flask/Flask-Smorest, SIN ejecutar el código.

python scripts/audit_flask.py --root /ruta/backend_sync --format json
Señales heurísticas de revisión, no pruebas de seguridad ni cobertura exhaustiva.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}


def literal(node: ast.AST | None) -> str | None:
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Call):
        return call_name(node.func)
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def decoration(node: ast.AST) -> tuple[str | None, str | None, ast.Call | None]:
    """Return object name, method, call for @obj.decorator(...) expressions."""
    func = node.func if isinstance(node, ast.Call) else node
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        return func.value.id, func.attr, node if isinstance(node, ast.Call) else None
    return None, call_name(func), node if isinstance(node, ast.Call) else None


def keywords(node: ast.Call | None) -> dict[str, ast.AST]:
    return {k.arg: k.value for k in node.keywords if k.arg is not None} if node else {}


def decorators_of(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    return [x for d in node.decorator_list if (x := call_name(d))]


def routes_of(node: ast.AST, prefixes: dict[str, str]) -> list[tuple[str, str, str]]:
    """Returns (method, path, source) for static path decorators (MethodView class emits ANY)."""
    output: list[tuple[str, str, str]] = []
    for d in getattr(node, "decorator_list", ()):
        obj, action, call = decoration(d)
        if not call or action not in HTTP_METHODS | {"route"} or obj not in prefixes:
            continue
        path = literal(call.args[0]) if call.args else ""
        if path is None:
            path = "<dynamic>"
        url = prefixes[obj].rstrip("/") + (path if path.startswith("/") else "/" + path)
        if not url.startswith("/"):
            url = "/" + url
        method = action.upper() if action in HTTP_METHODS else "ANY"
        if action == "route":
            kw = keywords(call).get("methods")
            if isinstance(kw, (ast.List, ast.Tuple)):
                const = [literal(x) for x in kw.elts]
                methods = [m.upper() for m in const if m]
            else:
                methods = []
            if methods:
                for m in methods:
                    output.append((m, url, obj))
                continue
        output.append((method, url, obj))
    return output


def _source_root(root: Path) -> Path:
    if (root / "src").is_dir():
        return root / "src"
    if (root / "backend_sync" / "src").is_dir():
        return root / "backend_sync" / "src"
    if (root / "flask-main" / "backend_sync" / "src").is_dir():
        return root / "flask-main" / "backend_sync" / "src"
    return root


def _risk_checks(endpoint: dict, warnings: list[dict]) -> None:
    d = endpoint["decorators"]
    path = endpoint["path"]
    method = endpoint["method"]
    location = {"file": endpoint["file"], "line": endpoint["line"]}
    if "require_auth" in d and "require_db_session" not in d:
        warnings.append({**location, "finding": "require_auth usa db, pero no se ve @require_db_session (revisar DI)"})
    if "require_role" in d and "require_auth" not in d:
        warnings.append({**location, "finding": "require_role sin require_auth visible: revisar permisos"})
    if "require_auth" in d and "require_db_session" in d and d.index("require_db_session") > d.index("require_auth"):
        warnings.append({**location, "finding": "Orden de decoradores: require_db_session debe envolver require_auth"})
    if "require_role" in d and "require_auth" in d and d.index("require_auth") > d.index("require_role"):
        warnings.append({**location, "finding": "Orden de decoradores: require_auth debe envolver require_role"})
    if (path.rstrip("/").endswith("/register") and method in {"POST", "ANY"}
            and ("require_auth" not in d or "require_role" not in d)):
        warnings.append({**location, "finding": "Alta de usuarios sin protecciones de auth/rol visibles; confirmar autorización efectiva"})


def audit(root: Path) -> dict:
    root = root.expanduser().resolve()
    source = _source_root(root)
    if not source.is_dir():
        raise ValueError(f"Directorio inexistente: {root}")
    results: list[dict] = []
    warnings: list[dict] = []
    errors: list[dict] = []
    parsed = 0
    for file in sorted(source.rglob("*.py")):
        if file.is_symlink():
            continue
        rel = file.relative_to(root).as_posix()
        try:
            if file.stat().st_size > 2_000_000:
                warnings.append({"file": rel, "finding": "Archivo >2 MB omitido"})
                continue
            content = file.read_text(encoding="utf-8-sig")
            tree = ast.parse(content, filename=str(file))
        except (OSError, UnicodeError, SyntaxError) as exc:
            errors.append({"file": rel, "error": f"{type(exc).__name__}: {exc}"})
            continue
        parsed += 1
        prefixes: dict[str, str] = {"app": ""}
        for node in tree.body:
            if not isinstance(node, (ast.Assign, ast.AnnAssign)) or not isinstance(node.value, ast.Call):
                continue
            if call_name(node.value.func) not in {"Blueprint"}:
                continue
            names = [x.id for x in node.targets if isinstance(x, ast.Name)] if isinstance(node, ast.Assign) else ([node.target.id] if isinstance(node.target, ast.Name) else [])
            for name in names:
                prefixes[name] = literal(keywords(node.value).get("url_prefix")) or ""
        # Detect contextmanager typing annotation of Iterator (editor warning).
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if (any(call_name(d) == "contextmanager" for d in node.decorator_list)
                        and isinstance(node.returns, (ast.Subscript, ast.Name))
                        and call_name(node.returns.value if isinstance(node.returns, ast.Subscript) else node.returns) == "Iterator"):
                    warnings.append({"file": rel, "line": node.lineno, "finding": "@contextmanager con -> Iterator: preferir Generator[...]"})
        for top in tree.body:
            if isinstance(top, ast.ClassDef):
                route_entries = routes_of(top, prefixes)
                for member in top.body:
                    if not isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        continue
                    if member.name not in HTTP_METHODS:
                        continue
                    method_routes = routes_of(member, prefixes)
                    for method, path, _ in route_entries + method_routes:
                        if method not in {"ANY", member.name.upper()}:
                            continue
                        item = {"method": member.name.upper(), "path": path,
                                "handler": f"{top.name}.{member.name}", "file": rel,
                                "line": member.lineno, "decorators": decorators_of(member)}
                        results.append(item)
                        _risk_checks(item, warnings)
            elif isinstance(top, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for method, path, _ in routes_of(top, prefixes):
                    item = {"method": method, "path": path, "handler": top.name,
                            "file": rel, "line": top.lineno, "decorators": decorators_of(top)}
                    results.append(item)
                    _risk_checks(item, warnings)
        if rel.endswith("core/security.py") and "request.args.get" in content and '"apikey"' in content:
            warnings.append({"file": rel, "finding": "API key en query permitida por legado: no replicar en endpoints nuevos"})
        # Catch accidental per-request Engine recreation in view/controller code as hint.
        if "applications/" in rel:
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and call_name(node.func) in {"create_engine", "sessionmaker"}:
                    warnings.append({"file": rel, "line": node.lineno,
                                     "finding": "Creación de Engine/sessionmaker dentro de applications: comprobar ciclo de vida"})
    results.sort(key=lambda e: (e["file"], e["line"], e["method"]))
    return {
        "root": str(root), "python_files_parsed": parsed,
        "endpoints": results, "warnings": warnings, "parse_errors": errors,
        "limitations": "Análisis estático: no verifica registro real de Blueprints, rutas dinámicas, decoradores heredados, lógica indirecta ni exploitabilidad."
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    opts = parser.parse_args(argv)
    try:
        result = audit(opts.root)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    if opts.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Raíz: {result['root']} | Python analizados: {result['python_files_parsed']}")
        for e in result["endpoints"]:
            print(f"  {e['method']:7} {e['path']:28} {e['file']}:{e['line']} {e['handler']}")
        for w in result["warnings"]:
            print("REVISAR:", w["file"], w.get("line", ""), w["finding"])
        for e in result["parse_errors"]:
            print("ERROR:", e["file"], e["error"])
        print("Limitaciones:", result["limitations"])
    return 2 if result["parse_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
