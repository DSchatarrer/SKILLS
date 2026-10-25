"""Guardrail tests for the bundled policy/evaluation documentation.

These check consistency of distributed artifacts, NOT actual agent behaviour.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestFirstArtifacts(unittest.TestCase):
    def test_acceptance_phase_precedes_implementation_phase_in_skill(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertLess(skill.index("### 2.1. Pruebas de aceptación matemática primero"),
                        skill.index("### 3. Implementación incremental"))
        self.assertIn("registra primero el test de aceptación", skill)
        self.assertIn("no prueban que se escribieran primero", skill)

    def test_evals_cover_order_and_analytic_gradients(self):
        evals = json.loads((ROOT / "evals" / "evals.json").read_text(encoding="utf-8"))["evals"]
        by_id = {case["id"]: case for case in evals}
        self.assertIn(11, by_id)
        self.assertIn(12, by_id)
        self.assertTrue(any("secuencia" in a.lower() for a in by_id[11]["assertions"]))
        self.assertTrue(any("dos pasos" in a.lower() for a in by_id[12]["assertions"]))
        # In the prompts, do not tell the model to do test-first; evaluate initiative.
        for case_id in (11, 12):
            self.assertNotIn("tests primero", by_id[case_id]["prompt"].lower())

    def test_rubric_rejects_unobserved_order_claims(self):
        rubric = (ROOT / "evals" / "test-first-rubric.md").read_text(encoding="utf-8")
        self.assertIn("NO OBSERVABLE", rubric)
        self.assertIn("INDETERMINADO", rubric)
        self.assertIn("sin la Skill", rubric)


if __name__ == "__main__":
    unittest.main()
