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

**Step 1 — Install**

```bash
curl -fsSL https://raw.githubusercontent.com/songblaq/oh-my-brain/main/plugin/scripts/bootstrap.sh | bash
```

**Step 2 — Verify**

```bash
omb status
```

**Step 3 — Search**

```bash
omb search "what is PLF"
```

That's it. Your LLM now has access to your personal knowledge vault.

---

## Install

| Method | Command | Best for |
|--------|---------|----------|
| **curl** | `curl -fsSL .../bootstrap.sh \| bash` | New machine, fastest |
| **Claude Code plugin** | `/plugin marketplace add https://github.com/songblaq/oh-my-brain` → `/plugin install oh-my-brain` → `/omb:setup` | Already using Claude Code |
| **Manual clone** | `git clone ... && bash plugin/scripts/install.sh` | Development / customization |

> **Note:** The `/plugin install` method registers skills automatically, but requires `/omb:setup` to install Python packages (pipx). This is the same "install → setup" pattern as oh-my-claudecode.

### Update

```bash
# Via skill (recommended)
/omb:update

# Or directly
git -C ~/omb/oh-my-brain pull && bash ~/omb/oh-my-brain/plugin/scripts/install.sh
```

---

## Runtime Support

oh-my-brain installs into every supported runtime automatically during `install.sh`.

| Runtime | Integration | Install method | Skills |
|---------|-------------|----------------|--------|
| **Claude Code** | `~/.agents/skills/` symlinks + `CLAUDE.md` block | `/plugin install` or `curl` | ✅ 6 skills |
| **Codex CLI** | Shared `~/.agents/skills/` + `CLAUDE.md` | Same plugin cache | ✅ 6 skills |
| **OpenCode** | Shared `~/.agents/skills/` symlinks | `curl` / `install.sh` | ✅ 6 skills |
| **Gemini CLI** | `gemini extensions install` + `GEMINI.md` | `curl` / `install.sh` | ✅ 6 skills |
| **OpenClaw** | `openclaw plugins install` (Node.js) | `curl` / `install.sh` | ✅ 4 tools* |
| **Hermes** | `~/.hermes/skills/knowledge/` symlinks | `curl` / `install.sh` | ✅ 6 skills |
| GitHub Copilot | ❌ | no user plugin system | — |

> \*OpenClaw exposes search/ingest/health/status as tools. compile/setup/update are multi-step LLM workflows and run as skills only.

### Manual runtime install

```bash
# Gemini CLI
gemini extensions install ~/omb/oh-my-brain/plugins/gemini

# OpenClaw
openclaw plugins install ~/omb/oh-my-brain/plugins/openclaw

# Hermes — symlink skills into the knowledge category
mkdir -p ~/.hermes/skills/knowledge
for s in ~/omb/oh-my-brain/skills/omb-*/; do
  ln -sfn "$s" ~/.hermes/skills/knowledge/"$(basename "$s")"
done
```

---

## Skills

Invoke skills from within any supported agent session:

| Skill | Trigger | What it does |
|-------|---------|--------------|
| `/omb:search` | "omb search", "브레인 검색" | 3-layer vault search → read top results → answer with evidence |
| `/omb:ingest` | "omb ingest", "브레인에 추가" | Ingest file or text → rebuild index |
| `/omb:health` | "omb health", "커버리지 확인" | Source coverage report → suggest next ingestion |
| `/omb:compile` | "omb compile", "컴파일" | Pick pending topic → dump entries → LLM writes narrative |
| `/omb:setup` | "omb 설치", "setup omb" | Install/reinstall everything (pipx + vault + skills) |
| `/omb:update` | "omb update", "브레인 업데이트" | `git pull` → reinstall what changed → report |

### Default reflex

When you ask a knowledge question, the LLM searches the vault *before* answering:

```
question → omb search → read compiled/<topic>.md → answer with evidence
                      → if no match: answer from training + suggest omb ingest
```

---

## CLI

```bash
omb status               # vault overview
omb search "<query>"     # 3-layer search (compiled + entries + graph)
omb ingest <file>        # add a file to vault
omb ingest --text "..."  # add raw text
omb health               # source coverage check
```

Internal vault engine (for maintenance):

```bash
akasha compile --dry-run          # show pending topics
akasha compile --dump <topic>     # dump entries → LLM writes compiled/<topic>.md
akasha index                      # rebuild INDEX.md + GRAPH.tsv
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
  skills/          shared skills (all runtimes via symlinks)
  plugins/
    openclaw/      OpenClaw plugin (Node.js, register(api))
    gemini/        Gemini extension (gemini-extension.json)
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
