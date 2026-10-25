#!/usr/bin/env python3
"""Structural and executable-test audit; NOT scientific certification.

WARNING: --run-tests executes local project code. Use only on trusted projects.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

CLAIM_LEVELS = ["no_evaluado", "tests_unitarios", "componente_verificado", "reproduccion_parcial", "reproduccion_experimental"]
SOURCE_TYPES = {"article", "preprint", "conference_paper", "book", "thesis", "technical_report", "documentation", "specification", "notebook", "other"}


def _exists_under(project: Path, relpath: Any) -> bool:
    if not isinstance(relpath, str) or not relpath or Path(relpath).is_absolute():
        return False
    resolved_root = project.resolve()
    resolved_path = (project / relpath).resolve()
    return resolved_path.is_relative_to(resolved_root) and resolved_path.is_file()


def evaluate_manifest(project: Path) -> dict:
    """Check manifest coherence, presence of evidence files and lack of unsupported claims."""
    issues: list[str] = []
    warnings: list[str] = []
    manifest_path = project / "implementation_spec.json"
    if not manifest_path.is_file():
        return {"issues": ["Falta implementation_spec.json"], "warnings": [], "claim_level": "no_evaluado"}
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"issues": [f"No se puede leer el manifiesto: {exc}"], "warnings": [], "claim_level": "no_evaluado"}
    if not isinstance(data, dict):
        return {"issues": ["El manifiesto debe ser un objeto JSON"], "warnings": [], "claim_level": "no_evaluado"}
    if data.get("schema_version") != "2.0":
        issues.append("schema_version desconocida; esperado 2.0")
    source = data.get("source", {})
    if not isinstance(source, dict):
        issues.append("source debe ser un objeto")
        source = {}
    if source.get("type") not in SOURCE_TYPES:
        issues.append("source.type desconocido o ausente")
    if not isinstance(source.get("title"), str) or not source["title"].strip():
        issues.append("Falta source.title")
    if not any(isinstance(source.get(field), str) and source[field].strip()
               for field in ("url", "local_path", "identifier")):
        issues.append("Falta referencia de origen: source.url, source.local_path o source.identifier")
    if source.get("url") is not None:
        from urllib.parse import urlparse
        url=source["url"]
        if not isinstance(url, str):
            issues.append("source.url debe ser cadena HTTP(S)")
        else:
            parsed=urlparse(url)
            if parsed.scheme not in ("http", "https") or not parsed.netloc:
                issues.append("source.url no es HTTP(S) válida")
    if not source.get("source_accessed_at"):
        warnings.append("No está documentada la fecha de acceso a fuente")
    if not source.get("primary_source"):
        issues.append("Falta source.primary_source, enlace o ubicación primaria verificada")
    if not source.get("license_reviewed"):
        warnings.append("Falta revisión de licencias de código/datos")
    scope = data.get("scope", {})
    if not isinstance(scope, dict) or not scope.get("target") or "PENDIENTE" in str(scope.get("target")):
        issues.append("Alcance concreto no definido en scope.target")
    eqs = data.get("equations", [])
    if not isinstance(eqs, list) or not eqs:
        issues.append("No hay ecuaciones/algoritmos trazados en equations")
        eqs = []
    seen = set()
    for idx, eq in enumerate(eqs):
        key = f"equations[{idx}]"
        if not isinstance(eq, dict):
            issues.append(f"{key} debe ser objeto")
            continue
        eq_id = eq.get("id")
        if not isinstance(eq_id, str) or not eq_id.strip() or eq_id in seen:
            issues.append(f"{key}.id ausente o duplicado")
        seen.add(eq_id)
        for field in ("source_section", "expression", "symbols", "input_shapes", "output_shape", "implementation", "reference_implementation", "test_file"):
            if not eq.get(field):
                issues.append(f"{key}.{field} ausente")
        for field in ("implementation", "reference_implementation", "test_file"):
            val = eq.get(field)
            if val and not _exists_under(project, val):
                issues.append(f"{key}.{field}: ruta inexistente o fuera del proyecto: {val}")
        if eq.get("status") not in ("unverified", "unit_tested", "verified", "blocked"):
            issues.append(f"{key}.status desconocido")
        if not isinstance(eq.get("assumptions"), list):
            issues.append(f"{key}.assumptions debe ser lista (puede estar vacía)")
    env = data.get("environment", {})
    if not isinstance(env, dict):
        issues.append("environment debe ser objeto")
    elif not env.get("python") or not env.get("dependencies"):
        warnings.append("Entorno/dependencias sin versionar")
    evidence = data.get("evidence", {})
    if not isinstance(evidence, dict):
        issues.append("evidence debe ser objeto")
        evidence = {}
    level = evidence.get("claim_level", "no_evaluado")
    if level not in CLAIM_LEVELS:
        issues.append(f"claim_level inválido: {level}")
        level = "no_evaluado"
    if level in ("componente_verificado", "reproduccion_parcial", "reproduccion_experimental"):
        if not evidence.get("independent_reference"):
            issues.append("Afirmación de componente verificado sin referencia independiente registrada")
        if any(eq.get("status") != "verified" for eq in eqs if isinstance(eq, dict)):
            issues.append("Afirmación de verificación con ecuaciones sin estado verified")
    if level in ("reproduccion_parcial", "reproduccion_experimental"):
        if not evidence.get("reported_experiments") or not data.get("experiments"):
            issues.append("Reproducción experimental declarada sin experimentos con evidencia")
    if level == "reproduccion_experimental" and data.get("unknowns"):
        warnings.append("Reproducción experimental declarada con incertidumbres pendientes")
    if not (project / "REPRODUCTION_REPORT.md").is_file():
        warnings.append("Falta informe REPRODUCTION_REPORT.md")
    return {"issues": issues, "warnings": warnings, "claim_level": level, "equations_checked": len(eqs)}


def audit_project(project: Path, *, run_tests: bool = False, timeout: int = 120) -> dict:
    result = evaluate_manifest(project)
    if run_tests:
        if not (project / "tests").is_dir():
            result["issues"].append("No hay directorio tests")
        else:
            try:
                proc = subprocess.run(
                    [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                    cwd=project, capture_output=True, text=True, timeout=timeout, check=False,
                )
                combined = proc.stdout + proc.stderr
                result["test_run"] = {"returncode": proc.returncode, "output": combined[-12000:]}
                match = re.search(r"Ran (\d+) tests? in", combined)
                if proc.returncode != 0 or not match or int(match.group(1)) == 0:
                    result["issues"].append("Tests fallaron o no se descubrió ninguno")
            except (OSError, subprocess.TimeoutExpired) as exc:
                result["issues"].append(f"No se ejecutaron tests: {exc}")
    return result


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--run-tests", action="store_true", help="Ejecuta código del proyecto. SOLO proyectos confiables")
    p.add_argument("--strict", action="store_true", help="Warnings también fallan")
    p.add_argument("--json", action="store_true", help="Imprime auditoría JSON")
    p.add_argument("--timeout", type=int, default=120)
    args = p.parse_args()
    if args.timeout <= 0:
        p.error("--timeout debe ser positivo")
    result = audit_project(args.project, run_tests=args.run_tests, timeout=args.timeout)
    failed = bool(result["issues"] or (args.strict and result["warnings"]))
    result["passed"] = not failed
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Estado de auditoría: {'FALLÓ' if failed else 'SIN ERRORES ESTRUCTURALES'}")
        print(f"Claim nivel: {result.get('claim_level')}")
        for msg in result["issues"]:
            print("ERROR:", msg)
        for msg in result["warnings"]:
            print("AVISO:", msg)
        if "test_run" in result:
            print(result["test_run"]["output"])
        print("AVISO: una auditoría estructural exitosa NO garantiza reproducibilidad científica.")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
