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

1. **Read from `~/omb/source/` only.** No view reads another view's derived
   artifacts as input. If cairn needs something from owl, the
   underlying source should be in source, not another view's derived files.
2. **Own its vault directory.** Each view writes exclusively to its
   own subdirectory under `~/omb/vault/`. No cross-writes.
3. **Support `search <query>`.** Whether via CLI, script, or manual
   grep — the view must be queryable. This is how benchmarks run.
4. **Document its format.** What does a file look like? What metadata
   is required? What are the naming rules? This lives in the view's
   own docs/ or README.
5. **Be rebuildable from source.** If the view's derived data is
   deleted, it should be possible to regenerate it entirely from
   `~/omb/source/` (possibly via LLM processing). This guarantees source
   is the true ground truth.

## Optional capabilities

Views MAY:

- Provide a CLI (owl and cairn do; wiki does not)
- Run health checks (owl does; cairn and wiki do not)
- Have slash commands and subagents for Claude Code integration
- Support parallel writes (cairn does; owl's compile loop is sequential)
- Maintain an index/catalog file (cairn's INDEX.md)

## Adding a new view

1. Create `vault/<name>/` in the omb repo (code, if any)
2. Create `~/omb/vault/<name>/` or `~/omb/vault/<name>/<product>/` for derived data
3. Write a format spec in `vault/<name>/docs/` or `vault/<name>/README.md`
4. Implement `search` (CLI, script, or documented manual process)
5. Ingest or compile from `~/omb/source/` using the view's own method
6. Add to benchmarks when ready for comparison

## Current views

| view | CLI | vault path | format | entry point | status |
|------|-----|-----------|--------|-------------|--------|
| akasha | `akasha` | ~/omb/vault/akasha | entries/ + compiled/ + GRAPH.tsv | INDEX.md | **active (primary writable — omb 의 메인)** |
| wiki | (manual, grep / qmd 후보) | ~/omb/vault/wiki | entities/ + concepts/ + sources/ + syntheses/ | index.md | **active (companion — Karpathy LLM Wiki 패턴, 사람 읽기 최적)** |
| capsule | `capsule` | ~/omb/vault/capsule/<product> | pages/ + ATLAS.md + llms.txt + ctx/ + meta/ + manifest.json | ATLAS.md | **active (read-only delivery, `omb search` 가 query 매칭 시 자동 첨부)** |

### akasha specifics

- Atomic entries: `entries/<slug>.md` — YAML frontmatter + ~500 token claim body
- Compiled narratives: `compiled/<topic>.md` — LLM-written synthesis per topic
- INDEX.md: master index with topic clusters and entry list
- GRAPH.tsv: topic/concept adjacency list (135 edges as of 2026-04-15)
- ALIASES.tsv: surface form → canonical name map
- 3-layer search: compiled → entries → graph expansion
- **Ingest contract v2** (`docs/ingest-contract-v2.md`): every write passes a machine-checked contract. Key preconditions: canonical naming (`YYYY-MM-DD-<topic>-<slug>.md`), required frontmatter fields (`id`, `type`, `topics`, `confidence`, `source`, `authored`, `ingested`, `supersedes`, `edges`), required body blocks (claim / Why it matters / Evidence), pre-write duplicate search, resolvable `source:` path, and at least one graph edge. Contract violations cause ingest to fail.
- **Supersede protocol**: `omb supersede <new-id> --replaces <old-ids>` writes the chain into the new entry's frontmatter AND physically moves the old entries into `superseded/`. Frontmatter-only supersede is not enough.
- **View merges require normalize**: when folding a deprecated view's content into akasha, naming/frontmatter/source paths must be normalized before import, never copied verbatim. The 2026-04-15 lattice/cairn/owl merger skipped this and the cost is documented in `docs/experiment-3way-2026-04-17.md`.

### wiki specifics

- Karpathy LLM Wiki 패턴 (spec: [karpathy/llm-wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f))
- 페이지 단위: 1 파일 = 1 entity / concept / source-summary / synthesis (akasha 의 atomic claim 과 반대 축)
- `index.md` content-oriented catalog, `log.md` chronological append-only
- akasha 와 **독립** view — 서로의 derived artifact 읽지 않음, 둘 다 `~/omb/source/` 에서 직접 ingest
- 오픈소스 차용 (규약/형식만): `ussumant/llm-wiki-compiler`, `tobi/qmd`, `Ar9av/obsidian-wiki`
- 상세: `docs/view-wiki.md`

### capsule specifics

- Built from `sources/` only — no Akasha artifacts as input
- Product-owned directories: `~/omb/vault/capsule/<product>/`
- Read-only compiled output for agents, not a writable brain
- Expected files: `pages/**`, `ATLAS.md`, `llms.txt`, `ctx/**`, `meta/pages.json`, `manifest.json`
- Search surface: bundle pages + indexes, without entries/graph semantics

## Deprecated views (benchmark history)

These views were evaluated and superseded by akasha. Code preserved in `views/` for reference; no longer operated.

| view | deprecated reason |
|------|-------------------|
| owl | ops overhead; akasha covers same knowledge surface with less tooling |
| facet | sharding complexity without clear retrieval benefit |
| lattice | content-addressed IDs created friction; GRAPH.tsv adopted into akasha |
| cairn | merged into akasha (akasha = cairn entries + lattice graph + owl compiled) |
| wiki | no CLI made LLM integration awkward; akasha compiled/ serves same purpose |
