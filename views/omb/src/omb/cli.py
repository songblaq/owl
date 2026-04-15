"""omb — oh-my-brain, LLM-managed knowledge platform

External interface. Internal vault implementation (akasha) is not
exposed directly — all user-facing operations go through `omb`.

Architecture:
    sources/    shared raw input (immutable)
    vaults/
      akasha    primary vault — LLM-managed knowledge layer (internal)

Deprecated vaults (benchmark/experimental, no longer operated):
    owl / facet / lattice / cairn / wiki / rehalf / rezero
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from typing import List, Optional


# ── internal helpers ──────────────────────────────────────────────────────────

def _akasha(args: List[str]) -> int:
    """Delegate to the akasha vault engine. Internal use only."""
    path = shutil.which("akasha")
    if not path:
        print("omb: vault engine (akasha) not found on PATH.", file=sys.stderr)
        print("  Reinstall: cd views/akasha && pipx install -e .", file=sys.stderr)
        return 127
    return subprocess.call([path] + args)


def _flush_print(*args, **kwargs):
    """Print and flush immediately to keep output order correct with subprocess."""
    print(*args, **kwargs, flush=True)


# ── public commands ───────────────────────────────────────────────────────────

def cmd_status(args: List[str]) -> int:
    """Show vault status and entry counts."""
    from omb import __version__

    _flush_print(f"omb (oh-my-brain) v{__version__}")
    _flush_print("=" * 40)
    return _akasha(["status"] + args)


def cmd_search(args: List[str]) -> int:
    """Search the knowledge vault."""
    import argparse

    parser = argparse.ArgumentParser(prog="omb search", add_help=False)
    parser.add_argument("query", nargs="*")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--json", action="store_true")
    parsed, _ = parser.parse_known_args(args)

    query = " ".join(parsed.query)
    if not query:
        print("omb search: query required", file=sys.stderr)
        print("  usage: omb search <query> [--limit N] [--json]", file=sys.stderr)
        return 2

    search_args = [query, "--limit", str(parsed.limit)]
    if parsed.json:
        search_args.append("--json")

    return _akasha(["search"] + search_args)


def cmd_ingest(args: List[str]) -> int:
    """Add new knowledge to the vault.

    Examples:
        omb ingest notes.md
        omb ingest --text "..." --title "my-note"
        omb ingest --topic llm notes.md
        omb ingest --dry-run notes.md
    """
    if not args:
        print("omb ingest: source required", file=sys.stderr)
        print("  usage: omb ingest <file>", file=sys.stderr)
        print("         omb ingest --text \"...\" [--title <slug>]", file=sys.stderr)
        print("         omb ingest --topic <name> <file>", file=sys.stderr)
        return 2
    return _akasha(["ingest"] + args)


def cmd_health(args: List[str]) -> int:
    """Coverage check: how many sources have been ingested."""
    return _akasha(["health"] + args)


# ── command dispatch ──────────────────────────────────────────────────────────

COMMANDS = {
    "status": cmd_status,
    "search": cmd_search,
    "ingest": cmd_ingest,
    "health": cmd_health,
}

_deprecated = {
    "cairn": "omb ingest",
    "wiki": "omb ingest",
    "rehalf": "omb ingest",
    "rezero": "omb ingest",
    "owl": "omb search / omb ingest",
    "facet": "omb search / omb ingest",
    "lattice": "omb search / omb ingest",
}


def main(argv: Optional[List[str]] = None) -> None:
    args = argv if argv is not None else sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        _print_help()
        sys.exit(0)

    if args[0] in ("-V", "--version"):
        from omb import __version__
        print(f"omb {__version__}")
        sys.exit(0)

    cmd = args[0]
    rest = args[1:]

    if cmd in COMMANDS:
        sys.exit(COMMANDS[cmd](rest))

    if cmd in _deprecated:
        replacement = _deprecated[cmd]
        print(f"omb: '{cmd}' is deprecated — use '{replacement}' instead", file=sys.stderr)
        sys.exit(1)

    print(f"omb: unknown command '{cmd}'", file=sys.stderr)
    _print_help()
    sys.exit(2)


def _print_help() -> None:
    from omb import __version__
    print(f"omb (oh-my-brain) v{__version__}")
    print()
    print("Usage: omb <command> [args...]")
    print()
    print("Commands:")
    print("  status                Show vault status and counts")
    print("  search <query>        Search knowledge vault")
    print("    --limit N             Results per search (default: 5)")
    print("    --json                Machine-readable output")
    print("  ingest <file>         Add a file to the vault")
    print("    --text \"...\"          Add raw text directly")
    print("    --title <slug>        Filename hint (with --text)")
    print("    --topic <name>        Assign topic explicitly")
    print("    --dry-run             Preview without writing")
    print("  health                Coverage check: sources vs vault")
    print("    --json                Machine-readable output")
    print()
    print("Deprecated (use omb search / omb ingest instead):")
    print("  owl / facet / lattice / cairn / wiki / rehalf / rezero")
