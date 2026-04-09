"""owl — a personal LLM-maintained wiki.

You bring the sources. The LLM does everything else — files them,
cross-references them, keeps the wiki alive.

Implements Andrej Karpathy's "LLM Wiki" pattern (2026), spiritually
descended from Vannevar Bush's Memex (1945).

This package is the operational layer that turns owl's policy docs
(under ``docs/``) into actual Claude Code behavior — CLI dispatcher, hooks,
slash commands, and owl-* subagents.

The vault (``~/owl-vault`` by default) stays pure data. Behavior lives
here in the project repo and gets wired into Claude Code via ``owl init``.
"""

__version__ = "0.1.0"
