"""``akasha`` CLI entry point.

omb platform / akasha vault — LLM-managed knowledge layer.

Commands:
    init        Initialize a new vault
    status      Show vault state
    index       Rebuild INDEX.md + GRAPH.tsv
    compile     Show compile status / dump entries for LLM to write narrative
    ingest      Add a new source: file path or raw text → entries/ + reindex
    search      3-layer search (compiled + entries + graph)
    health      Coverage check
    use         Switch active vault
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Sequence

from akasha import __version__


PROG = "akasha"
DESCRIPTION = (
    "akasha — LLM-managed knowledge vault (omb platform). "
    "Write: atomic entries. Read: LLM-compiled narrative docs + graph. "
    "Optimized for LLM-first retrieval inside Claude Code."
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=PROG, description=DESCRIPTION)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    # ── init ──────────────────────────────────────────────────────────────────
    sp_init = subparsers.add_parser("init", help="Initialize an akasha vault.")
    sp_init.add_argument("path", nargs="?", default=None,
                         help="Vault path (default: ~/omb/vault/akasha)")
    sp_init.add_argument("--refresh", action="store_true",
                         help="Overwrite existing marker / template files")
    sp_init.add_argument("--no-activate", action="store_true",
                         help="Do not set as active vault")

    # ── status ────────────────────────────────────────────────────────────────
    sp_status = subparsers.add_parser("status", help="Show vault state and entry counts.")
    sp_status.add_argument("--vault", default=None, help="Override vault path")
    sp_status.add_argument("--json", action="store_true", help="JSON output")

    # ── index ─────────────────────────────────────────────────────────────────
    sp_index = subparsers.add_parser("index", help="Rebuild INDEX.md and GRAPH.tsv.")
    sp_index.add_argument("--vault", default=None, help="Override vault path")

    # ── compile ───────────────────────────────────────────────────────────────
    sp_compile = subparsers.add_parser(
        "compile",
        help="Show compile status (--dry-run) or dump entries for LLM narrative writing.",
    )
    sp_compile.add_argument("--vault", default=None, help="Override vault path")
    sp_compile.add_argument(
        "--dump", default=None, metavar="TOPIC",
        help="Dump all entries for TOPIC — LLM reads this and writes compiled/<topic>.md",
    )
    sp_compile.add_argument("--topic", default=None, help="Alias for --dump")
    sp_compile.add_argument(
        "--dry-run", action="store_true",
        help="Show topic list with pending/compiled status (no LLM action)",
    )

    # ── ingest ────────────────────────────────────────────────────────────────
    sp_ingest = subparsers.add_parser(
        "ingest",
        help="Ingest a source into akasha: file path or raw text → entries/ + reindex.",
    )
    sp_ingest.add_argument(
        "source", nargs="?", default=None,
        help="File path to ingest (markdown/text). Omit to read from stdin.",
    )
    sp_ingest.add_argument(
        "--text", "-t", default=None, metavar="TEXT",
        help="Raw text content to ingest directly (instead of file).",
    )
    sp_ingest.add_argument(
        "--title", default=None,
        help="Title / slug hint for the source (used in filename).",
    )
    sp_ingest.add_argument(
        "--topic", default=None,
        help="Primary topic to assign entries. Auto-detected if omitted.",
    )
    sp_ingest.add_argument(
        "--vault", default=None, help="Override vault path",
    )
    sp_ingest.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be ingested without writing files.",
    )

    # ── search ────────────────────────────────────────────────────────────────
    sp_search = subparsers.add_parser(
        "search",
        help="Search the vault (3-layer: compiled + entries + graph).",
        add_help=False,
    )
    sp_search.add_argument("args", nargs=argparse.REMAINDER)

    # ── health ────────────────────────────────────────────────────────────────
    sp_health = subparsers.add_parser("health", help="Coverage check: sources/ vs entries.")
    sp_health.add_argument("--vault", default=None, help="Override vault path")
    sp_health.add_argument("--json", action="store_true", help="JSON output")

    # ── use ───────────────────────────────────────────────────────────────────
    sp_use = subparsers.add_parser("use", help="Switch the active vault.")
    sp_use.add_argument("path", help="Vault path to activate")

    return parser


# ── dispatch helpers ──────────────────────────────────────────────────────────

def _run_init(args: argparse.Namespace) -> int:
    from akasha.initcmd import init_vault
    return init_vault(
        vault_arg=args.path,
        activate=not args.no_activate,
        refresh=args.refresh,
    )


def _run_status(args: argparse.Namespace) -> int:
    from akasha.statuscmd import show_status
    return show_status(vault_arg=args.vault, json_out=args.json)


def _run_index(args: argparse.Namespace) -> int:
    from akasha.indexcmd import rebuild_index
    return rebuild_index(vault_arg=args.vault)


def _run_compile(args: argparse.Namespace) -> int:
    from akasha.compiler import run_compile
    topic = getattr(args, "dump", None) or args.topic
    return run_compile(
        vault_arg=args.vault,
        topic_filter=topic,
        dry_run=args.dry_run,
    )


def _run_ingest(args: argparse.Namespace) -> int:
    from akasha.ingestcmd import run_ingest
    return run_ingest(
        vault_arg=args.vault,
        source_path=args.source,
        text=args.text,
        title=args.title,
        topic=args.topic,
        dry_run=args.dry_run,
    )


def _run_search(rest: List[str]) -> int:
    from akasha.searchcmd import cli as search_cli
    return search_cli(rest)


def _run_health(args: argparse.Namespace) -> int:
    from akasha.healthcmd import run_health
    return run_health(vault_arg=args.vault, json_out=args.json)


def _run_use(args: argparse.Namespace) -> int:
    from akasha.vault import set_active_vault
    target = Path(args.path).expanduser().resolve()
    if not target.exists():
        print(f"error: vault path does not exist: {target}", file=sys.stderr)
        return 2
    if not target.is_dir():
        print(f"error: not a directory: {target}", file=sys.stderr)
        return 2
    set_active_vault(target)
    print(f"Active akasha vault set to: {target}")
    print()
    print("Next steps:")
    print("  akasha status   # confirm the new vault is recognized")
    return 0


# ── main ──────────────────────────────────────────────────────────────────────

def main(argv: Optional[Sequence[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        build_parser().print_help()
        return 0

    # Pre-dispatch: search uses REMAINDER so bypass normal parse
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
    if command == "compile":
        return _run_compile(args)
    if command == "ingest":
        return _run_ingest(args)
    if command == "health":
        return _run_health(args)
    if command == "use":
        return _run_use(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
