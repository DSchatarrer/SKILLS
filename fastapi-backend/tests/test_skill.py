"""Offline tests of skill packaging, safe installation and static backend inventory."""
from __future__ import annotations

import hashlib
import importlib.util
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
auditor = load_script("audit_backend.py")


class TestSkillManifest(unittest.TestCase):
    def test_frontmatter_and_references(self):
        installer.validate_skill(SKILL)
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertLess(len(text.splitlines()), 500)
        name = re.search(r"(?m)^name:\s*(.+)$", text)
        self.assertEqual(name.group(1).strip(), "fastapi-backend")
        for link in re.findall(r"\]\((references/[^)#]+)\)", text):
            self.assertTrue((SKILL / link).is_file(), link)
        self.assertGreaterEqual(len(list((SKILL / "references").glob("*.md"))), 5)

    def test_evals_valid_and_includes_negative_case(self):
        evaluation = json.loads((SKILL / "evals" / "evals.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(evaluation["scenarios"]), 3)
        self.assertIn("no-activar-frontend", {e["id"] for e in evaluation["scenarios"]})


class TestInstaller(unittest.TestCase):
    def test_destinations_project_and_user(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shared = root / ".agents/skills/fastapi-backend"
            self.assertEqual(shared, next(iter(installer.destinations("both", "project", root).values())))
            self.assertEqual(shared, next(iter(installer.destinations("codex", "user", root).values())))
            self.assertEqual(root / ".opencode/skills/fastapi-backend",
                             next(iter(installer.destinations("opencode", "project", root).values())))
            self.assertEqual(root / ".config/opencode/skills/fastapi-backend",
                             next(iter(installer.destinations("opencode", "user", root).values())))

    def test_dry_run_installs_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = installer.install(scope="project", root=root, dry_run=True)
            self.assertEqual(result["installed"], [])
            self.assertFalse((root / ".agents").exists())

    def test_install_and_no_silent_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = installer.install(scope="project", root=root)
            self.assertEqual(report["installed"], ["codex-y-opencode"])
            dest = root / ".agents/skills/fastapi-backend"
            self.assertTrue((dest / "SKILL.md").is_file())
            self.assertEqual((dest / "SKILL.md").read_bytes(), (SKILL / "SKILL.md").read_bytes())
            with self.assertRaises(FileExistsError):
                installer.install(scope="project", root=root)
            (dest / "file-user.txt").write_text("local", encoding="utf-8")
            installer.install(scope="project", root=root, force=True)
            self.assertFalse((dest / "file-user.txt").exists())
            self.assertTrue((dest / "references" / "security.md").exists())

    def test_reject_symlink_at_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / ".agents/skills"
            base.mkdir(parents=True)
            external = root / "elsewhere"
            external.mkdir()
            link = base / "fastapi-backend"
            try:
                link.symlink_to(external, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("Symlinks sin permiso en sistema operativo")
            with self.assertRaises(ValueError):
                installer.install(scope="project", root=root, force=True)
            self.assertEqual(list(external.iterdir()), [])


class TestAudit(unittest.TestCase):
    def test_router_inventory_and_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src" / "applications" / "login").mkdir(parents=True)
            path = root / "src" / "applications" / "login" / "router.py"
            path.write_text('''from fastapi import APIRouter
login_router = APIRouter(prefix="/login", tags=["login"])
@login_router.post("/alta-usuario")
async def create_user():
    return {"ok": True}
''', encoding="utf-8")
            report = auditor.audit(root)
            self.assertEqual(len(report["endpoints"]), 1)
            self.assertEqual(report["endpoints"][0]["path"], "/login/alta-usuario")
            self.assertEqual(len(report["warnings"]), 1)
            self.assertEqual(report["parse_errors"], [])

    def test_router_with_role_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "routes.py").write_text('''from fastapi import APIRouter, Depends
from core.security import require_roles
router = APIRouter(prefix="/login", dependencies=[Depends(require_roles("admin"))])
@router.post("/alta-usuario")
async def add():
    return {}
''', encoding="utf-8")
            report = auditor.audit(root)
            self.assertEqual(len(report["warnings"]), 0)
            self.assertTrue(report["endpoints"][0]["router_has_role_dependency"])

    def test_audit_does_not_execute_imports(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "foo.py").write_text('raise RuntimeError("THIS MUST NOT RUN")\n', encoding="utf-8")
            result = auditor.audit(root)
            self.assertEqual(result["python_files_parsed"], 1)
            self.assertEqual(result["parse_errors"], [])



class TestSourceExamples(unittest.TestCase):
    """All shipped samples must match the manifest of the user's source archive."""

    def test_manifest_and_all_original_backend_files(self):
        manifest=json.loads((SKILL/'examples/source-manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['source_archive'], 'fastapi-main.zip')
        self.assertEqual(manifest['source_archive_root'], 'fastapi-main/backend_async/')
        self.assertTrue(manifest['copied_unchanged'])
        self.assertEqual(manifest['file_count'], 36)
        base=SKILL/'examples/backend_async'
        actual={p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()}
        listed={e['path'] for e in manifest['files']}
        self.assertEqual(actual, listed)
        for entry in manifest['files']:
            data=(base/entry['path']).read_bytes()
            self.assertEqual(len(data),entry['bytes'],entry['path'])
            self.assertEqual(hashlib.sha256(data).hexdigest(),entry['sha256'],entry['path'])

    def test_exact_root_readme_and_license_warning(self):
        manifest=json.loads((SKILL/'examples/source-manifest.json').read_text(encoding='utf-8'))
        original=(SKILL/'examples/source-root-README.md').read_bytes()
        self.assertEqual(len(original),manifest['additional_original_file']['bytes'])
        self.assertEqual(hashlib.sha256(original).hexdigest(),manifest['additional_original_file']['sha256'])
        license=(SKILL/'examples/backend_async/LICENSE.md').read_text(encoding='utf-8')
        self.assertIn('Iberdrola S.A.',license)
        self.assertIn('permission',license)
        self.assertIn('licencia', (SKILL/'examples/README.md').read_text(encoding='utf-8').lower())

    def test_real_code_and_progressive_links(self):
        main=(SKILL/'examples/backend_async/src/main.py').read_text(encoding='utf-8')
        db=(SKILL/'examples/backend_async/src/core/manager_db_async.py').read_text(encoding='utf-8')
        router=(SKILL/'examples/backend_async/src/applications/pacientes/router.py').read_text(encoding='utf-8')
        self.assertIn('def create_app()',main)
        self.assertIn('async_sessionmaker',db)
        self.assertIn('AsyncSession',db)
        self.assertIn('require_roles("admin")',router)
        text=(SKILL/'SKILL.md').read_text(encoding='utf-8')
        for link in re.findall(r'\]\((examples/[^)#]+)\)',text):
            self.assertTrue((SKILL/link).is_file(),link)
        self.assertIn('examples/README.md',text)

    def test_installer_preserves_example_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            installer.install(scope='project',root=root)
            expected=(SKILL/'examples/backend_async/src/core/manager_db_async.py').read_bytes()
            installed=(root/'.agents/skills/fastapi-backend/examples/backend_async/src/core/manager_db_async.py').read_bytes()
            self.assertEqual(installed,expected)

if __name__ == "__main__":
    unittest.main()
