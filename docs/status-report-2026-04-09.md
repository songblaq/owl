# agent-brain Status Report — 2026-04-09 (Final)

## 1. Project Identity

**agent-brain** is a personal LLM-maintained knowledge system built as a
monorepo. Three independent **views** (strategies) operate over a shared
immutable **source** corpus so their strengths can be measured and combined.

| | owl | cairn | wiki |
|---|---|---|---|
| Philosophy | Karpathy LLM Wiki + ops infra | LLM-first atomic claims | Pure Karpathy (control group) |
| Version | 0.1.0 | 0.0.1 (pre-alpha) | planned |
| CLI | `owl` (9 subcommands) | `cairn` (5 subcommands) | none |
| Vault | `~/owl-vault` | `~/cairn-vault` | `~/brain-vault/wiki/` |
| Claude Code | 7 slash commands + 3 subagents | CLI only | none |
| Tests | none | none | n/a |

---

## 2. Repository Layout

```
~/_/projects/agent-brain/              GitHub: songblaq/agent-brain
  README.md
  LICENSE                              MIT
  docs/
    source-layer-spec.md               immutable source pool contract
    view-contract.md                   required interface for all views
    benchmark-v0.md                    partial migration benchmark
    benchmark-v1.md                    full coverage benchmark
    status-report-2026-04-09.md        this report
  views/
    owl/                               11 Python modules, 52 docs, 9 plans
      pyproject.toml                   v0.1.0
      install.sh                       curl | sh bootstrap
      AGENTS.md                        operational schema
      src/owl/                         cli, vault, search, health, hooks, ...
      src/owl/claude_assets/           3 agents, 7 commands, vault template
      docs/                            3,971 lines of specs
    cairn/                             7 Python modules
      pyproject.toml                   v0.0.1
      src/cairn/                       cli, vault, entry, search, index, ...
    wiki/
      docs/wiki-view-spec.md           specification only
```

---

## 3. Data Layer

```
~/brain-vault/                          symlink hub (data home)
  sources/ --> ~/owl-vault/raw          immutable source pool
  owl/     --> ~/owl-vault              owl view vault
  cairn/   --> ~/cairn-vault            cairn view vault
  wiki/                                 empty (planned)
```

### Vault Statistics

| Metric | owl | cairn |
|---|---|---|
| Active documents | 232 compiled | 421 entries |
| Raw/source files | 125 | 0 (reads from sources/) |
| Archived | -- | 16 superseded |
| INDEX startup | -- | 131 KB master catalog |
| Views | 10 MDV | -- |
| Outputs | 19 files | -- |
| Health issues | 195 (21 med, 174 low) | -- |

### Benchmark Results (v1, full coverage)

cairn wins 6/6 dimensions vs owl:

| Dimension | owl | cairn | Winner |
|---|---|---|---|
| Storage density | 232 docs / 1.2 MB | 421 entries / 1.0 MB | cairn (-19%) |
| Retrieval speed | score + read doc | INDEX scan + read entry | cairn (26% faster) |
| Search quality | doc-level matches | atomic-level matches | cairn (more specific) |
| Session startup | read CLAUDE.md + search | read INDEX.md (131 KB) | cairn (single file) |
| Write throughput | sequential (LLM bottleneck) | parallel (atomic) | cairn |
| Write ergonomics | 5-step compile cycle | 1 frontmatter + body | cairn |

**Recommendation (from benchmark-v1):** run both. owl = human-facing wiki
(Obsidian browsable). cairn = LLM-facing brain (INDEX-driven atomic retrieval).

---

## 4. Restructure Migration Checklist

### Phase 1-3: Completed in previous session (2026-04-09)

- [x] brain-vault symlink hub created (`~/brain-vault/`)
- [x] Monorepo structure (`views/owl/`, `views/cairn/`, `views/wiki/`, `docs/`)
- [x] GitHub repo renamed `songblaq/owl` -> `songblaq/agent-brain`
- [x] Local directory renamed `~/_/projects/owl` -> `~/_/projects/agent-brain`

### Phase 4: Completed in this session

| Task | Status | Detail |
|---|---|---|
| owl CLI reinstall | DONE | `pipx install -e views/owl --force` |
| cairn CLI reinstall | DONE | `pipx install -e views/cairn --force` |
| `owl status` | DONE | v0.1.0, vault OK, 232 compiled, 125 raw |
| `cairn status` | DONE | v0.0.1, vault OK, 421 entries |
| `git push` | DONE | main -> main |
| Broken symlinks (10) | FIXED | `owl setup --non-interactive` |
| install.sh | FIXED | repo URL, default path, cd path |
| Subagent prompts (3) | FIXED | owl-compiler, owl-librarian, owl-health |
| Vault template CLAUDE.md | FIXED | 3 path references |
| AGENTS.md | FIXED | 4 path references |
| Operational docs (8) | FIXED | all `~/_/projects/owl` -> `agent-brain` |
| Live vault CLAUDE.md | FIXED | 3 path references |
| Global CLAUDE.md | FIXED | project path + vault stats |
| `owl search` e2e test | PASS | "filing loop" returns score 15 |
| `cairn search` e2e test | PASS | "karpathy" returns score 13 |
| Stale ref audit | PASS | 0 remaining (excl. plans/ historical) |

### Remaining stale references (intentionally not modified)

- `views/owl/plans/` — 9 historical plan documents reference old paths.
  These are frozen records of past decisions. Modifying them would distort history.

---

## 5. Architecture Flow Diagrams

### 5-1. Overall System Architecture

```
                    +--------------------------------------------+
                    |           agent-brain (monorepo)            |
                    |         github.com/songblaq/agent-brain     |
                    |                                            |
                    |  docs/          views/                     |
                    |  +----------+   +------+------+------+    |
                    |  | specs    |   | owl/ |cairn/| wiki/|    |
                    |  | benchmarks|  |      |      |      |    |
                    |  +----------+   +--+---+--+---+--+---+    |
                    +-------------------|---------|---------|-----+
                                        |         |         |
                               pipx -e  |         | pipx -e |  (no CLI)
                                        v         v         v
                                  ~/.local/bin/  ~/.local/bin/
                                      owl          cairn
                                        |         |
                           vault        |         |        vault
                          discovery     v         v      discovery
                                  ~/owl-vault  ~/cairn-vault
                                        \         /
                                  +------+-------+------+
                                  |   ~/brain-vault/    |
                                  |   sources/ (shared) |
                                  +---------------------+
```

### 5-2. Data Flow: Source to Views

```
 [User/External]
       |
       | drops raw material
       v
 +---------------------+
 | brain-vault/sources/ |  (immutable, 125 files)
 | = owl-vault/raw/     |  (symlinked)
 +--+--------+--------+-+
    |        |        |
    v        v        v
 +------+ +-------+ +------+
 | owl  | | cairn | | wiki |
 |      | |       | |      |
 | LLM  | | LLM   | | LLM  |
 |compiles|atomizes| |compiles
 |      | |       | |      |
 | 232  | | 421   | | (0)  |
 |compiled|entries | |planned
 +--+---+ +---+---+ +------+
    |         |
    v         v
 +--+---------+--+
 | LLM sessions  |
 | query/compile |
 | /file/promote |
 +---------------+
```

### 5-3. owl Operational Loop

```
 [User]                    [Claude Code]                    [owl CLI]
   |                            |                               |
   |  /owl-search "query"       |                               |
   +--------------------------->|                               |
   |                            |  ! owl search --json "query"  |
   |                            +------------------------------>|
   |                            |           JSON results        |
   |                            |<------------------------------+
   |                            |                               |
   |                            |  (LLM clusters & explains)    |
   |    organized answer        |                               |
   |<---------------------------+                               |
   |                            |                               |
   |  /owl-compile raw/X.md     |                               |
   +--------------------------->|                               |
   |                            |  ! owl compile raw/X.md       |
   |                            +------------------------------>|
   |                            |         compile metadata JSON |
   |                            |<------------------------------+
   |                            |                               |
   |                            |  [owl-compiler subagent]      |
   |                            |  Read raw -> Write compiled   |
   |                            |  -> ! owl health --json       |
   |    compiled doc created    |                               |
   |<---------------------------+                               |
   |                            |                               |
   |                   [5 lifecycle hooks]                       |
   |                   session_start: vault context injection    |
   |                   user_prompt: keyword routing hints        |
   |                   post_tool_use: health warnings on write   |
   |                   pre_compact: session snapshot to logs/    |
   |                   stop: orphaned raw warnings               |
```

### 5-4. cairn Session Pattern

```
 [LLM session start]
        |
        v
 +----------------------+
 | Read INDEX.md        |   <-- 131 KB single-file context load
 | (421 entries table)  |       id | type | topics | summary | confidence
 +----------+-----------+
            |
            |  LLM scans table
            v
 +----------------------+
 | Pick relevant        |   <-- no search needed; INDEX is the brain
 | entry IDs            |
 +----------+-----------+
            |
            v
 +----------------------+
 | Read entries/*.md    |   <-- ~400 tokens each, parallel OK
 | (atomic claims)      |
 +----------+-----------+
            |
            v
 +----------------------+
 | Answer with          |
 | entry citations      |
 +----------------------+
```

### 5-5. Claude Code Integration Map

```
 ~/.claude/
 +-- agents/                              SYMLINKS (all verified LIVE)
 |   +-- owl-compiler.md ----+
 |   +-- owl-health.md ------+--> agent-brain/views/owl/src/owl/claude_assets/agents/
 |   +-- owl-librarian.md ---+
 |
 +-- commands/                            SYMLINKS (all verified LIVE)
 |   +-- owl-search.md ------+
 |   +-- owl-query.md -------+
 |   +-- owl-compile.md -----+
 |   +-- owl-ingest.md ------+--> agent-brain/views/owl/src/owl/claude_assets/commands/
 |   +-- owl-file.md --------+
 |   +-- owl-health.md ------+
 |   +-- owl-promote.md -----+
 |
 +-- CLAUDE.md                   owl section (monorepo paths, updated stats)

 ~/owl-vault/.claude/
 +-- settings.json               5 lifecycle hooks (owl hook <name>)
                                 hooks use `owl` CLI via PATH (OK)

 ~/cairn-vault/
 +-- (no Claude Code integration yet)
```

### 5-6. Monorepo Restructure Migration Flow

```
 Phase 1                Phase 2                Phase 3
 brain-vault hub        monorepo structure     repo rename
 +-----------+          +-----------+          +-----------+
 | ~/brain-  |          | views/    |          | songblaq/ |
 | vault/    |          |   owl/    |          | agent-    |
 |  sources  |--------->|   cairn/  |--------->| brain     |
 |  owl      |          |   wiki/   |          | (GitHub)  |
 |  cairn    |          | docs/     |          |           |
 |  wiki     |          |           |          |           |
 +-----------+          +-----------+          +-----------+
                                                     |
                                                     v
 Phase 4 (this session)
 +--------------------------------------------------+
 | CLI reinstall (pipx -e views/owl, views/cairn)   |
 | Symlink repair (owl setup --non-interactive)      |
 | Path migration (18 files, 30+ references)         |
 | E2E verification (search, status, symlink read)   |
 +--------------------------------------------------+
```

---

## 6. Next Steps (Roadmap)

### Phase T: Cairn integration parity
- Cairn slash commands (`/cairn-search`, `/cairn-ingest`)
- Cairn subagents (`cairn-scribe`, `cairn-auditor`)
- Cairn vault hooks (session_start with INDEX.md injection)

### Phase U: Testing foundation
- pytest for owl (search, health, vault discovery, ingest primitives)
- pytest for cairn (entry parsing, search scoring, index generation)
- CI via GitHub Actions

### Phase V: Wiki view + three-way benchmark
- Implement wiki view (pure Karpathy, no extensions)
- Run 10-question LLM session comparison across all three views
- Publish benchmark-v2 with real retrieval quality metrics

### Phase W: Sync & convergence
- One-way owl -> cairn freshness loop (automated rebuild)
- Source layer decoupling (brain-vault/sources/ as independent dir)
- Cairn tag taxonomy cleanup (70% singleton tags)

---

## 7. Key Design Decisions

1. **Three views, not one** — compare strategies empirically, not theoretically
2. **Shared immutable sources** — all views derive from the same ground truth
3. **CLI does decidable work, LLM does interpretive work** — owl's core pattern
4. **One claim per file** (cairn) vs **one topic per doc** (owl) — the central trade-off
5. **Supersede, never mutate** (cairn) vs **edit in place** (owl) — provenance vs convenience
6. **INDEX.md as brain** (cairn) — single-file session startup, no search needed
7. **Monorepo** — shared specs, benchmarks, and future cross-view tooling

---

## 8. Verification Evidence

All checks performed at 2026-04-09T23:10 KST.

```
Symlinks:     10/10 live (agent-brain/views/owl/src/owl/claude_assets/)
owl status:   v0.1.0, vault OK, 232 compiled, 125 raw, hooks installed
cairn status: v0.0.1, vault OK, 421 entries, 16 superseded
owl search:   "filing loop" -> score 15 (strong match)
cairn search: "karpathy" -> score 13 (strong match)
Stale refs:   0 in runtime files (plans/ historical only)
Git:          14 modified + 1 new (uncommitted, ready for commit)
```
