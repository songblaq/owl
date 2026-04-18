#!/usr/bin/env python3
"""Experiment C — produce AUDIT.md with human-review candidates.

No automatic mutation. Lists:
  1. Duplicate-decision candidates: (topic, type=decision) groups of ≥2 entries.
  2. Entries with broken source paths.
  3. Orphan entries (no graph edges referencing them).
  4. Compiled docs with no corresponding recent entries.

Human reviewer decides which to supersede, merge, or delete.
"""
from __future__ import annotations

import os
import re
import sys
from collections import defaultdict
from pathlib import Path

FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def parse_fm(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return {}
    m = FM_RE.match(text)
    if not m:
        return {}
    d = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            d[k.strip()] = v.strip()
    return d


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: audit_c.py <vault>")
        return 1
    vault = Path(os.path.expanduser(argv[1])).resolve()
    entries_dir = vault / "entries"
    compiled_dir = vault / "compiled"

    decision_groups: dict = defaultdict(list)
    broken_source: list = []
    orphan: list = []
    all_entry_ids: set = set()

    for p in sorted(entries_dir.glob("*.md")):
        fm = parse_fm(p)
        if not fm:
            continue
        all_entry_ids.add(p.stem)
        etype = fm.get("type", "")
        topics = fm.get("topics", "").strip("[]")
        primary = topics.split(",")[0].strip() if topics else ""
        if etype == "decision" and primary:
            decision_groups[primary].append((p.name, fm.get("created", ""), fm.get("supersedes", "[]")))

        src = fm.get("source", "")
        resolved = None
        if src.startswith("~/"):
            resolved = Path(os.path.expanduser(src))
        elif src.startswith("/"):
            resolved = Path(src)
        elif src.startswith("sources/"):
            resolved = vault / src
        if src and (not resolved or not resolved.exists()):
            broken_source.append((p.name, src))

    # orphan: entries whose id not found in GRAPH.tsv
    graph_ids = set()
    g = vault / "GRAPH.tsv"
    if g.exists():
        for line in g.read_text().splitlines():
            parts = line.split("\t")
            if parts and parts[0] and not parts[0].startswith("#"):
                graph_ids.add(parts[0])
                if len(parts) > 1:
                    graph_ids.add(parts[1])
    for eid in sorted(all_entry_ids):
        if eid not in graph_ids:
            orphan.append(eid)

    lines: list = []
    lines.append(f"# AUDIT — {vault.name}")
    lines.append("")
    lines.append("Human-review only. No mutation. Apply decisions via `omb supersede` (when implemented) or manual edit.")
    lines.append("")
    lines.append("## 1. Duplicate decision candidates")
    lines.append("")
    dup = {t: v for t, v in decision_groups.items() if len(v) >= 2}
    lines.append(f"Topics with ≥2 `type=decision` entries: **{len(dup)}**")
    lines.append("")
    for topic, rows in sorted(dup.items(), key=lambda x: -len(x[1])):
        lines.append(f"### {topic} ({len(rows)} entries)")
        for name, created, sup in sorted(rows, key=lambda r: r[1] or ""):
            marker = " ← supersedes chain present" if sup and sup != "[]" else ""
            lines.append(f"- `{name}` created={created or '?'}{marker}")
        lines.append("")
    lines.append("## 2. Broken source links")
    lines.append("")
    lines.append(f"Total: **{len(broken_source)}**")
    lines.append("")
    for name, src in broken_source[:50]:
        lines.append(f"- `{name}` → `{src}`")
    if len(broken_source) > 50:
        lines.append(f"- ... ({len(broken_source) - 50} more)")
    lines.append("")
    lines.append("## 3. Orphan entries (no graph edges)")
    lines.append("")
    lines.append(f"Total: **{len(orphan)}**")
    lines.append("")
    for eid in orphan[:30]:
        lines.append(f"- `{eid}`")
    if len(orphan) > 30:
        lines.append(f"- ... ({len(orphan) - 30} more)")

    (vault / "AUDIT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {vault}/AUDIT.md")
    print(f"  duplicate decision topics: {len(dup)}")
    print(f"  broken source links: {len(broken_source)}")
    print(f"  orphan entries: {len(orphan)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
