---
id: atlas-v1
status: active
created: 2026-04-15
---

# oh-my-brain (omb) — Atlas

Quick entry point for external reference. Covers architecture, CLI, data model, and operational patterns.

---

## What it is

**omb** is a personal LLM-maintained knowledge system. Raw materials (articles, notes, conversations) go in; the LLM organizes them into a searchable, compiled vault. The system is designed so the LLM is the primary writer and reader — not a human filing things manually.

Single active vault: **akasha** — an LLM-managed knowledge layer with atomic entries, compiled narratives, and a traversable graph.

---

## Architecture

```
~/omb/
  source/             raw input (immutable — read-only after ingestion)
  vault/
    akasha/           primary brain
      entries/        386 atomic knowledge units (~500 tok each)
      compiled/       57 LLM-written narrative docs (by topic)
      INDEX.md        master index (entry list + topic clusters)
      GRAPH.tsv       135 topic/concept edges (adjacency list)
      ALIASES.tsv     surface form → canonical name map
```

```
oh-my-brain/          this repo (code + specs + benchmarks)
  views/
    omb/              omb CLI (unified dispatcher)
    akasha/           akasha CLI (vault engine)
    [deprecated]      owl / facet / lattice / cairn / wiki
  docs/               specs, benchmarks, design notes
```

**Data flow:**
```
raw input → akasha ingest → entries/ → akasha index → INDEX.md + GRAPH.tsv
                                     → akasha compile → compiled/<topic>.md
```

---

## CLI Reference

### `omb` — public interface

외부에서 사용하는 유일한 CLI. 내부 vault 구현(akasha)을 직접 알 필요 없음.

```bash
# 상태
omb status

# 검색
omb search "<query>"
omb search "<query>" --limit N
omb search "<query>" --json

# 지식 추가
omb ingest <file.md>
omb ingest --text "..."
omb ingest --text "..." --title <slug>
omb ingest --topic <name> <file.md>
omb ingest --dry-run <file.md>      # 미리보기

# 커버리지 확인
omb health
omb health --json
```

### `akasha` — internal vault engine

내부 유지보수 및 LLM 컴파일 워크플로우용. 일반 사용자는 `omb`만 사용.

```bash
# 인덱스 재빌드
akasha index

# LLM 컴파일 워크플로우
akasha compile --dry-run              # 토픽별 pending/compiled 현황
akasha compile --dump <topic>         # entries 덤프 → LLM에게 붙여넣기 → compiled/<topic>.md 저장

# vault 초기화/전환
akasha init [path]
akasha use <path>
```

### Deprecated (all superseded by akasha)
`owl`, `facet`, `lattice`, `cairn`, `wiki` — no longer operated. Use `omb` instead.

---

## Data Model

### Entry (entries/<slug>.md)

```yaml
---
id: <date>-<slug>
topic: <primary-topic>
tags: [tag1, tag2]
sources: [<source-slug>]
created: YYYY-MM-DD
---

<atomic claim in ~500 tokens — one coherent idea>
```

### Compiled doc (compiled/<topic>.md)

LLM-written narrative synthesis of all entries for a topic. Updated by running:
```bash
akasha compile --dump <topic>
# → paste output to LLM → LLM writes the narrative → save as compiled/<topic>.md
```

### GRAPH.tsv

Tab-separated adjacency list:
```
concept_a    concept_b    <edge_weight>
```
Used for graph expansion during search (3rd layer after compiled + entries match).

---

## Search Layers

`akasha search "<query>"` runs three layers in sequence:

1. **Compiled** — search compiled/*.md for topic-level matches (fast, high signal)
2. **Entries** — search entries/*.md for atomic claim matches
3. **Graph expansion** — if hits found, expand to adjacent concepts via GRAPH.tsv

---

## Operational Cycle

**Adding new knowledge:**
```bash
# Option A: file
akasha ingest ~/Downloads/article.md

# Option B: conversation / raw text
akasha ingest --text "<paste content>" --title "concept-name"
```

**Compiling a topic (LLM does the writing):**
```bash
akasha compile --dry-run          # see what topics need a compiled doc
akasha compile --dump <topic>     # dump entries for LLM → LLM writes narrative
# paste output to LLM, ask it to write compiled/<topic>.md, then save
```

**Rebuilding index after manual edits:**
```bash
akasha index
```

---

## Claude Code Integration

The system is designed for use inside Claude Code sessions. Typical pattern:

```
before answering → akasha search "<topic>"
→ if found: read compiled/<topic>.md → answer with evidence
→ if not found: note the gap, answer from training, suggest ingest
```

CLAUDE.md registers this reflex globally.

---

## Install

```bash
cd views/omb && pipx install -e .
cd views/akasha && pipx install -e .

# verify
omb status
akasha status
```

Requires Python 3.10+, pipx.

---

## Design Principles

1. **Raw = immutable** — source files are never modified after ingestion
2. **LLM is the writer** — entries and compiled docs are written by LLM, not manually curated
3. **Vault = data only** — no Python or code inside the vault directories
4. **Evidence with records** — entries include why + alternatives considered, not just conclusions
5. **Rebuildable** — delete vault, re-ingest sources, get equivalent result
