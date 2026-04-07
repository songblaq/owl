"""User-global configuration for owl.

Lives at ``~/.owl/`` and stores small text files only:

    ~/.owl/
    ├── active-vault     ← single line: absolute path to currently active vault
    └── installed-at     ← ISO datetime when ``owl setup`` last ran

This dir is intentionally tiny. The vault stores knowledge, the project repo
stores logic, and ``~/.owl/`` only holds the user-level "which vault am I
working with right now" pointer.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from owl.vault import ACTIVE_VAULT_FILE, USER_CONFIG_DIR


def ensure_config_dir() -> Path:
    """Create ``~/.owl/`` if it doesn't exist. Return the path."""
    USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return USER_CONFIG_DIR


def set_active_vault(path: Path) -> None:
    """Persist the active vault path so future ``owl`` invocations find it."""
    ensure_config_dir()
    ACTIVE_VAULT_FILE.write_text(str(path.expanduser().resolve()) + "\n", encoding="utf-8")


def get_active_vault() -> Optional[Path]:
    """Return the persisted active vault path, or None if never set."""
    if not ACTIVE_VAULT_FILE.exists():
        return None
    text = ACTIVE_VAULT_FILE.read_text(encoding="utf-8").strip()
    if not text:
        return None
    return Path(text)


def clear_active_vault() -> None:
    """Forget the active vault setting."""
    if ACTIVE_VAULT_FILE.exists():
        ACTIVE_VAULT_FILE.unlink()


def mark_setup_completed() -> None:
    """Record the timestamp of the last successful ``owl setup`` run."""
    ensure_config_dir()
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (USER_CONFIG_DIR / "installed-at").write_text(stamp + "\n", encoding="utf-8")


def get_setup_timestamp() -> Optional[str]:
    """Return the ISO timestamp recorded by ``owl setup``, if any."""
    f = USER_CONFIG_DIR / "installed-at"
    if not f.exists():
        return None
    return f.read_text(encoding="utf-8").strip()
