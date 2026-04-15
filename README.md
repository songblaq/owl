# oh-my-brain (omb)

[![version](https://img.shields.io/badge/version-0.1.0-blue)](https://github.com/songblaq/oh-my-brain/releases)
[![python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![runtimes](https://img.shields.io/badge/runtimes-Claude%20Code%20%7C%20Codex%20%7C%20OpenCode%20%7C%20OpenClaw%20%7C%20Hermes%20%7C%20Gemini-blueviolet)](#runtime-support)

**Personal LLM-maintained knowledge system.**

Raw materials go in — the LLM organizes them into a searchable, compiled vault. Designed so the LLM is the primary writer *and* reader.

Single active vault: **akasha** — atomic entries + compiled narratives + concept graph.

---

## Quick Start

**1. Install**

```bash
curl -fsSL https://raw.githubusercontent.com/songblaq/oh-my-brain/main/plugin/scripts/bootstrap.sh | bash
```

**2. Verify**

```bash
omb status
```

**3. Search**

```bash
omb search "what is PLF"
```

---

## Install

### Option A — One-liner (new machine)

```bash
curl -fsSL https://raw.githubusercontent.com/songblaq/oh-my-brain/main/plugin/scripts/bootstrap.sh | bash
```

Prerequisites: `git`, `python3`, `pipx`. On macOS:

```bash
brew install pipx
pipx ensurepath
```

### Option B — Claude Code plugin

```bash
/plugin marketplace add https://github.com/songblaq/oh-my-brain
```

```bash
/plugin install oh-my-brain
```

```bash
/omb:setup
```

> `/plugin install` registers skills automatically. `/omb:setup` installs Python packages via pipx.

### Option C — Manual clone

```bash
git clone https://github.com/songblaq/oh-my-brain.git ~/omb/oh-my-brain
```

```bash
bash ~/omb/oh-my-brain/plugin/scripts/install.sh
```

### Update

Via skill (recommended):

```bash
/omb:update
```

Or directly:

```bash
git -C ~/omb/oh-my-brain pull
```

```bash
bash ~/omb/oh-my-brain/plugin/scripts/install.sh
```

### Uninstall

```bash
bash ~/omb/oh-my-brain/plugin/scripts/uninstall.sh
```

---

## Runtime Support

`install.sh` detects and installs into all available runtimes automatically.

| Runtime | Integration | Skills |
|---------|-------------|--------|
| **Claude Code** | `~/.agents/skills/` symlinks + `CLAUDE.md` block | 6 skills |
| **Codex CLI** | Shared `~/.agents/skills/` + `CLAUDE.md` | 6 skills |
| **OpenCode** | `~/.agents/skills/` symlinks | 6 skills |
| **Gemini CLI** | `gemini extensions install` + `GEMINI.md` | 6 skills |
| **OpenClaw** | `openclaw plugins install` | 4 tools |
| **Hermes** | `hermes skills install` per skill | 6 skills |

### Manual runtime install

Gemini CLI:

```bash
gemini extensions install ~/omb/oh-my-brain/plugins/gemini
```

OpenClaw:

```bash
openclaw plugins install ~/omb/oh-my-brain/plugins/openclaw
```

Hermes (one per skill):

```bash
hermes skills install ~/omb/oh-my-brain/plugins/hermes/skills/omb-search
```

```bash
hermes skills install ~/omb/oh-my-brain/plugins/hermes/skills/omb-ingest
```

```bash
hermes skills install ~/omb/oh-my-brain/plugins/hermes/skills/omb-health
```

```bash
hermes skills install ~/omb/oh-my-brain/plugins/hermes/skills/omb-compile
```

```bash
hermes skills install ~/omb/oh-my-brain/plugins/hermes/skills/omb-setup
```

```bash
hermes skills install ~/omb/oh-my-brain/plugins/hermes/skills/omb-update
```

OpenCode — add to `~/.config/opencode/opencode.json`:

```json
{
  "plugin": ["~/omb/oh-my-brain/plugins/opencode"]
}
```

---

## Skills

| Skill | Trigger | What it does |
|-------|---------|--------------|
| `/omb:search` | "omb search", "브레인 검색" | 3-layer vault search, read top results, answer with evidence |
| `/omb:ingest` | "omb ingest", "브레인에 추가" | Ingest file or text, rebuild index |
| `/omb:health` | "omb health", "커버리지 확인" | Source coverage report, suggest next ingestion |
| `/omb:compile` | "omb compile", "컴파일" | Pick pending topic, dump entries, LLM writes narrative |
| `/omb:setup` | "omb 설치", "setup omb" | Install/reinstall everything (pipx + vault + skills) |
| `/omb:update` | "omb update", "브레인 업데이트" | git pull, reinstall what changed, report |

### Default reflex

When you ask a knowledge question, the LLM searches the vault *before* answering:

```
question → omb search → read compiled/<topic>.md → answer with evidence
                      → if no match: answer from training + suggest omb ingest
```

---

## CLI

### omb (public interface)

```bash
omb status
```

```bash
omb search "transformer architecture"
```

```bash
omb ingest ~/Documents/paper.pdf
```

```bash
omb ingest --text "PLF stands for Product-Led Flywheel"
```

```bash
omb health
```

### akasha (vault engine, for maintenance)

```bash
akasha compile --dry-run
```

```bash
akasha compile --dump transformer-architecture
```

```bash
akasha index
```

---

## Architecture

```
~/omb/
  source/          raw inputs (immutable — read-only after ingestion)
  vault/akasha/    active vault
    entries/       atomic knowledge units (~500 tokens each)
    compiled/      LLM-written narrative docs (by topic)
    INDEX.md       master index (auto-generated)
    GRAPH.tsv      concept graph (topic/concept edges)
    ALIASES.tsv    surface form → canonical name map

oh-my-brain/       this repo (code + specs)
  vault/omb/       omb CLI (public interface)
  vault/akasha/    akasha vault engine (11 modules)
  skills/          shared skills (Claude Code / Codex / OpenCode / Gemini)
  plugins/
    openclaw/      OpenClaw plugin (Node.js, register(api))
    hermes/        Hermes skills (extended SKILL.md frontmatter)
    gemini/        Gemini extension (gemini-extension.json)
    opencode/      OpenCode plugin package
  plugin/          install scripts + context files
    CLAUDE.md      global context (Claude Code / Codex)
    scripts/
      bootstrap.sh   curl one-liner
      install.sh     full install (all runtimes)
      uninstall.sh
  GEMINI.md        global context (Gemini CLI)
  .claude-plugin/  Codex manifest
  docs/            specs and design notes
```

### 3-Layer Search

```
omb search "<query>"
  Layer 1: compiled/*.md     TF-IDF on narrative docs (fast, broad)
  Layer 2: entries/*.md      TF-IDF + alias resolution (atomic claims)
  Layer 3: GRAPH.tsv         1-hop expansion from top-3 hits
```

---

## Design Principles

1. **Raw = immutable** — source files are never modified after ingestion
2. **LLM is the writer** — entries and compiled docs are written by LLM, not curated manually
3. **Vault = data only** — no code inside the vault directories
4. **Evidence with records** — entries include why + alternatives, not just conclusions
5. **Rebuildable** — delete vault, re-ingest sources, get equivalent result

---

## License

MIT
