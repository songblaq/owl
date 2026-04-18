"""Vault operations that enforce Tier 0 integrity invariants.

These are implemented at the omb layer (not delegated to akasha) because
they encode priorities that must survive even if the underlying view changes:

  P0.1 Truth singularity — supersede physically moves old entries
  P0.2 Traceability — source: field must resolve
  P1.2 Health fails loudly — violations surface explicitly

See docs/priorities.md and docs/ingest-contract-v2.md.
"""
from __future__ import annotations

import os
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path


FM_RE = re.compile(r"^(---\n)(.*?)(\n---\n)", re.DOTALL)
SOURCE_ROOT = Path(os.path.expanduser("~/omb/source"))


def active_vault() -> Path | None:
    pointer = Path(os.path.expanduser("~/.config/akasha/active-vault"))
    if pointer.exists():
        p = Path(pointer.read_text().strip()).expanduser()
        if p.exists():
            return p
    default = Path(os.path.expanduser("~/omb/bench/akasha"))
    return default if default.exists() else None


def parse_fm(path: Path) -> tuple[str, dict, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return "", {}, ""
    m = FM_RE.match(text)
    if not m:
        return "", {}, text
    fm_text = m.group(2)
    body = text[m.end():]
    fields: dict = {}
    for line in fm_text.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fields[k.strip()] = v.strip()
    return fm_text, fields, body


def write_fm(path: Path, fm_text: str, body: str) -> None:
    path.write_text("---\n" + fm_text + "\n---\n" + body, encoding="utf-8")


def rewrite_field(fm_text: str, key: str, value: str) -> str:
    lines = fm_text.splitlines()
    out = []
    seen = False
    for line in lines:
        if line.startswith(f"{key}:"):
            out.append(f"{key}: {value}")
            seen = True
        else:
            out.append(line)
    if not seen:
        out.append(f"{key}: {value}")
    return "\n".join(out)


def _resolve_source(src: str, vault: Path) -> Path | None:
    if not src:
        return None
    if src.startswith("~/"):
        return Path(os.path.expanduser(src))
    if src.startswith("/"):
        return Path(src)
    if src.startswith("sources/"):
        return vault / src
    return vault / src


# ── Supersede (P0.1) ──────────────────────────────────────────────────────────

def supersede(new_id: str, old_ids: list[str]) -> int:
    """Move `old_ids` into superseded/, record chain in `new_id`'s frontmatter.

    Enforces P0.1 (Truth singularity): the old entries are physically removed
    from entries/ so search cannot return them as current truth.
    """
    vault = active_vault()
    if vault is None:
        print("omb: no active vault", file=sys.stderr)
        return 2

    entries = vault / "entries"
    superseded = vault / "superseded"
    superseded.mkdir(exist_ok=True)

    new_path = entries / f"{new_id}.md"
    if not new_path.exists():
        print(f"omb supersede: new entry not found: {new_id}", file=sys.stderr)
        return 2

    missing = [oid for oid in old_ids if not (entries / f"{oid}.md").exists()]
    if missing:
        print(f"omb supersede: old entries not found: {', '.join(missing)}", file=sys.stderr)
        return 2

    # 1) update new entry's supersedes field
    fm, fields, body = parse_fm(new_path)
    existing_sup = fields.get("supersedes", "[]").strip("[]").strip()
    existing_list = [s.strip() for s in existing_sup.split(",") if s.strip()] if existing_sup else []
    merged = sorted(set(existing_list + old_ids))
    new_fm = rewrite_field(fm, "supersedes", "[" + ", ".join(merged) + "]")
    write_fm(new_path, new_fm, body)

    # 2) physically move old entries
    moved = []
    for oid in old_ids:
        src = entries / f"{oid}.md"
        dst = superseded / f"{oid}.md"
        if dst.exists():
            print(f"omb supersede: already in superseded/: {oid} — skipping", file=sys.stderr)
            continue
        shutil.move(str(src), str(dst))
        moved.append(oid)

    print(f"supersede: {new_id} now supersedes {len(moved)} entries")
    for oid in moved:
        print(f"  - moved {oid} → superseded/")
    print()
    print("note: run `akasha index` (or `omb status`) to rebuild INDEX/GRAPH.")
    return 0


# ── Audit (P0.1, P0.2, Tier-0 visibility) ─────────────────────────────────────

def audit() -> int:
    """Produce AUDIT.md with Tier 0 / Tier 1 violations.

    Does not mutate. Human reviewer decides per-violation action.
    """
    vault = active_vault()
    if vault is None:
        print("omb: no active vault", file=sys.stderr)
        return 2

    entries_dir = vault / "entries"
    if not entries_dir.exists():
        print(f"omb audit: no entries/ in {vault}", file=sys.stderr)
        return 2

    decision_groups: dict = defaultdict(list)
    broken_source: list = []
    orphan: list = []

    graph_ids: set = set()
    g = vault / "GRAPH.tsv"
    if g.exists():
        for line in g.read_text().splitlines():
            parts = line.split("\t")
            if parts and parts[0] and not parts[0].startswith("#"):
                for p in parts[:2]:
                    graph_ids.add(p)

    entry_ids: set = set()
    for p in sorted(entries_dir.glob("*.md")):
        fm, fields, body = parse_fm(p)
        if not fm:
            continue
        entry_ids.add(p.stem)
        etype = fields.get("type", "")
        topics = fields.get("topics", "").strip("[]")
        primary = topics.split(",")[0].strip() if topics else ""
        if etype == "decision" and primary:
            decision_groups[primary].append((p.name, fields.get("authored", fields.get("created", "")), fields.get("supersedes", "[]")))
        src = fields.get("source", "")
        resolved = _resolve_source(src, vault)
        if src and (resolved is None or not resolved.exists()):
            broken_source.append((p.name, src))

    for eid in sorted(entry_ids):
        if eid not in graph_ids:
            orphan.append(eid)

    superseded_dir = vault / "superseded"
    superseded_count = len(list(superseded_dir.glob("*.md"))) if superseded_dir.exists() else 0

    lines: list = []
    lines.append(f"# AUDIT — {vault.name}")
    lines.append("")
    lines.append("Generated by `omb audit`. Tier 0 / Tier 1 violations (see docs/priorities.md).")
    lines.append("")

    # Tier 0 summary
    dup = {t: v for t, v in decision_groups.items() if len(v) >= 2}
    lines.append("## Tier 0 summary")
    lines.append("")
    lines.append(f"- P0.1 Truth singularity: **{len(dup)}** duplicate-decision topics, **{superseded_count}** entries in superseded/")
    lines.append(f"- P0.2 Traceability: **{len(broken_source)}** broken source links (of {len(entry_ids)} entries)")
    lines.append(f"- P2.3 Orphan entries: **{len(orphan)}** entries not in GRAPH.tsv")
    lines.append("")
    lines.append("## P0.1 Duplicate-decision candidates")
    lines.append("")
    for topic, rows in sorted(dup.items(), key=lambda x: -len(x[1])):
        lines.append(f"### {topic} ({len(rows)} entries)")
        for name, when, sup in sorted(rows, key=lambda r: r[1] or ""):
            marker = " ← supersedes chain present" if sup and sup != "[]" else ""
            lines.append(f"- `{name}` authored={when or '?'}{marker}")
        lines.append("")
        lines.append(f"→ suggested: `omb supersede <latest-id> --replaces <older-ids>`")
        lines.append("")
    lines.append("## P0.2 Broken source links")
    lines.append("")
    lines.append(f"Total: **{len(broken_source)}**. Either fix `source:` path or move the raw into `~/omb/source/`.")
    lines.append("")
    for name, src in broken_source[:50]:
        lines.append(f"- `{name}` → `{src}`")
    if len(broken_source) > 50:
        lines.append(f"- ... ({len(broken_source) - 50} more)")
    lines.append("")
    lines.append("## P2.3 Orphan entries (no graph edges)")
    lines.append("")
    lines.append(f"Total: **{len(orphan)}** of {len(entry_ids)}.")
    lines.append("")
    for eid in orphan[:30]:
        lines.append(f"- `{eid}`")
    if len(orphan) > 30:
        lines.append(f"- ... ({len(orphan) - 30} more)")
    lines.append("")

    out = vault / "AUDIT.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    print(f"  duplicate decision topics: {len(dup)}")
    print(f"  broken source links: {len(broken_source)}")
    print(f"  orphan entries: {len(orphan)}")
    print(f"  superseded/ population: {superseded_count}")
    return 0


# ── Audit JSON variant (T1-B) ─────────────────────────────────────────────────

def audit_json() -> dict:
    vault = active_vault()
    if vault is None:
        return {"error": "no active vault"}
    entries_dir = vault / "entries"
    if not entries_dir.exists():
        return {"error": f"no entries/ in {vault}"}

    decision_groups: dict = defaultdict(list)
    broken_source: list = []
    entry_ids: set = set()
    graph_ids: set = set()

    g = vault / "GRAPH.tsv"
    if g.exists():
        for line in g.read_text().splitlines():
            parts = line.split("\t")
            if parts and parts[0] and not parts[0].startswith("#"):
                for p in parts[:2]:
                    graph_ids.add(p)

    for p in sorted(entries_dir.glob("*.md")):
        _, fields, _ = parse_fm(p)
        if not fields:
            continue
        entry_ids.add(p.stem)
        etype = fields.get("type", "")
        topics = fields.get("topics", "").strip("[]")
        primary = topics.split(",")[0].strip() if topics else ""
        if etype == "decision" and primary:
            decision_groups[primary].append(p.name)
        src = fields.get("source", "")
        resolved = _resolve_source(src, vault)
        if src and (resolved is None or not resolved.exists()):
            broken_source.append({"entry": p.name, "source": src})

    orphan = sorted([eid for eid in entry_ids if eid not in graph_ids])
    superseded_dir = vault / "superseded"
    superseded_count = len(list(superseded_dir.glob("*.md"))) if superseded_dir.exists() else 0
    duplicate_groups = {t: v for t, v in decision_groups.items() if len(v) >= 2}

    return {
        "vault": str(vault),
        "entries": len(entry_ids),
        "duplicate_topics": len(duplicate_groups),
        "duplicate_detail": duplicate_groups,
        "broken_source_count": len(broken_source),
        "broken_source_sample": broken_source[:20],
        "orphan_count": len(orphan),
        "orphan_sample": orphan[:20],
        "superseded_count": superseded_count,
    }


# ── Rebuild (T1-C) skeleton ───────────────────────────────────────────────────

def rebuild_plan() -> int:
    source_root = Path(os.path.expanduser("~/omb/source"))
    if not source_root.exists():
        print(f"no source at {source_root}", file=sys.stderr)
        return 2
    sources = sorted(source_root.rglob("*.md"))
    rc_path = Path(os.path.expanduser("~/omb/bench/sandbox/akasha-rc1"))
    print(f"rebuild plan (dry-run)")
    print(f"  source root: {source_root}")
    print(f"  sources:     {len(sources)}")
    print(f"  target rc:   {rc_path}")
    print(f"  already exists: {rc_path.exists()}")
    print()
    print(f"  not yet implemented — requires LLM calls for C3 evidence + C4 pre-write search.")
    print(f"  MVP: use `omb rebuild --apply` to skeleton empty rc; manual ingest for now.")
    return 0


def rebuild_apply() -> int:
    rc_path = Path(os.path.expanduser("~/omb/bench/sandbox/akasha-rc1"))
    if rc_path.exists():
        print(f"rebuild abort: {rc_path} already exists. remove first.", file=sys.stderr)
        return 2
    (rc_path / "entries").mkdir(parents=True)
    (rc_path / "compiled").mkdir()
    (rc_path / "superseded").mkdir()
    (rc_path / ".akasha-vault").write_text("rc1\n")
    sources_link = rc_path / "sources"
    if not sources_link.exists():
        sources_link.symlink_to(Path(os.path.expanduser("~/omb/source")))
    print(f"created empty rc: {rc_path}")
    print(f"  next: ingest sources one by one through `omb ingest` + `omb validate`.")
    return 0


# ── Import normalize (I-A) skeleton ───────────────────────────────────────────

def import_normalize(path_str: str, normalize: bool) -> int:
    from omb.validator import validate_entry, Finding
    path = Path(os.path.expanduser(path_str)).resolve()
    if not path.exists():
        print(f"no such file: {path}", file=sys.stderr)
        return 2
    vault = active_vault()
    if vault is None:
        print("no active vault", file=sys.stderr)
        return 2
    findings: list[Finding] = validate_entry(path, vault)
    critical = [f for f in findings if f.severity == "critical"]
    if critical and not normalize:
        print(f"import rejected — {len(critical)} critical contract violations:")
        for f in critical:
            print(f"  [{f.rule}] {f.message}")
        print(f"\nuse `--normalize` to attempt fixes (not yet implemented) or fix manually.")
        return 1
    if critical and normalize:
        print(f"normalize requested but auto-fix not yet implemented. {len(critical)} violations remain.")
        return 1
    print(f"import OK: {path} passes contract v2 (no critical violations).")
    print(f"  next: move to {vault / 'entries' / path.name} manually, or wire ingest pipeline.")
    return 0


# ── Strict health (P1.2) ──────────────────────────────────────────────────────

def health_strict() -> int:
    """Fail loudly on Tier 0 violations. Returns non-zero if unhealthy."""
    vault = active_vault()
    if vault is None:
        print("omb health: no active vault", file=sys.stderr)
        return 2

    entries_dir = vault / "entries"
    entries = list(entries_dir.glob("*.md")) if entries_dir.exists() else []
    total = len(entries)

    broken = 0
    for p in entries:
        _, fields, _ = parse_fm(p)
        src = fields.get("source", "")
        resolved = _resolve_source(src, vault)
        if src and (resolved is None or not resolved.exists()):
            broken += 1

    superseded_dir = vault / "superseded"
    superseded_count = len(list(superseded_dir.glob("*.md"))) if superseded_dir.exists() else 0

    source_pct = (total - broken) / total * 100 if total else 0.0
    findings: list = []
    status = "healthy"

    if source_pct < 95.0:
        status = "critical"
        findings.append(f"CRITICAL P0.2 Traceability: source integrity {source_pct:.1f}% (target ≥ 95%). {broken} broken links.")

    if superseded_count == 0 and total > 100:
        if status != "critical":
            status = "warning"
        findings.append(f"WARNING P0.1 Truth singularity: superseded/ is empty despite {total} entries. Supersede discipline likely unused. Run `omb audit` to see candidates.")

    canonical_re = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z][a-z0-9-]*\.md$")
    non_canonical = sum(1 for p in entries if not canonical_re.match(p.name))
    naming_pct = (total - non_canonical) / total * 100 if total else 0.0
    if naming_pct < 95.0:
        if status == "healthy":
            status = "warning"
        findings.append(f"WARNING naming conformance: {naming_pct:.1f}% canonical (target ≥ 95%). {non_canonical} non-canonical.")

    print(f"akasha health (strict — Tier 0/1)")
    print(f"{'=' * 40}")
    print(f"  vault:          {vault}")
    print(f"  entries:        {total}")
    print(f"  source coverage:{source_pct:.1f}%")
    print(f"  superseded/:    {superseded_count}")
    print(f"  naming canonical:{naming_pct:.1f}%")
    print()
    print(f"  status: {status.upper()}")
    if findings:
        print()
        for f in findings:
            print(f"  {f}")
    else:
        print("  (no Tier 0/1 violations)")
    return 0 if status == "healthy" else 1
