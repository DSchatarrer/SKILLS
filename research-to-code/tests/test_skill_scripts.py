"""Offline tests for our skill utilities and audit fail-closed behavior."""
import copy
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from init_project import initialize_project
from audit_project import audit_project, evaluate_manifest
from numeric_checks import compare_arrays, finite_difference_gradient, check_gradient


class InitProjectTests(unittest.TestCase):
    def test_scaffold_is_unverified_and_audit_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "study"
            initialize_project(target, "Paper ejemplo", source_type="preprint", source_id="1706.03762v7", source_url="https://example.org/paper")
            data = json.loads((target / "implementation_spec.json").read_text())
            self.assertEqual(data["evidence"]["claim_level"], "no_evaluado")
            self.assertEqual(data["equations"], [])
            self.assertEqual(data["source"]["type"], "preprint")
            self.assertGreater(len(evaluate_manifest(target)["issues"]), 0)

    def test_rejects_invalid_url_and_duplicate_scaffold(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "study"
            with self.assertRaises(ValueError):
                initialize_project(target, "Título", source_url="not-a-valid-url")
            initialize_project(target, "Título", source_url="https://example.org/research.pdf")
            with self.assertRaises(FileExistsError):
                initialize_project(target, "Título", source_url="https://example.org/research.pdf")

    def test_local_specification_source(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory)
            path=initialize_project(base / "spec", "Rotación 2D", source_type="specification", source_path="docs/rotation.md", version="rev-3")
            manifest=json.loads(path.read_text())
            self.assertEqual(manifest["source"]["local_path"], "docs/rotation.md")
            self.assertEqual(manifest["source"]["version"], "rev-3")
            self.assertFalse(manifest["source"]["version_verified"])
            self.assertEqual(manifest["schema_version"], "2.0")

    def test_book_without_url_is_supported(self):
        with tempfile.TemporaryDirectory() as directory:
            path=initialize_project(Path(directory) / "book", "Métodos numéricos", source_type="book", source_id="ISBN-EXAMPLE-000")
            result=json.loads(path.read_text())
            self.assertEqual(result["source"]["identifier"], "ISBN-EXAMPLE-000")
            self.assertEqual(result["source"]["type"], "book")

    def test_doi_url_is_supported(self):
        with tempfile.TemporaryDirectory() as directory:
            path=initialize_project(Path(directory) / "study", "Artículo con DOI", source_type="article", source_url="https://doi.org/10.1234/example")
            data=json.loads(path.read_text())
            self.assertEqual(data["source"]["url"], "https://doi.org/10.1234/example")

    def test_rejects_dual_sources_and_invalid_type(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory) / "x"
            with self.assertRaisesRegex(ValueError, "no ambos"):
                initialize_project(root, "X", source_url="https://example.org/a", source_path="a.pdf")
            with self.assertRaisesRegex(ValueError, "desconocido"):
                initialize_project(root, "X", source_type="unknown_provider")

    def test_auditor_accepts_non_preprint_documentation(self):
        with tempfile.TemporaryDirectory() as directory:
            project=Path(directory)
            initialize_project(project, "Guía técnica", source_type="documentation", source_url="https://example.org/guide")
            spec=json.loads((project / "implementation_spec.json").read_text())
            spec["source"].update(primary_source="https://example.org/guide#section-2",source_accessed_at="2026-10-25",license_reviewed=True)
            (project / "implementation_spec.json").write_text(json.dumps(spec))
            issues=evaluate_manifest(project)["issues"]
            self.assertFalse(any("source." in i for i in issues), issues)

    def test_auditor_rejects_malformed_source_url_without_crashing(self):
        with tempfile.TemporaryDirectory() as directory:
            project=Path(directory)
            initialize_project(project,"Malformed",source_type="documentation",source_url="https://example.org")
            path=project / "implementation_spec.json"
            spec=json.loads(path.read_text())
            spec["source"]["url"]=42
            path.write_text(json.dumps(spec))
            self.assertTrue(any("source.url" in msg for msg in evaluate_manifest(project)["issues"]))


class NumericalTests(unittest.TestCase):
    def test_compare_fails_on_silent_broadcast(self):
        with self.assertRaisesRegex(AssertionError, "Shape"):
            compare_arrays(np.ones((2, 1)), np.ones((2, 2)))

    def test_compare_fails_on_wrong_result(self):
        with self.assertRaisesRegex(AssertionError, "Valores distintos"):
            compare_arrays(np.array([1.0]), np.array([2.0]), atol=1e-8)

    def test_compare_fails_on_nan(self):
        with self.assertRaisesRegex(AssertionError, "NaN/Inf"):
            compare_arrays(np.array([np.nan]), np.array([1.]))

    def test_exact_array_even_at_zero_tolerance(self):
        stats = compare_arrays(np.array([0., 3.]), np.array([0., 3.]), rtol=0, atol=0)
        self.assertEqual(stats.max_scaled_error, 0.0)
        self.assertEqual(stats.n_elements, 2)

    def test_finite_differences_against_known_gradient(self):
        x = np.array([1., -3., 2.])
        got = finite_difference_gradient(lambda t: float(np.sum(t * t)), x)
        np.testing.assert_allclose(got, 2 * x, rtol=1e-9, atol=1e-9)

    def test_two_step_gradient_matches_hand_derived_weighted_mean(self):
        p = np.array([0.9, 0.1], dtype=np.float64)
        x = np.array([2., 10.], dtype=np.float64)
        result = check_gradient(lambda t: float(np.sum(p * t)), x, expected_gradient=p)
        self.assertEqual(result.relative_steps, (1e-4, 1e-5))
        self.assertEqual(len(result.max_abs_errors), 2)
        self.assertLess(max(result.max_abs_errors), 1e-9)
        self.assertLess(result.max_step_disagreement, 1e-9)

    def test_two_step_gradient_rejects_wrong_analytic_oracle(self):
        p = np.array([0.9, 0.1], dtype=np.float64)
        with self.assertRaisesRegex(AssertionError, "Gradiente incorrecto"):
            check_gradient(lambda t: float(np.sum(p * t)),
                           np.array([2., 10.]), expected_gradient=np.array([0.5, 0.5]))

    def test_two_step_gradient_validates_steps_and_shapes(self):
        f = lambda x: float(np.sum(x ** 2))
        with self.assertRaisesRegex(ValueError, "dos pasos distintos"):
            check_gradient(f, np.array([1.]), np.array([2.]), relative_steps=(1e-4, 1e-4))
        with self.assertRaisesRegex(ValueError, "Shape del gradiente"):
            check_gradient(f, np.array([1.]), np.array([2., 4.]))

    def test_two_step_gradient_rejects_nonfinite_objective(self):
        with self.assertRaisesRegex(ValueError, "función no es finita"):
            check_gradient(lambda x: float('nan'), np.array([1.]), np.array([2.]))


class MutationDetectionTests(unittest.TestCase):
    def test_bad_scaling_is_caught_by_paper_tests(self):
        """Mutate a correct formula and verify that at least one test FAILS."""
        src = ROOT / "examples/attention_1706_03762"
        with tempfile.TemporaryDirectory() as directory:
            scratch = Path(directory)
            shutil.copy2(src / "attention.py", scratch / "attention.py")
            shutil.copytree(src / "tests", scratch / "tests", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            source = (scratch / "attention.py").read_text()
            correct = "scores = np.matmul(q, np.swapaxes(k, -1, -2)) / math.sqrt(q.shape[-1])"
            self.assertIn(correct, source)
            (scratch / "attention.py").write_text(source.replace(correct,
                "scores = np.matmul(q, np.swapaxes(k, -1, -2)) / q.shape[-1]", 1))
            proc = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                                  cwd=scratch, capture_output=True, text=True, timeout=45)
            self.assertNotEqual(proc.returncode, 0, "El test no detectó escalado incorrecto")
            self.assertIn("FAIL", proc.stderr)


class AuditTests(unittest.TestCase):
    def test_verified_example_passes_structural_audit(self):
        result = evaluate_manifest(ROOT / "examples/attention_1706_03762")
        self.assertEqual(result["issues"], [])
        self.assertEqual(result["warnings"], [])

    def test_audit_detects_false_reproducibility_claims(self):
        example = ROOT / "examples/attention_1706_03762"
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            doc = json.loads((example / "implementation_spec.json").read_text())
            doc["evidence"]["claim_level"] = "reproduccion_experimental"
            doc["evidence"]["reported_experiments"] = False
            # Keep source test files local; audit should also detect missing paths.
            (project / "implementation_spec.json").write_text(json.dumps(doc))
            result = evaluate_manifest(project)
            self.assertTrue(any("sin experimentos" in x for x in result["issues"]))
            self.assertTrue(any("ruta inexistente" in x for x in result["issues"]))

    def test_audit_rejects_path_escape(self):
        example = ROOT / "examples/attention_1706_03762"
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            spec = json.loads((example / "implementation_spec.json").read_text())
            spec["equations"][0]["implementation"] = "../../etc/passwd"
            (project / "implementation_spec.json").write_text(json.dumps(spec))
            result = evaluate_manifest(project)
            self.assertTrue(any("ruta inexistente o fuera" in x for x in result["issues"]))

    def test_audit_runs_example_tests(self):
        example = ROOT / "examples/attention_1706_03762"
        result = audit_project(example, run_tests=True)
        self.assertFalse(result["issues"], result["issues"])
        self.assertIn("Ran ", result["test_run"]["output"])


if __name__ == "__main__":
    unittest.main()
