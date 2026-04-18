#!/usr/bin/env python3
"""W-B: wiki lint — AGENTS.md checklist 의 스크립트화.

Usage:
    python3 tools/wiki_lint.py [wiki-path]
    python3 tools/wiki_lint.py ~/omb/vault/wiki --json

Checks:
  L1 broken [[wiki link]]
  L2 orphan page (inbound link 0, index.md 제외)
  L3 frontmatter required fields (type, updated, sources)
  L4 type in {entity, concept, source-summary, synthesis}
  L5 sources: 중 raw/ 링크가 실존하는지
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path


WIKI_LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
VALID_TYPES = {"entity", "concept", "source-summary", "synthesis"}
REQUIRED_FM = ("type", "updated")


def parse_fm(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return {}
    m = FM_RE.match(text)
    if not m:
        return {}
    out: dict = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip()
    return out


def all_pages(wiki: Path) -> list[Path]:
    pages: list[Path] = []
    for sub in ("entities", "concepts", "sources", "syntheses"):
        d = wiki / sub
        if d.exists():
            pages.extend(sorted(d.glob("*.md")))
    return pages


def link_target_id(link: str) -> str:
    # "[[entities/dgx-spark]]" -> "entities/dgx-spark"
    return link.strip()


def resolve_link(wiki: Path, target: str) -> Path | None:
    # target like "entities/dgx-spark"
    candidate = wiki / f"{target}.md"
    return candidate if candidate.exists() else None


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if a != "--json"]
    json_mode = "--json" in argv
    wiki = Path(os.path.expanduser(args[0] if args else "~/omb/vault/wiki")).resolve()
    if not wiki.exists():
        print(f"no wiki at {wiki}", file=sys.stderr)
        return 2

    pages = all_pages(wiki)
    findings: list[dict] = []
    inbound: dict[str, int] = defaultdict(int)
    page_ids: set[str] = set()

    for p in pages:
        # "entities/dgx-spark"
        rel_id = f"{p.parent.name}/{p.stem}"
        page_ids.add(rel_id)

    for p in pages:
        rel_id = f"{p.parent.name}/{p.stem}"
        text = p.read_text(encoding="utf-8")

        # L3/L4 frontmatter
        fm = parse_fm(p)
        if not fm:
            findings.append({"page": rel_id, "rule": "L3", "severity": "critical", "message": "no frontmatter"})
            continue
        for field in REQUIRED_FM:
            if not fm.get(field):
                findings.append({"page": rel_id, "rule": "L3", "severity": "warning", "message": f"missing frontmatter: {field}"})
        etype = fm.get("type", "").strip()
        if etype and etype not in VALID_TYPES:
            findings.append({"page": rel_id, "rule": "L4", "severity": "warning", "message": f"unknown type: {etype}"})

        # L5 sources: raw links
        srcs = fm.get("sources", "").strip("[]")
        if srcs:
            for s in [x.strip() for x in srcs.split(",") if x.strip()]:
                if s.startswith("raw/"):
                    real = wiki / s
                    if not real.exists():
                        findings.append({"page": rel_id, "rule": "L5", "severity": "critical", "message": f"broken source ref: {s}"})

        # L1 wiki links + inbound count
        for m in WIKI_LINK_RE.finditer(text):
            target = link_target_id(m.group(1))
            # strip any alias "target|alias"
            target = target.split("|")[0]
            if target not in page_ids:
                findings.append({"page": rel_id, "rule": "L1", "severity": "critical", "message": f"broken [[{target}]]"})
            else:
                inbound[target] += 1

    # L2 orphan (no inbound — index.md 참조는 아래서 체크)
    index_path = wiki / "index.md"
    index_text = index_path.read_text() if index_path.exists() else ""
    for pid in sorted(page_ids):
        if inbound.get(pid, 0) == 0 and f"[[{pid}]]" not in index_text:
            findings.append({"page": pid, "rule": "L2", "severity": "warning", "message": "orphan — no inbound link"})

    result = {
        "wiki": str(wiki),
        "pages": len(pages),
        "findings_total": len(findings),
        "critical": sum(1 for f in findings if f["severity"] == "critical"),
        "warning": sum(1 for f in findings if f["severity"] == "warning"),
        "findings": findings,
    }

    if json_mode:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 1 if result["critical"] > 0 else 0

    print(f"wiki lint — {wiki}")
    print("=" * 50)
    print(f"  pages:     {result['pages']}")
    print(f"  findings:  {result['findings_total']} (critical={result['critical']}, warning={result['warning']})")
    print()
    for f in findings:
        print(f"  [{f['rule']}] {f['severity'].upper():8s} {f['page']}: {f['message']}")
    print()
    status = "HEALTHY" if result["critical"] == 0 else "CRITICAL"
    print(f"  status: {status}")
    return 0 if result["critical"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
