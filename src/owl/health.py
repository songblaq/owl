"""Vault health check — 8 integrity rules for the wiki.

This is the deterministic health primitive used by ``owl health`` and the
``owl-health`` subagent. The 8 rules implement ``docs/health-check-spec-v0.md``
and check for: missing summaries, missing related-item sections, broken output
links, concept candidates, index candidates, orphan concepts, stale indexes,
and weak backlinks.

The legacy ``src/brain_health_check.py`` is now a 3-line wrapper around
``cli()`` here, preserving the documented invocation.

Adds a ``--json`` mode (over the legacy script) so slash commands can pipe
results into LLM interpretation in a single turn.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set

from owl.vault import discover_vault

STOP_TERMS = {
    "owl",
    "OpenClaw",
    "Hermes",
    "Index",
    "Memory",
    "Profile",
    "Registry",
    "Summary",
    "Note",
    "Report",
    "Obsidian",
    "AGENTS.md",
    "USER.md",
}
BRAIN_LINK_RE = re.compile(r"(?:compiled|raw|outputs|views|research)/[^`\s)]*\.[A-Za-z0-9._-]+")


@dataclass
class Issue:
    rule: str
    severity: str
    path: Path
    detail: str


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""


def compiled_files(base: Path) -> List[Path]:
    root = base / "compiled"
    if not root.exists():
        return []
    return sorted([p for p in root.rglob("*.md") if p.is_file()])


def raw_files(base: Path) -> List[Path]:
    root = base / "raw"
    if not root.exists():
        return []
    return sorted([p for p in root.rglob("*.md") if p.is_file()])


def has_related_header(content: str) -> bool:
    return "관련 항목:" in content or "## 관련 자료" in content or "## 관련 항목" in content


def raw_to_summary_name(raw_path: Path) -> str:
    return raw_path.name.replace("-raw.md", "-summary.md")


def compiled_kind(content: str) -> str:
    match = re.search(r"^유형:\s*(.+)$", content, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def extract_related_terms(content: str) -> List[str]:
    match = re.search(r"^관련 항목:\s*(.+)$", content, flags=re.MULTILINE)
    if not match:
        return []
    raw = match.group(1).strip()
    parts = [p.strip().strip("`") for p in raw.split(",")]
    terms: List[str] = []
    for part in parts:
        if not part or "/" in part or ".md" in part:
            continue
        terms.append(part)
    return terms


def slugify(text: str) -> str:
    text = text.casefold()
    text = re.sub(r"[^a-z0-9가-힣]+", "-", text)
    return text.strip("-")


def base_subject_from_filename(path: Path) -> str:
    name = path.stem
    m = re.match(r"^\d{4}-\d{2}-\d{2}-(.+?)-(summary|note|report|concept|index)$", name)
    return m.group(1) if m else ""


def relative_path(base: Path, path: Path) -> str:
    return str(path.relative_to(base))


def extract_brain_links(content: str) -> List[str]:
    return BRAIN_LINK_RE.findall(content)


def existing_brain_paths(base: Path) -> Set[str]:
    paths: Set[str] = set()
    for root_name in ("compiled", "raw", "outputs", "views", "research"):
        root = base / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file():
                paths.add(relative_path(base, path))
    return paths


def check_missing_summaries(base: Path) -> List[Issue]:
    issues: List[Issue] = []
    compiled_names = {p.name for p in compiled_files(base)}
    for raw in raw_files(base):
        expected = raw_to_summary_name(raw)
        if expected not in compiled_names:
            issues.append(
                Issue(
                    rule="missing-summary-for-raw",
                    severity="high",
                    path=raw,
                    detail=f"expected compiled/{expected}",
                )
            )
    return issues


def check_missing_related(base: Path) -> List[Issue]:
    issues: List[Issue] = []
    for path in compiled_files(base):
        content = read_text(path)
        kind = compiled_kind(content)
        if kind in {"summary", "concept", "index", "report", "comparison"}:
            if not has_related_header(content):
                issues.append(
                    Issue(
                        rule="compiled-missing-related",
                        severity="medium",
                        path=path,
                        detail=f"type={kind} has no 관련 항목/관련 자료 section",
                    )
                )
    return issues


def extract_output_links(content: str) -> List[str]:
    return re.findall(r"outputs/[^`\s)]+", content)


def check_report_outputs(base: Path) -> List[Issue]:
    issues: List[Issue] = []
    for path in compiled_files(base):
        content = read_text(path)
        kind = compiled_kind(content)
        if kind != "report":
            continue
        links = extract_output_links(content)
        if not links:
            issues.append(
                Issue(
                    rule="report-missing-output-links",
                    severity="medium",
                    path=path,
                    detail="report has no outputs/* links",
                )
            )
            continue
        for rel in links:
            target = base / rel
            if not target.exists():
                issues.append(
                    Issue(
                        rule="report-broken-output-link",
                        severity="high",
                        path=path,
                        detail=f"missing target: {rel}",
                    )
                )
    return issues


def check_concept_candidates(base: Path) -> List[Issue]:
    issues: List[Issue] = []
    summaries = []
    for path in compiled_files(base):
        content = read_text(path)
        if compiled_kind(content) == "summary":
            summaries.append((path, content))

    term_to_paths: Dict[str, List[Path]] = defaultdict(list)
    for path, content in summaries:
        for term in extract_related_terms(content):
            if term in STOP_TERMS:
                continue
            if len(term) < 3:
                continue
            term_to_paths[term].append(path)

    concept_files = {p.name.casefold() for p in compiled_files(base) if p.name.endswith("-concept.md")}
    for term, paths in sorted(term_to_paths.items()):
        unique_paths = sorted(set(paths))
        if len(unique_paths) < 2:
            continue
        slug = slugify(term)
        if not slug:
            continue
        expected_fragment = f"{slug}-concept.md"
        if any(expected_fragment in name for name in concept_files):
            continue
        examples = ", ".join(p.name for p in unique_paths[:3])
        issues.append(
            Issue(
                rule="concept-candidate-missing",
                severity="low",
                path=unique_paths[0],
                detail=f'term="{term}" appears in {len(unique_paths)} summaries; candidate summaries: {examples}',
            )
        )
    return issues


def check_index_candidates(base: Path) -> List[Issue]:
    issues: List[Issue] = []
    counts: Counter = Counter()
    representative: Dict[str, Path] = {}
    index_subjects: Set[str] = set()

    for path in compiled_files(base):
        subject = base_subject_from_filename(path)
        if not subject:
            continue
        kind = path.stem.rsplit("-", 1)[-1]
        if kind == "index":
            index_subjects.add(subject)
            continue
        counts[subject] += 1
        representative.setdefault(subject, path)

    for subject, count in sorted(counts.items()):
        if count < 3:
            continue
        if subject in index_subjects:
            continue
        issues.append(
            Issue(
                rule="index-candidate-missing",
                severity="low",
                path=representative[subject],
                detail=f'subject="{subject}" has {count} compiled docs but no index file',
            )
        )
    return issues


def check_orphan_concepts(base: Path) -> List[Issue]:
    issues: List[Issue] = []
    files = compiled_files(base)
    contents = {path: read_text(path) for path in files}
    for path in files:
        if not path.name.endswith("-concept.md"):
            continue
        rel = relative_path(base, path)
        inbound = []
        for other, content in contents.items():
            if other == path:
                continue
            if rel in content:
                inbound.append(other)
        if not inbound:
            issues.append(
                Issue(
                    rule="orphan-concept",
                    severity="medium",
                    path=path,
                    detail="concept has no inbound link from other compiled docs",
                )
            )
    return issues


def check_stale_indexes(base: Path) -> List[Issue]:
    issues: List[Issue] = []
    all_paths = existing_brain_paths(base)
    for path in compiled_files(base):
        if not path.name.endswith("-index.md"):
            continue
        content = read_text(path)
        links = sorted(set(extract_brain_links(content)))
        compiled_links = [link for link in links if link.startswith("compiled/")]
        if len(compiled_links) < 3:
            issues.append(
                Issue(
                    rule="stale-index-link-density",
                    severity="low",
                    path=path,
                    detail=f"index references only {len(compiled_links)} compiled docs; add more entry links",
                )
            )
        broken = [link for link in links if link not in all_paths]
        for link in broken:
            issues.append(
                Issue(
                    rule="index-broken-link",
                    severity="high",
                    path=path,
                    detail=f"missing target: {link}",
                )
            )
    return issues


def check_weak_backlinks(base: Path) -> List[Issue]:
    issues: List[Issue] = []
    for path in compiled_files(base):
        content = read_text(path)
        kind = compiled_kind(content)
        if kind not in {"summary", "report"}:
            continue
        links = sorted(set(extract_brain_links(content)))
        compiled_links = [link for link in links if link.startswith("compiled/")]
        if not compiled_links:
            issues.append(
                Issue(
                    rule="weak-backlinks",
                    severity="low",
                    path=path,
                    detail="summary/report has no compiled/* cross-links",
                )
            )
    return issues


ALL_RULES = (
    check_missing_summaries,
    check_missing_related,
    check_report_outputs,
    check_concept_candidates,
    check_index_candidates,
    check_orphan_concepts,
    check_stale_indexes,
    check_weak_backlinks,
)


def run_health_check(base: Path) -> List[Issue]:
    """Run all health-check rules against the vault and return collected issues."""
    issues: List[Issue] = []
    for rule_fn in ALL_RULES:
        issues.extend(rule_fn(base))
    return issues


def summarize(issues: List[Issue], base: Path) -> str:
    lines: List[str] = []
    lines.append("owl Wiki Health Check")
    lines.append(f"vault: {base}")
    lines.append(f"issues: {len(issues)}")
    if not issues:
        lines.append("status: clean")
        lines.append("")
        lines.append("Next steps: vault is healthy. Continue with other work.")
        return "\n".join(lines)

    grouped: Dict[str, List[Issue]] = {}
    severity_counts: Counter = Counter()
    for issue in issues:
        grouped.setdefault(issue.rule, []).append(issue)
        severity_counts[issue.severity] += 1

    for rule, entries in grouped.items():
        lines.append("")
        lines.append(f"[{rule}] count={len(entries)}")
        for item in entries:
            rel = item.path.relative_to(base)
            lines.append(f"- ({item.severity}) {rel} :: {item.detail}")

    # Next steps — LLM consumption hints (also helpful to humans).
    # Worst rule = highest count among the highest severity tier.
    lines.append("")
    lines.append("Next steps (for LLM agents and humans):")
    high_n = severity_counts.get("high", 0)
    if high_n >= 50:
        lines.append(f"  - {high_n} HIGH-severity issues. This is urgent — escalate to user.")
    elif high_n >= 10:
        lines.append(f"  - {high_n} high-severity issues. Use `owl health --json` for structured input to subagents.")
    # Find the worst rule by count, restricted to high if any high exist
    candidate_rules = (
        [(r, len(es)) for r, es in grouped.items() if any(e.severity == "high" for e in es)]
        if high_n
        else [(r, len(es)) for r, es in grouped.items()]
    )
    if candidate_rules:
        worst_rule, worst_count = max(candidate_rules, key=lambda x: x[1])
        delegate = {
            "missing-summary-for-raw": "owl-compiler subagent",
            "broken-cross-reference": "owl-librarian subagent",
            "dangling-link": "owl-librarian subagent",
            "report-broken-output-link": "owl-librarian subagent",
            "weak-backlinks": "owl-librarian subagent",
            "stale-compiled-newer-raw": "user review (do NOT auto-fix)",
            "concept-candidate-missing": "owl-librarian subagent (promotion)",
            "index-candidate-missing": "owl-librarian subagent (promotion)",
            "orphan-concept": "user review (delete or backlink)",
        }.get(worst_rule, "owl-librarian or owl-compiler subagent")
        lines.append(f"  - Worst rule: {worst_rule} ({worst_count} entries) → delegate to {delegate}.")
    lines.append("  - Pipe `owl health --json` to /owl-health for an LLM-interpreted fix plan.")
    return "\n".join(lines)


def issues_to_json(issues: List[Issue], base: Path) -> str:
    grouped: Dict[str, List[dict]] = {}
    severity_counts: Counter = Counter()
    for issue in issues:
        rel = str(issue.path.relative_to(base))
        grouped.setdefault(issue.rule, []).append(
            {"severity": issue.severity, "path": rel, "detail": issue.detail}
        )
        severity_counts[issue.severity] += 1

    payload = {
        "vault": str(base),
        "total_issues": len(issues),
        "by_severity": dict(severity_counts),
        "rules": grouped,
        "status": "clean" if not issues else "issues_found",
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run owl wiki integrity checks (8 rules)."
    )
    parser.add_argument(
        "--vault",
        "--brain",
        dest="vault",
        default=None,
        help="Vault root path (default: $OWL_VAULT or active-vault config or marker walk or ~/owl-vault)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON (for slash commands)",
    )
    return parser.parse_args(argv)


def cli(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    base = discover_vault(args.vault)
    if not base.exists():
        print(f"Vault path does not exist: {base}", file=sys.stderr)
        return 2

    issues = run_health_check(base)
    if args.json:
        print(issues_to_json(issues, base))
    else:
        print(summarize(issues, base))
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(cli())
