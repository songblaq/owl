"""``akasha search <query>`` — 3-layer unified retrieval.

Layer 1: compiled/ TF-IDF (narrative docs, broad context)
Layer 2: entries/ TF-IDF + alias resolution (atomic claims)
Layer 3: 1-hop graph expansion (top-3 entry hits)

Results are merged, deduplicated, ranked by score, prefixed with
[compiled], [entry], or [+graph] for traceability.

Scoring: simple token-count + id/topic boosts. No embeddings.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from akasha.aliases import load_aliases, resolve_topic
from akasha.entry import Entry, iter_entries, load_entry
from akasha.graph import load_graph, expand_one_hop
from akasha.vault import discover_vault


@dataclass
class EntryMatch:
    entry: Entry
    score: int
    snippet: str
    expanded: bool = False  # reached via graph expansion


@dataclass
class CompiledMatch:
    path: Path
    topic: str
    score: int
    snippet: str


def tokenize_query(q: str) -> List[str]:
    tokens = re.findall(r"[\w가-힣]+", q.casefold())
    return [t for t in tokens if len(t) > 1]


def score_entry(entry: Entry, tokens: List[str]) -> int:
    """Token-count scoring with id/topics boosts."""
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


def _score_compiled(text: str, topic: str, tokens: List[str]) -> int:
    """Score a compiled doc's text against query tokens."""
    score = 0
    text_lower = text.casefold()
    for t in tokens:
        score += text_lower.count(t)
    topic_lower = topic.casefold()
    for t in tokens:
        if t in topic_lower:
            score += 5
    return score


def _build_compiled_snippet(text: str, tokens: List[str], width: int = 120) -> str:
    """Find best snippet in compiled doc, skipping frontmatter."""
    body = text
    if text.startswith("---"):
        end = text.find("\n---\n", 3)
        if end != -1:
            body = text[end + 5:]
    body_lower = body.casefold()
    for t in tokens:
        idx = body_lower.find(t)
        if idx >= 0:
            start = max(0, idx - width // 3)
            end = min(len(body), start + width)
            return body[start:end].replace("\n", " ").strip()
    for line in body.strip().splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            return s[:width]
    return "(empty)"


def _search_compiled(vault: Path, tokens: List[str]) -> List[CompiledMatch]:
    """Search compiled/ narrative docs."""
    compiled_dir = vault / "compiled"
    if not compiled_dir.exists():
        return []
    results: List[CompiledMatch] = []
    for f in sorted(compiled_dir.glob("*.md")):
        if not f.is_file():
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        topic = f.stem
        score = _score_compiled(text, topic, tokens)
        if score > 0:
            snippet = _build_compiled_snippet(text, tokens)
            results.append(CompiledMatch(path=f, topic=topic, score=score, snippet=snippet))
    return results


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

    # Layer 1: compiled search
    compiled_matches = _search_compiled(vault, tokens)

    # Layer 2: entry search with alias resolution
    aliases = load_aliases(vault)
    resolved_topic = resolve_topic(query, aliases)

    all_entries = iter_entries(vault, include_superseded=include_superseded)
    if not all_entries:
        print("No entries in vault.")
        return 0

    # Filter by topic if alias resolved
    if resolved_topic:
        candidate_entries = [e for e in all_entries if resolved_topic in e.topics]
        if not candidate_entries:
            candidate_entries = all_entries
    else:
        candidate_entries = all_entries

    # Score entries
    entry_id_to_entry: Dict[str, Entry] = {e.id: e for e in all_entries}

    scored: List[EntryMatch] = []
    for e in candidate_entries:
        s = score_entry(e, tokens)
        if s > 0:
            scored.append(EntryMatch(
                entry=e, score=s, snippet=build_snippet(e, tokens), expanded=False
            ))

    scored.sort(key=lambda m: (-m.score, m.entry.id))

    # Layer 3: 1-hop graph expansion on top-3 entry hits
    if not no_expand:
        graph = load_graph(vault)
        if graph:
            top3_ids = [m.entry.id for m in scored[:3]]
            expanded_ids = expand_one_hop(top3_ids, graph)
            expanded_set = set(expanded_ids) - set(top3_ids)
            existing_ids = {m.entry.id for m in scored}
            for eid in expanded_set:
                if eid not in existing_ids and eid in entry_id_to_entry:
                    e = entry_id_to_entry[eid]
                    s = score_entry(e, tokens)
                    # Include expanded entries even with score 0 (graph context)
                    scored.append(EntryMatch(
                        entry=e,
                        score=s,
                        snippet=build_snippet(e, tokens),
                        expanded=True,
                    ))

    scored.sort(key=lambda m: (-m.score, m.entry.id))

    if json_out:
        scored_top = scored[:limit]
        payload = {
            "vault": str(vault),
            "query": query,
            "resolved_topic": resolved_topic,
            "count": len(scored_top),
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
                for m in scored_top
            ],
            "compiled_matches": [
                {
                    "path": str(cm.path.relative_to(vault)),
                    "topic": cm.topic,
                    "score": cm.score,
                    "snippet": cm.snippet,
                }
                for cm in sorted(compiled_matches, key=lambda x: -x.score)
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    # Merge compiled + entry results, rank by score, apply limit
    all_results: list = []
    for m in scored:
        all_results.append((m.score, "entry", m))
    for cm in compiled_matches:
        all_results.append((cm.score, "compiled", cm))

    all_results.sort(key=lambda x: (-x[0], x[1]))
    all_results = all_results[:limit]

    if not all_results:
        print("No matches.")
        print()
        print("Next steps:")
        print("  - Try broader keywords")
        print("  - `akasha index` to rebuild GRAPH.tsv if new entries were added")
        print("  - `akasha compile` to build narrative docs for compiled/ layer")
        if resolved_topic:
            print(f"  - Query resolved to topic '{resolved_topic}' — check entries have that topic")
        return 0

    if resolved_topic:
        print(f"[alias resolved: '{query}' -> topic '{resolved_topic}']")
        print()

    for i, (score, kind, result) in enumerate(all_results, 1):
        if kind == "compiled":
            cm: CompiledMatch = result
            rel = cm.path.relative_to(vault)
            print(f"[{i}] [compiled] {cm.topic}  (score: {cm.score})")
            print(f"    path: {rel}")
            print(f"    snippet: {cm.snippet}")
        else:
            m: EntryMatch = result
            rel = m.entry.path.relative_to(vault)
            expanded_tag = " [+graph]" if m.expanded else ""
            print(f"[{i}] [entry]{expanded_tag} {rel}  (score: {m.score})")
            print(f"    id: {m.entry.id}")
            print(f"    type: {m.entry.type}   topics: {', '.join(m.entry.topics)}")
            if m.entry.edges:
                edges_str = ", ".join(
                    e.get("to", "") for e in m.entry.edges[:5] if e.get("to")
                )
                if edges_str:
                    print(f"    edges: {edges_str}")
            print(f"    snippet: {m.snippet}")
        print()

    top_score = all_results[0][0] if all_results else 0
    print("Next steps:")
    if top_score >= 10:
        print(f"  - Top hit score {top_score} is strong — read the file directly.")
    elif top_score < 3:
        print(f"  - Top score {top_score} is weak — refine the query or run `akasha index`.")
    if len(all_results) >= limit:
        print(f"  - {limit}+ results — show top-3 first, ask for more if needed.")
    if any(kind == "entry" and result.expanded for _, kind, result in all_results):
        print("  - Some results reached via graph expansion ([+graph])")
    return 0


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Search akasha vault.")
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
