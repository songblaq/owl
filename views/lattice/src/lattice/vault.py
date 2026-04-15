"""Vault discovery for lattice.

lattice-vault is a local directory marked by a ``.lattice-vault`` file.
Discovery order (first hit wins):

1. ``--vault`` CLI flag
2. ``$LATTICE_VAULT`` environment variable
3. ``~/.lattice/active-vault`` config pointer
4. Walk up from cwd looking for a ``.lattice-vault`` marker
5. Default: ``~/lattice-vault``
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

MARKER_FILE = ".lattice-vault"
USER_CONFIG_DIR = Path.home() / ".lattice"
ACTIVE_VAULT_FILE = USER_CONFIG_DIR / "active-vault"
DEFAULT_VAULT = Path.home() / "lattice-vault"


def discover_vault(vault_arg: Optional[str] = None) -> Path:
    """Return the active vault path using the discovery chain."""
    if vault_arg:
        return Path(vault_arg).expanduser().resolve()
    env = os.environ.get("LATTICE_VAULT")
    if env:
        return Path(env).expanduser().resolve()
    if ACTIVE_VAULT_FILE.exists():
        text = ACTIVE_VAULT_FILE.read_text(encoding="utf-8").strip()
        if text:
            return Path(text).expanduser().resolve()
    cwd = Path.cwd()
    for ancestor in [cwd] + list(cwd.parents):
        if (ancestor / MARKER_FILE).exists():
            return ancestor.resolve()
    return DEFAULT_VAULT.expanduser().resolve()


def discovery_source(vault_arg: Optional[str] = None) -> str:
    if vault_arg:
        return "CLI --vault argument"
    if os.environ.get("LATTICE_VAULT"):
        return "$LATTICE_VAULT env var"
    if ACTIVE_VAULT_FILE.exists():
        return f"active-vault config ({ACTIVE_VAULT_FILE})"
    cwd = Path.cwd()
    for ancestor in [cwd] + list(cwd.parents):
        if (ancestor / MARKER_FILE).exists():
            return f"marker walk ({ancestor / MARKER_FILE})"
    return f"default ({DEFAULT_VAULT})"


def ensure_config_dir() -> Path:
    USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return USER_CONFIG_DIR


def set_active_vault(path: Path) -> None:
    ensure_config_dir()
    ACTIVE_VAULT_FILE.write_text(str(path.expanduser().resolve()) + "\n", encoding="utf-8")
