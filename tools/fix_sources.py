#!/usr/bin/env python3
"""T0-A: broken source: fuzzy-match recovery.

Strategy (conservative — false positive is worse than false negative):
  1. Parse each entry's `source:` field.
  2. If already resolvable → skip.
  3. Extract slug from declared source (e.g., sources/2026-04-15-homelab-infra-reorg-2026-04-15.md
     → keywords: 2026-04-15, homelab, infra, reorg).
  4. Search ~/omb/input/ for files whose filename contains ALL non-date keywords.
  5. If exactly 1 match → rewrite `source:` to canonical absolute path.
  6. If 0 or >1 → leave unchanged (report).

Usage:
    python3 tools/fix_sources.py <vault-path> [--apply]
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path


FM_RE = re.compile(r"^(---\n)(.*?)(\n---\n)", re.DOTALL)
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def parse_fm(text: str) -> tuple[str, str, str]:
    m = FM_RE.match(text)
    if not m:
        return "", "", text
    return m.group(1), m.group(2), text[m.end():]


def fm_field(fm: str, key: str) -> str:
    for line in fm.splitlines():
        if line.startswith(f"{key}:"):
            return line.split(":", 1)[1].strip()
    return ""


def rewrite_fm_field(fm: str, key: str, value: str) -> str:
    lines = fm.splitlines()
    for i, line in enumerate(lines):
        if line.startswith(f"{key}:"):
            lines[i] = f"{key}: {value}"
            return "\n".join(lines)
    lines.append(f"{key}: {value}")
    return "\n".join(lines)


def keywords_from_src(src: str) -> list[str]:
    name = Path(src).stem
    # remove date and common suffixes
    parts = name.split("-")
    kws: list[str] = []
    for p in parts:
        if DATE_RE.match(f"{p}-00-00"[:10]):
            continue
        if len(p) >= 3 and not p.isdigit():
            kws.append(p.lower())
    return kws


def resolve_existing(src: str, vault: Path, source_root: Path) -> bool:
    if src.startswith("~/"):
        return Path(os.path.expanduser(src)).exists()
    if src.startswith("/"):
        return Path(src).exists()
    if src.startswith("sources/"):
        rel = src[len("sources/"):]
        return (source_root / rel).exists() or (vault / src).exists()
    return (vault / src).exists()


def fuzzy_find(src: str, source_root: Path) -> list[Path]:
    kws = keywords_from_src(src)
    if not kws:
        return []
    date = ""
    m = DATE_RE.search(Path(src).stem)
    if m:
        date = m.group(0)
    candidates: list[Path] = []
    for f in source_root.rglob("*.md"):
        name_lower = f.name.lower()
        if date and date not in name_lower:
            continue
        if all(k in name_lower for k in kws):
            candidates.append(f)
    return candidates


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: fix_sources.py <vault-path> [--apply]")
        return 1
    vault = Path(os.path.expanduser(argv[1])).resolve()
    apply = "--apply" in argv
    source_root = Path(os.path.expanduser("~/omb/input")).resolve()
    entries_dir = vault / "entries"
    if not entries_dir.exists():
        print(f"no entries/ in {vault}", file=sys.stderr)
        return 2

    fixed = 0
    ambiguous = 0
    unresolvable = 0
    already_ok = 0

    for p in sorted(entries_dir.glob("*.md")):
        text = p.read_text(encoding="utf-8")
        open_tag, fm, body = parse_fm(text)
        if not fm:
            continue
        src = fm_field(fm, "source")
        if not src:
            continue
        if resolve_existing(src, vault, source_root):
            already_ok += 1
            continue
        matches = fuzzy_find(src, source_root)
        if len(matches) == 1:
            new_src = "~/omb/input/" + str(matches[0].relative_to(source_root))
            if apply:
                new_fm = rewrite_fm_field(fm, "source", new_src)
                p.write_text(open_tag + new_fm + "\n---\n" + body, encoding="utf-8")
            fixed += 1
        elif len(matches) > 1:
            ambiguous += 1
        else:
            unresolvable += 1

    total = fixed + ambiguous + unresolvable + already_ok
    print(f"fix_sources — {vault}")
    print(f"  scanned:       {total}")
    print(f"  already OK:    {already_ok}")
    print(f"  fixed:         {fixed} {'(applied)' if apply else '(dry-run)'}")
    print(f"  ambiguous:     {ambiguous} (multiple fuzzy matches — left alone)")
    print(f"  unresolvable:  {unresolvable} (no match in ~/omb/input/)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
