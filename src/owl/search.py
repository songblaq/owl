"""Vault search — token-scored lookup across raw/compiled/research/views.

This is the deterministic search primitive used by the ``owl search`` CLI and
by the ``owl-librarian`` / ``owl-compiler`` subagents. It deliberately avoids
RAG/embeddings per the small-scale-no-rag policy: a well-maintained wiki +
simple token scoring is sufficient for the vault sizes this system targets.

The legacy ``src/wiki_search.py`` script is now a 3-line wrapper around
``cli()`` here, preserving backward compatibility for the documented
``python3 src/wiki_search.py "filing loop" --scope all`` invocation.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

from owl.vault import discover_vault

SEARCH_DIRS = ("compiled", "raw", "research", "views")
TEXT_EXTENSIONS = {".md", ".txt", ".csv", ".py"}


@dataclass
class Match:
    path: Path
    score: int
    title: str
    kind: str
    snippet: str


def normalize(text: str) -> str:
    return text.casefold()


def tokenize_query(query: str) -> List[str]:
    return [p.strip() for p in re.split(r"\s+", query) if p.strip()]


def iter_files(base: Path, scope: str) -> Iterable[Path]:
    scopes = [scope] if scope != "all" else list(SEARCH_DIRS)
    for part in scopes:
        root = base / part
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS:
                yield path


def extract_title(content: str, fallback: str) -> str:
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def extract_kind(content: str, fallback: str) -> str:
    for line in content.splitlines()[:20]:
        if line.startswith("유형:"):
            return line.split(":", 1)[1].strip()
    return fallback


def build_snippet(content: str, terms: List[str]) -> str:
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    folded_terms = [normalize(t) for t in terms]
    for line in lines:
        lowered = normalize(line)
        if all(term in lowered for term in folded_terms):
            return line[:220]
    for line in lines:
        lowered = normalize(line)
        if any(term in lowered for term in folded_terms):
            return line[:220]
    return (lines[0] if lines else "")[:220]


def score_match(path: Path, content: str, terms: List[str]) -> int:
    lowered_content = normalize(content)
    lowered_path = normalize(str(path))
    score = 0
    for term in terms:
        if term in lowered_path:
            score += 6
        count = lowered_content.count(term)
        score += min(count, 8)
    if "# " in content:
        title = extract_title(content, path.stem)
        lowered_title = normalize(title)
        for term in terms:
            if term in lowered_title:
                score += 5
    return score


def search(
    base: Path,
    query: str,
    scope: str = "all",
    kind_filter: Optional[str] = None,
    limit: int = 10,
) -> List[Match]:
    """Run a token-scored search across the vault.

    Args:
        base: Vault root path.
        query: Whitespace-separated search terms.
        scope: One of ``all``, ``compiled``, ``raw``, ``research``, ``views``.
        kind_filter: Optional document type filter (substring match against
            the ``유형:`` header).
        limit: Maximum number of matches to return (sorted by score desc).

    Returns:
        List of ``Match`` objects sorted by descending score.
    """
    terms = [normalize(t) for t in tokenize_query(query)]
    if not terms:
        return []

    results: List[Match] = []
    for path in iter_files(base, scope):
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        title = extract_title(content, path.stem)
        kind = extract_kind(content, path.parent.name)
        if kind_filter and normalize(kind_filter) not in normalize(kind):
            continue

        lowered_content = normalize(content)
        lowered_path = normalize(str(path))
        if not any(term in lowered_content or term in lowered_path for term in terms):
            continue

        score = score_match(path, content, terms)
        snippet = build_snippet(content, terms)
        results.append(Match(path=path, score=score, title=title, kind=kind, snippet=snippet))

    results.sort(key=lambda m: (-m.score, str(m.path)))
    return results[:limit]


def format_results(base: Path, matches: List[Match]) -> str:
    if not matches:
        return "No matches found."

    lines: List[str] = []
    for idx, match in enumerate(matches, start=1):
        rel = match.path.relative_to(base)
        lines.append(f"[{idx}] {rel}")
        lines.append(f"    title: {match.title}")
        lines.append(f"    type: {match.kind}")
        lines.append(f"    score: {match.score}")
        lines.append(f"    snippet: {match.snippet}")
    return "\n".join(lines)


def matches_to_json(base: Path, matches: List[Match]) -> str:
    payload = [
        {
            "path": str(m.path.relative_to(base)),
            "score": m.score,
            "title": m.title,
            "kind": m.kind,
            "snippet": m.snippet,
        }
        for m in matches
    ]
    return json.dumps({"vault": str(base), "count": len(payload), "matches": payload}, ensure_ascii=False, indent=2)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search Agent Brain raw/compiled/wiki files without fancy RAG."
    )
    parser.add_argument("query", help='Search query, e.g. "filing loop" or "priority query"')
    parser.add_argument(
        "--vault",
        "--brain",
        dest="vault",
        default=None,
        help="Vault root path (default: $OWL_VAULT or active-vault config or marker walk or ~/owl-vault)",
    )
    parser.add_argument(
        "--scope",
        choices=["all", "compiled", "raw", "research", "views"],
        default="all",
        help="Restrict search to one subtree",
    )
    parser.add_argument(
        "--type",
        dest="kind_filter",
        help="Filter by document type text, e.g. summary, report, note",
    )
    parser.add_argument("--limit", type=int, default=10, help="Max number of results to print")
    parser.add_argument("--json", action="store_true", help="Output results as JSON (for slash commands)")
    return parser.parse_args(argv)


def cli(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    base = discover_vault(args.vault)
    if not base.exists():
        print(f"Vault path does not exist: {base}", file=sys.stderr)
        return 2

    matches = search(
        base=base,
        query=args.query,
        scope=args.scope,
        kind_filter=args.kind_filter,
        limit=args.limit,
    )
    if args.json:
        print(matches_to_json(base, matches))
    else:
        print(format_results(base, matches))
    return 0 if matches else 1


if __name__ == "__main__":
    raise SystemExit(cli())
