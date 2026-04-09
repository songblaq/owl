#!/usr/bin/env python3
"""Backward-compatible CLI wrapper for ``owl.health``.

The actual health-check logic moved to ``src/owl/health.py`` so it can be
shared with the ``owl health`` CLI and the ``owl-health`` subagent. This
8-line wrapper preserves the documented invocation:

    python3 src/brain_health_check.py

It works without ``pip install`` because Python adds the script's directory
(``src/``) to ``sys.path[0]``, which makes the ``owl`` package importable
from its sibling location.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from owl.health import cli  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(cli())
