"""``owl setup`` — interactive post-install configuration.

Runs after ``curl ... | sh`` to:
    1. Diagnose the environment (Python version, ``owl`` in PATH).
    2. Find or prompt for a vault and offer ``owl init``.
    3. Create user-global symlinks for ``owl-*`` subagents in
       ``~/.claude/agents/``.
    4. Create OpenClaw L0 symlinks at ``~/.agents/skills/owl-*``
       (per ``plans/openclaw-skill-structure-principles-2026-04-04.md``).
    5. Stamp ``~/.owl/installed-at``.

This is the human-facing entry point. ``install.sh`` exec's it. Users can
also re-run it any time to re-symlink after a ``git pull`` of the project.
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from owl import __version__
from owl.config import (
    USER_CONFIG_DIR,
    ensure_config_dir,
    get_active_vault,
    mark_setup_completed,
)
from owl.initcmd import _prompt_yes_no, init_vault
from owl.vault import DEFAULT_VAULT

ASSETS_DIR = Path(__file__).parent / "claude_assets"
USER_CLAUDE_AGENTS = Path.home() / ".claude" / "agents"
USER_AGENTS_SKILLS = Path.home() / ".agents" / "skills"

OWL_SUBAGENTS = ("owl-librarian", "owl-compiler", "owl-health")


def diagnose_env() -> Tuple[bool, List[str]]:
    """Return (ok, messages) for the environment diagnostic step."""
    msgs: List[str] = []
    ok = True

    py = sys.version_info
    msgs.append(f"  Python:       {py.major}.{py.minor}.{py.micro}")
    if py < (3, 9):
        msgs.append("    ✗ Python 3.9+ required")
        ok = False
    else:
        msgs.append("    ✓")

    owl_path = shutil.which("owl")
    if owl_path:
        msgs.append(f"  owl CLI:      {owl_path}")
        msgs.append("    ✓")
    else:
        msgs.append("  owl CLI:      NOT FOUND on PATH")
        msgs.append("    ✗ ~/.local/bin probably not in PATH; add it to your shell rc")
        ok = False

    msgs.append(f"  version:      {__version__}")

    return ok, msgs


def find_vault_candidates() -> List[Path]:
    """Best-effort scan for likely vault locations."""
    candidates: List[Path] = []
    if DEFAULT_VAULT.exists():
        candidates.append(DEFAULT_VAULT)

    active = get_active_vault()
    if active and active not in candidates and active.exists():
        candidates.append(active)

    return candidates


def _symlink_subagent(name: str, source_root: Path, target_root: Path) -> str:
    """Create a single subagent symlink. Returns a status message."""
    src = source_root / f"{name}.md"
    dst = target_root / f"{name}.md"

    if not src.exists():
        return f"  - {name}: source asset not found at {src} — skipping"

    target_root.mkdir(parents=True, exist_ok=True)

    if dst.is_symlink() or dst.exists():
        try:
            dst.unlink()
        except OSError as e:
            return f"  - {name}: could not remove existing target: {e}"

    try:
        dst.symlink_to(src)
        return f"  - {name}: → {src}"
    except OSError as e:
        return f"  - {name}: symlink failed: {e}"


def install_subagent_symlinks() -> List[str]:
    """Symlink owl-* subagents into ~/.claude/agents/ and ~/.agents/skills/."""
    agents_src = ASSETS_DIR / "agents"
    msgs = ["Symlinking subagents to ~/.claude/agents/ ..."]
    for name in OWL_SUBAGENTS:
        msgs.append(_symlink_subagent(name, agents_src, USER_CLAUDE_AGENTS))

    msgs.append("Symlinking subagents to ~/.agents/skills/ (OpenClaw L0 canonical) ...")
    for name in OWL_SUBAGENTS:
        msgs.append(_symlink_subagent(name, agents_src, USER_AGENTS_SKILLS))

    return msgs


def setup(interactive: bool = True) -> int:
    """Run the full setup flow."""
    print("owl — setup")
    print("===========\n")

    print("1) Environment diagnostic")
    ok, msgs = diagnose_env()
    for m in msgs:
        print(m)
    if not ok:
        print(
            "\n  ✗ environment problems detected. Fix the issues above, then re-run `owl setup`.",
            file=sys.stderr,
        )
        return 1

    ensure_config_dir()
    print(f"\n  ↳ user config dir: {USER_CONFIG_DIR}")

    print("\n2) Vault discovery")
    candidates = find_vault_candidates()
    chosen: Optional[Path] = None
    if candidates:
        print("  Found existing vault(s):")
        for c in candidates:
            print(f"    - {c}")
        chosen = candidates[0]
        print(f"\n  Using {chosen} as the default for `owl init`.")
        if interactive and _prompt_yes_no(f"Run `owl init {chosen}` now?", default=True):
            init_vault(str(chosen), hooks=None, interactive=interactive)
        else:
            print("  Skipped. You can run `owl init <path>` later.")
    else:
        print(f"  No vault found at {DEFAULT_VAULT} or in active-vault config.")
        if interactive and _prompt_yes_no("Create one and run `owl init` now?", default=True):
            init_vault(None, hooks=None, interactive=interactive)
        else:
            print("  Skipped. You can run `owl init <path>` later.")

    print("\n3) User-global subagent symlinks")
    for line in install_subagent_symlinks():
        print(line)

    print("\n4) Marking setup complete")
    mark_setup_completed()
    print(f"  ✓ stamped {USER_CONFIG_DIR}/installed-at")

    print("\nSetup complete. Try:")
    print("  owl status")
    print("  owl search 'filing loop'")
    print("  owl health")
    return 0
