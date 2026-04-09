"""``cairn search <query>`` — lexical search over entries + INDEX.md.

Two-stage retrieval per the design:
1. Scan INDEX.md for candidate entry IDs matching query keywords
2. Load and score the full body of candidates
3. Return top N with path + one-line summary

Scoring is simple token-count. No embeddings, no stemming — we're deliberately
minimal so retrieval is debuggable.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence

from cairn.entry import Entry, iter_entries
from cairn.vault import discover_vault


@dataclass
class Match:
    entry: Entry
    score: int
    snippet: str


def normalize(s: str) -> str:
    return s.casefold()


def tokenize_query(q: str) -> List[str]:
    tokens = re.findall(r"[\w가-힣]+", q.casefold())
    return [t for t in tokens if len(t) > 1]


def score_entry(entry: Entry, tokens: List[str]) -> int:
    """Count token occurrences across frontmatter + body. Title/topics weighted higher."""
    score = 0
    content = entry.raw.casefold()
    for t in tokens:
        score += content.count(t)
    # boost for id match
    id_lower = entry.id.casefold()
    for t in tokens:
        if t in id_lower:
            score += 5
    # boost for topic match
    topics_joined = ",".join(entry.topics).casefold()
    for t in tokens:
        if t in topics_joined:
            score += 3
    return score


def build_snippet(entry: Entry, tokens: List[str], width: int = 120) -> str:
    body_lower = entry.body.casefold()
    for t in tokens:
        idx = body_lower.find(t)
        if idx >= 0:
            start = max(0, idx - width // 3)
            end = min(len(entry.body), start + width)
            snippet = entry.body[start:end].replace("\n", " ").strip()
            return snippet
    # fallback: first line
    for line in entry.body.strip().splitlines():
        s = line.strip()
        if s:
            return s[:width]
    return "(empty)"


def run_search(
    query: str,
    vault_arg: Optional[str] = None,
    limit: int = 10,
    include_superseded: bool = False,
    json_out: bool = False,
) -> int:
    vault = discover_vault(vault_arg)
    if not vault.exists():
        print(f"error: vault does not exist: {vault}", file=sys.stderr)
        return 2

    tokens = tokenize_query(query)
    if not tokens:
        print("error: empty query", file=sys.stderr)
        return 2

    entries = iter_entries(vault, include_superseded=include_superseded)
    matches: List[Match] = []
    for e in entries:
        s = score_entry(e, tokens)
        if s > 0:
            matches.append(Match(entry=e, score=s, snippet=build_snippet(e, tokens)))

    matches.sort(key=lambda m: (-m.score, m.entry.id))
    matches = matches[:limit]

    if json_out:
        payload = {
            "vault": str(vault),
            "query": query,
            "count": len(matches),
            "matches": [
                {
                    "path": str(m.entry.path.relative_to(vault)),
                    "id": m.entry.id,
                    "type": m.entry.type,
                    "topics": m.entry.topics,
                    "score": m.score,
                    "snippet": m.snippet,
                }
                for m in matches
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if not matches:
        print("No matches.")
        print()
        print("Next steps:")
        print("  - Try broader keywords")
        print("  - `cairn search --include-superseded` to include archived entries")
        print("  - If the topic isn't in cairn yet, drop a source in sources/ for future ingestion")
        return 0

    for i, m in enumerate(matches, 1):
        rel = m.entry.path.relative_to(vault)
        print(f"[{i}] {rel}  (score: {m.score})")
        print(f"    id: {m.entry.id}")
        print(f"    type: {m.entry.type}   topics: {', '.join(m.entry.topics)}")
        print(f"    snippet: {m.snippet}")
        print()

    # Next-step hints
    top_score = matches[0].score if matches else 0
    print("Next steps (for LLM agents and humans):")
    if top_score >= 10:
        print(f"  - Top hit score {top_score} is strong — read the file directly.")
    elif top_score < 3:
        print(f"  - Top score {top_score} is weak — refine the query or widen scope.")
    if len(matches) >= limit:
        print(f"  - {limit}+ results — show top-3 first, ask for more if needed.")
    return 0


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Search cairn vault.")
    p.add_argument("query", help="Search query")
    p.add_argument("--vault", dest="vault", default=None, help="Vault path override")
    p.add_argument("--limit", type=int, default=10, help="Max results (default 10)")
    p.add_argument("--include-superseded", action="store_true", help="Also search superseded/")
    p.add_argument("--json", action="store_true", help="JSON output")
    return p.parse_args(argv)


def cli(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    return run_search(
        query=args.query,
        vault_arg=args.vault,
        limit=args.limit,
        include_superseded=args.include_superseded,
        json_out=args.json,
    )


if __name__ == "__main__":
    raise SystemExit(cli())
