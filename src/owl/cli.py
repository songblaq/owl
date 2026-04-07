"""owl CLI dispatcher (the ``owl`` command).

CLI surface:
    owl status                   — vault summary
    owl init [path] [--hooks]    — initialize a vault
    owl setup                    — post-install setup (env diag + symlinks)
    owl use <vault>              — switch active vault
    owl search "<query>"         — token-scored vault search
    owl health [--json]          — vault integrity check (8 rules)
    owl ingest <path>            — file a candidate into raw/
    owl compile <raw-path>       — hand off to owl-compiler subagent
    owl file <output> <kind>     — file an output back into compiled/
    owl hook <name>              — hook dispatcher (called by Claude Code)

Note on the name: the CLI is ``owl`` because it implements Karpathy's
"LLM Wiki" idea (LLM Wiki → wl → owl, plus the wisdom-keeper metaphor).
``brain`` was rejected because macOS ships ``/usr/sbin/ab`` and we wanted
zero risk of confusion. ``owl`` lives in its own namespace and pairs
naturally with future Brain-family tools (Brain Memory, etc.).

Design notes:
    - Each subcommand is lazy-imported on first use to keep ``owl --help``
      and ``owl status`` startup time tiny (no JSON encoder load for a
      status check, no health check load for a search, etc.).
    - All subcommands share vault discovery via ``owl.vault``.
    - The dispatcher is built with argparse subparsers for clean ``--help``
      output and shell completion compatibility.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Sequence

from owl import __version__


PROG = "owl"
DESCRIPTION = (
    "owl — a personal LLM-maintained wiki. Karpathy LLM Wiki implementation. "
    "Pairs deterministic vault operations (search, health) with LLM-driven "
    "wiki maintenance via Claude Code hooks, slash commands, and owl-* subagents."
)

# Empty extension point for future planned subcommands.
PLANNED_STUBS: dict = {}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=PROG, description=DESCRIPTION)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    # status
    sp_status = subparsers.add_parser("status", help="Show active vault, version, and health summary.")
    sp_status.add_argument("--vault", "--brain", dest="vault", default=None, help="Override vault path")
    sp_status.add_argument("--json", action="store_true", help="JSON output")

    # init
    sp_init = subparsers.add_parser("init", help="Initialize a vault (write .owl-vault, CLAUDE.md, .claude/).")
    sp_init.add_argument("path", nargs="?", default=None, help="Vault path (default: prompt)")
    hooks_group = sp_init.add_mutually_exclusive_group()
    hooks_group.add_argument("--hooks", dest="hooks", action="store_true", default=None, help="Install Claude Code hooks (no prompt)")
    hooks_group.add_argument("--no-hooks", dest="hooks", action="store_false", help="Skip hook installation (no prompt)")
    sp_init.add_argument("--refresh", action="store_true", help="Overwrite existing CLAUDE.md / settings.json")
    sp_init.add_argument("--non-interactive", action="store_true", help="Never prompt; fail if input would be needed")
    sp_init.add_argument("--no-activate", action="store_true", help="Do not set this vault as active")

    # setup
    sp_setup = subparsers.add_parser("setup", help="Post-install setup: diagnose env, create symlinks, offer init.")
    sp_setup.add_argument("--non-interactive", action="store_true", help="Never prompt")

    # use
    sp_use = subparsers.add_parser("use", help="Switch the active vault.")
    sp_use.add_argument("path", help="Vault path to activate")

    # search
    sp_search = subparsers.add_parser(
        "search",
        help="Search vault raw/compiled/research/views without RAG.",
        add_help=False,
    )
    sp_search.add_argument("args", nargs=argparse.REMAINDER)

    # health
    sp_health = subparsers.add_parser(
        "health",
        help="Run vault integrity checks (8 rules).",
        add_help=False,
    )
    sp_health.add_argument("args", nargs=argparse.REMAINDER)

    # hook (invoked by Claude Code, not directly by users)
    sp_hook = subparsers.add_parser(
        "hook",
        help="Hook dispatcher (called by Claude Code, not by users directly).",
    )
    sp_hook.add_argument(
        "name",
        choices=["session_start", "user_prompt", "post_tool_use", "pre_compact", "stop"],
        help="Hook lifecycle event name",
    )

    # ingest — deterministic primitive
    sp_ingest = subparsers.add_parser(
        "ingest",
        help="Move a candidate file into raw/ with naming convention. LLM follow-up via /owl-ingest.",
    )
    sp_ingest.add_argument("path", help="Source file path")
    sp_ingest.add_argument("--vault", "--brain", dest="vault", default=None, help="Override vault path")
    sp_ingest.add_argument("--copy", action="store_true", help="Copy instead of move (preserve original)")

    # compile — metadata for owl-compiler subagent
    sp_compile = subparsers.add_parser(
        "compile",
        help="Print compile metadata for a raw file (for the owl-compiler subagent).",
    )
    sp_compile.add_argument("path", help="Raw file path (absolute or vault-relative)")
    sp_compile.add_argument("--vault", "--brain", dest="vault", default=None, help="Override vault path")

    # file — output filing
    sp_file = subparsers.add_parser(
        "file",
        help="Move an output (slide/figure/visual) into vault/outputs/<kind>/.",
    )
    sp_file.add_argument("path", help="Output file path")
    sp_file.add_argument("kind", choices=["slide", "slides", "figure", "figures", "visual", "visuals"], help="Output kind")
    sp_file.add_argument("--vault", "--brain", dest="vault", default=None, help="Override vault path")

    # Planned stubs (currently empty)
    for name, (phase, help_text) in PLANNED_STUBS.items():
        subparsers.add_parser(name, help=f"{help_text}  [{phase} — not yet implemented]")

    return parser


def _run_search(rest: List[str]) -> int:
    from owl.search import cli as search_cli
    return search_cli(rest)


def _run_health(rest: List[str]) -> int:
    from owl.health import cli as health_cli
    return health_cli(rest)


def _run_status(args: argparse.Namespace) -> int:
    from owl.statuscmd import show_status
    return show_status(vault_arg=args.vault, json_out=args.json)


def _run_init(args: argparse.Namespace) -> int:
    from owl.initcmd import init_vault
    return init_vault(
        vault_arg=args.path,
        hooks=args.hooks,
        refresh=args.refresh,
        interactive=not args.non_interactive,
        activate=not args.no_activate,
    )


def _run_setup(args: argparse.Namespace) -> int:
    from owl.setupcmd import setup
    return setup(interactive=not args.non_interactive)


def _run_use(args: argparse.Namespace) -> int:
    from owl.config import set_active_vault
    target = Path(args.path).expanduser().resolve()
    if not target.exists():
        print(f"error: vault path does not exist: {target}", file=sys.stderr)
        return 2
    if not target.is_dir():
        print(f"error: not a directory: {target}", file=sys.stderr)
        return 2
    set_active_vault(target)
    print(f"Active vault set to: {target}")
    return 0


def _run_hook(args: argparse.Namespace) -> int:
    from owl.hooks import dispatch
    return dispatch(args.name)


def _run_ingest(args: argparse.Namespace) -> int:
    from owl.ingestcmd import ingest_file
    return ingest_file(source=args.path, vault_arg=args.vault, copy=args.copy)


def _run_compile(args: argparse.Namespace) -> int:
    from owl.ingestcmd import compile_metadata
    return compile_metadata(raw_path=args.path, vault_arg=args.vault)


def _run_file(args: argparse.Namespace) -> int:
    from owl.ingestcmd import file_output
    return file_output(output_path=args.path, kind=args.kind, vault_arg=args.vault)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        parser.print_help()
        return 0

    args = parser.parse_args(argv)
    command = args.command

    if command == "search":
        return _run_search(args.args or [])
    if command == "health":
        return _run_health(args.args or [])
    if command == "status":
        return _run_status(args)
    if command == "init":
        return _run_init(args)
    if command == "setup":
        return _run_setup(args)
    if command == "use":
        return _run_use(args)
    if command == "hook":
        return _run_hook(args)
    if command == "ingest":
        return _run_ingest(args)
    if command == "compile":
        return _run_compile(args)
    if command == "file":
        return _run_file(args)

    if command in PLANNED_STUBS:
        phase, help_text = PLANNED_STUBS[command]
        print(
            f"owl: '{command}' is planned for {phase} and not yet implemented.\n"
            f"     {help_text}",
            file=sys.stderr,
        )
        return 2

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
