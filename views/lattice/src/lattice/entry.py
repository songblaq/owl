"""Entry parsing for lattice.

Same atomic-claim markdown+frontmatter format as cairn/facet, with one
addition: an ``edges`` frontmatter field listing related entry IDs for
graph traversal.

  edges: [entry-id-a, entry-id-b, entry-id-c]
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


@dataclass
class Entry:
    """A parsed lattice entry."""

    path: Path
    id: str = ""
    type: str = ""
    topics: List[str] = field(default_factory=list)
    confidence: str = ""
    source: str = ""
    supersedes: List[str] = field(default_factory=list)
    edges: List[str] = field(default_factory=list)
    created: str = ""
    last_retrieved: str = ""
    deprecated: bool = False
    body: str = ""
    raw: str = ""

    @property
    def one_line_summary(self) -> str:
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
    """Minimal YAML-ish frontmatter parser.

    Supports:
      key: scalar
      key: [a, b, c]            # inline list
      key:                      # multi-line list
        - item
        - {to: "slug", type: rel}  # dict-style edge item (extracts 'to')
    """
    data: Dict[str, object] = {}
    current_list_key: Optional[str] = None

    for line in raw.splitlines():
        line = line.rstrip()
        if not line or line.startswith("#"):
            current_list_key = None
            continue

        # Multi-line list item: "  - ..."
        if line.startswith("  - ") or line.startswith("\t- "):
            item = line.strip()[2:].strip()  # strip leading "- "
            if current_list_key is not None:
                # Dict-style: {to: "slug", type: rel}
                if item.startswith("{") and item.endswith("}"):
                    inner = item[1:-1]
                    to_match = re.search(r'to:\s*["\']?([^"\',}]+)["\']?', inner)
                    if to_match:
                        item = to_match.group(1).strip()
                    else:
                        continue
                data[current_list_key] = data.get(current_list_key, [])  # type: ignore[assignment]
                if not isinstance(data[current_list_key], list):
                    data[current_list_key] = [data[current_list_key]]
                cast_list = data[current_list_key]
                assert isinstance(cast_list, list)
                cast_list.append(item.strip('"').strip("'"))
            continue

        if ":" not in line:
            current_list_key = None
            continue

        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()

        if not value:
            # Start of a multi-line list
            current_list_key = key
            data[key] = []
            continue

        current_list_key = None  # scalar value resets list context

        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1]
            items = [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]
            data[key] = items
            continue
        if value.lower() == "true":
            data[key] = True
            continue
        if value.lower() == "false":
            data[key] = False
            continue
        data[key] = value.strip('"').strip("'")
    return data


def load_entry(path: Path) -> Optional[Entry]:
    """Load and parse a single entry file. Returns None if parse fails."""
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    e = Entry(path=path, raw=raw)
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
    edges = front.get("edges") or []
    if isinstance(edges, list):
        e.edges = [str(x) for x in edges]
    elif isinstance(edges, str) and edges:
        e.edges = [edges]
    return e


def iter_entries(vault: Path, include_superseded: bool = False) -> List[Entry]:
    """Yield all entries in vault/entries/ (and optionally vault/superseded/)."""
    results: List[Entry] = []
    entries_dir = vault / "entries"
    if entries_dir.exists():
        for f in sorted(entries_dir.rglob("*.md")):
            if f.is_file():
                e = load_entry(f)
                if e:
                    results.append(e)
    if include_superseded:
        sup_dir = vault / "superseded"
        if sup_dir.exists():
            for f in sorted(sup_dir.rglob("*.md")):
                if f.is_file():
                    e = load_entry(f)
                    if e:
                        results.append(e)
    return results
