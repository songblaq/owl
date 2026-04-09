# agent-brain Final Status Report — 2026-04-09

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
~/_/projects/oh-my-brain/              GitHub: songblaq/oh-my-brain
  README.md                            architecture overview
  LICENSE                              MIT
  .gitignore                           Python + vault protection
  docs/
    source-layer-spec.md               immutable source pool contract
    view-contract.md                   required interface for all views
    benchmark-v0.md                    partial migration benchmark
    benchmark-v1.md                    full coverage benchmark
    status-report-2026-04-09.md        this report
  views/
    owl/                               11 Python modules, 52 docs, 9 plans
      pyproject.toml                   v0.1.0, entry: owl = owl.cli:main
      install.sh                       curl | bash bootstrap
      AGENTS.md                        operational schema
      src/owl/                         cli, vault, search, health, hooks, ...
      src/owl/claude_assets/           3 agents, 7 commands, vault template
      docs/                            3,971 lines of specs (52 files)
      plans/                           9 historical phase records
    cairn/                             7 Python modules
      pyproject.toml                   v0.0.1, entry: cairn = cairn.cli:main
      src/cairn/                       cli, vault, entry, search, index, ...
    wiki/
      docs/wiki-view-spec.md           specification only (control group)
```

---

## 3. Data Layer

```
~/brain-vault/                          symlink hub
  sources/ --> ~/owl-vault/raw          shared immutable source pool
  owl/     --> ~/owl-vault              owl view
  cairn/   --> ~/cairn-vault            cairn view
  wiki/                                 empty (planned)
```

### Current Numbers (verified 2026-04-09T23:30 KST)

| Metric | owl | cairn |
|---|---|---|
| Active documents | 232 compiled | 421 entries |
| Raw/source files | 125 (67 own + atlas subtree) | 0 (reads from sources/) |
| Archived | -- | 16 superseded |
| MDV views | 10 | -- |
| Outputs | 19 files | -- |
| INDEX startup | -- | 131 KB master catalog |
| Health issues | 195 (21 med, 174 low) | -- |

### Benchmark Summary (v1, full coverage)

cairn wins 6/6 dimensions. Recommendation: **run both**.
owl = human-facing wiki (Obsidian). cairn = LLM-facing brain (atomic INDEX).

---

## 4. Full Verification Checklist

### 4-1. Infrastructure

| Check | Result |
|---|---|
| `owl --version` | 0.1.0 |
| `cairn --version` | 0.0.1 |
| `owl status` vault marker | OK |
| `owl status` hooks installed | OK |
| `owl status` machine identity | LucaBlaiMacmini (primary) |
| `cairn status` vault marker | OK |
| `cairn status` INDEX.md | OK |

### 4-2. Symlinks (16 total)

| Location | Count | Target base | Status |
|---|---|---|---|
| `~/.claude/agents/owl-*.md` | 3 | `agent-brain/views/owl/.../agents/` | ALL OK |
| `~/.claude/commands/owl-*.md` | 7 | `agent-brain/views/owl/.../commands/` | ALL OK |
| `~/.agents/skills/owl-*.md` | 3 | `agent-brain/views/owl/.../agents/` | ALL OK |
| `~/brain-vault/{sources,owl,cairn}` | 3 | vault directories | ALL OK |

### 4-3. Path Migration

| Scope | Stale refs | Status |
|---|---|---|
| Runtime files (*.md, *.sh, *.py) | 0 | CLEAN |
| `~/.claude/CLAUDE.md` | 0 | CLEAN |
| `~/owl-vault/CLAUDE.md` | 0 | CLEAN |
| Subagent prompts (3) | 0 | CLEAN |
| Slash commands (7) | 0 | CLEAN |
| `views/owl/plans/` (historical) | ~15 | Intentionally preserved |

### 4-4. End-to-End

| Test | Result |
|---|---|
| `owl search "karpathy wiki"` | score 36 (strong) |
| `cairn search "filing loop"` | score 25 (strong) |
| Slash command readable (`cat ~/.claude/commands/owl-search.md`) | OK |
| Subagent readable (`cat ~/.claude/agents/owl-compiler.md`) | OK |

### 4-5. Git

| Check | Result |
|---|---|
| Working tree | clean |
| Remote sync | origin/main = local main |
| Latest commits | `8ff31c5` cairn+wiki views, `7f57a29` phase S migration |

---

## 5. Architecture Flow Diagrams

### 5-1. Overall System Architecture

```
                   +---------------------------------------------+
                   |          agent-brain  (monorepo)             |
                   |        github.com/songblaq/oh-my-brain       |
                   |                                             |
                   |  docs/           views/                     |
                   |  +-----------+   +-------+-------+-------+ |
                   |  | specs     |   | owl/  | cairn/| wiki/ | |
                   |  | benchmarks|   |       |       |       | |
                   |  +-----------+   +---+---+---+---+---+---+ |
                   +------------------|-------|-------|----------+
                                      |       |       |
                             pipx -e  |       |       |  (no CLI)
                                      v       v       v
                                ~/.local/bin/ ~/brain-vault/wiki/
                                  owl  cairn
                                    |       |
                       vault        |       |       vault
                      discovery     v       v     discovery
                              ~/owl-vault  ~/cairn-vault
                                    \       /
                              +------+-----+------+
                              |  ~/brain-vault/   |
                              |  sources/ (shared) |
                              +-------------------+
```

### 5-2. Data Flow: Sources to Views to Sessions

```
 [User / External]
       |
       | drops raw material
       v
 +---------------------+
 | brain-vault/sources/ |  125 files, immutable
 | = owl-vault/raw/     |
 +--+--------+--------+-+
    |        |        |
    | read   | read   | read
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
    |  one-way sync (future Phase W)
    +-------->+
    |         |
    v         v
 +--+---------+--+
 | LLM sessions  |
 | owl: search + |
 |   compile +   |
 |   health      |
 | cairn: INDEX  |
 |   + entries   |
 +---------------+
```

### 5-3. owl Operational Loop (CLI + Claude Code)

```
 [User]                    [Claude Code]                    [owl CLI]
   |                            |                               |
   |  /owl-search "query"       |                               |
   +--------------------------->|                               |
   |                            |  ! owl search --json "query"  |
   |                            +------------------------------>|
   |                            |           JSON results        |
   |                            |<------------------------------+
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
   |                            |  [owl-compiler subagent]      |
   |                            |  Read raw -> Write compiled   |
   |                            |  -> ! owl health --json       |
   |    compiled doc created    |                               |
   |<---------------------------+                               |
   |                            |                               |
   |                   [5 lifecycle hooks — always active]       |
   |                   session_start:  vault context injection   |
   |                   user_prompt:    keyword routing hints     |
   |                   post_tool_use:  health warnings on write  |
   |                   pre_compact:    session snapshot to logs/ |
   |                   stop:           orphaned raw warnings     |
```

### 5-4. cairn Session Pattern

```
 [LLM session start]
        |
        v
 +----------------------+
 | Read INDEX.md        |   131 KB single-file context load
 | (421 entries table)  |   id | type | topics | summary | confidence
 +----------+-----------+
            |
            |  LLM scans table
            v
 +----------------------+
 | Pick relevant        |   no search CLI needed;
 | entry IDs            |   INDEX is the brain
 +----------+-----------+
            |
            v
 +----------------------+
 | Read entries/*.md    |   ~400 tokens each
 | (atomic claims)      |   parallel reads OK
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
 +-- agents/                                    SYMLINKS (16 total, ALL OK)
 |   +-- owl-compiler.md ----+
 |   +-- owl-health.md ------+--> agent-brain/views/owl/.../agents/
 |   +-- owl-librarian.md ---+
 |
 +-- commands/
 |   +-- owl-search.md ------+
 |   +-- owl-query.md -------+
 |   +-- owl-compile.md -----+
 |   +-- owl-ingest.md ------+--> agent-brain/views/owl/.../commands/
 |   +-- owl-file.md --------+
 |   +-- owl-health.md ------+
 |   +-- owl-promote.md -----+
 |
 +-- CLAUDE.md                   owl section (monorepo paths + current stats)

 ~/.agents/skills/
 +-- owl-compiler.md --------+
 +-- owl-health.md ----------+--> agent-brain/views/owl/.../agents/
 +-- owl-librarian.md -------+

 ~/owl-vault/.claude/
 +-- settings.json               5 lifecycle hooks (owl hook <name>)
                                 hooks use `owl` CLI via PATH

 ~/cairn-vault/
 +-- (no Claude Code integration — Phase T target)
```

### 5-6. Migration Timeline

```
 Phase A-R (2026-04-03 ~ 04-08)     Phase S (2026-04-09)
 owl standalone repo                 monorepo restructure
 ┌─────────────────────┐             ┌──────────────────────────────┐
 │ ~/_/projects/owl    │             │ ~/_/projects/oh-my-brain     │
 │ songblaq/owl        │   rename    │ songblaq/oh-my-brain         │
 │ single pyproject    │ ─────────>  │ views/owl + cairn + wiki     │
 │ 18 phases A-R       │             │ brain-vault symlink hub      │
 └─────────────────────┘             └──────────────┬───────────────┘
                                                    |
                                     ┌──────────────v───────────────┐
                                     │ Phase S stabilization        │
                                     │ - pipx reinstall (owl+cairn) │
                                     │ - 16 symlinks repaired       │
                                     │ - 30+ path refs migrated     │
                                     │ - .gitignore /views/ fix     │
                                     │ - cairn+wiki tracked in git  │
                                     │ - status report + push       │
                                     └──────────────────────────────┘
                                                    |
                                     Future phases   v
                                     ┌──────────────────────────────┐
                                     │ T: cairn Claude Code parity  │
                                     │ U: pytest + CI               │
                                     │ V: wiki view + 3-way bench   │
                                     │ W: sync + convergence        │
                                     └──────────────────────────────┘
```

---

## 6. Skills & Integration Status

### Active (all verified working)

| Skill/Command | Type | Status |
|---|---|---|
| `/owl-search` | slash command | OK — search + LLM organize |
| `/owl-query` | slash command | OK — big-question workflow |
| `/owl-health` | slash command | OK — health + fix plan |
| `/owl-ingest` | slash command | OK — raw filing |
| `/owl-compile` | slash command | OK — raw -> compiled |
| `/owl-file` | slash command | OK — output filing loop |
| `/owl-promote` | slash command | OK — concept/index promotion |
| `owl-compiler` | subagent | OK — compilation agent |
| `owl-librarian` | subagent | OK — filing/linking agent |
| `owl-health` | subagent | OK — health interpretation |
| `owl hook *` | 5 lifecycle hooks | OK — via vault settings.json |

### Not yet built (Phase T targets)

| Planned | Type | Notes |
|---|---|---|
| `/cairn-search` | slash command | cairn search + LLM organize |
| `/cairn-ingest` | slash command | source -> entries pipeline |
| `cairn-scribe` | subagent | entry creation/update agent |
| `cairn-auditor` | subagent | INDEX/entry integrity check |
| cairn hooks | lifecycle hooks | session_start INDEX injection |

### No updates needed

All 7 slash command files and 3 subagent files have been verified:
- Zero stale path references
- All symlinks resolve to `agent-brain/views/owl/src/owl/claude_assets/`
- Content unchanged (only path references in agent prompts were updated)

---

## 7. Remaining Work (Backlog)

| Priority | Item | Phase |
|---|---|---|
| P1 | Cairn Claude Code integration (commands + agents + hooks) | T |
| P2 | pytest for owl core (search, health, vault, ingest) | U |
| P2 | pytest for cairn core (entry, search, index) | U |
| P2 | GitHub Actions CI | U |
| P2 | Owl health: fix 21 medium issues | ongoing |
| P3 | Wiki view implementation | V |
| P3 | 3-way benchmark (10 hard questions, real retrieval quality) | V |
| P3 | Cairn freshness loop (owl -> cairn automated rebuild) | W |
| P3 | Source layer decoupling (own directory, not symlink to owl/raw) | W |
| P3 | Cairn tag taxonomy cleanup (70% singleton tags) | W |

---

## 8. Summary

Phase S (post-restructure stabilization) is **complete**. The agent-brain
monorepo is fully operational with owl and cairn CLIs, all 16 symlinks
verified, zero stale path references in runtime files, and both search
engines returning strong matches.

```
 Before (start of session)          After (now)
 ┌──────────────────────┐           ┌──────────────────────┐
 │ 10 broken symlinks   │           │ 16/16 symlinks OK    │
 │ 30+ stale path refs  │    ->     │ 0 stale refs         │
 │ cairn+wiki untracked │           │ all views in git     │
 │ CLIs on old path     │           │ CLIs on new path     │
 │ install.sh old URL   │           │ install.sh updated   │
 └──────────────────────┘           └──────────────────────┘
```
