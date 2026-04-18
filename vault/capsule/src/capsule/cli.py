from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence

from capsule import __version__
from capsule.buildcmd import run_build
from capsule.searchcmd import run_search
from capsule.statuscmd import run_status


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="capsule",
        description=(
            "capsule — read-only compiled bundle view for OMB. "
            "Build agent-facing documentation bundles from canonical source."
        ),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    sp_build = subparsers.add_parser("build", help="Build a read-only capsule bundle for a product.")
    sp_build.add_argument("product", help="Product key, e.g. openclaw or hermes-agent")
    sp_build.add_argument("--source", default=None, help="Override source root (default: ~/omb/input/<product>)")
    sp_build.add_argument("--vault-root", default=None, help="Override capsule vault root (default: ~/omb/brain/readonly)")
    sp_build.add_argument("--include-i18n", action="store_true", help="Include i18n docs copies when supported")
    sp_build.add_argument("--max-chars-per-part", type=int, default=None, help="Override ctx shard size")
    sp_build.add_argument("--skip-verify", action="store_true", help="Skip verify step after build")

    sp_search = subparsers.add_parser("search", help="Search a product capsule bundle.")
    sp_search.add_argument("product", help="Product key, e.g. openclaw or hermes-agent")
    sp_search.add_argument("query", nargs="+", help="Search query")
    sp_search.add_argument("--vault-root", default=None, help="Override capsule vault root")
    sp_search.add_argument("--limit", type=int, default=5, help="Max hits to show")
    sp_search.add_argument("--json", action="store_true", help="JSON output")

    sp_status = subparsers.add_parser("status", help="Show capsule vault status.")
    sp_status.add_argument("product", nargs="?", default=None, help="Optional product key")
    sp_status.add_argument("--vault-root", default=None, help="Override capsule vault root")
    sp_status.add_argument("--json", action="store_true", help="JSON output")

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    try:
        if args.command == "build":
            return run_build(
                product_name=args.product,
                source=args.source,
                vault_root=args.vault_root,
                include_i18n=args.include_i18n,
                max_chars_per_part=args.max_chars_per_part,
                skip_verify=args.skip_verify,
            )
        if args.command == "search":
            return run_search(
                product_name=args.product,
                query=" ".join(args.query),
                limit=args.limit,
                vault_root=args.vault_root,
                json_out=args.json,
            )
        if args.command == "status":
            return run_status(
                product_name=args.product,
                vault_root=args.vault_root,
                json_out=args.json,
            )
    except (FileNotFoundError, KeyError, RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
