#!/usr/bin/env python3
"""T0-B: fix `YYYY-MM-DD-YYYY-MM-DD-<hex8>-<slug>.md` → `YYYY-MM-DD-<slug>.md`.

Legacy artifact of lattice migration (migrate_a.py v1 bug):
  original: lattice-<hex8>-<date>-<slug>.md
  after v1: <date>-<date>-<hex8>-<slug>.md   (date prepended even though stem already had one)

Fix: keep ONE date, drop hex8, keep slug. Rewrite frontmatter id.

Usage:
    python3 tools/fix_double_date.py <vault> [--apply]
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path


PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})-(\d{4}-\d{2}-\d{2})-([0-9a-z]{8})-(.+)\.md$")
FM_RE = re.compile(r"^(---\n)(.*?)(\n---\n)", re.DOTALL)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: fix_double_date.py <vault> [--apply]")
        return 1
    vault = Path(os.path.expanduser(argv[1])).resolve()
    apply = "--apply" in argv
    entries = vault / "entries"
    renames = 0
    for p in sorted(entries.glob("*.md")):
        m = PATTERN.match(p.name)
        if not m:
            continue
        d1, d2, _hash, slug = m.groups()
        # prefer the inner date (original) when they differ; usually identical
        date = d2 if d1 == d2 else d2
        new_name = f"{date}-{slug}.md"
        new_path = entries / new_name
        if new_path.exists() and new_path != p:
            import hashlib
            h = hashlib.md5(p.stem.encode()).hexdigest()[:4]
            new_name = f"{date}-{slug}-{h}.md"
            new_path = entries / new_name
        if apply:
            text = p.read_text(encoding="utf-8")
            fm_match = FM_RE.match(text)
            if fm_match:
                fm_text = fm_match.group(2)
                new_id = new_path.stem
                lines = fm_text.splitlines()
                for i, line in enumerate(lines):
                    if line.startswith("id:"):
                        lines[i] = f"id: {new_id}"
                        break
                text = fm_match.group(1) + "\n".join(lines) + fm_match.group(3) + text[fm_match.end():]
                p.write_text(text, encoding="utf-8")
            p.rename(new_path)
        renames += 1
    print(f"fix_double_date: {renames} files {'renamed' if apply else '(dry-run)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
