"""Vault discovery for akasha.

akasha-vault is a local directory marked by a ``.akasha-vault`` file.
Discovery order (first hit wins):

1. ``--vault`` CLI flag
2. ``$AKASHA_VAULT`` environment variable
3. ``~/.config/akasha/active-vault`` config pointer
4. Walk up from cwd looking for a ``.akasha-vault`` marker
5. Default: ``~/omb/vault/akasha``
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

MARKER_FILE = ".akasha-vault"
USER_CONFIG_DIR = Path.home() / ".config" / "akasha"
ACTIVE_VAULT_FILE = USER_CONFIG_DIR / "active-vault"
DEFAULT_VAULT = Path.home() / "omb" / "vault" / "akasha"


def discover_vault(vault_arg: Optional[str] = None) -> Path:
    """Return the active vault path using the discovery chain."""
    # 1. explicit arg
    if vault_arg:
        return Path(vault_arg).expanduser().resolve()

    # 2. env var
    env = os.environ.get("AKASHA_VAULT")
    if env:
        return Path(env).expanduser().resolve()

    # 3. active-vault config
    if ACTIVE_VAULT_FILE.exists():
        text = ACTIVE_VAULT_FILE.read_text(encoding="utf-8").strip()
        if text:
            return Path(text).expanduser().resolve()

    # 4. marker walk
    cwd = Path.cwd()
    for ancestor in [cwd] + list(cwd.parents):
        if (ancestor / MARKER_FILE).exists():
            return ancestor.resolve()

    # 5. default
    return DEFAULT_VAULT.expanduser().resolve()


def discovery_source(vault_arg: Optional[str] = None) -> str:
    """Return a short human-readable string describing which discovery step fired."""
    if vault_arg:
        return "CLI --vault argument"
    if os.environ.get("AKASHA_VAULT"):
        return "$AKASHA_VAULT env var"
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
