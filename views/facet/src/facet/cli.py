"""``facet`` CLI entry point."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Sequence

from facet import __version__


PROG = "facet"
DESCRIPTION = (
    "facet — shard-aware LLM knowledge base with alias resolution. "
    "Evolution of cairn: same atomic-claim philosophy with ALIASES.tsv "
    "and per-shard _index.md for structured retrieval."
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=PROG, description=DESCRIPTION)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    # init
    sp_init = subparsers.add_parser("init", help="Initialize a facet vault.")
    sp_init.add_argument("path", nargs="?", default=None, help="Vault path (default: ~/facet-vault)")
    sp_init.add_argument("--refresh", action="store_true", help="Overwrite existing marker / template files")
    sp_init.add_argument("--no-activate", action="store_true", help="Do not set as active vault")

    # status
    sp_status = subparsers.add_parser("status", help="Show vault state and shard counts.")
    sp_status.add_argument("--vault", default=None, help="Override vault path")
    sp_status.add_argument("--json", action="store_true", help="JSON output")

    # index
    sp_index = subparsers.add_parser("index", help="Rebuild MANIFEST.md and all shard _index.md files.")
    sp_index.add_argument("--vault", default=None, help="Override vault path")

    # search
    sp_search = subparsers.add_parser(
        "search",
        help="Search the facet vault (alias-aware).",
        add_help=False,
    )
    sp_search.add_argument("args", nargs=argparse.REMAINDER)

    # health
    sp_health = subparsers.add_parser("health", help="Coverage check: sources/ vs shard entries.")
    sp_health.add_argument("--vault", default=None, help="Override vault path")
    sp_health.add_argument("--json", action="store_true", help="JSON output")

    # compile
    sp_compile = subparsers.add_parser(
        "compile",
        help="Compile shard entries into narrative docs (Layer 2).",
    )
    sp_compile.add_argument("--vault", default=None, help="Override vault path")
    sp_compile.add_argument("--shard", default=None, help="Compile only one shard")

    # use
    sp_use = subparsers.add_parser("use", help="Switch the active vault.")
    sp_use.add_argument("path", help="Vault path to activate")

    return parser


def _run_init(args: argparse.Namespace) -> int:
    from facet.initcmd import init_vault
    return init_vault(
        vault_arg=args.path,
        activate=not args.no_activate,
        refresh=args.refresh,
    )


def _run_status(args: argparse.Namespace) -> int:
    from facet.statuscmd import show_status
    return show_status(vault_arg=args.vault, json_out=args.json)


def _run_index(args: argparse.Namespace) -> int:
    from facet.indexcmd import rebuild_index
    return rebuild_index(vault_arg=args.vault)


def _run_search(rest: List[str]) -> int:
    from facet.searchcmd import cli as search_cli
    return search_cli(rest)


def _run_health(args: argparse.Namespace) -> int:
    from facet.healthcmd import run_health
    return run_health(vault_arg=args.vault, json_out=args.json)


def _run_compile(args: argparse.Namespace) -> int:
    from facet.compilecmd import run_compile
    return run_compile(vault_arg=args.vault, shard_filter=args.shard)


def _run_use(args: argparse.Namespace) -> int:
    from facet.vault import set_active_vault
    target = Path(args.path).expanduser().resolve()
    if not target.exists():
        print(f"error: vault path does not exist: {target}", file=sys.stderr)
        return 2
    if not target.is_dir():
        print(f"error: not a directory: {target}", file=sys.stderr)
        return 2
    set_active_vault(target)
    print(f"Active facet vault set to: {target}")
    print()
    print("Next steps:")
    print("  facet status   # confirm the new vault is recognized")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        build_parser().print_help()
        return 0

    # Pre-dispatch for search (same REMAINDER-bug workaround as cairn)
    if argv[0] == "search":
        return _run_search(list(argv[1:]))

    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command

    if command == "init":
        return _run_init(args)
    if command == "status":
        return _run_status(args)
    if command == "index":
        return _run_index(args)
    if command == "health":
        return _run_health(args)
    if command == "compile":
        return _run_compile(args)
    if command == "use":
        return _run_use(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
