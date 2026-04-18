#!/usr/bin/env python3
"""Experiment A — migrate an akasha vault in place.

Steps:
  1. Rename entries to `<YYYY-MM-DD>-<topic>-<slug>.md` canonical form.
     - `lattice-<hash>-<rest>.md` → pull date from frontmatter `created:`, drop hash.
     - `<topic>--<date>-<rest>.md` → `<date>-<topic>-<rest>.md` (merge double-dash).
     - Keep already-canonical names.
  2. Rewrite frontmatter `id:` to match new stem.
  3. Fix `source:` paths: relative `sources/X` → absolute `~/omb/input/X` when the file exists there,
     or mark as `source_orphan: true` with original path preserved in `source:`.
  4. Symlink `<vault>/sources` → `~/omb/input` so the relative form resolves.
  5. Leave supersedes/graph untouched — that needs LLM judgment, not mechanical migration.

Idempotent: rerunning on a migrated vault is a no-op.
"""
from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path


FM_RE = re.compile(r"^(---\n)(.*?)(\n---\n)", re.DOTALL)
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
SLUG_CHARS = re.compile(r"[^a-z0-9-]+")


def read_frontmatter(text: str) -> tuple[str, str, str]:
    m = FM_RE.match(text)
    if not m:
        return "", "", text
    return m.group(1), m.group(2), text[m.end():]


def parse_fm_fields(fm: str) -> dict:
    d: dict = {}
    for line in fm.splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        d[k.strip()] = v.strip()
    return d


def rewrite_fm_field(fm: str, key: str, value: str) -> str:
    lines = fm.splitlines()
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


def slugify(s: str) -> str:
    s = s.lower()
    s = SLUG_CHARS.sub("-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def plan_rename(path: Path, fields: dict) -> str | None:
    name = path.name
    stem = path.stem

    # already canonical
    if re.match(r"^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*$", stem):
        return None

    created = fields.get("created", "")
    date_match = DATE_RE.search(stem) or DATE_RE.search(created)
    date_str = date_match.group(0) if date_match else fields.get("created", "")
    if not DATE_RE.match(date_str or ""):
        # fallback to file mtime date
        import datetime
        date_str = datetime.date.fromtimestamp(path.stat().st_mtime).isoformat()

    # lattice-<hash>-<rest>
    if stem.startswith("lattice-"):
        # strip lattice- prefix, optionally 8-hex-hash, re-attach date + rest
        rest = stem[len("lattice-"):]
        rest = re.sub(r"^[0-9a-f]{8}-", "", rest)
        rest = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", rest)  # remove embedded date if present
        slug = slugify(rest)
        return f"{date_str}-{slug}.md"

    # <topic>--<date>-<rest>
    m = re.match(r"^([a-z][a-z0-9-]*)--(\d{4}-\d{2}-\d{2})-(.+)$", stem)
    if m:
        topic, dt, rest = m.groups()
        # dedupe topic prefix if rest already contains it
        if rest.startswith(topic + "-"):
            rest = rest[len(topic) + 1:]
        slug = slugify(f"{topic}-{rest}")
        return f"{dt}-{slug}.md"

    # other patterns — just prepend date + slugify the rest
    slug = slugify(stem)
    # if stem already begins with a date, keep it
    if DATE_RE.match(stem):
        return f"{slug}.md"
    return f"{date_str}-{slug}.md"


def migrate_source_link(vault: Path, fields: dict) -> str:
    src = fields.get("source", "").strip()
    if not src:
        return ""
    if src.startswith("sources/"):
        rel = src[len("sources/"):]
        real = Path(os.path.expanduser("~/omb/input")) / rel
        if real.exists():
            return f"~/omb/input/{rel}"
    return src  # leave unchanged if unresolvable


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: migrate_a.py <vault-path> [--dry-run]")
        return 1
    vault = Path(os.path.expanduser(argv[1])).resolve()
    dry = "--dry-run" in argv
    entries_dir = vault / "entries"
    if not entries_dir.exists():
        print(f"no entries/ in {vault}", file=sys.stderr)
        return 2

    renames: list[tuple[Path, Path]] = []
    rewrites = 0
    source_fixed = 0
    skipped = 0

    for p in sorted(entries_dir.glob("*.md")):
        text = p.read_text(encoding="utf-8")
        open_tag, fm, body = read_frontmatter(text)
        if not fm:
            skipped += 1
            continue
        fields = parse_fm_fields(fm)
        new_name = plan_rename(p, fields)

        # always rewrite source link
        new_source = migrate_source_link(vault, fields)
        fm_new = fm
        if new_source and new_source != fields.get("source", ""):
            fm_new = rewrite_fm_field(fm_new, "source", new_source)
            source_fixed += 1

        if new_name and new_name != p.name:
            new_id = Path(new_name).stem
            fm_new = rewrite_fm_field(fm_new, "id", new_id)

        if fm_new != fm:
            if not dry:
                p.write_text(open_tag + fm_new + "\n---\n" + body, encoding="utf-8")
            rewrites += 1

        if new_name and new_name != p.name:
            dest = entries_dir / new_name
            if dest.exists() and dest != p:
                # collision — append short hash
                import hashlib
                h = hashlib.md5(p.stem.encode()).hexdigest()[:4]
                dest = entries_dir / (dest.stem + f"-{h}.md")
            renames.append((p, dest))

    for src, dest in renames:
        if dry:
            continue
        src.rename(dest)

    # symlink sources → ~/omb/input
    sources_link = vault / "sources"
    target = Path(os.path.expanduser("~/omb/input"))
    if not sources_link.exists():
        if not dry:
            sources_link.symlink_to(target)

    print(f"vault: {vault}")
    print(f"  renames planned: {len(renames)}")
    print(f"  frontmatter rewrites: {rewrites}")
    print(f"  source links fixed: {source_fixed}")
    print(f"  skipped (no frontmatter): {skipped}")
    print(f"  sources symlink: {'would create' if dry else 'created'} → ~/omb/input")
    if dry:
        print("  [dry-run — no files changed]")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
