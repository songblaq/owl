"""Entry parsing for facet.

Identical to cairn's entry parsing — same atomic-claim markdown+frontmatter
format. Shards contain regular entries/ sub-directories, or entries directly
at the shard root.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


@dataclass
class Entry:
    """A parsed facet entry."""

    path: Path
    shard: str = ""
    id: str = ""
    type: str = ""
    topics: List[str] = field(default_factory=list)
    confidence: str = ""
    source: str = ""
    edges: List[Dict[str, str]] = field(default_factory=list)
    supersedes: List[str] = field(default_factory=list)
    created: str = ""
    last_retrieved: str = ""
    deprecated: bool = False
    body: str = ""
    raw: str = ""

    @property
    def one_line_summary(self) -> str:
        """Extract the first non-header, non-bullet paragraph line."""
        for line in self.body.strip().splitlines():
            s = line.strip()
            if s and not s.startswith("#") and not s.startswith("-"):
                return s[:140]
        for line in self.body.strip().splitlines():
            s = line.strip()
            if s:
                return s[:140]
        return "(no summary)"


def parse_frontmatter(raw: str) -> Dict[str, object]:
    """Minimal YAML-ish frontmatter parser supporting block lists (edges:)."""
    data: Dict[str, object] = {}
    lines = raw.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line or line.startswith("#"):
            i += 1
            continue
        if ":" not in line:
            i += 1
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if not value:
            # Could be a block list (e.g., edges:\n  - item)
            block_items: List[str] = []
            i += 1
            while i < len(lines) and lines[i].startswith("  - "):
                block_items.append(lines[i].strip()[2:].strip())
                i += 1
            if block_items:
                data[key] = block_items
            else:
                data[key] = ""
            continue
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1]
            items = [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]
            data[key] = items
            i += 1
            continue
        if value.lower() == "true":
            data[key] = True
            i += 1
            continue
        if value.lower() == "false":
            data[key] = False
            i += 1
            continue
        data[key] = value.strip('"').strip("'")
        i += 1
    return data


def _parse_edges(raw_edges: object) -> List[Dict[str, str]]:
    """Parse edges from frontmatter into list of dicts."""
    if not raw_edges:
        return []
    if isinstance(raw_edges, list):
        result: List[Dict[str, str]] = []
        for item in raw_edges:
            if isinstance(item, str):
                # e.g. '{to: "other-slug", type: supports}'
                edge: Dict[str, str] = {}
                for kv in re.finditer(r'(\w+)\s*:\s*"?([^",}]+)"?', item):
                    edge[kv.group(1)] = kv.group(2).strip()
                if edge:
                    result.append(edge)
        return result
    return []


def load_entry(path: Path, shard: str = "") -> Optional[Entry]:
    """Load and parse a single entry file. Returns None if parse fails."""
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    e = Entry(path=path, raw=raw, shard=shard)
    m = FRONTMATTER_RE.match(raw)
    if not m:
        e.id = path.stem
        e.body = raw
        return e

    front = parse_frontmatter(m.group(1))
    e.body = m.group(2)
    e.id = str(front.get("id") or path.stem)
    e.type = str(front.get("type") or "")
    e.confidence = str(front.get("confidence") or "")
    e.source = str(front.get("source") or "")
    e.created = str(front.get("created") or "")
    e.last_retrieved = str(front.get("last_retrieved") or "")
    e.deprecated = bool(front.get("deprecated") or False)
    topics = front.get("topics") or front.get("topic") or []
    if isinstance(topics, list):
        e.topics = [str(t) for t in topics]
    elif isinstance(topics, str) and topics:
        e.topics = [topics]
    supersedes = front.get("supersedes") or []
    if isinstance(supersedes, list):
        e.supersedes = [str(s) for s in supersedes]
    elif isinstance(supersedes, str) and supersedes:
        e.supersedes = [supersedes]
    e.edges = _parse_edges(front.get("edges"))
    return e


def iter_shard_entries(shard_path: Path, shard_name: str = "") -> List[Entry]:
    """Yield all entries in a shard directory (*.md, skip _index.md)."""
    results: List[Entry] = []
    if not shard_path.exists():
        return results
    for f in sorted(shard_path.rglob("*.md")):
        if f.is_file() and f.name != "_index.md":
            e = load_entry(f, shard=shard_name)
            if e:
                results.append(e)
    return results


def iter_all_entries(vault: Path, include_superseded: bool = False) -> List[Entry]:
    """Yield all entries across all shards."""
    from facet.vault import iter_shards
    results: List[Entry] = []
    for shard_name, shard_path in iter_shards(vault):
        results.extend(iter_shard_entries(shard_path, shard_name))
    if include_superseded:
        sup_dir = vault / "superseded"
        if sup_dir.exists():
            for f in sorted(sup_dir.rglob("*.md")):
                if f.is_file():
                    e = load_entry(f, shard="superseded")
                    if e:
                        results.append(e)
    return results
