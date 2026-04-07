"""Vault discovery — single source of truth for resolving the active vault path.

Resolution priority (first hit wins):
    1. Explicit argument (e.g. CLI ``--vault`` flag)
    2. ``$OWL_VAULT`` environment variable
    3. ``~/.owl/active-vault`` (set by ``owl use``)
    4. Walk up from cwd looking for a ``.owl-vault`` marker file
    5. Legacy default ``~/.agents/brain`` (only if it exists, for backward compat)
    6. Default ``~/owl-vault``

Used by every CLI subcommand and every hook so vault location is consistent
across the entire operational layer.

Note: ``~/owl-vault`` is the new default. Pre-2026-04-07 vaults at
``~/.agents/brain`` are still recognized as a fallback if the new path
doesn't exist, so the rename is non-destructive.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

DEFAULT_VAULT = Path.home() / "owl-vault"
LEGACY_VAULT = Path.home() / ".agents" / "brain"
MARKER_FILE = ".owl-vault"
ENV_VAR = "OWL_VAULT"
USER_CONFIG_DIR = Path.home() / ".owl"
ACTIVE_VAULT_FILE = USER_CONFIG_DIR / "active-vault"

# Backward-compatible alias for the legacy name. Existing wrappers and any
# external scripts that imported ``DEFAULT_BRAIN`` keep working. Will be
# removed in a future major version.
DEFAULT_BRAIN = DEFAULT_VAULT


def _read_active_vault() -> Optional[Path]:
    """Read the user-configured active vault path, if any."""
    if not ACTIVE_VAULT_FILE.exists():
        return None
    try:
        text = ACTIVE_VAULT_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not text:
        return None
    return Path(text).expanduser().resolve()


def discover_vault(explicit: Optional[str] = None) -> Path:
    """Return the active vault root path.

    Args:
        explicit: Optional explicit path (typically from a ``--vault`` CLI flag).
            Highest priority when provided.

    Returns:
        Resolved absolute Path to the vault root. Existence is NOT verified —
        callers should check ``path.exists()`` themselves and produce a useful
        error message if the vault is missing.
    """
    if explicit:
        return Path(explicit).expanduser().resolve()

    env = os.environ.get(ENV_VAR)
    if env:
        return Path(env).expanduser().resolve()

    active = _read_active_vault()
    if active:
        return active

    cwd = Path.cwd().resolve()
    for candidate in [cwd, *cwd.parents]:
        if (candidate / MARKER_FILE).exists():
            return candidate

    # Prefer the new default; fall back to the legacy location only if
    # the new path doesn't exist. This makes the 2026-04-07 rename
    # non-destructive — pre-existing vaults at ~/.agents/brain still work.
    if DEFAULT_VAULT.exists() or not LEGACY_VAULT.exists():
        return DEFAULT_VAULT.resolve()
    return LEGACY_VAULT.resolve()


def discovery_source(explicit: Optional[str] = None) -> str:
    """Return a human-readable label for which discovery method resolved the vault.

    Useful for ``owl status`` to explain *why* a particular vault is active.
    """
    if explicit:
        return "explicit --vault flag"
    if os.environ.get(ENV_VAR):
        return f"${ENV_VAR} environment variable"
    if _read_active_vault():
        return f"active-vault config ({ACTIVE_VAULT_FILE})"
    cwd = Path.cwd().resolve()
    for candidate in [cwd, *cwd.parents]:
        if (candidate / MARKER_FILE).exists():
            return f"{MARKER_FILE} marker at {candidate}"
    if DEFAULT_VAULT.exists() or not LEGACY_VAULT.exists():
        return f"default ({DEFAULT_VAULT})"
    return f"legacy default ({LEGACY_VAULT})"


def find_marker_upward(start: Optional[Path] = None) -> Optional[Path]:
    """Walk up from ``start`` (default: cwd) looking for ``.owl-vault``.

    Returns the directory containing the marker, or None if not found.
    Useful for hook scripts that want to fail silently when not in a vault.
    """
    base = (start or Path.cwd()).resolve()
    for candidate in [base, *base.parents]:
        if (candidate / MARKER_FILE).exists():
            return candidate
    return None
