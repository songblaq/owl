---
id: view-contract-v1
status: active
created: 2026-04-09
updated: 2026-04-15
---

# View contract

A **view** is one strategy for organizing, storing, and retrieving
knowledge from the shared source pool. Each view lives in its own
directory and follows its own rules. This document defines what
every view must provide to be a first-class citizen of agent-brain.

## Required interface

Every view MUST:

1. **Read from sources/ only.** No view reads another view's derived
   artifacts as input. If cairn needs something from owl, the
   underlying source should be in sources/, not owl/compiled/.
2. **Own its vault directory.** Each view writes exclusively to its
   own subdirectory under brain-vault/ (e.g., brain-vault/owl/,
   brain-vault/cairn/). No cross-writes.
3. **Support `search <query>`.** Whether via CLI, script, or manual
   grep — the view must be queryable. This is how benchmarks run.
4. **Document its format.** What does a file look like? What metadata
   is required? What are the naming rules? This lives in the view's
   own docs/ or README.
5. **Be rebuildable from sources.** If the view's derived data is
   deleted, it should be possible to regenerate it entirely from
   sources/ (possibly via LLM processing). This guarantees sources/
   is the true ground truth.

## Optional capabilities

Views MAY:

- Provide a CLI (owl and cairn do; wiki does not)
- Run health checks (owl does; cairn and wiki do not)
- Have slash commands and subagents for Claude Code integration
- Support parallel writes (cairn does; owl's compile loop is sequential)
- Maintain an index/catalog file (cairn's INDEX.md)

## Adding a new view

1. Create `views/<name>/` in the agent-brain repo (code, if any)
2. Create `brain-vault/<name>/` for derived data
3. Write a format spec in `views/<name>/docs/` or `views/<name>/README.md`
4. Implement `search` (CLI, script, or documented manual process)
5. Ingest from sources/ using the view's own method
6. Add to benchmarks when ready for comparison

## Current views

| view | CLI | vault path | format | entry point | status |
|------|-----|-----------|--------|-------------|--------|
| akasha | `akasha` | ~/omb/vault/akasha | entries/ + compiled/ + GRAPH.tsv | INDEX.md | **active (primary)** |

### akasha specifics

- Atomic entries: `entries/<slug>.md` — YAML frontmatter + ~500 token claim body
- Compiled narratives: `compiled/<topic>.md` — LLM-written synthesis per topic
- INDEX.md: master index with topic clusters and entry list
- GRAPH.tsv: topic/concept adjacency list (135 edges as of 2026-04-15)
- ALIASES.tsv: surface form → canonical name map
- 3-layer search: compiled → entries → graph expansion

## Deprecated views (benchmark history)

These views were evaluated and superseded by akasha. Code preserved in `views/` for reference; no longer operated.

| view | deprecated reason |
|------|-------------------|
| owl | ops overhead; akasha covers same knowledge surface with less tooling |
| facet | sharding complexity without clear retrieval benefit |
| lattice | content-addressed IDs created friction; GRAPH.tsv adopted into akasha |
| cairn | merged into akasha (akasha = cairn entries + lattice graph + owl compiled) |
| wiki | no CLI made LLM integration awkward; akasha compiled/ serves same purpose |
