"""Pruebas offline de la skill y herramientas; ninguna conexión externa."""
from __future__ import annotations

import importlib.util
import hashlib
import json
import re
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = SKILL / "scripts" / name
    spec = importlib.util.spec_from_file_location(name[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


installer = load_script("install_skill.py")
auditor = load_script("audit_flask.py")


class TestSkillManifest(unittest.TestCase):
    def test_frontmatter_links_and_length(self):
        installer.validate_skill(SKILL)
        body = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertLess(len(body.splitlines()), 500)
        self.assertEqual(re.search(r"(?m)^name: (.+)$", body).group(1), "flask-backend")
        for link in re.findall(r"\]\((references/[^)#]+)\)", body):
            self.assertTrue((SKILL / link).is_file(), link)
        self.assertGreaterEqual(len(list((SKILL / "references").glob("*.md"))), 5)

    def test_evals_include_negative_activation(self):
        data = json.loads((SKILL / "evals/evals.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(data["scenarios"]), 6)
        self.assertGreaterEqual(sum(not x["should_activate"] for x in data["scenarios"]), 2)

    def test_reference_follows_original_manager_db(self):
        src = (SKILL / "references/database-di.md").read_text(encoding="utf-8")
        for token in ("class_=Session", "Generator[Session, None, None]", "rollback()", "app.extensions"):
            self.assertIn(token, src)


class TestInstaller(unittest.TestCase):
    def test_paths_for_project_and_user(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(root / ".agents/skills/flask-backend",
                             next(iter(installer.destinations("both", "project", root).values())))
            self.assertEqual(root / ".agents/skills/flask-backend",
                             next(iter(installer.destinations("codex", "user", root).values())))
            self.assertEqual(root / ".opencode/skills/flask-backend",
                             next(iter(installer.destinations("opencode", "project", root).values())))
            self.assertEqual(root / ".config/opencode/skills/flask-backend",
                             next(iter(installer.destinations("opencode", "user", root).values())))

    def test_dry_run_changes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = installer.install(root=root, dry_run=True)
            self.assertFalse((root / ".agents").exists())
            self.assertEqual(result["installed"], [])

    def test_real_install_and_explicit_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = installer.install(root=root)
            self.assertEqual(report["installed"], ["codex-y-opencode"])
            dest = root / ".agents/skills/flask-backend"
            self.assertEqual((dest / "SKILL.md").read_bytes(), (SKILL / "SKILL.md").read_bytes())
            with self.assertRaises(FileExistsError):
                installer.install(root=root)
            (dest / "local-extra.txt").write_text("not part of the skill", encoding="utf-8")
            installer.install(root=root, force=True)
            self.assertFalse((dest / "local-extra.txt").exists())

    def test_symlink_target_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            link = root / ".agents/skills/flask-backend"
            link.parent.mkdir(parents=True)
            outside = root / "outside"
            outside.mkdir()
            try:
                link.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("Entorno sin permiso para symlinks")
            with self.assertRaises(ValueError):
                installer.install(root=root, force=True)
            self.assertEqual(list(outside.iterdir()), [])


class TestAuditor(unittest.TestCase):
    def test_methodview_blueprints(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src/applications/login"
            src.mkdir(parents=True)
            (src / "router.py").write_text('''from flask_smorest import Blueprint
from flask.views import MethodView
blp = Blueprint("login", "login", url_prefix="/login")
@blp.route("/register")
class Register(MethodView):
    @require_db_session
    @require_auth()
    @require_role("admin")
    def post(self, payload, *, db):
        return {}
''', encoding="utf-8")
            result = auditor.audit(root)
            self.assertEqual([(e["method"], e["path"]) for e in result["endpoints"]],
                             [("POST", "/login/register")])
            self.assertEqual(result["warnings"], [])

    def test_missing_register_auth_is_a_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            root.mkdir(exist_ok=True)
            (root / "routes.py").write_text('''blp = Blueprint("x", "x", url_prefix="/login")
@blp.route("/register")
class Register(MethodView):
    def post(self): pass
''', encoding="utf-8")
            result = auditor.audit(root)
            self.assertEqual(len(result["warnings"]), 1)
            self.assertIn("Alta de usuarios", result["warnings"][0]["finding"])

    def test_wrong_decorator_order_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "routes.py").write_text('''blp = Blueprint("login", "login", url_prefix="/login")
@blp.route("/register")
class Register(MethodView):
    @require_auth()
    @require_db_session
    @require_role("admin")
    def post(self, *, db): pass
''', encoding="utf-8")
            findings = [w["finding"] for w in auditor.audit(root)["warnings"]]
            self.assertTrue(any("Orden de decoradores" in w for w in findings))

    def test_contextmanager_iterator_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "manager_db.py").write_text('''from contextlib import contextmanager
from typing import Iterator
@contextmanager
def get_session() -> Iterator[Session]:
    yield Session()
''', encoding="utf-8")
            result = auditor.audit(root)
            self.assertTrue(any("Iterator" in w["finding"] for w in result["warnings"]))

    def test_generator_has_no_deprecation_hint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "manager_db.py").write_text('''from contextlib import contextmanager
from collections.abc import Generator
@contextmanager
def get_session() -> Generator[Session, None, None]:
    yield Session()
''', encoding="utf-8")
            self.assertEqual(auditor.audit(root)["warnings"], [])

    def test_ast_does_not_execute_user_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "bad.py").write_text('raise SystemExit("WOULD EXECUTE")\n', encoding="utf-8")
            result = auditor.audit(root)
            self.assertEqual(result["python_files_parsed"], 1)
            self.assertEqual(result["parse_errors"], [])

    def test_syntax_error_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "bad.py").write_text('def broken(\n', encoding="utf-8")
            self.assertEqual(len(auditor.audit(root)["parse_errors"]), 1)



class TestSourceExamples(unittest.TestCase):
    """Los ejemplos originales deben permanecer idénticos a los del ZIP del usuario."""

    def test_all_examples_match_manifest(self):
        manifest = json.loads((SKILL / "examples/source-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["source_archive"], "flask-estructura-fastapi-tipado-corregido.zip")
        self.assertTrue(manifest["copied_unchanged"])
        paths = {item["path"] for item in manifest["files"]}
        base = SKILL / "examples/backend_sync"
        self.assertEqual(len(paths), manifest["file_count"])
        actual = {p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()}
        self.assertEqual(actual, paths)
        for item in manifest["files"]:
            content = (base / item["path"]).read_bytes()
            self.assertEqual(len(content), item["bytes"], item["path"])
            self.assertEqual(hashlib.sha256(content).hexdigest(), item["sha256"], item["path"])

    def test_original_manager_db_and_app_factory(self):
        manager = (SKILL / 'examples/backend_sync/src/core/manager_db.py').read_text(encoding='utf-8')
        main = (SKILL / 'examples/backend_sync/src/main.py').read_text(encoding='utf-8')
        for token in ('class_=Session', 'expire_on_commit=False', 'pool_pre_ping=True',
                      'pool_recycle=1800', 'db.rollback()', 'Generator[Session, None, None]'):
            self.assertIn(token, manager)
        self.assertIn('def create_app(', main)
        self.assertIn('configure_database(app)', main)

    def test_examples_are_routed_from_skill_and_index(self):
        readme = (SKILL / 'examples/README.md').read_text(encoding='utf-8')
        main = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
        self.assertIn('examples/README.md', main)
        self.assertIn('examples/backend_sync/src/core/manager_db.py', main)
        self.assertIn('backend_sync/tests/test_auth.py', readme)
        self.assertIn('backend_sync/migrations/versions/', readme)

    def test_installer_copies_examples(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            installer.install(root=root)
            installed=root/'.agents/skills/flask-backend/examples/backend_sync/src/core/manager_db.py'
            source=SKILL/'examples/backend_sync/src/core/manager_db.py'
            self.assertEqual(installed.read_bytes(), source.read_bytes())


if __name__ == "__main__":
    unittest.main()
