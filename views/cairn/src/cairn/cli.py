"""``cairn`` CLI entry point."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Sequence

from cairn import __version__


PROG = "cairn"
DESCRIPTION = (
    "cairn — an LLM-first knowledge base. Atomic claims, flat directory, "
    "INDEX-driven retrieval. Sideline experiment parallel to owl. "
    "See docs/design-v0.md."
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=PROG, description=DESCRIPTION)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    # init
    sp_init = subparsers.add_parser("init", help="Initialize a cairn vault.")
    sp_init.add_argument("path", nargs="?", default=None, help="Vault path (default: ~/cairn-vault)")
    sp_init.add_argument("--refresh", action="store_true", help="Overwrite existing marker / template files")
    sp_init.add_argument("--no-activate", action="store_true", help="Do not set as active vault")

    # status
    sp_status = subparsers.add_parser("status", help="Show vault state and counts.")
    sp_status.add_argument("--vault", default=None, help="Override vault path")
    sp_status.add_argument("--json", action="store_true", help="JSON output")

    # index
    sp_index = subparsers.add_parser("index", help="Rebuild INDEX.md from entries/.")
    sp_index.add_argument("--vault", default=None, help="Override vault path")

    # search (delegates to searchcmd module which has its own argparse)
    sp_search = subparsers.add_parser(
        "search",
        help="Search the cairn vault.",
        add_help=False,
    )
    sp_search.add_argument("args", nargs=argparse.REMAINDER)

    # use
    sp_use = subparsers.add_parser("use", help="Switch the active vault.")
    sp_use.add_argument("path", help="Vault path to activate")

    return parser


def _run_init(args: argparse.Namespace) -> int:
    from cairn.initcmd import init_vault
    return init_vault(
        vault_arg=args.path,
        activate=not args.no_activate,
        refresh=args.refresh,
    )


def _run_status(args: argparse.Namespace) -> int:
    from cairn.statuscmd import show_status
    return show_status(vault_arg=args.vault, json_out=args.json)


def _run_index(args: argparse.Namespace) -> int:
    from cairn.indexcmd import rebuild_index
    return rebuild_index(vault_arg=args.vault)


def _run_search(rest: List[str]) -> int:
    from cairn.searchcmd import cli as search_cli
    return search_cli(rest)


def _run_use(args: argparse.Namespace) -> int:
    from cairn.vault import set_active_vault
    target = Path(args.path).expanduser().resolve()
    if not target.exists():
        print(f"error: vault path does not exist: {target}", file=sys.stderr)
        return 2
    if not target.is_dir():
        print(f"error: not a directory: {target}", file=sys.stderr)
        return 2
    set_active_vault(target)
    print(f"Active cairn vault set to: {target}")
    print()
    print("Next steps:")
    print("  cairn status   # confirm the new vault is recognized")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        build_parser().print_help()
        return 0

    # Pre-dispatch for search (same REMAINDER-bug workaround as owl)
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
    if command == "use":
        return _run_use(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
