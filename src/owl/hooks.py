"""Claude Code hooks for owl vaults.

These functions are invoked by Claude Code via ``owl hook <name>`` commands
declared in the vault's ``.claude/settings.json``. Each hook reads the
Claude Code event payload from stdin (JSON), produces brief stdout output
that Claude Code injects as session context, and **always exits 0** so a
broken hook never blocks the user.

Five lifecycle hooks:

    session_start  → on `claude` startup: surface vault state, recent logs,
                     inbox count, unresolved health issue summary
    user_prompt    → every user message: keyword routing (file/ingest/compile
                     /search → suggest the right slash command or subagent)
    post_tool_use  → after Write/Edit on raw/* or compiled/*: targeted health
                     warnings, throttled to once per N seconds
    pre_compact    → before context compaction: snapshot session state to logs/
    stop           → on session end: warn about orphaned raw files

Strict invariant: hooks live in this Python module under the project repo,
NOT inside the vault. The vault's settings.json only contains the string
``owl hook <name>``; the actual logic is here so ``git pull`` upgrades
all vaults at once.

Output budget per hook: aim for ≤ 30 lines so SessionStart doesn't blow
out the user's context window. Use ``HOOK_OUTPUT_LIMIT`` to enforce.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from owl.vault import discover_vault, find_marker_upward

HOOK_OUTPUT_LIMIT = 30  # lines
COOLDOWN_SECONDS = 30   # PostToolUse throttle


def _read_stdin_json() -> Dict[str, Any]:
    """Read a JSON payload from stdin if any. Return empty dict on failure.

    Claude Code passes hook context as JSON on stdin. We never raise — a
    malformed payload should not break the user's session.
    """
    if sys.stdin.isatty():
        return {}
    try:
        raw = sys.stdin.read()
    except OSError:
        return {}
    if not raw or not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _get_active_vault() -> Optional[Path]:
    """Resolve the vault for hook context.

    Hooks run in the directory where ``claude`` was launched, so the marker
    walk almost always finds the right vault. Fall back to the user-config
    active vault. If neither resolves to an existing dir, return None and
    the hook should silently no-op.
    """
    marker = find_marker_upward()
    if marker and marker.exists():
        return marker
    candidate = discover_vault()
    if candidate.exists() and (candidate / ".owl-vault").exists():
        return candidate
    return None


def _truncate_output(lines: List[str]) -> List[str]:
    if len(lines) <= HOOK_OUTPUT_LIMIT:
        return lines
    head = lines[: HOOK_OUTPUT_LIMIT - 1]
    head.append(f"  … ({len(lines) - HOOK_OUTPUT_LIMIT + 1} more lines suppressed)")
    return head


def _print_block(title: str, lines: List[str]) -> None:
    """Print a labeled block as `<system-reminder>` content for Claude Code."""
    if not lines:
        return
    print(f"<system-reminder source=\"owl:{title}\">")
    for line in _truncate_output(lines):
        print(line)
    print("</system-reminder>")


# ----------------------------------------------------------------------------
# session_start
# ----------------------------------------------------------------------------

def session_start() -> int:
    """Inject vault state at the start of a Claude Code session."""
    vault = _get_active_vault()
    if vault is None:
        return 0  # not in a vault — silent no-op

    lines: List[str] = [
        f"owl vault active: {vault}",
        "",
    ]

    # Vault counts
    raw_count = sum(1 for p in (vault / "raw").rglob("*.md") if p.is_file()) if (vault / "raw").exists() else 0
    compiled_count = sum(1 for p in (vault / "compiled").rglob("*.md") if p.is_file()) if (vault / "compiled").exists() else 0
    inbox_count = sum(1 for p in (vault / "inbox").rglob("*") if p.is_file()) if (vault / "inbox").exists() else 0
    lines.append(f"Counts: raw={raw_count}, compiled={compiled_count}, inbox={inbox_count}")

    # Recent log entry
    logs_dir = vault / "logs"
    if logs_dir.exists():
        log_files = sorted(logs_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        if log_files:
            most_recent = log_files[0]
            try:
                first_lines = most_recent.read_text(encoding="utf-8").splitlines()[:3]
                lines.append("")
                lines.append(f"Most recent log: {most_recent.name}")
                for fl in first_lines:
                    lines.append(f"  {fl[:120]}")
            except OSError:
                pass

    # Inbox alert
    if inbox_count:
        lines.append("")
        lines.append(f"⚠ {inbox_count} item(s) waiting in inbox/ — consider /owl-ingest")

    # Health summary (quick: just total + high count)
    try:
        from owl.health import run_health_check
        issues = run_health_check(vault)
        if issues:
            high = sum(1 for i in issues if i.severity == "high")
            lines.append("")
            lines.append(f"Health: {len(issues)} issue(s), {high} high — run /owl-health for fixes")
    except Exception:
        pass

    lines.append("")
    lines.append("Wiki philosophy: this is an LLM-maintained wiki (Karpathy's LLM Wiki idea). raw is immutable; compile to summary/note/concept/index. See vault CLAUDE.md for the file contract.")

    _print_block("session-start", lines)
    return 0


# ----------------------------------------------------------------------------
# user_prompt
# ----------------------------------------------------------------------------

# Keyword → routing hint pairs. Order matters: first match wins.
ROUTING_RULES = [
    (re.compile(r"(?i)\b(file this|이 문서|filing|file the|파일링)\b"),
     "→ /owl-ingest can route this to raw/ + owl-librarian for naming/links."),
    (re.compile(r"(?i)\b(ingest|inbox|새 자료|새 문서|new raw)\b"),
     "→ /owl-ingest moves a candidate file into raw/ with the YYYY-MM-DD-<slug>-raw.md contract."),
    (re.compile(r"(?i)\b(compile|컴파일|raw to|summary 만들|note 만들)\b"),
     "→ /owl-compile delegates to owl-compiler subagent (raw → summary/note)."),
    (re.compile(r"(?i)\b(health|integrity|broken link|orphan|stale)\b"),
     "→ /owl-health runs the 8 integrity rules and routes fixes to owl-librarian/owl-compiler."),
    (re.compile(r"(?i)\b(search wiki|search vault|find in vault|찾아|검색)\b"),
     "→ /owl-search runs token-scored search across raw/compiled/research/views."),
    (re.compile(r"(?i)\b(promote|index|concept|승격)\b"),
     "→ /owl-promote walks owl-librarian through concept/index promotion."),
    (re.compile(r"(?i)\b(big question|큰 질문|deep dive|long form)\b"),
     "→ /owl-query orchestrates search → temporary wiki → report (workflow-v0 §4)."),
]


def user_prompt() -> int:
    """Inspect the user's prompt for keywords and inject a routing hint."""
    vault = _get_active_vault()
    if vault is None:
        return 0

    payload = _read_stdin_json()
    prompt = payload.get("prompt") or payload.get("user_prompt") or ""
    if not isinstance(prompt, str) or not prompt.strip():
        return 0

    hits: List[str] = []
    for pattern, hint in ROUTING_RULES:
        if pattern.search(prompt):
            hits.append(hint)
            if len(hits) >= 2:  # cap so we don't spam
                break

    if not hits:
        return 0

    lines = ["owl routing hints (keyword match):", ""]
    lines.extend(hits)
    _print_block("user-prompt-routing", lines)
    return 0


# ----------------------------------------------------------------------------
# post_tool_use
# ----------------------------------------------------------------------------

def _cooldown_path(vault: Path) -> Path:
    return vault / "tmp" / "owl-hook-cooldown"


def _check_cooldown(vault: Path) -> bool:
    """Return True if we're past the cooldown window (allowed to run)."""
    f = _cooldown_path(vault)
    if not f.exists():
        return True
    try:
        last = float(f.read_text().strip() or "0")
    except (OSError, ValueError):
        return True
    return (time.time() - last) > COOLDOWN_SECONDS


def _stamp_cooldown(vault: Path) -> None:
    f = _cooldown_path(vault)
    f.parent.mkdir(parents=True, exist_ok=True)
    try:
        f.write_text(str(time.time()))
    except OSError:
        pass


def post_tool_use() -> int:
    """After a Write/Edit on a vault file, run a quick health snapshot.

    Throttled by ``COOLDOWN_SECONDS`` to prevent recursion (since the hook
    output → user response → another tool call → another hook fire).
    """
    vault = _get_active_vault()
    if vault is None:
        return 0

    payload = _read_stdin_json()
    file_path_str = (
        payload.get("tool_input", {}).get("file_path")
        if isinstance(payload.get("tool_input"), dict)
        else payload.get("file_path")
    )
    if not file_path_str:
        return 0

    # Resolve both sides to canonical paths so symlinks (e.g. macOS /var → /private/var)
    # don't make a vault-internal write look external.
    file_path = Path(file_path_str).expanduser().resolve()
    resolved_vault = vault.resolve()
    try:
        file_path.relative_to(resolved_vault)
    except ValueError:
        return 0  # write was outside the vault
    vault = resolved_vault

    # Only care about raw/ and compiled/ writes
    rel_parts = file_path.relative_to(vault).parts
    if not rel_parts or rel_parts[0] not in {"raw", "compiled"}:
        return 0

    if not _check_cooldown(vault):
        return 0

    _stamp_cooldown(vault)

    # Run a focused subset of health checks (only the ones touching the file's neighborhood)
    try:
        from owl.health import (
            check_missing_summaries,
            check_missing_related,
            check_weak_backlinks,
        )
        targeted_issues = []
        targeted_issues.extend(check_missing_summaries(vault))
        targeted_issues.extend(check_missing_related(vault))
        targeted_issues.extend(check_weak_backlinks(vault))
    except Exception:
        return 0

    # Filter to issues mentioning the just-written file (or its sibling raw)
    file_name = file_path.name
    raw_sibling = file_name.replace("-summary.md", "-raw.md") if file_name.endswith("-summary.md") else file_name
    relevant = [
        i
        for i in targeted_issues
        if i.path.name == file_name or i.path.name == raw_sibling or file_name in i.detail
    ]
    if not relevant:
        return 0

    lines = [f"Wiki integrity warnings for {rel_parts[-1]}:"]
    for issue in relevant[:5]:
        lines.append(f"  ({issue.severity}) [{issue.rule}] {issue.detail}")
    if len(relevant) > 5:
        lines.append(f"  … {len(relevant) - 5} more — run /owl-health for full list")

    _print_block("post-tool-use", lines)
    return 0


# ----------------------------------------------------------------------------
# pre_compact
# ----------------------------------------------------------------------------

def pre_compact() -> int:
    """Snapshot session state before Claude Code compacts the conversation."""
    vault = _get_active_vault()
    if vault is None:
        return 0

    logs_dir = vault / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    payload = _read_stdin_json()
    summary = payload.get("session_summary") or payload.get("summary") or ""

    today = datetime.now().strftime("%Y-%m-%d")
    snapshot = logs_dir / f"{today}-session-state.md"

    body_lines = [
        f"# Session state snapshot — {datetime.now().isoformat(timespec='seconds')}",
        "",
        "Auto-generated by `owl hook pre_compact` before context compaction.",
        "",
    ]
    if summary:
        body_lines.append("## Summary")
        body_lines.append("")
        if isinstance(summary, str):
            body_lines.append(summary)
        else:
            body_lines.append(json.dumps(summary, ensure_ascii=False, indent=2))

    try:
        snapshot.write_text("\n".join(body_lines) + "\n", encoding="utf-8")
        _print_block("pre-compact", [f"Snapshotted session state → logs/{snapshot.name}"])
    except OSError:
        pass

    return 0


# ----------------------------------------------------------------------------
# stop
# ----------------------------------------------------------------------------

def stop() -> int:
    """On session end, warn about orphaned raw files created this session."""
    vault = _get_active_vault()
    if vault is None:
        return 0

    raw_dir = vault / "raw"
    compiled_dir = vault / "compiled"
    if not raw_dir.exists():
        return 0

    compiled_names = (
        {p.name for p in compiled_dir.rglob("*.md") if p.is_file()} if compiled_dir.exists() else set()
    )

    # Find raw files modified in the last hour without a matching summary
    now = time.time()
    recent_orphans: List[str] = []
    for raw in raw_dir.rglob("*-raw.md"):
        if not raw.is_file():
            continue
        if now - raw.stat().st_mtime > 3600:
            continue
        expected_summary = raw.name.replace("-raw.md", "-summary.md")
        if expected_summary not in compiled_names:
            recent_orphans.append(raw.name)

    if not recent_orphans:
        return 0

    lines = [
        f"⚠ {len(recent_orphans)} new raw file(s) without summaries in this session:",
    ]
    for name in recent_orphans[:5]:
        lines.append(f"  - {name}")
    if len(recent_orphans) > 5:
        lines.append(f"  … {len(recent_orphans) - 5} more")
    lines.append("")
    lines.append("Run /owl-compile <raw-path> for each, or /owl-ingest to batch.")

    _print_block("stop", lines)
    return 0


# ----------------------------------------------------------------------------
# Dispatcher entry point
# ----------------------------------------------------------------------------

HOOKS = {
    "session_start": session_start,
    "user_prompt": user_prompt,
    "post_tool_use": post_tool_use,
    "pre_compact": pre_compact,
    "stop": stop,
}


def dispatch(name: str) -> int:
    """Dispatch a hook by name. Always returns 0 (never block Claude Code)."""
    fn = HOOKS.get(name)
    if fn is None:
        # Unknown hook name — print to stderr but exit 0 so Claude doesn't block
        print(f"owl hook: unknown hook '{name}'", file=sys.stderr)
        return 0
    try:
        return fn()
    except Exception as e:
        # Defensive: never let a hook bug break the user's session
        print(f"owl hook {name}: error: {e}", file=sys.stderr)
        return 0
