#!/usr/bin/env python3
"""Check real examples integrity offline; optionally compare to the original ZIP."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]


def verify(root: Path = SKILL_ROOT, source_zip: Path | None = None) -> dict:
    data = json.loads((root / 'examples/source-manifest.json').read_text(encoding='utf-8'))
    files = data['files']
    bad = []
    if source_zip is not None and not source_zip.is_file():
        raise FileNotFoundError(source_zip)
    archive = zipfile.ZipFile(source_zip) if source_zip is not None else None
    try:
        for item in files:
            filename = root / item['skill_path']
            if not filename.resolve().is_relative_to(root.resolve()) or filename.is_symlink():
                bad.append({'file': item['skill_path'], 'error': 'ruta insegura'}); continue
            if not filename.is_file():
                bad.append({'file': item['skill_path'], 'error': 'falta el archivo'}); continue
            contents = filename.read_bytes()
            if hashlib.sha256(contents).hexdigest() != item['sha256'] or len(contents) != item['bytes']:
                bad.append({'file': item['skill_path'], 'error': 'sha256 o tamaño distinto'}); continue
            if archive is not None:
                try:
                    original = archive.read(item['source_path'])
                except KeyError:
                    bad.append({'file': item['source_path'], 'error': 'archivo no encontrado en ZIP'}); continue
                if contents != original:
                    bad.append({'file': item['source_path'], 'error': 'distinto del ZIP'});
    finally:
        if archive is not None:
            archive.close()
    found = {p.relative_to(root).as_posix() for p in (root/'examples'/'backend_async').rglob('*') if p.is_file()}
    if (root/'examples/project-root-README.md').is_file():
        found.add('examples/project-root-README.md')
    tracked = {item['skill_path'] for item in files}
    extras = sorted(found - tracked)
    if extras:
        bad.append({'error':'archivos inesperados en los ejemplos originales','files':extras})
    return {'verified': len(files) - sum(1 for x in bad if 'file' in x), 'total': len(files), 'ok': not bad, 'errors': bad, 'checked_against_zip': source_zip is not None}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-zip', type=Path, help='ZIP de origen opcional para cotejo byte a byte')
    opts = parser.parse_args()
    try:
        result = verify(source_zip=opts.source_zip)
    except (OSError, json.JSONDecodeError, zipfile.BadZipFile) as e:
        print(f'Error: {e}', file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
