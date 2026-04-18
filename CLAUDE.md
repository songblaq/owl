# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository

`oh-my-brain` (omb) — personal LLM-maintained knowledge system. This repo is the **code + spec**; the runtime data lives under `~/omb/` on the user's machine. The repo installs a CLI (`omb`) plus skills/plugins into multiple agent runtimes.

## Install / Dev

```bash
# full install (pipx packages + skills + runtime plugins)
bash plugin/scripts/install.sh

# reinstall a single Python package during development
cd vault/omb && pipx install -e . --force
cd vault/akasha && pipx install -e . --force
cd vault/capsule && pipx install -e . --force

# partial installs
bash plugin/scripts/install.sh --skills-only   # symlinks only
bash plugin/scripts/install.sh --claude-only   # CLAUDE.md patch only

# drift audit (run weekly — checks CLAUDE.md mappings × real paths × wiki deprecations)
bash tools/drift_audit.sh
```

No test suite or lint config is wired up. Verify changes by invoking the CLIs directly (`omb status`, `omb search "<q>"`, `akasha ...`, `capsule ...`).

## Architecture (big picture)

Three Python packages, one shell installer, skills shared across six agent runtimes.

**Runtime data layout** (`~/omb/`, created on install — not in this repo):

```
input/          raw inputs (immutable)
brain/
  live/         LLM-edited knowledge (Karpathy-style wiki: entities/ concepts/ sources/ syntheses/)
  readonly/     product capsule bundles (rebuilt from source)
bench/
  akasha/       prior-design backup (INACTIVE — access via `omb akasha <sub>` only)
  sandbox/      slot for future challenger vaults
```

**Repo layout**:

- `vault/omb/` — thin user-facing CLI (`omb`). Delegates to `akasha` and `capsule` via subprocess; defaults everything to the live wiki. Entry: `vault/omb/src/omb/cli.py`. Sub-modules: `wiki_ops.py` (primary), `vault_ops.py` (legacy akasha ops surfaced via `omb akasha …`), `validator.py`.
- `vault/akasha/` — INACTIVE legacy vault engine (atomic entries + compiled narratives + graph). Still installed for `omb akasha <sub>` access; never call directly in user-visible flows.
- `vault/capsule/` — read-only product-bundle engine (`omb capsule …`). Bundles are rebuilt from source, not edited.
- `skills/omb-*/` — six shared skills (search / ingest / health / compile / setup / update) symlinked into each runtime's skills dir during install.
- `plugins/gemini/`, `plugins/openclaw/` — runtime-specific plugin manifests.
- `plugin/CLAUDE.md` — the block patched into `~/.claude/CLAUDE.md` on install (global user context).
- `plugin/scripts/install.sh` — single source of truth for install across Claude Code, Codex, OpenCode, Gemini CLI, OpenClaw, Hermes.
- `tools/` — maintenance scripts (`drift_audit.sh`, `wiki_lint.py`, migration helpers).
- `docs/` — specs. `REZERO-2026-04-18.md` is the **active** design doc; most other docs carry `deprecated by docs/REZERO-2026-04-18.md` headers and are kept for history only.

**User-facing command surface** (`omb`):

- Default target is `brain/live` (the wiki). `omb search` auto-attaches matching capsule bundles from `brain/readonly/`.
- `omb akasha <sub>` is the only way to reach the legacy akasha engine.
- `omb capsule <sub>` drives the read-only bundle engine.
- The words `wiki`, `akasha`, `capsule` are **internal**: never surface them in `omb` output/help/errors. Folder names (`brain/live`, `brain/readonly`, `bench/`) are fine.

## Design rules (Re:Zero 2026-04-18)

These override older docs in `docs/` that still contain tier/contract/validator/supersede frameworks:

1. **source is immutable** — never modify files under `~/omb/input/` (legacy: `~/omb/source/`).
2. **wiki (`brain/live`) is MAIN** — LLM maintains it incrementally (Karpathy LLM-wiki model). No RAG pipeline.
3. **Don't stack automation beyond Karpathy's original** — no new tier/contract/enforcer layers. If a proposed feature isn't in the origin, push back before building.
4. **akasha & bench are INACTIVE** — results never flow into user-visible responses; backup/measurement only.
5. **Drift detection belongs in the design** — deprecations must be mirrored across (a) wiki entity page `status:`, (b) `~/.claude/CLAUDE.md` Korean-name mapping, (c) source. `tools/drift_audit.sh` verifies weekly.
6. **One place per fact** — version/contract/history live in `docs/` only; vault dirs contain data, not meta files like `VERSION.md`.

## Editing conventions

- Modifying `omb` behavior → edit `vault/omb/src/omb/*.py` then `pipx install -e . --force`.
- Adding/changing a skill → edit `skills/omb-<name>/SKILL.md`; the symlinks created by `install.sh` pick it up without reinstall.
- Changing the Claude Code global block → edit `plugin/CLAUDE.md` then rerun `install.sh --claude-only`. The block is delimited by `<!-- OMB:START -->` / `<!-- OMB:END -->`.
- When adding a deprecation, update all three drift points (wiki entity, CLAUDE.md mapping, any source reference) in the same commit so `drift_audit.sh` stays clean.

## 언어

모든 응답은 **한글**. 코드/주석은 영어 가능하지만, 사용자 대화·설명·커밋 메시지·에러 메시지는 한글로 작성한다.
