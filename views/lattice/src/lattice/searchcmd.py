"""``lattice search <query>`` — 3-stage retrieval with graph expansion.

Stage 1: BLOOM.txt pre-filter
  - Tokenize query. Check each token against BLOOM.txt sorted list.
  - If no tokens survive: warn (tokens not indexed) but continue.

Stage 2: MANIFOLD.tsv candidate lookup
  - For each surviving token, look up matching entry IDs in MANIFOLD.tsv.
  - Collect union of candidate IDs.

Stage 3: Score + graph expand
  - Load candidate entry files.
  - Score each with token-count algorithm (same as cairn/facet).
  - Expand top-K candidates by 1 hop via GRAPH.tsv edges.
  - Re-score expanded set and return top N.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from lattice.entry import Entry, load_entry, iter_entries
from lattice.manifold import (
    bloom_has_token,
    load_manifold,
    load_graph,
    query_manifold,
    expand_one_hop,
)
from lattice.vault import discover_vault


@dataclass
class Match:
    entry: Entry
    score: int
    snippet: str
    expanded: bool = False  # True if reached via graph expansion


def tokenize_query(q: str) -> List[str]:
    tokens = re.findall(r"[\w가-힣]+", q.casefold())
    return [t for t in tokens if len(t) > 1]


def score_entry(entry: Entry, tokens: List[str]) -> int:
    """Token-count scoring with id/topics/edges boosts."""
    score = 0
    content = entry.raw.casefold()
    for t in tokens:
        score += content.count(t)
    id_lower = entry.id.casefold()
    for t in tokens:
        if t in id_lower:
            score += 5
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
            return entry.body[start:end].replace("\n", " ").strip()
    for line in entry.body.strip().splitlines():
        s = line.strip()
        if s:
            return s[:width]
    return "(empty)"


def _load_entries_by_ids(
    vault: Path, entry_ids: List[str], all_entries: List[Entry]
) -> List[Entry]:
    """Return entries matching the given IDs from the pre-loaded list."""
    id_to_entry: Dict[str, Entry] = {e.id: e for e in all_entries}
    result: List[Entry] = []
    seen = set()
    for eid in entry_ids:
        if eid in id_to_entry and eid not in seen:
            seen.add(eid)
            result.append(id_to_entry[eid])
    return result


def run_search(
    query: str,
    vault_arg: Optional[str] = None,
    limit: int = 10,
    include_superseded: bool = False,
    json_out: bool = False,
    no_expand: bool = False,
) -> int:
    vault = discover_vault(vault_arg)
    if not vault.exists():
        print(f"error: vault does not exist: {vault}", file=sys.stderr)
        return 2

    tokens = tokenize_query(query)
    if not tokens:
        print("error: empty query", file=sys.stderr)
        return 2

    # Pre-load all entries (needed for expansion and scoring)
    all_entries = iter_entries(vault, include_superseded=include_superseded)
    if not all_entries:
        print("No entries in vault.")
        return 0

    # Stage 1: BLOOM pre-filter
    bloom_path = vault / "BLOOM.txt"
    if bloom_path.exists():
        surviving_tokens = [t for t in tokens if bloom_has_token(vault, t)]
        if not surviving_tokens:
            # BLOOM miss — fall back to full scan (tokens not in index yet)
            surviving_tokens = tokens
    else:
        surviving_tokens = tokens

    # Stage 2: MANIFOLD lookup
    manifold = load_manifold(vault)
    if manifold:
        candidate_ids = query_manifold(manifold, surviving_tokens)
    else:
        # No MANIFOLD yet — score all entries
        candidate_ids = [e.id for e in all_entries]

    if not candidate_ids:
        # Fallback: score all entries
        candidate_ids = [e.id for e in all_entries]

    # Stage 3: Graph expansion (1-hop)
    graph = load_graph(vault)
    if graph and not no_expand:
        # Take top candidates before expansion
        pre_expand = candidate_ids[:max(limit, 20)]
        expanded_ids = expand_one_hop(pre_expand, graph)
        expanded_set = set(expanded_ids) - set(pre_expand)
    else:
        expanded_ids = candidate_ids
        expanded_set = set()

    # Load and score
    candidates = _load_entries_by_ids(vault, expanded_ids, all_entries)
    if not candidates:
        candidates = all_entries

    matches: List[Match] = []
    for e in candidates:
        s = score_entry(e, tokens)
        if s > 0:
            is_expanded = e.id in expanded_set
            matches.append(Match(
                entry=e,
                score=s,
                snippet=build_snippet(e, tokens),
                expanded=is_expanded,
            ))

    matches.sort(key=lambda m: (-m.score, m.entry.id))
    matches = matches[:limit]

    if json_out:
        payload = {
            "vault": str(vault),
            "query": query,
            "bloom_tokens": surviving_tokens,
            "count": len(matches),
            "matches": [
                {
                    "path": str(m.entry.path.relative_to(vault)),
                    "id": m.entry.id,
                    "type": m.entry.type,
                    "topics": m.entry.topics,
                    "score": m.score,
                    "expanded": m.expanded,
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
        print("  - `lattice index` to rebuild MANIFOLD/BLOOM if new entries were added")
        print("  - `lattice search --include-superseded` to include archived entries")
        return 0

    for i, m in enumerate(matches, 1):
        rel = m.entry.path.relative_to(vault)
        expanded_tag = " [+graph]" if m.expanded else ""
        print(f"[{i}] {rel}  (score: {m.score}{expanded_tag})")
        print(f"    id: {m.entry.id}")
        print(f"    type: {m.entry.type}   topics: {', '.join(m.entry.topics)}")
        if m.entry.edges:
            print(f"    edges: {', '.join(m.entry.edges[:5])}")
        print(f"    snippet: {m.snippet}")
        print()

    top_score = matches[0].score if matches else 0
    print("Next steps:")
    if top_score >= 10:
        print(f"  - Top hit score {top_score} is strong — read the file directly.")
    elif top_score < 3:
        print(f"  - Top score {top_score} is weak — refine the query or run `lattice index`.")
    if len(matches) >= limit:
        print(f"  - {limit}+ results — show top-3 first, ask for more if needed.")
    if any(m.expanded for m in matches):
        print("  - Some results reached via graph expansion ([+graph])")
    return 0


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Search lattice vault.")
    p.add_argument("query", help="Search query")
    p.add_argument("--vault", dest="vault", default=None, help="Vault path override")
    p.add_argument("--limit", type=int, default=10, help="Max results (default 10)")
    p.add_argument("--include-superseded", action="store_true", help="Also search superseded/")
    p.add_argument("--no-expand", action="store_true", help="Disable graph expansion")
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
        no_expand=args.no_expand,
    )


if __name__ == "__main__":
    raise SystemExit(cli())
