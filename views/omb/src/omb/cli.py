"""omb — unified CLI dispatcher for oh-my-brain.

Usage:
    omb status                  # all views at a glance
    omb owl <subcommand>        # delegate to owl CLI
    omb cairn <subcommand>      # delegate to cairn CLI
    omb wiki <subcommand>       # wiki view operations
    omb search <query>          # search across all views
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from typing import List, Optional


def _delegate(cli_name: str, args: List[str]) -> int:
    """Run an external CLI, return its exit code."""
    path = shutil.which(cli_name)
    if not path:
        print(f"omb: '{cli_name}' CLI not found on PATH.", file=sys.stderr)
        print(f"  Install it: cd views/{cli_name} && pipx install -e .", file=sys.stderr)
        return 127
    return subprocess.call([path] + args)


def _flush_print(*args, **kwargs):
    """Print and flush immediately to keep output order correct with subprocess."""
    print(*args, **kwargs, flush=True)


def cmd_status(args: List[str]) -> int:
    """Show unified status of all views."""
    from omb import __version__

    _flush_print(f"omb (oh-my-brain) v{__version__}")
    _flush_print("=" * 40)

    # owl
    _flush_print("\n--- owl ---")
    owl_path = shutil.which("owl")
    if owl_path:
        subprocess.call([owl_path, "status"] + args)
    else:
        _flush_print("  (not installed)")

    # cairn
    _flush_print("\n--- cairn ---")
    cairn_path = shutil.which("cairn")
    if cairn_path:
        subprocess.call([cairn_path, "status"] + args)
    else:
        _flush_print("  (not installed)")

    # wiki
    _flush_print("\n--- wiki ---")
    _flush_print("  (planned — no CLI yet)")

    return 0


def cmd_search(args: List[str]) -> int:
    """Search across all installed views."""
    import argparse

    parser = argparse.ArgumentParser(prog="omb search", add_help=False)
    parser.add_argument("query", nargs="*")
    parser.add_argument("--view", choices=["owl", "cairn", "all"], default="all")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--json", action="store_true")
    parsed, remaining = parser.parse_known_args(args)

    query = " ".join(parsed.query)
    if not query:
        print("omb search: query required", file=sys.stderr)
        print("  usage: omb search <query> [--view owl|cairn|all] [--limit N]", file=sys.stderr)
        return 2

    search_args = [query, "--limit", str(parsed.limit)]
    if parsed.json:
        search_args.append("--json")

    found_any = False

    if parsed.view in ("owl", "all"):
        owl_path = shutil.which("owl")
        if owl_path:
            found_any = True
            if parsed.view == "all":
                _flush_print("--- owl ---")
            subprocess.call([owl_path, "search"] + search_args)
            if parsed.view == "all":
                _flush_print()

    if parsed.view in ("cairn", "all"):
        cairn_path = shutil.which("cairn")
        if cairn_path:
            found_any = True
            if parsed.view == "all":
                _flush_print("--- cairn ---")
            subprocess.call([cairn_path, "search"] + search_args)

    if not found_any:
        print("omb search: no search backends available", file=sys.stderr)
        return 1

    return 0


COMMANDS = {
    "status": cmd_status,
    "search": cmd_search,
}

DELEGATE_VIEWS = {"owl", "cairn"}


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

    # omb owl ... / omb cairn ...
    if cmd in DELEGATE_VIEWS:
        sys.exit(_delegate(cmd, rest))

    # omb status / omb search ...
    if cmd in COMMANDS:
        sys.exit(COMMANDS[cmd](rest))

    # omb wiki ... (placeholder)
    if cmd == "wiki":
        print("omb wiki: not yet implemented (Phase V)")
        print("  See: views/wiki/docs/wiki-view-spec.md")
        sys.exit(0)

    print(f"omb: unknown command '{cmd}'", file=sys.stderr)
    _print_help()
    sys.exit(2)


def _print_help() -> None:
    from omb import __version__
    print(f"omb (oh-my-brain) v{__version__}")
    print()
    print("Usage: omb <command> [args...]")
    print()
    print("Views:")
    print("  owl <subcommand>      Delegate to owl CLI (LLM Wiki)")
    print("  cairn <subcommand>    Delegate to cairn CLI (atomic claims)")
    print("  wiki <subcommand>     Wiki view (planned)")
    print()
    print("Unified commands:")
    print("  status                Show all views at a glance")
    print("  search <query>        Search across all views")
    print("    --view owl|cairn|all  Restrict to one view (default: all)")
    print("    --limit N             Results per view (default: 5)")
    print()
    print("Examples:")
    print("  omb status")
    print("  omb owl search 'karpathy'")
    print("  omb cairn status --json")
    print("  omb search 'filing loop'")
    print("  omb search 'wiki' --view cairn --limit 3")
