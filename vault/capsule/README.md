# capsule

`capsule` is the read-only compiled bundle view for OMB.

- Input: `~/omb/source/<product>/`
- Output: `~/omb/vault/capsule/<product>/`
- Purpose: package product docs into agent-friendly bundles without creating writable brain artifacts

Unlike `akasha`, Capsule does not maintain entries, compiled narratives, or a graph. It builds delivery bundles such as:

- `pages/**`
- `ATLAS.md`
- `llms.txt`
- `ctx/**`
- `meta/pages.json`
- `manifest.json`

Capsule is a sibling view to Akasha, not a replacement for it.
