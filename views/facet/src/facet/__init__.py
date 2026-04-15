"""facet — shard-aware LLM knowledge base with alias resolution.

Evolution of cairn: same atomic-claim philosophy, but entries are organized
into named shards. Each shard has its own _index.md. An ALIASES.tsv maps
surface forms to canonical shard names for query-time synonym resolution.

Key ideas:
- One atomic claim per file, ~400 token hard cap (same as cairn)
- Sharded directory: shards/<name>/  (vs cairn's flat entries/)
- ALIASES.tsv for surface-form → canonical shard mapping
- Per-shard _index.md (auto-generated)
- MANIFEST.md as top-level table of contents across all shards
- .facet-vault marker file (same discovery chain as cairn)
"""

__version__ = "0.1.0"
