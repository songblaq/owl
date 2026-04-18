"""wiki_ops — omb 의 기본 대상(wiki) 용 얇은 유틸.

Re:Zero 2026-04-18 이후: omb search/status/ingest 의 default = wiki.
Karpathy 원안 그대로. 검색은 grep + index.md, ingest 는 LLM 이 직접 페이지 편집
하도록 skeleton 만 제공.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path


WIKI_ROOT = Path(os.path.expanduser("~/omb/brain/live"))
SECTIONS = ("entities", "concepts", "sources", "syntheses")


def wiki_status() -> int:
    if not WIKI_ROOT.exists():
        print(f"no data at {WIKI_ROOT}", file=sys.stderr)
        return 2
    counts = {}
    for s in SECTIONS:
        counts[s] = len(list((WIKI_ROOT / s).glob("*.md"))) if (WIKI_ROOT / s).exists() else 0
    total = sum(counts.values())
    log = WIKI_ROOT / "log.md"

    capsule_root = Path(os.path.expanduser("~/omb/brain/readonly"))
    capsule_count = 0
    if capsule_root.exists():
        capsule_count = sum(1 for p in capsule_root.iterdir() if p.is_dir() and not p.name.startswith("."))

    print(f"omb")
    print(f"{'─' * 40}")
    print(f"  지식     {total} 항목  ({counts['entities']} 개체 / {counts['concepts']} 개념 / {counts['sources']} 원본요약 / {counts['syntheses']} 합성)")
    print(f"  제품 번들  {capsule_count} 개")
    return 0


def wiki_search(query: str, limit: int = 10) -> int:
    if not query.strip():
        print("usage: omb search <query>", file=sys.stderr)
        return 2
    if not WIKI_ROOT.exists():
        print(f"no data at {WIKI_ROOT}", file=sys.stderr)
        return 2
    hits: list[tuple[Path, int, str]] = []
    q_lower = query.lower()
    for s in SECTIONS:
        d = WIKI_ROOT / s
        if not d.exists():
            continue
        for p in sorted(d.glob("*.md")):
            text = p.read_text(encoding="utf-8", errors="ignore")
            score = text.lower().count(q_lower)
            if score > 0:
                snippet = ""
                for line in text.splitlines():
                    if q_lower in line.lower():
                        snippet = line.strip()[:120]
                        break
                hits.append((p, score, snippet))
    hits.sort(key=lambda x: -x[1])
    print(f"omb search — {query}")
    print(f"{'─' * 50}")
    if not hits:
        print("  (일치 없음)")
    for i, (p, score, snip) in enumerate(hits[:limit], 1):
        rel = p.relative_to(WIKI_ROOT)
        print(f"[{i}] {rel}  (적중: {score})")
        if snip:
            print(f"    {snip}")
    return 0


def wiki_new(kind: str, name: str) -> int:
    """Create a page skeleton. LLM fills in the content separately."""
    if kind not in SECTIONS:
        print(f"kind must be one of: {', '.join(SECTIONS)}", file=sys.stderr)
        return 2
    slug = re.sub(r"[^a-z0-9-]+", "-", name.lower()).strip("-")
    dest = WIKI_ROOT / kind / f"{slug}.md"
    if dest.exists():
        print(f"exists: {dest}", file=sys.stderr)
        return 1
    today = subprocess.check_output(["date", "-u", "+%Y-%m-%d"]).decode().strip()
    skeleton = f"""---
type: {kind.rstrip('s') if kind != 'sources' else 'source-summary'}
updated: {today}
sources: []
---

# {name}

_LLM: fill in. Use [[section/page]] for wiki links, cite sources via (→ raw/<file>)._
"""
    dest.write_text(skeleton, encoding="utf-8")
    # log
    log = WIKI_ROOT / "log.md"
    entry = f"\n## [{today}] new | {kind}/{slug} (skeleton)\n- created by `omb ingest` (LLM fills content)\n"
    with log.open("a", encoding="utf-8") as f:
        f.write(entry)
    print(f"created: {dest}")
    print(f"logged:  {log}")
    return 0
