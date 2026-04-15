# oh-my-brain (omb)

Personal LLM-maintained knowledge system.
Unified CLI `omb` wraps the vault engine under a single entry point.

## Architecture

```
.omb/                            (data home — ~/.omb)
├── source/                      (shared immutable source pool)
└── vault/                       (akasha — LLM-managed knowledge)

oh-my-brain/                     (this repo — code + specs)
├── vault/
│   ├── omb/                     (omb CLI: unified entry point)
│   └── akasha/                  (vault engine: ingest, search, health)
└── docs/                        (specs + roadmap)
```

## Install

```bash
# vault engine
cd vault/akasha && pipx install -e .

# unified CLI (recommended)
cd vault/omb && pipx install -e .
```

## Usage

```bash
omb status               # vault overview
omb search "<query>"     # search knowledge
omb ingest <file>        # add to vault
omb health               # source coverage check
```

## License

MIT
