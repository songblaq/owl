"""``akasha ingest`` — add a source (file or raw text) to the vault.

Usage:
    akasha ingest path/to/file.md          # ingest a markdown/text file
    akasha ingest --text "..."             # ingest raw text directly
    cat file.md | akasha ingest            # ingest from stdin
    akasha ingest path/to/file.md --title my-topic --topic aria

What this does:
1. Copies the source file into ~/omb/source/ (if file path given)
2. Prints an LLM action prompt — the LLM reads the source and writes
   atomic entries into entries/ following the akasha entry format
3. Optionally runs `akasha index` to rebuild INDEX.md + GRAPH.tsv

The LLM (Claude Code) is the engine that converts raw text → entries.
This command prepares the input and instructs the LLM what to do.
"""
from __future__ import annotations

import hashlib
import shutil
import sys
from datetime import date
from pathlib import Path
from typing import Optional

from akasha.vault import discover_vault


def _slugify(text: str, max_len: int = 40) -> str:
    import re
    s = text.lower().strip()
    s = re.sub(r"[^\w가-힣]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:max_len] or "source"


def _short_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:8]


def run_ingest(
    vault_arg: Optional[str] = None,
    source_path: Optional[str] = None,
    text: Optional[str] = None,
    title: Optional[str] = None,
    topic: Optional[str] = None,
    dry_run: bool = False,
) -> int:
    vault = discover_vault(vault_arg)
    today = str(date.today())

    # ── resolve content ───────────────────────────────────────────────────────
    content: Optional[str] = None
    source_file: Optional[Path] = None

    if text:
        content = text
    elif source_path:
        p = Path(source_path).expanduser().resolve()
        if not p.exists():
            print(f"error: file not found: {p}", file=sys.stderr)
            return 2
        if not p.is_file():
            print(f"error: not a file: {p}", file=sys.stderr)
            return 2
        content = p.read_text(encoding="utf-8", errors="replace")
        source_file = p
    else:
        # stdin
        if sys.stdin.isatty():
            print("error: no source provided.", file=sys.stderr)
            print("  Usage: akasha ingest <file>", file=sys.stderr)
            print("         akasha ingest --text 'raw content'", file=sys.stderr)
            print("         cat file.md | akasha ingest", file=sys.stderr)
            return 2
        content = sys.stdin.read()

    if not content or not content.strip():
        print("error: source content is empty.", file=sys.stderr)
        return 2

    # ── derive title / slug ───────────────────────────────────────────────────
    if not title:
        if source_file:
            title = source_file.stem
        elif topic:
            title = topic
        else:
            # first non-empty line, capped short
            first_line = next((l.strip().lstrip("#").strip()
                               for l in content.splitlines() if l.strip()), "")
            title = first_line[:40] or "untitled"

    slug = _slugify(title)
    h = _short_hash(content)

    # ── destination paths ─────────────────────────────────────────────────────
    source_dir = vault.parent.parent / "source"   # ~/omb/source/
    if not source_dir.exists():
        source_dir = vault / "sources"            # fallback: vault/sources/

    dest_source = source_dir / f"{today}-{slug}.md"
    entries_dir = vault / "entries"

    # ── dry run ───────────────────────────────────────────────────────────────
    if dry_run:
        print(f"akasha ingest --dry-run")
        print()
        print(f"  source  : {source_file or '(inline text)'}")
        print(f"  title   : {title}")
        print(f"  slug    : {slug}")
        print(f"  hash    : {h}")
        print(f"  topic   : {topic or '(auto-detect)'}")
        print(f"  save to : {dest_source}")
        print(f"  entries : {entries_dir}/")
        print()
        print("  (dry-run) no files written.")
        return 0

    # ── copy source file ──────────────────────────────────────────────────────
    if source_dir.exists():
        dest_source.write_text(content, encoding="utf-8")
        print(f"  saved source → {dest_source}")
    else:
        print(f"  (source dir not found: {source_dir} — skipping source copy)")

    # ── LLM action prompt ─────────────────────────────────────────────────────
    topic_hint = f"primary topic: {topic}" if topic else "primary topic: (infer from content)"
    entries_rel = entries_dir.relative_to(Path.home()) if entries_dir.is_relative_to(Path.home()) else entries_dir

    print()
    print("=" * 60)
    print("  LLM ACTION REQUIRED")
    print("=" * 60)
    print()
    print(f"Source ingested: {dest_source.name}")
    print(f"  {topic_hint}")
    print(f"  entries target: ~/{entries_rel}/")
    print()
    print("Read the source and extract atomic entries in akasha format:")
    print()
    print("  ---")
    print(f"  id: {today}-<slug>")
    print(f"  type: definition|fact|claim|observation")
    print(f"  topics: [{topic or '<primary-topic>'}, ...]")
    print(f"  confidence: high|medium|low")
    print(f"  source: sources/{today}-{slug}.md")
    print(f"  edges: []")
    print(f"  created: {today}")
    print(f"  supersedes: []")
    print(f"  ---")
    print()
    print(f"  ## <claim title>")
    print(f"  <body — atomic claim, 100-300 words>")
    print()
    print(f"  ## Why it matters")
    print(f"  <why this is significant>")
    print()
    print("After writing entries, run:")
    print("  akasha index              # rebuild INDEX.md + GRAPH.tsv")
    print(f"  akasha compile --dump {topic or '<topic>'}  # then write compiled/<topic>.md")
    print()
    print("Source content preview (first 500 chars):")
    print("-" * 40)
    print(content[:500])
    if len(content) > 500:
        print(f"  ... [{len(content) - 500} more chars]")
    print("-" * 40)

    return 0
