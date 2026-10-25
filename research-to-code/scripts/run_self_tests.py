#!/usr/bin/env python3
"""Offline, reproducible smoke/regression suite for this installed skill.

Executes bundled trusted test code only; does not fetch papers or repositories.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def suite() -> dict:
    suites = [
        ("skill_scripts_and_mutation", ROOT, [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]),
        ("attention_1706_03762v7", ROOT / "examples/attention_1706_03762", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]),
        ("local_specification", ROOT / "examples/local_specification", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]),
        ("math_translation", ROOT / "examples/math_patterns", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]),
        ("frameworks_pytorch_tensorflow", ROOT / "examples/frameworks", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]),
        ("sparsemax_1602_02068v2", ROOT / "examples/sparsemax_1602_02068", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]),
        ("manifest_and_attention", ROOT, [sys.executable, "scripts/audit_project.py", "--project", "examples/attention_1706_03762", "--run-tests", "--strict"]),
        ("manifest_and_local_specification", ROOT, [sys.executable, "scripts/audit_project.py", "--project", "examples/local_specification", "--run-tests", "--strict"]),
        ("manifest_and_sparsemax", ROOT, [sys.executable, "scripts/audit_project.py", "--project", "examples/sparsemax_1602_02068", "--run-tests", "--strict"]),
    ]
    results = []
    total = 0
    skipped_total = 0
    for name, cwd, command in suites:
        proc = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=120, check=False)
        output = proc.stdout + proc.stderr
        match = re.search(r"Ran (\d+) tests? in", output)
        n = int(match.group(1)) if match else 0
        skipped_match = re.search(r"skipped=(\d+)", output)
        skipped = int(skipped_match.group(1)) if skipped_match else 0
        if not name.startswith("manifest_and_"):
            total += n - skipped
            skipped_total += skipped
        status = proc.returncode == 0 and (name.startswith("manifest_and_") or n > 0)
        results.append({"name": name, "returncode": proc.returncode, "pass": status,
                        "tests_defined": n, "tests_executed": n - skipped, "tests_skipped": skipped, "command": " ".join(command[1:]), "last_output": output[-2400:]})
    try:
        import numpy as np
        np_version = np.__version__
    except ImportError:
        np_version = "NO INSTALADO"
    def framework_state(name: str) -> str:
        try:
            module = __import__(name)
            return str(module.__version__)
        except ImportError:
            return "NOT INSTALLED / NOT TESTED"
        except Exception as exc:
            return "IMPORT ERROR: " + str(exc)
    return {"timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "python": sys.version.split()[0], "numpy": np_version,
            "torch": framework_state("torch"), "tensorflow": framework_state("tensorflow"),
            "unique_test_cases_executed": total, "unique_test_cases_skipped": skipped_total,
            "all_executed_passed": all(r["pass"] for r in results), "suites": results,
            "limitations": ["No se ejecutaron los agentes Codex, OpenCode ni Claude Code usando esta skill; solo se validaron rutas de instalación y comportamiento del código", "TensorFlow no se declara verificado si está ausente", "No se entrenó el modelo del artículo", "Ningún caso reproduce métricas experimentales: solo operadores matemáticos"]}


def main() -> int:
    result = suite()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["all_executed_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
