from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


_LIGATURES = {
    "\ufb00": "ff",
    "\ufb01": "fi",
    "\ufb02": "fl",
    "\ufb03": "ffi",
    "\ufb04": "ffl",
}


@dataclass(frozen=True)
class MarkdownExtractResult:
    source_id: str
    output_path: Path
    pdf_path: Path


def _load_metadata(source_dir: Path) -> dict:
    path = source_dir / "metadata.json"
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _find_single_pdf(source_dir: Path) -> Path:
    pdfs = sorted(source_dir.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(f"No PDF found in {source_dir}")
    if len(pdfs) > 1:
        names = ", ".join(p.name for p in pdfs)
        raise ValueError(f"Expected one PDF in {source_dir}; found: {names}")
    return pdfs[0]


def _extract_pdf_text(pdf_path: Path) -> str:
    proc = subprocess.run(
        ["pdftotext", str(pdf_path), "-"],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"pdftotext failed for {pdf_path}")
    return proc.stdout


def _normalize_text(text: str) -> str:
    for src, dst in _LIGATURES.items():
        text = text.replace(src, dst)
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\f", "\n\n--- page break ---\n\n")
    lines: list[str] = []
    blank = False
    for raw in text.splitlines():
        line = raw.rstrip()
        line = re.sub(r"[ \t]{2,}", " ", line).strip()
        if not line:
            if not blank:
                lines.append("")
            blank = True
            continue
        blank = False
        lines.append(line)
    return "\n".join(lines).strip() + "\n"


def extract_source_markdown(
    *,
    repo_root: Path,
    source_id: str,
    overwrite: bool = False,
) -> MarkdownExtractResult:
    source_dir = repo_root / "raw" / source_id
    if not source_dir.is_dir():
        raise FileNotFoundError(f"Source folder not found: raw/{source_id}/")
    meta = _load_metadata(source_dir)
    pdf = _find_single_pdf(source_dir)
    output_dir = repo_root / "ir" / "extracts"
    output_path = output_dir / f"{source_id}.md"
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"Extract already exists: {output_path.relative_to(repo_root)}")

    title = meta.get("title") or pdf.stem
    text = _normalize_text(_extract_pdf_text(pdf))
    body = (
        f"# {title}\n\n"
        "> Derived Markdown text extracted from the PDF for ingestion.\n"
        "> The PDF under `raw/` remains the source of truth.\n\n"
        f"- source_id: `{source_id}`\n"
        f"- raw_pdf: `raw/{source_id}/{pdf.name}`\n\n"
        "## Extracted Text\n\n"
        f"{text}"
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_text(body, encoding="utf-8")
    return MarkdownExtractResult(source_id=source_id, output_path=output_path, pdf_path=pdf)
