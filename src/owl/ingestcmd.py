"""``owl ingest`` / ``owl compile`` / ``owl file`` — deterministic primitives.

These three commands form the deterministic side of the wiki maintenance loop.
Each one does **only** the file-system part: moving/renaming/validating paths.
The interpretive work — actually compiling content, choosing related items,
writing summaries — is handed off to an owl-* subagent via the matching slash
command (`/owl-ingest`, `/owl-compile`, `/owl-file`).

This is the core of the Agent CLI First + LLM hybrid pattern: CLI handles
what is decidable, LLM handles what requires judgment.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from owl.vault import discover_vault

# Output kind → outputs subdirectory
OUTPUT_KINDS = {
    "slide": "slides",
    "slides": "slides",
    "figure": "figures",
    "figures": "figures",
    "visual": "visuals",
    "visuals": "visuals",
}

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-")
SLUG_RE = re.compile(r"[^a-z0-9가-힣\-]+")


def _slugify(text: str) -> str:
    text = text.casefold()
    text = SLUG_RE.sub("-", text)
    return text.strip("-")


def _today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def ingest_file(source: str, vault_arg: Optional[str] = None, copy: bool = False) -> int:
    """Move (or copy) a candidate file into vault/raw/ with naming convention.

    Naming: ``YYYY-MM-DD-<slug>-raw.md`` where:
        - YYYY-MM-DD comes from the source file's mtime if no date in name,
          otherwise the existing date is preserved.
        - <slug> is derived from the source filename, stripping the original
          extension and any trailing -raw suffix.

    The CLI does NOT decide whether the file is "good enough" to be raw —
    that's a judgment call delegated to owl-librarian via /owl-ingest.
    """
    vault = discover_vault(vault_arg)
    if not vault.exists():
        print(f"error: vault does not exist: {vault}", file=sys.stderr)
        return 2

    raw_dir = vault / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    src = Path(source).expanduser().resolve()
    if not src.exists():
        print(f"error: source file does not exist: {src}", file=sys.stderr)
        return 2
    if not src.is_file():
        print(f"error: not a file: {src}", file=sys.stderr)
        return 2

    # Build target filename
    stem = src.stem
    if stem.endswith("-raw"):
        stem = stem[: -len("-raw")]

    if DATE_RE.match(stem):
        date_part = stem[:10]
        rest = stem[11:]
    else:
        date_part = _today_str()
        rest = stem

    slug = _slugify(rest) or "untitled"
    target_name = f"{date_part}-{slug}-raw.md"
    target = raw_dir / target_name

    if target.exists():
        print(f"error: target already exists (raw is immutable): {target}", file=sys.stderr)
        return 2

    if copy:
        shutil.copyfile(src, target)
        action = "copied"
    else:
        shutil.move(str(src), target)
        action = "moved"

    payload = {
        "vault": str(vault),
        "source": str(src),
        "target": str(target.relative_to(vault)),
        "target_absolute": str(target),
        "action": action,
        "expected_summary": f"compiled/{date_part}-{slug}-summary.md",
        "next_step": (
            "Hand off to owl-librarian via /owl-ingest, "
            "or directly compile via /owl-compile " + target_name
        ),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def compile_metadata(raw_path: str, vault_arg: Optional[str] = None) -> int:
    """Print compile metadata for a raw file (for owl-compiler subagent).

    Does NOT actually compile — just outputs JSON describing the target raw,
    expected summary path, and naming components. The /owl-compile slash
    command consumes this and hands off to the owl-compiler subagent.
    """
    vault = discover_vault(vault_arg)
    if not vault.exists():
        print(f"error: vault does not exist: {vault}", file=sys.stderr)
        return 2

    candidate = Path(raw_path).expanduser()
    if not candidate.is_absolute():
        # Try as vault-relative
        candidate = vault / raw_path
    candidate = candidate.resolve()

    if not candidate.exists():
        print(f"error: raw file not found: {candidate}", file=sys.stderr)
        return 2

    try:
        rel = candidate.relative_to(vault.resolve())
    except ValueError:
        print(f"error: file is not inside the vault: {candidate}", file=sys.stderr)
        return 2

    if rel.parts[0] != "raw":
        print(f"warning: file is not under raw/: {rel}", file=sys.stderr)

    name = candidate.stem
    if name.endswith("-raw"):
        name = name[: -len("-raw")]
    if DATE_RE.match(name):
        date_part = name[:10]
        slug = name[11:]
    else:
        date_part = _today_str()
        slug = name

    summary_name = f"{date_part}-{slug}-summary.md"
    note_name = f"{date_part}-{slug}-note.md"

    payload = {
        "vault": str(vault),
        "raw": str(rel),
        "raw_absolute": str(candidate),
        "date": date_part,
        "slug": slug,
        "expected_summary": f"compiled/{summary_name}",
        "expected_note": f"compiled/{note_name}",
        "summary_exists": (vault / "compiled" / summary_name).exists(),
        "note_exists": (vault / "compiled" / note_name).exists(),
        "next_step": (
            "Hand off to owl-compiler subagent via /owl-compile. "
            "The subagent will read the raw and produce summary (and optionally note) "
            "following compiled-format-spec-v0.md."
        ),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def file_output(output_path: str, kind: str, vault_arg: Optional[str] = None) -> int:
    """Move an output file (slide/figure/visual) into vault/outputs/<kind>/.

    Closes part of the filing loop — the LLM-side step (linking the output
    from a compiled report) is delegated to owl-librarian via /owl-file.
    """
    vault = discover_vault(vault_arg)
    if not vault.exists():
        print(f"error: vault does not exist: {vault}", file=sys.stderr)
        return 2

    subdir_name = OUTPUT_KINDS.get(kind.casefold())
    if subdir_name is None:
        print(
            f"error: unknown output kind '{kind}'. Use one of: slide, figure, visual",
            file=sys.stderr,
        )
        return 2

    src = Path(output_path).expanduser().resolve()
    if not src.exists():
        print(f"error: output file does not exist: {src}", file=sys.stderr)
        return 2

    target_dir = vault / "outputs" / subdir_name
    target_dir.mkdir(parents=True, exist_ok=True)

    target = target_dir / src.name
    if target.exists():
        # Disambiguate by appending timestamp
        target = target_dir / f"{target.stem}-{int(datetime.now().timestamp())}{target.suffix}"

    shutil.move(str(src), target)

    payload = {
        "vault": str(vault),
        "source": str(src),
        "target": str(target.relative_to(vault)),
        "target_absolute": str(target),
        "kind": subdir_name,
        "next_step": (
            "Hand off to owl-librarian via /owl-file to add a link from "
            "the relevant compiled/*-report.md (closing the filing loop)."
        ),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0
