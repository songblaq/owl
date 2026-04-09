"""User-global configuration for owl.

Lives at ``~/.owl/`` and stores small text files only:

    ~/.owl/
    ├── active-vault     ← single line: absolute path to currently active vault
    ├── installed-at     ← ISO datetime when ``owl setup`` last ran
    └── machine.json     ← optional: machine identity (hostname, role, primary)

This dir is intentionally tiny. The vault stores knowledge, the project repo
stores logic, and ``~/.owl/`` only holds the user-level "which vault am I
working with right now" pointer — plus optional machine identity for
multi-machine deployments.

Multi-machine model (see docs/multi-machine-setup-v0.md):

- Each machine has its own ``~/.owl/`` and its own project repo clone
- Each machine's ``active-vault`` points to the LOCAL path of the vault
  (which may be synced content from a primary machine or a separate copy)
- ``machine.json`` records role (primary/mirror/client) for clarity
"""
from __future__ import annotations

import json
import platform
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from owl.vault import ACTIVE_VAULT_FILE, USER_CONFIG_DIR

MACHINE_FILE = USER_CONFIG_DIR / "machine.json"


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


def detect_machine() -> dict:
    """Return the current machine's identity (hostname, os, arch).

    Used both for generating a default machine.json and for owl status
    display on multi-machine setups.
    """
    return {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "os_release": platform.release(),
        "arch": platform.machine(),
        "python": platform.python_version(),
    }


def get_machine_info() -> Optional[dict]:
    """Return the persisted machine info from ~/.owl/machine.json, or None.

    The file is optional. Its presence signals the user has opted into
    multi-machine tracking. Schema:

        {
          "hostname": "LucaBlaiMacmini",
          "role": "primary" | "mirror" | "client",
          "primary": true | false,
          "vault_path": "/Users/.../owl-vault",
          "os": "Darwin",
          "os_release": "25.3.0",
          "arch": "arm64",
          "python": "3.14.3",
          "recorded_at": "2026-04-08T..."
        }
    """
    if not MACHINE_FILE.exists():
        return None
    try:
        return json.loads(MACHINE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def set_machine_info(
    *,
    role: str = "primary",
    primary: bool = True,
    vault_path: Optional[Path] = None,
    extra: Optional[dict] = None,
) -> dict:
    """Write ~/.owl/machine.json with current machine identity + role.

    Called by ``owl setup --mark-primary`` or similar. Auto-detects
    hostname/os/arch/python via detect_machine(). Caller decides role.
    """
    ensure_config_dir()
    payload = {
        **detect_machine(),
        "role": role,
        "primary": primary,
        "vault_path": str(vault_path) if vault_path else None,
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    if extra:
        payload.update(extra)
    MACHINE_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return payload
