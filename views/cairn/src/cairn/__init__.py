"""cairn — an LLM-first knowledge base.

Atomic claims, flat directory, INDEX-driven retrieval. Sideline experiment
parallel to owl. See docs/design-v0.md for the full design.

Lineage: a fresh Claude instance (2026-04-09) was asked from first principles
how to design a knowledge base with LLM as the primary reader. The design
this package implements came from that zero-context query.

Key ideas:
- One atomic claim per file, ~400 token hard cap
- Flat directory (entries/ sources/ superseded/)
- INDEX.md as the brain's table of contents — read first every session
- Supersede-never-mutate
- Single-writer scribe + lockfile for multi-agent safety
- User has 3 verbs: drop, ask, audit (user does not write entries)
"""

__version__ = "0.0.1"
