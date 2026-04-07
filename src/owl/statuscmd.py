"""``owl status`` — at-a-glance vault health summary.

Reports:
    - Installed owl version
    - Active vault path + how it was discovered
    - Vault subdirectory counts (raw, compiled, views, outputs)
    - Brief health summary (issue counts by severity)
    - Whether hooks are installed in the vault's .claude/settings.json
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Optional

from owl import __version__
from owl.config import get_active_vault, get_setup_timestamp
from owl.health import run_health_check
from owl.vault import MARKER_FILE, discover_vault, discovery_source


def _count_files(directory: Path, suffix: str = ".md") -> int:
    if not directory.exists():
        return 0
    return sum(1 for p in directory.rglob(f"*{suffix}") if p.is_file())


def _hooks_installed(vault: Path) -> bool:
    settings = vault / ".claude" / "settings.json"
    if not settings.exists():
        return False
    try:
        data = json.loads(settings.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    hooks = data.get("hooks", {})
    if not isinstance(hooks, dict):
        return False
    # Check at least one hook contains an "owl hook" command
    for entries in hooks.values():
        for entry in entries or []:
            for h in entry.get("hooks", []):
                cmd = h.get("command", "")
                if "owl hook" in cmd:
                    return True
    return False


def show_status(vault_arg: Optional[str] = None, json_out: bool = False) -> int:
    vault = discover_vault(vault_arg)
    source = discovery_source(vault_arg)
    active = get_active_vault()
    setup_at = get_setup_timestamp()

    info = {
        "version": __version__,
        "vault": str(vault),
        "discovery": source,
        "active_vault_config": str(active) if active else None,
        "setup_at": setup_at,
        "vault_exists": vault.exists(),
        "marker_present": (vault / MARKER_FILE).exists() if vault.exists() else False,
        "claude_md_present": (vault / "CLAUDE.md").exists() if vault.exists() else False,
        "hooks_installed": _hooks_installed(vault) if vault.exists() else False,
        "counts": {},
        "health": None,
    }

    if vault.exists():
        info["counts"] = {
            "raw": _count_files(vault / "raw"),
            "compiled": _count_files(vault / "compiled"),
            "views": _count_files(vault / "views"),
            "outputs_files": sum(_count_files(vault / "outputs" / sub, "*") for sub in ("slides", "figures", "visuals") if (vault / "outputs" / sub).exists()),
            "research": _count_files(vault / "research"),
            "inbox": _count_files(vault / "inbox"),
        }
        try:
            issues = run_health_check(vault)
            severity_counts: Counter = Counter(i.severity for i in issues)
            info["health"] = {
                "total": len(issues),
                "by_severity": dict(severity_counts),
                "status": "clean" if not issues else "issues_found",
            }
        except Exception as e:
            info["health"] = {"error": str(e)}

    if json_out:
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return 0

    # Human-readable output
    print("owl status")
    print("==========")
    print(f"  version:        {info['version']}")
    print(f"  vault:          {info['vault']}")
    print(f"    discovered via: {info['discovery']}")
    if active:
        print(f"  active config:  {active}")
    if setup_at:
        print(f"  setup at:       {setup_at}")
    else:
        print(f"  setup at:       (never — run `owl setup`)")

    if not info["vault_exists"]:
        print(f"\n  ✗ vault directory does not exist: {vault}")
        print(f"    Run: owl init {vault}")
        return 1

    print()
    print("Vault state:")
    print(f"  marker ({MARKER_FILE}):   {'✓' if info['marker_present'] else '✗  (run `owl init`)'}")
    print(f"  CLAUDE.md:              {'✓' if info['claude_md_present'] else '✗  (run `owl init`)'}")
    print(f"  hooks installed:        {'✓' if info['hooks_installed'] else '✗  (run `owl init --hooks`)'}")

    print()
    print("Counts:")
    counts = info["counts"]
    for k, v in counts.items():
        print(f"  {k:20s} {v}")

    print()
    health = info["health"]
    if health and "total" in health:
        print(f"Health: {health['total']} issue(s)")
        for severity in ("high", "medium", "low"):
            if health["by_severity"].get(severity):
                print(f"  {severity:10s} {health['by_severity'][severity]}")
        if health["total"]:
            print("  Run `owl health` for the full list, or `/owl-health` for LLM-interpreted fixes.")
    elif health and "error" in health:
        print(f"Health: error — {health['error']}")

    return 0
