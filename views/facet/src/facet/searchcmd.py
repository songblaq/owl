"""``facet search <query>`` — 2-stage shard-aware search.

Stage 1: ALIASES.tsv resolution
  - Normalize query, look up in ALIASES.tsv
  - If match: narrow search to that shard's _index.md
  - If no match: grep all shards' _index.md (fallback)

Stage 2: Score full entry bodies of candidates
  - Load candidate entries from resolved shard(s)
  - Score using token-count algorithm (same as cairn)
  - Return top N

Also searches compiled/ narrative docs (one doc per shard) and merges
results — compiled hits are prefixed with [compiled] in output.

Scoring is intentionally simple: token count with id/topic boosts.
No embeddings, no stemming — retrieval must be debuggable.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence

from facet.aliases import load_aliases, resolve_shard
from facet.entry import Entry, iter_shard_entries, iter_all_entries
from facet.vault import discover_vault, iter_shards


@dataclass
class Match:
    entry: Entry
    score: int
    snippet: str


@dataclass
class CompiledMatch:
    path: Path
    shard: str
    score: int
    snippet: str


def tokenize_query(q: str) -> List[str]:
    tokens = re.findall(r"[\w가-힣]+", q.casefold())
    return [t for t in tokens if len(t) > 1]


def score_entry(entry: Entry, tokens: List[str]) -> int:
    """Count token occurrences across frontmatter + body. Title/topics weighted higher."""
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
    # boost for shard name match
    shard_lower = entry.shard.casefold()
    for t in tokens:
        if t in shard_lower:
            score += 2
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
    for line in entry.body.strip().splitlines():
        s = line.strip()
        if s:
            return s[:width]
    return "(empty)"


def _candidates_from_shard_index(shard_path: Path, tokens: List[str]) -> List[str]:
    """Read shard/_index.md and return entry IDs/stems that mention any token."""
    index_path = shard_path / "_index.md"
    if not index_path.exists():
        return []
    text = index_path.read_text(encoding="utf-8").casefold()
    hits: List[str] = []
    for line in text.splitlines():
        if any(t in line for t in tokens):
            # Extract backtick-quoted id if present: `some-id`
            for m in re.finditer(r"`([^`]+)`", line):
                hits.append(m.group(1))
    return hits


def _load_shard_entries_filtered(
    shard_path: Path, shard_name: str, candidate_ids: List[str]
) -> List[Entry]:
    """Load all entries from shard; if candidate_ids given, prefer those files first."""
    all_entries = iter_shard_entries(shard_path, shard_name)
    if not candidate_ids:
        return all_entries
    # prioritise candidate_ids but still return all (we'll score all)
    id_set = set(c.casefold() for c in candidate_ids)
    prioritised = [e for e in all_entries if e.id.casefold() in id_set]
    rest = [e for e in all_entries if e.id.casefold() not in id_set]
    return prioritised + rest


def _score_compiled(text: str, shard_name: str, tokens: List[str]) -> int:
    """Score a compiled doc's raw text against query tokens."""
    score = 0
    text_lower = text.casefold()
    for t in tokens:
        score += text_lower.count(t)
    shard_lower = shard_name.casefold()
    for t in tokens:
        if t in shard_lower:
            score += 5
    return score


def _build_compiled_snippet(text: str, tokens: List[str], width: int = 120) -> str:
    """Find the best snippet in a compiled doc."""
    # Skip frontmatter block
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
        if s and not s.startswith("#") and not s.startswith("*Auto-compiled"):
            return s[:width]
    return "(empty)"


def _search_compiled(vault: Path, tokens: List[str]) -> List[CompiledMatch]:
    """Search compiled/ narrative docs and return scored matches."""
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
        shard_name = f.stem
        score = _score_compiled(text, shard_name, tokens)
        if score > 0:
            snippet = _build_compiled_snippet(text, tokens)
            results.append(CompiledMatch(path=f, shard=shard_name, score=score, snippet=snippet))
    return results


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

    aliases = load_aliases(vault)
    resolved_shard = resolve_shard(query, aliases)

    candidate_entries: List[Entry] = []

    if resolved_shard:
        # Stage 1 hit: narrow to this shard
        shard_path = vault / "shards" / resolved_shard
        if shard_path.exists():
            candidate_ids = _candidates_from_shard_index(shard_path, tokens)
            candidate_entries = _load_shard_entries_filtered(shard_path, resolved_shard, candidate_ids)
        else:
            print(f"warning: alias resolves to shard '{resolved_shard}' but shard dir not found", file=sys.stderr)
            # fall through to full scan

    if not candidate_entries:
        # Fallback: grep all shards' _index.md to find candidates, then load those shards
        candidate_shard_names = set()
        for shard_name, shard_path in iter_shards(vault):
            ids = _candidates_from_shard_index(shard_path, tokens)
            if ids:
                candidate_shard_names.add(shard_name)

        if candidate_shard_names:
            for shard_name, shard_path in iter_shards(vault):
                if shard_name in candidate_shard_names:
                    candidate_entries.extend(iter_shard_entries(shard_path, shard_name))
        else:
            # Final fallback: load all entries
            candidate_entries = iter_all_entries(vault, include_superseded=include_superseded)

    if include_superseded and resolved_shard is None:
        sup_dir = vault / "superseded"
        if sup_dir.exists():
            from facet.entry import load_entry
            for f in sorted(sup_dir.rglob("*.md")):
                if f.is_file():
                    e = load_entry(f, shard="superseded")
                    if e:
                        candidate_entries.append(e)

    matches: List[Match] = []
    for e in candidate_entries:
        s = score_entry(e, tokens)
        if s > 0:
            matches.append(Match(entry=e, score=s, snippet=build_snippet(e, tokens)))

    # Also search compiled/ narrative docs (always, independent of shard resolution)
    compiled_matches = _search_compiled(vault, tokens)

    if json_out:
        matches.sort(key=lambda m: (-m.score, m.entry.id))
        matches = matches[:limit]
        payload = {
            "vault": str(vault),
            "query": query,
            "resolved_shard": resolved_shard,
            "count": len(matches),
            "matches": [
                {
                    "path": str(m.entry.path.relative_to(vault)),
                    "id": m.entry.id,
                    "shard": m.entry.shard,
                    "type": m.entry.type,
                    "topics": m.entry.topics,
                    "score": m.score,
                    "snippet": m.snippet,
                }
                for m in matches
            ],
            "compiled_matches": [
                {
                    "path": str(cm.path.relative_to(vault)),
                    "shard": cm.shard,
                    "score": cm.score,
                    "snippet": cm.snippet,
                }
                for cm in sorted(compiled_matches, key=lambda x: -x.score)
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    # Merge compiled + entry matches, sort by score, apply limit
    # Use a unified list of (score, label, display_fn) to interleave results
    all_results: List[tuple] = []
    for m in matches:
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
        print("  - Add an alias to ALIASES.tsv for better shard routing")
        print("  - `facet search --include-superseded` to include archived entries")
        if resolved_shard:
            print(f"  - Query resolved to shard '{resolved_shard}' — check that shard has entries")
        return 0

    if resolved_shard:
        print(f"[alias resolved: '{query}' -> shard '{resolved_shard}']")
        print()

    for i, (score, kind, result) in enumerate(all_results, 1):
        if kind == "compiled":
            cm: CompiledMatch = result
            rel = cm.path.relative_to(vault)
            print(f"[{i}] [compiled] {cm.shard}  (score: {cm.score})")
            print(f"    path: {rel}")
            print(f"    snippet: {cm.snippet}")
        else:
            m: Match = result
            rel = m.entry.path.relative_to(vault)
            print(f"[{i}] {rel}  (score: {m.score})")
            print(f"    id: {m.entry.id}   shard: {m.entry.shard}")
            print(f"    type: {m.entry.type}   topics: {', '.join(m.entry.topics)}")
            print(f"    snippet: {m.snippet}")
        print()

    top_score = all_results[0][0] if all_results else 0
    print("Next steps:")
    if top_score >= 10:
        print(f"  - Top hit score {top_score} is strong — read the file directly.")
    elif top_score < 3:
        print(f"  - Top score {top_score} is weak — refine the query or check ALIASES.tsv.")
    if len(all_results) >= limit:
        print(f"  - {limit}+ results — show top-3 first, ask for more if needed.")
    return 0


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Search facet vault.")
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
