#!/usr/bin/env python3
"""Benchmark an akasha vault against design principles.

Usage:
    python tools/benchmark_vault.py <vault-path> [<vault-path> ...]
    python tools/benchmark_vault.py ~/omb/vault/akasha-archive-2026-04-17 ~/omb/vault/akasha-a-migrate

Outputs a side-by-side comparison table of the same metrics across vaults.
Metrics directly map to the 5 design principles and the observed regressions.
"""
from __future__ import annotations

import os
import re
import sys
from collections import defaultdict
from pathlib import Path


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
NAMING_CANONICAL = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*\.md$")
NAMING_LATTICE = re.compile(r"^lattice-")
NAMING_TOPIC_DATE = re.compile(r"^[a-z][a-z0-9-]*--\d{4}-\d{2}-\d{2}-")


def parse_frontmatter(path: Path) -> dict | None:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return None
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    fm: dict = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        fm[k.strip()] = v.strip()
    return fm


def classify_naming(name: str) -> str:
    if NAMING_CANONICAL.match(name):
        return "canonical"
    if NAMING_LATTICE.match(name):
        return "lattice"
    if NAMING_TOPIC_DATE.match(name):
        return "topic--date"
    return "other"


def measure(vault: Path, source_root: Path) -> dict:
    entries = sorted((vault / "entries").glob("*.md")) if (vault / "entries").exists() else []
    compiled = sorted((vault / "compiled").glob("*.md")) if (vault / "compiled").exists() else []
    superseded = sorted((vault / "superseded").glob("*.md")) if (vault / "superseded").exists() else []

    total = len(entries)
    naming_counts: dict = defaultdict(int)
    supersedes_nonempty = 0
    source_link_ok = 0
    source_link_broken = 0
    source_link_missing_field = 0
    topics_decisions: dict = defaultdict(list)
    edges_nodes: set = set()

    graph_path = vault / "GRAPH.tsv"
    if graph_path.exists():
        for line in graph_path.read_text().splitlines():
            parts = line.split("\t")
            if len(parts) >= 2 and parts[0] and not parts[0].startswith("#"):
                edges_nodes.add(parts[0])
                edges_nodes.add(parts[1])

    for p in entries:
        naming_counts[classify_naming(p.name)] += 1
        fm = parse_frontmatter(p) or {}

        sup = fm.get("supersedes", "[]")
        if sup and sup != "[]":
            supersedes_nonempty += 1

        src = fm.get("source")
        if not src:
            source_link_missing_field += 1
        else:
            resolved = None
            if src.startswith("sources/"):
                resolved = vault / src
            elif src.startswith("~/"):
                resolved = Path(os.path.expanduser(src))
            elif src.startswith("/"):
                resolved = Path(src)
            else:
                resolved = vault / src
            if resolved and resolved.exists():
                source_link_ok += 1
            else:
                source_link_broken += 1

        etype = fm.get("type", "").strip()
        topics = fm.get("topics", "").strip("[]")
        primary_topic = topics.split(",")[0].strip() if topics else ""
        if etype == "decision" and primary_topic:
            topics_decisions[primary_topic].append(p.name)

    orphan_count = 0
    entry_ids = {p.stem for p in entries}
    for p in entries:
        if p.stem not in edges_nodes:
            orphan_count += 1

    duplicate_groups = {t: ids for t, ids in topics_decisions.items() if len(ids) >= 2}

    def pct(n: int, d: int) -> str:
        return f"{(n / d * 100):.1f}%" if d else "n/a"

    return {
        "path": str(vault),
        "entries": total,
        "compiled": len(compiled),
        "superseded_dir": len(superseded),
        "graph_nodes": len(edges_nodes),
        "naming_canonical": naming_counts["canonical"],
        "naming_lattice": naming_counts["lattice"],
        "naming_topic_date": naming_counts["topic--date"],
        "naming_other": naming_counts["other"],
        "naming_conformance": pct(naming_counts["canonical"], total),
        "supersedes_nonempty": supersedes_nonempty,
        "supersedes_coverage": pct(supersedes_nonempty, total),
        "source_ok": source_link_ok,
        "source_broken": source_link_broken,
        "source_missing_field": source_link_missing_field,
        "source_integrity": pct(source_link_ok, total),
        "orphan_entries": orphan_count,
        "orphan_ratio": pct(orphan_count, total),
        "duplicate_decision_topics": len(duplicate_groups),
        "duplicate_samples": dict(list(duplicate_groups.items())[:5]),
    }


def print_table(results: list[dict]) -> None:
    if not results:
        return
    keys = [
        "entries", "compiled", "superseded_dir",
        "naming_conformance", "naming_canonical", "naming_lattice", "naming_topic_date", "naming_other",
        "supersedes_coverage", "supersedes_nonempty",
        "source_integrity", "source_ok", "source_broken", "source_missing_field",
        "orphan_ratio", "orphan_entries", "graph_nodes",
        "duplicate_decision_topics",
    ]
    name_col = 28
    cols = []
    for r in results:
        label = Path(r["path"]).name
        cols.append(label[:18].ljust(18))
    header = " metric".ljust(name_col) + "| " + " | ".join(cols)
    print(header)
    print("-" * len(header))
    for k in keys:
        row = f" {k}".ljust(name_col) + "| "
        row += " | ".join(str(r.get(k, "")).ljust(18) for r in results)
        print(row)
    print()
    print("duplicate_samples (primary_topic → decision entries):")
    for r in results:
        print(f"\n  [{Path(r['path']).name}]")
        samples = r.get("duplicate_samples", {})
        if not samples:
            print("    (none)")
            continue
        for topic, ids in samples.items():
            print(f"    {topic}: {len(ids)} entries")
            for fn in ids[:4]:
                print(f"      - {fn}")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 1
    source_root = Path(os.path.expanduser("~/omb/input"))
    results = []
    for raw in argv[1:]:
        vault = Path(os.path.expanduser(raw)).resolve()
        if not vault.exists():
            print(f"MISS: {vault}", file=sys.stderr)
            continue
        results.append(measure(vault, source_root))
    print_table(results)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
