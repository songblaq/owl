"""Ingest contract v2 validator — C1..C6 checks (docs/ingest-contract-v2.md).

T1-A MVP. Used by `omb validate` and optionally by `omb ingest --validate`.
Reports violations; does not auto-fix.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from omb.vault_ops import parse_fm, active_vault, _resolve_source


NAMING_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z][a-z0-9-]*\.md$")
REQUIRED_FIELDS = ("id", "type", "topics", "confidence", "source")
VALID_TYPES = {"claim", "fact", "procedure", "decision", "observation", "definition", "preference", "open-question"}
EVIDENCE_MARKERS = ("## Evidence", "## evidence", "**Evidence**", "근거")
WHY_MARKERS = ("## Why it matters", "## why", "**Why**", "왜 중요")


@dataclass
class Finding:
    entry: str
    rule: str          # C1..C6
    severity: str      # critical | warning | info
    message: str


@dataclass
class ValidationReport:
    entry_count: int = 0
    findings: list[Finding] = field(default_factory=list)

    def by_rule(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for f in self.findings:
            out[f.rule] = out.get(f.rule, 0) + 1
        return out

    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "critical")


def validate_entry(path: Path, vault: Path) -> list[Finding]:
    findings: list[Finding] = []
    name = path.name
    stem = path.stem

    # C1 naming
    if not NAMING_RE.match(name):
        findings.append(Finding(stem, "C1", "critical", f"naming: {name} does not match YYYY-MM-DD-<topic>-<slug>.md"))

    fm_text, fields, body = parse_fm(path)
    if not fm_text:
        findings.append(Finding(stem, "C2", "critical", "no frontmatter"))
        return findings

    # C2 required fields
    missing = [f for f in REQUIRED_FIELDS if not fields.get(f)]
    if missing:
        findings.append(Finding(stem, "C2", "critical", f"missing frontmatter: {', '.join(missing)}"))

    etype = fields.get("type", "").strip()
    if etype and etype not in VALID_TYPES:
        findings.append(Finding(stem, "C2", "warning", f"unknown type: {etype}"))

    fm_id = fields.get("id", "").strip()
    if fm_id and fm_id != stem:
        findings.append(Finding(stem, "C2", "warning", f"frontmatter id '{fm_id}' != filename '{stem}'"))

    # C3 body blocks
    body_lower = body.lower() if body else ""
    has_why = any(m.lower() in body_lower for m in WHY_MARKERS)
    has_evidence = any(m.lower() in body_lower for m in EVIDENCE_MARKERS)
    if not has_why:
        findings.append(Finding(stem, "C3", "warning", "missing 'Why it matters' / '왜 중요' block"))
    if not has_evidence:
        findings.append(Finding(stem, "C3", "warning", "missing 'Evidence' / '근거' block"))

    # C5 source resolvable
    src = fields.get("source", "").strip()
    if src:
        resolved = _resolve_source(src, vault)
        if resolved is None or not resolved.exists():
            findings.append(Finding(stem, "C5", "critical", f"source path unresolvable: {src}"))

    # C6 edges
    edges = fields.get("edges", "[]").strip("[]").strip()
    if not edges:
        findings.append(Finding(stem, "C6", "info", "no graph edges (may be acceptable for seed/new-topic)"))

    return findings


def validate_vault(vault: Path | None = None, entry_id: str | None = None) -> ValidationReport:
    v = vault or active_vault()
    if v is None:
        raise RuntimeError("no active vault")
    entries_dir = v / "entries"
    report = ValidationReport()
    if entry_id:
        paths = [entries_dir / f"{entry_id}.md"]
    else:
        paths = sorted(entries_dir.glob("*.md"))
    for p in paths:
        if not p.exists():
            continue
        report.entry_count += 1
        report.findings.extend(validate_entry(p, v))
    return report


def format_report(report: ValidationReport, limit: int = 50) -> str:
    lines = [
        f"validate — contract v2",
        f"=" * 40,
        f"  entries scanned: {report.entry_count}",
        f"  findings total:  {len(report.findings)}",
        f"  critical:        {report.critical_count()}",
        f"  by rule:         {report.by_rule()}",
        "",
    ]
    crit = [f for f in report.findings if f.severity == "critical"]
    warn = [f for f in report.findings if f.severity == "warning"]
    if crit:
        lines.append(f"CRITICAL ({len(crit)}):")
        for f in crit[:limit]:
            lines.append(f"  [{f.rule}] {f.entry}: {f.message}")
        if len(crit) > limit:
            lines.append(f"  ... ({len(crit)-limit} more)")
    if warn:
        lines.append("")
        lines.append(f"WARNING ({len(warn)}):")
        for f in warn[:limit]:
            lines.append(f"  [{f.rule}] {f.entry}: {f.message}")
        if len(warn) > limit:
            lines.append(f"  ... ({len(warn)-limit} more)")
    return "\n".join(lines)


def validate_to_json(report: ValidationReport) -> dict:
    return {
        "entry_count": report.entry_count,
        "findings_total": len(report.findings),
        "critical_count": report.critical_count(),
        "by_rule": report.by_rule(),
        "findings": [
            {"entry": f.entry, "rule": f.rule, "severity": f.severity, "message": f.message}
            for f in report.findings
        ],
    }
