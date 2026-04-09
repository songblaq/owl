"""Entry parsing for cairn.

Each entry is a markdown file with YAML frontmatter. This module parses
frontmatter without requiring a YAML dependency — we use a minimal parser
because cairn entries have a constrained shape.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


@dataclass
class Entry:
    """A parsed cairn entry."""

    path: Path
    id: str = ""
    type: str = ""
    topics: List[str] = field(default_factory=list)
    confidence: str = ""
    source: str = ""
    supersedes: List[str] = field(default_factory=list)
    created: str = ""
    last_retrieved: str = ""
    deprecated: bool = False
    body: str = ""
    raw: str = ""

    @property
    def one_line_summary(self) -> str:
        """Extract the first paragraph or first non-empty line of the body."""
        for line in self.body.strip().splitlines():
            s = line.strip()
            if s and not s.startswith("#") and not s.startswith("-"):
                return s[:140]
        # fallback: first non-empty
        for line in self.body.strip().splitlines():
            s = line.strip()
            if s:
                return s[:140]
        return "(no summary)"


def parse_frontmatter(raw: str) -> Dict[str, object]:
    """Minimal YAML-ish frontmatter parser.

    Supports:
      key: value                 → string
      key: [a, b, c]              → list
      key: true / false           → bool

    Does NOT support nested structures. For cairn's constrained schema this
    is sufficient and removes the PyYAML dependency.
    """
    data: Dict[str, object] = {}
    for line in raw.splitlines():
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if not value:
            data[key] = ""
            continue
        # list
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1]
            items = [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]
            data[key] = items
            continue
        # bool
        if value.lower() == "true":
            data[key] = True
            continue
        if value.lower() == "false":
            data[key] = False
            continue
        # string (strip quotes)
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
        # No frontmatter — treat whole file as body, id = filename stem
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
