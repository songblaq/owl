"""lattice — graph-augmented LLM knowledge base.

3-stage retrieval: BLOOM token filter → MANIFOLD ngram lookup → full entry
scoring with 1-hop graph expansion via GRAPH.tsv edges.

Key ideas:
- One atomic claim per file (same as cairn)
- BLOOM.txt: sorted unique token list for fast pre-filter
- MANIFOLD.tsv: ngram → entry_id reverse index
- GRAPH.tsv: entry_id → edge_id adjacency for 1-hop expansion
- MAP.md: topic-level table of contents (human-readable)
- .lattice-vault marker file (same discovery chain as cairn/facet)
"""

__version__ = "0.1.0"
