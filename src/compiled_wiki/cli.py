from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from compiled_wiki import __version__
from compiled_wiki.index_build import build_ir_index
from compiled_wiki.ir_validate import validate_ir
from compiled_wiki.lint_repo import lint_repo
from compiled_wiki.llm_claims import generate_llm_claim_candidates
from compiled_wiki.pdf_extract import extract_source_markdown
from compiled_wiki.qa import resolve_answer_provider, run_ask
from compiled_wiki.repo import find_repo_root
from compiled_wiki.source_bundle import bundle_pdf_source


_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,62}$")


def _cmd_info(root: Path) -> int:
    print(f"repo root: {root}")
    print(f"cw version: {__version__}")
    return 0


def _cmd_stats(root: Path) -> int:
    def load_list(rel: str) -> list:
        p = root / rel
        if not p.is_file():
            print(f"{rel}: (missing)")
            return []
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"{rel}: invalid JSON ({e})")
            return []
        if not isinstance(data, list):
            print(f"{rel}: (not an array)")
            return []
        return data

    claims = load_list("ir/claims.json")
    entities = load_list("ir/entities.json")
    conflicts = load_list("ir/conflicts.json")
    raw_dirs = sorted([p.name for p in (root / "raw").iterdir() if p.is_dir()]) if (root / "raw").is_dir() else []

    print(f"claims:    {len(claims)}")
    print(f"entities:  {len(entities)}")
    print(f"conflicts: {len(conflicts)}")
    print(f"raw/ source folders: {len(raw_dirs)}")
    if raw_dirs:
        for name in raw_dirs[:20]:
            print(f"  - raw/{name}/")
        if len(raw_dirs) > 20:
            print(f"  ... and {len(raw_dirs) - 20} more")
    return 0


def _cmd_validate(root: Path) -> int:
    errs = validate_ir(root)
    if errs:
        print("validate: FAILED")
        for e in errs:
            print(f"  - {e}")
        return 1
    print("validate: OK (IR matches JSON Schema)")
    return 0


def _cmd_lint(root: Path) -> int:
    errs, warns = lint_repo(root)
    for w in warns:
        print(f"warning: {w}")
    if errs:
        print("lint: ERRORS")
        for e in errs:
            print(f"  error: {e}")
        return 1
    print("lint: OK (no errors" + (", warnings above)" if warns else ")"))
    return 0


def _cmd_index_build(root: Path, overwrite: bool) -> int:
    try:
        result = build_ir_index(root, overwrite=overwrite)
    except (FileExistsError, ValueError, json.JSONDecodeError) as e:
        print(str(e), file=sys.stderr)
        return 2
    print(f"wrote: {result.output_path.relative_to(root)}")
    print(f"docs: {result.doc_count}")
    print(f"tokens: {result.token_count}")
    return 0


def _cmd_raw_init(root: Path, source_id: str, title: str | None) -> int:
    if not _SLUG_RE.match(source_id):
        print(
            "Invalid source_id. Use a short slug: lowercase letters, digits, hyphen/underscore, "
            "1–63 chars, e.g. paper_alpha_2024",
            file=sys.stderr,
        )
        return 2

    dest = root / "raw" / source_id
    if dest.exists():
        print(f"Already exists: {dest}", file=sys.stderr)
        return 2

    dest.mkdir(parents=True)
    meta = {
        "source_id": source_id,
        "title": title or "",
        "notes": "Fill title; add files next to this folder (PDF, md, etc.).",
    }
    (dest / "metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (dest / "NOTES.md").write_text(
        "# Notes\n\n"
        "Put the **original** or a verbatim copy of your material in this folder.\n\n"
        "Examples:\n\n"
        "- `article.pdf`\n"
        "- `transcript.txt`\n"
        "- `web_snapshot.md`\n\n"
        "Keep `source_id` in `metadata.json` equal to the folder name so `cw lint` can trace claims.\n",
        encoding="utf-8",
    )
    print(f"Created {dest}")
    print("Next: copy your document(s) into that folder, then run ingest (see AGENTS.md) or `cw stats`.")
    return 0


def _cmd_raw_bundle_pdf(root: Path, pdf: Path, source_id: str, title: str, execute: bool) -> int:
    try:
        result = bundle_pdf_source(
            repo_root=root,
            pdf_path=pdf,
            source_id=source_id,
            title=title,
            execute=execute,
        )
    except (FileNotFoundError, FileExistsError, ValueError) as e:
        print(str(e), file=sys.stderr)
        return 2

    rel_dir = result.source_dir.relative_to(root)
    mode = "created" if result.executed else "would create"
    print(f"{mode}: {rel_dir}/")
    print(f"{'moved' if result.executed else 'would move'}: {result.pdf_name}")
    print(f"{'wrote' if result.executed else 'would write'}: metadata.json, NOTES.md")
    if not result.executed:
        print("dry-run only; add --execute to write changes")
    return 0


def _cmd_extract_markdown(root: Path, source_id: str, overwrite: bool) -> int:
    try:
        result = extract_source_markdown(repo_root=root, source_id=source_id, overwrite=overwrite)
    except (FileNotFoundError, FileExistsError, RuntimeError, ValueError, json.JSONDecodeError) as e:
        print(str(e), file=sys.stderr)
        return 2

    print(f"wrote: {result.output_path.relative_to(root)}")
    print(f"source: {result.pdf_path.relative_to(root)}")
    return 0


def _cmd_extract_llm_claims(
    root: Path,
    source_id: str,
    provider: str,
    model: str | None,
    max_chars: int,
    overwrite: bool,
) -> int:
    try:
        result = generate_llm_claim_candidates(
            repo_root=root,
            source_id=source_id,
            provider=provider,
            model=model,
            max_chars=max_chars,
            overwrite=overwrite,
        )
    except (FileNotFoundError, FileExistsError, RuntimeError, ValueError, json.JSONDecodeError) as e:
        print(str(e), file=sys.stderr)
        return 2

    print(f"wrote: {result.output_path.relative_to(root)}")
    print(f"provider: {result.provider}")
    print(f"model: {result.model}")
    print(f"candidate claims: {result.claim_count}")
    return 0


def _cmd_ask(
    root: Path,
    question: str,
    limit: int,
    no_refs: bool,
) -> int:
    try:
        print(run_ask(root, question, limit=limit, show_refs=not no_refs, provider="auto", model=None))
    except (FileNotFoundError, json.JSONDecodeError, ValueError, RuntimeError) as e:
        print(str(e), file=sys.stderr)
        return 2
    return 0


def _cmd_chat(root: Path, limit: int) -> int:
    provider = resolve_answer_provider(root, "auto")
    print(f"Compiled-Wiki chat ({provider}). Type 'exit' or 'quit' to leave.")
    while True:
        try:
            question = input("cw> ").strip()
        except EOFError:
            print()
            return 0
        if not question:
            continue
        if question.lower() in {"exit", "quit", ":q"}:
            return 0
        code = _cmd_ask(root, question, limit=limit, no_refs=False)
        if code:
            return code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cw", description="Compiled-Wiki CLI helpers")
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root (default: auto-detect from cwd)",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_info = sub.add_parser("info", help="Print detected repo root and cw version")
    p_stats = sub.add_parser("stats", help="Show counts for IR and raw/ sources")
    p_val = sub.add_parser("validate", help="Validate ir/*.json against compiler/schemas")
    p_lint = sub.add_parser("lint", help="Cross-check IR references and wiki links")
    p_index = sub.add_parser("index", help="Build retrieval index artifacts from IR")
    index_sub = p_index.add_subparsers(dest="index_cmd", required=True)
    p_index_build = index_sub.add_parser("build", help="Build ir/index.json")
    p_index_build.add_argument("--overwrite", action="store_true", help="Replace existing ir/index.json")
    p_ask = sub.add_parser("ask", help="Ask a question against wiki/IR and show retrieved citations")
    p_ask.add_argument("question", help="Question to answer from compiled wiki knowledge")
    p_ask.add_argument("--limit", type=int, default=5, help="Number of retrieved claims to show")
    p_ask.add_argument("--no-refs", action="store_true", help="Only print the answer")
    p_chat = sub.add_parser("chat", help="Interactive CLI chat against wiki/IR")
    p_chat.add_argument("--limit", type=int, default=5, help="Number of retrieved claims to show")

    p_extract = sub.add_parser("extract", help="Create derived extraction artifacts")
    extract_sub = p_extract.add_subparsers(dest="extract_cmd", required=True)
    p_extract_md = extract_sub.add_parser("markdown", help="Extract normalized Markdown from raw/<source_id>/*.pdf")
    p_extract_md.add_argument("source_id", help="Source folder under raw/")
    p_extract_md.add_argument("--overwrite", action="store_true", help="Replace an existing extract")
    p_llm_claims = extract_sub.add_parser(
        "llm-claims",
        help="Generate candidate claims from ir/extracts/<source_id>.md using an LLM API",
    )
    p_llm_claims.add_argument("source_id", help="Source folder under raw/")
    p_llm_claims.add_argument("--provider", default="deepseek", choices=["deepseek"])
    p_llm_claims.add_argument("--model", default=None, help="Provider model name, default from env or deepseek-chat")
    p_llm_claims.add_argument("--max-chars", type=int, default=22000, help="Maximum extract characters to send")
    p_llm_claims.add_argument("--overwrite", action="store_true", help="Replace an existing candidate file")

    p_raw = sub.add_parser("raw", help="Manage raw/ sources (human side)")
    raw_sub = p_raw.add_subparsers(dest="raw_cmd", required=True)
    p_init = raw_sub.add_parser("init", help="Create raw/<source_id>/ with metadata + NOTES.md")
    p_init.add_argument("source_id", help="Folder name under raw/, e.g. acme_handbook_v1")
    p_init.add_argument("--title", default=None, help="Optional human title for metadata.json")

    p_bundle = raw_sub.add_parser(
        "bundle-pdf",
        help="Create raw/<source_id>/ for a PDF already placed under raw/ (dry-run by default)",
    )
    p_bundle.add_argument("pdf", type=Path, help="PDF file path under raw/")
    p_bundle.add_argument("--source-id", required=True, help="Stable source_id folder name")
    p_bundle.add_argument("--title", required=True, help="Human title for metadata.json")
    p_bundle.add_argument("--execute", action="store_true", help="Actually create files and move the PDF")

    args = parser.parse_args(argv)
    try:
        root = args.root.resolve() if args.root else find_repo_root()
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 2

    if args.cmd == "info":
        return _cmd_info(root)
    if args.cmd == "stats":
        return _cmd_stats(root)
    if args.cmd == "validate":
        return _cmd_validate(root)
    if args.cmd == "lint":
        return _cmd_lint(root)
    if args.cmd == "index":
        if args.index_cmd == "build":
            return _cmd_index_build(root, args.overwrite)
    if args.cmd == "ask":
        return _cmd_ask(root, args.question, args.limit, args.no_refs)
    if args.cmd == "chat":
        return _cmd_chat(root, args.limit)
    if args.cmd == "extract":
        if args.extract_cmd == "markdown":
            return _cmd_extract_markdown(root, args.source_id, args.overwrite)
        if args.extract_cmd == "llm-claims":
            return _cmd_extract_llm_claims(
                root,
                args.source_id,
                args.provider,
                args.model,
                args.max_chars,
                args.overwrite,
            )
    if args.cmd == "raw":
        if args.raw_cmd == "init":
            return _cmd_raw_init(root, args.source_id, args.title)
        if args.raw_cmd == "bundle-pdf":
            return _cmd_raw_bundle_pdf(root, args.pdf, args.source_id, args.title, args.execute)
    print("unknown command", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
