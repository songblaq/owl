"""``owl init`` — initialize a vault directory.

Writes the minimal vault glue:
    <vault>/.owl-vault            (marker file, 1-line metadata)
    <vault>/CLAUDE.md             (governance, copied from template)
    <vault>/.claude/settings.json (hook entries, only if --hooks)
    <vault>/.claude/commands/     (slash commands, copied from template)

Strict invariant: this command never writes Python or other executable code
into the vault. The vault is data; behavior lives in ``~/.local/bin/owl``
and ``~/.claude/agents/owl-*``. settings.json contains only hook command
strings that call ``owl hook <name>`` from PATH.

The default subdirectory layout from AGENTS.md §4 is created if missing
(raw, compiled, views, outputs, inbox, research, logs, tmp, config).
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import List, Optional

from owl import __version__
from owl.config import set_active_vault
from owl.vault import MARKER_FILE

VAULT_SUBDIRS = (
    "raw",
    "compiled",
    "views",
    "outputs",
    "inbox",
    "research",
    "logs",
    "tmp",
    "config",
)

ASSETS_DIR = Path(__file__).parent / "claude_assets" / "vault-template"


def _prompt_yes_no(question: str, default: bool = True) -> bool:
    """Tiny stdlib-only yes/no prompt with default."""
    suffix = " [Y/n] " if default else " [y/N] "
    while True:
        try:
            answer = input(question + suffix).strip().lower()
        except EOFError:
            return default
        if not answer:
            return default
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("  ↳ please answer y or n")


def _prompt_path(question: str, default: Path) -> Path:
    """Tiny path prompt with ``~`` expansion and default."""
    try:
        answer = input(f"{question} [{default}] ").strip()
    except EOFError:
        return default
    if not answer:
        return default
    return Path(answer).expanduser().resolve()


def write_marker(vault: Path) -> None:
    """Write the ``.owl-vault`` marker file."""
    marker = vault / MARKER_FILE
    payload = (
        "# owl vault marker\n"
        "version: 1\n"
        f"installer-version: {__version__}\n"
    )
    marker.write_text(payload, encoding="utf-8")


def write_claude_md(vault: Path, refresh: bool = False) -> bool:
    """Copy the template CLAUDE.md into the vault.

    Returns True if written, False if skipped because the file already exists
    (and refresh=False).
    """
    src = ASSETS_DIR / "CLAUDE.md"
    dst = vault / "CLAUDE.md"
    if dst.exists() and not refresh:
        return False
    shutil.copyfile(src, dst)
    return True


def install_slash_commands(vault: Path, refresh: bool = False) -> List[str]:
    """Copy slash command markdown files from claude_assets/commands/ to the vault.

    Returns a list of command names that were written. Skips files that already
    exist unless ``refresh=True``.
    """
    src_dir = ASSETS_DIR.parent / "commands"
    if not src_dir.exists():
        return []

    dst_dir = vault / ".claude" / "commands"
    dst_dir.mkdir(parents=True, exist_ok=True)

    copied: List[str] = []
    for src in sorted(src_dir.glob("*.md")):
        dst = dst_dir / src.name
        if dst.exists() and not refresh:
            continue
        shutil.copyfile(src, dst)
        copied.append(src.stem)
    return copied


def write_hooks(vault: Path, refresh: bool = False) -> bool:
    """Install ``.claude/settings.json`` with the 5 owl hooks.

    Returns True if written, False if skipped.
    """
    src = ASSETS_DIR / "settings.json"
    dst_dir = vault / ".claude"
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / "settings.json"

    if dst.exists() and not refresh:
        # Don't blow away an existing settings.json (might have user customizations).
        # Instead, attempt to merge the owl hooks into it.
        try:
            existing = json.loads(dst.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            existing = {}
        if not isinstance(existing, dict):
            existing = {}
        template = json.loads(src.read_text(encoding="utf-8"))
        existing.setdefault("hooks", {})
        for event_name, event_entries in template.get("hooks", {}).items():
            existing["hooks"].setdefault(event_name, [])
            existing["hooks"][event_name] = event_entries  # overwrite event-level
        dst.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return True

    shutil.copyfile(src, dst)
    return True


def ensure_subdirs(vault: Path) -> List[str]:
    """Create AGENTS.md §4 default subdirectories if missing.

    Returns the list of dirs that were newly created.
    """
    created = []
    for sub in VAULT_SUBDIRS:
        target = vault / sub
        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)
            created.append(sub)
    return created


def init_vault(
    vault_arg: Optional[str],
    hooks: Optional[bool] = None,
    refresh: bool = False,
    interactive: bool = True,
    activate: bool = True,
) -> int:
    """Initialize a vault.

    Args:
        vault_arg: Vault path from CLI argument, or None to prompt.
        hooks: True to install hooks, False to skip, None to ask interactively.
        refresh: Overwrite existing CLAUDE.md / settings.json if True.
        interactive: If False, never prompt — fail on missing vault path.
        activate: Set this vault as the active vault after init.

    Returns:
        Exit code (0 = success).
    """
    print("owl — vault initialization")
    print("==========================")

    # Resolve vault path
    if vault_arg:
        vault = Path(vault_arg).expanduser().resolve()
    elif interactive:
        from owl.vault import DEFAULT_VAULT
        vault = _prompt_path("Vault path?", DEFAULT_VAULT)
    else:
        print("error: vault path required (give it as an argument)", file=sys.stderr)
        return 2

    if not vault.exists():
        print(f"\nVault directory does not exist: {vault}")
        # In non-interactive mode the user explicitly asked us not to prompt,
        # so creating is the only sensible default. In interactive mode we
        # confirm before creating.
        if not interactive or _prompt_yes_no("Create it?", default=True):
            vault.mkdir(parents=True, exist_ok=True)
            print(f"  ↳ created {vault}")
        else:
            print("aborted.", file=sys.stderr)
            return 2

    if not vault.is_dir():
        print(f"error: not a directory: {vault}", file=sys.stderr)
        return 2

    # Subdirs (AGENTS.md §4)
    created_dirs = ensure_subdirs(vault)
    if created_dirs:
        print(f"\nCreated vault subdirs: {', '.join(created_dirs)}")
    else:
        print("\nVault subdirs already in place ✓")

    # Marker
    write_marker(vault)
    print(f"Wrote {vault.name}/{MARKER_FILE} ✓")

    # CLAUDE.md
    if write_claude_md(vault, refresh=refresh):
        print(f"Wrote {vault.name}/CLAUDE.md ✓")
    else:
        print(f"Skipped CLAUDE.md (already exists; pass --refresh to overwrite)")

    # Hooks
    if hooks is None and interactive:
        print()
        hooks = _prompt_yes_no(
            "Install Claude Code hooks (SessionStart, UserPromptSubmit, etc.)?",
            default=True,
        )

    if hooks:
        write_hooks(vault, refresh=refresh)
        print(f"Wrote {vault.name}/.claude/settings.json ✓ (5 hooks)")
        copied_cmds = install_slash_commands(vault, refresh=refresh)
        if copied_cmds:
            print(f"Wrote {vault.name}/.claude/commands/ ✓ ({len(copied_cmds)} slash commands)")
        else:
            print(f"Skipped slash commands (already up to date; pass --refresh to overwrite)")
    else:
        print("Skipped hook installation. Run `owl init --hooks` later to enable.")

    # Activate
    if activate:
        set_active_vault(vault)
        print(f"\nSet {vault} as active vault ✓")

    print("\nDone. Next steps (for humans and LLM agents):")
    print(f"  cd {vault}")
    print(f"  claude   # start a Claude Code session here")
    print(f"  owl status   # confirm vault marker / CLAUDE.md / hooks are all ✓")
    print()
    print("  LLM agents: this vault now has /owl-* slash commands and SessionStart")
    print("  hooks installed. New Claude Code sessions in this directory will auto-")
    print("  load the wiki context. Use owl-{librarian,compiler,health} subagents")
    print("  for filing / compilation / health-check work.")
    return 0
