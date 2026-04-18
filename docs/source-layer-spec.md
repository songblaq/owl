---
id: source-layer-spec-v0
status: draft
created: 2026-04-09
---

# Source layer specification

## What is a source?

A **source** is an immutable original document that enters the system
before any view processes it. Sources are the shared ground truth —
every view reads from them, no view writes to them.

## Location

`~/omb/source/`.

## Invariants

1. **Immutable.** Once a source is added, its content does not change.
   Corrections are added as new sources that supersede the old one.
2. **View-independent.** No source contains view-specific metadata
   (no owl headers, no cairn frontmatter). Sources are raw inputs.
3. **Complete.** Every piece of knowledge in any view must trace back
   to a source (or to a chain of sources). Views that generate new
   knowledge (filing loop, research reports) file the result back as
   a new source.
4. **Resolvable reference.** Any entry that references a source MUST
   use a path that resolves to an existing file under `~/omb/source/`.
   Accepted forms: absolute path (`~/omb/source/<file>`), or vault-relative
   via symlink (`<vault>/sources/<file>` where `sources` is a symlink to
   `~/omb/source`). Entries with unresolvable `source:` fields fail
   `omb health` (principle 7 in ATLAS).

## What counts as a source

- Transcripts (session logs, discord threads, meeting notes)
- External references (articles, gists, papers, documentation)
- Raw data (atlas knowledge pack, runtime configs, schema dumps)
- Filed outputs (research reports, analyses that become inputs for
  future views)

## What does NOT count as a source

- View-derived artifacts (owl's compiled/, cairn's entries/)
- Index/navigation files (cairn's INDEX.md, owl's CLAUDE.md)
- Tool configuration (pyproject.toml, install.sh)

## Source filename convention

Sources follow the originating system's naming — no enforced schema.
If the source comes from owl, it keeps owl's `YYYY-MM-DD-<slug>-raw.md`
pattern. If from an external system, it keeps whatever name it arrived
with. The source layer is not opinionated about filenames.

## Adding a new source

1. Drop the file into `~/omb/source/` (or the appropriate
   subdirectory)
2. Each view decides independently whether and how to ingest it
3. No automatic propagation — views pull on demand, not push

Examples:
- `akasha` ingests sources into writable knowledge artifacts
- `capsule` compiles sources into read-only delivery bundles
