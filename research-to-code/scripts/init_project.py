#!/usr/bin/env python3
"""Create an offline, unverified scientific or technical implementation scaffold."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

SOURCE_TYPES = ("article", "preprint", "conference_paper", "book", "thesis", "technical_report", "documentation", "specification", "notebook", "other")


def initialize_project(root: Path, title: str, *, source_type: str = "article",
                       source_url: str | None = None, source_path: str | None = None,
                       source_id: str | None = None, version: str | None = None) -> Path:
    """Create files, recording source metadata as *unverified* until examined."""
    if not title or not title.strip():
        raise ValueError("Se requiere un título")
    if source_type not in SOURCE_TYPES:
        raise ValueError(f"Tipo de fuente desconocido: {source_type}")
    if source_url and source_path:
        raise ValueError("Indica --source-url o --source-path, no ambos")
    if source_url:
        parsed=urlparse(source_url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("--source-url debe ser una URL HTTP(S) válida")
    if source_path is not None and not str(source_path).strip():
        raise ValueError("--source-path no puede estar vacío")
    root=Path(root)
    manifest_path=root / "implementation_spec.json"
    if manifest_path.exists():
        raise FileExistsError(f"Ya existe {manifest_path}")
    root.mkdir(parents=True,exist_ok=True)
    for subdir in ("src", "tests", "configs", "experiments", "results"):
        folder=root / subdir
        folder.mkdir(exist_ok=True)
        (folder / ".gitkeep").touch(exist_ok=True)
    source={
        "type":source_type, "title":title.strip(), "identifier":source_id,
        "url":source_url, "local_path":source_path, "version":version,
        "version_verified":False, "source_accessed_at":None,
        "primary_source":None, "authors_code_url":None, "license_reviewed":False,
    }
    manifest={
        "schema_version":"2.0", "source":source,
        "scope":{"target":"PENDIENTE: definir componente o experimento", "kind":"component", "out_of_scope":[]},
        "equations":[], "experiments":[],
        "environment":{"python":None,"dependencies":[],"seed":None,"hardware":None},
        "unknowns":["Verificar la fuente original, identificar versión y resolver hipótesis"],
        "evidence":{"claim_level":"no_evaluado","independent_reference":False,"reported_experiments":False},
    }
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    origin=source_url or source_path or source_id or "PENDIENTE"
    (root / "README.md").write_text(
        f"# {title.strip()}\n\nTipo de fuente: {source_type}\nReferencia: {origin}\n\n"
        "Estado: no evaluado. Completar `implementation_spec.json`, código y pruebas.\n",
        encoding="utf-8",
    )
    (root / "REPRODUCTION_REPORT.md").write_text(
        "# REPRODUCTION_REPORT\n\nEstado: **NO EVALUADO**. No se han ejecutado pruebas ni experimentos.\n\n"
        "- Fuente y versión: pendiente\n- Ecuación → función → test: pendiente\n"
        "- Protocolo, diferencias y límites: pendiente\n- Comandos y logs reales: pendiente\n",
        encoding="utf-8",
    )
    return manifest_path


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,required=True)
    parser.add_argument("--title",required=True)
    parser.add_argument("--source-type",choices=SOURCE_TYPES,default="article")
    parser.add_argument("--source-url")
    parser.add_argument("--source-path")
    parser.add_argument("--source-id")
    parser.add_argument("--version")
    args=parser.parse_args()
    try:
        path=initialize_project(args.root,args.title,source_type=args.source_type,
                                source_url=args.source_url,source_path=args.source_path,
                                source_id=args.source_id,version=args.version)
    except (OSError,ValueError) as exc:
        parser.error(str(exc))
    print(f"Creado: {path}\nEstado inicial: NO EVALUADO")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
