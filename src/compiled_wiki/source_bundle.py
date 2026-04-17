from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from datetime import date
from pathlib import Path


_SOURCE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,62}$")


@dataclass(frozen=True)
class BundleResult:
    source_id: str
    source_dir: Path
    pdf_name: str
    executed: bool


def validate_source_id(source_id: str) -> None:
    if not _SOURCE_ID_RE.match(source_id):
        raise ValueError(
            "Invalid source_id. Use lowercase letters, digits, hyphen/underscore, "
            "1-63 chars, e.g. sun_2024_dc_voltage_prediction_mvdc"
        )


def bundle_pdf_source(
    *,
    repo_root: Path,
    pdf_path: Path,
    source_id: str,
    title: str,
    execute: bool,
    added_date: str | None = None,
) -> BundleResult:
    """Create raw/<source_id>/ around a PDF, optionally moving the PDF there."""
    validate_source_id(source_id)
    root = repo_root.resolve()
    pdf = pdf_path.resolve()
    raw_root = (root / "raw").resolve()

    if not pdf.is_file():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    if pdf.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a .pdf file: {pdf_path}")
    try:
        pdf.relative_to(raw_root)
    except ValueError as exc:
        raise ValueError(f"PDF must live under raw/: {pdf_path}") from exc

    source_dir = raw_root / source_id
    dest_pdf = source_dir / pdf.name
    meta_path = source_dir / "metadata.json"
    notes_path = source_dir / "NOTES.md"

    if source_dir.exists():
        raise FileExistsError(f"Source folder already exists: {source_dir.relative_to(root)}")
    if dest_pdf.exists() or meta_path.exists() or notes_path.exists():
        raise FileExistsError(f"Refusing to overwrite files in: {source_dir.relative_to(root)}")

    if execute:
        source_dir.mkdir(parents=True)
        shutil.move(str(pdf), str(dest_pdf))
        metadata = {
            "source_id": source_id,
            "title": title,
            "document_type": "pdf",
            "original_filename": pdf.name,
            "files": [pdf.name],
            "added_date": added_date or date.today().isoformat(),
            "notes": "Created by cw raw bundle-pdf from a PDF placed under raw/.",
        }
        meta_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        notes_path.write_text(
            "# Notes\n\n"
            "Original PDF source bundle for compiled-wiki ingest.\n\n"
            "Do not edit the PDF in place. Add extraction notes here only when needed.\n",
            encoding="utf-8",
        )

    return BundleResult(source_id=source_id, source_dir=source_dir, pdf_name=pdf.name, executed=execute)
