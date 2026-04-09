---
id: wiki-view-spec-v0
status: planned
created: 2026-04-09
---

# wiki view — pure Karpathy specification

## Intent

The wiki view implements Andrej Karpathy's LLM Wiki pattern (2026)
exactly as described, with zero additions. No CLI, no health checks,
no install flow, no multi-machine sync, no custom metadata. The LLM
reads sources and maintains the wiki via the filing loop. Period.

This is an intentional **control group** — by running pure Karpathy
alongside owl (Karpathy + ops) and cairn (atomic departure), we can
measure exactly what owl's operational infrastructure adds and what
cairn's structural departure gains.

## The Karpathy method (verbatim)

1. Human drops source material into raw/
2. LLM reads raw, writes compiled docs (summary, note, concept,
   index, report)
3. Human asks questions; LLM answers using compiled docs
4. Good answers get filed back as new compiled docs (filing loop)
5. Repeat — wiki grows from both ingestion and exploration

## Directory structure

```
brain-vault/wiki/
├── raw/        (symlinked or copied from brain-vault/sources/)
└── compiled/   (LLM-generated: summary, note, concept, index, report)
```

## Compiled doc format

Plain markdown. Karpathy's gist specifies these types:
- **summary** — condensed version of a source
- **note** — observation, insight, or connection
- **concept** — definition of a term or idea
- **index** — directory of related docs
- **report** — analysis or comparison

Each compiled doc has a simple header:

```markdown
# <Title>

상태: compiled
유형: summary|note|concept|index|report
출처: raw/<source-filename>
작성일: YYYY-MM-DD
관련 항목: tag1, tag2, tag3
```

No YAML frontmatter. No machine-readable schema. The LLM reads
natural language headers because it can.

## What wiki does NOT have

- CLI tool (use grep/find to search, or ask the LLM)
- Health checks (no enforcement — if the wiki degrades, that's data)
- Install script
- Multi-machine sync (single vault, single machine)
- Atomic decomposition (documents stay as documents)
- INDEX.md session entry point (the LLM navigates by reading)
- Slash commands or subagents
- Frontmatter schema validation

## Search

Manual: `grep -rl "<query>" brain-vault/wiki/compiled/`

Or: ask the LLM to search the wiki directory during a session.

No ranked results, no scoring, no snippets. The LLM IS the
search engine.

## How to populate

Not yet implemented. When ready:
1. Symlink or copy brain-vault/sources/ → brain-vault/wiki/raw/
2. Start an LLM session and ask it to compile each raw source
3. Let the filing loop run naturally from exploration
4. Compare resulting wiki against owl and cairn after 1 week

## Benchmark role

Wiki is the baseline. If owl beats wiki, the ops infrastructure
earns its complexity. If cairn beats wiki, the atomic format
earns its departure from Karpathy. If wiki beats both, simplicity
wins and the other views are over-engineered.
