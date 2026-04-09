# oh-my-brain (omb)

Personal LLM-maintained knowledge system. Multiple **views** (strategies)
over a shared **source** corpus — each view manages the same knowledge
differently so their strengths can be compared and combined.

Unified CLI: `omb` wraps all views under one command.

## Architecture

```
brain-vault/                     (data home — ~/brain-vault)
├── sources/     → owl-vault/raw (shared immutable source pool)
├── owl/         → owl-vault     (owl view — LLM wiki + ops infra)
├── cairn/       → cairn-vault   (cairn view — atomic claims + INDEX)
└── wiki/                        (wiki view — pure Karpathy, no tooling)

oh-my-brain/                     (this repo — code + specs + benchmarks)
├── views/
│   ├── omb/                     (omb CLI: unified entry point)
│   ├── owl/                     (owl CLI: owl search, owl health, ...)
│   ├── cairn/                   (cairn CLI: cairn search, cairn index, ...)
│   └── wiki/                    (no CLI — LLM IS the tool)
├── docs/                        (umbrella specs + benchmarks)
└── README.md
```

## Views

### owl

Karpathy LLM Wiki (2026) implementation with operational infrastructure:
health checks, install flow, Obsidian integration, multi-machine sync
via WebDAV, slash commands, subagents.

- **Format:** raw/ + compiled/ (summary, note, concept, index, report)
- **CLI:** `owl` (pipx install)
- **Vault:** `~/owl-vault`

### cairn

LLM-first atomic knowledge base. Flat directory, one claim per file,
INDEX.md as session entry point, parallel write-friendly.

- **Format:** entries/ (YAML frontmatter + ~400 token atomic claims)
- **CLI:** `cairn` (pipx install)
- **Vault:** `~/cairn-vault`

### wiki (planned)

Pure Karpathy method — no CLI, no health checks, no ops layer. The LLM
reads sources and maintains raw/ + compiled/ via the filing loop described
in Karpathy's original gist. Intentional control group.

- **Format:** raw/ + compiled/ (Karpathy spec, no owl extensions)
- **CLI:** none
- **Vault:** `~/brain-vault/wiki/`

## Shared sources

`brain-vault/sources/` holds the immutable original materials that all
views can read from. No view writes to sources/. New material enters
here first, then each view ingests it in its own way.

Currently symlinked to `owl-vault/raw/` (125 files including the atlas
external reference subtree). Will decouple to its own directory when
the source layer matures.

## Benchmarks

See `docs/` for benchmark reports comparing views across 6 dimensions:
storage density, retrieval speed, search quality, session startup,
write throughput, and write ergonomics.

## Install

```bash
# omb (unified CLI — recommended)
cd views/omb && pipx install -e .

# individual views (also available via omb owl/cairn)
cd views/owl && pipx install -e .
cd views/cairn && pipx install -e .

# wiki — no install needed
```

## License

MIT
