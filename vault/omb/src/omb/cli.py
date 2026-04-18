"""omb — oh-my-brain, LLM-managed knowledge platform

External interface. Internal vault implementation (akasha) is not
exposed directly — all user-facing operations go through `omb`.

Architecture:
    .omb/
      source/   shared raw input (immutable)
      vault/    akasha — primary writable vault, capsule — read-only bundle view
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
        print("  Reinstall: cd vault/akasha && pipx install -e .", file=sys.stderr)
        return 127
    return subprocess.call([path] + args)


def _capsule(args: List[str]) -> int:
    """Delegate to the capsule bundle engine. Internal use only."""
    path = shutil.which("capsule")
    if not path:
        print("omb: capsule view not found on PATH.", file=sys.stderr)
        print("  Reinstall: cd vault/capsule && pipx install -e .", file=sys.stderr)
        return 127
    return subprocess.call([path] + args)


def _flush_print(*args, **kwargs):
    """Print and flush immediately to keep output order correct with subprocess."""
    print(*args, **kwargs, flush=True)


# ── public commands ───────────────────────────────────────────────────────────

def cmd_status(args: List[str]) -> int:
    """omb status — 현재 지식 · 제품번들 · 벤치 상태."""
    from omb.wiki_ops import wiki_status
    return wiki_status()


def cmd_search(args: List[str]) -> int:
    """omb search — 지식 + 관련 제품번들 자동 첨부."""
    import argparse
    import os
    from pathlib import Path
    from omb.wiki_ops import wiki_search

    parser = argparse.ArgumentParser(prog="omb search", add_help=False)
    parser.add_argument("query", nargs="*")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--no-capsule", action="store_true", help="Skip capsule attach")
    parsed, _ = parser.parse_known_args(args)

    query = " ".join(parsed.query)
    if not query:
        print("omb search: query required", file=sys.stderr)
        print("  usage: omb search <query> [--limit N] [--no-capsule]", file=sys.stderr)
        print("  note:  searches wiki (MAIN). For akasha backup: `omb akasha search`", file=sys.stderr)
        return 2

    rc = wiki_search(query, limit=parsed.limit)

    if parsed.no_capsule:
        return rc

    capsule_root = Path(os.path.expanduser("~/omb/brain/readonly"))
    if not capsule_root.is_dir():
        return rc

    q_lower = query.lower()
    for product_dir in sorted(capsule_root.iterdir()):
        if not product_dir.is_dir() or product_dir.name.startswith("."):
            continue
        product = product_dir.name
        if product.lower() in q_lower:
            _flush_print("")
            _flush_print(f"── 제품번들: {product} ─────────────────────────────")
            _capsule(["search", product, query, "--limit", "3"])

    return rc


def cmd_ingest(args: List[str]) -> int:
    """omb ingest — 새 페이지 뼈대 생성. 내용은 LLM 이 편집."""
    from omb.wiki_ops import wiki_new
    if len(args) < 2:
        print("usage: omb ingest <유형> <이름>", file=sys.stderr)
        print("  유형: 개체 / 개념 / 원본요약 / 합성", file=sys.stderr)
        return 2
    kind_map = {"개체": "entities", "개념": "concepts", "원본요약": "sources", "합성": "syntheses",
                "entities": "entities", "concepts": "concepts", "sources": "sources", "syntheses": "syntheses"}
    kind = kind_map.get(args[0], args[0])
    return wiki_new(kind, " ".join(args[1:]))


def cmd_health(args: List[str]) -> int:
    """Coverage check: Tier 0 / Tier 1 violations surface loudly (P1.2).

    --legacy: old permissive output (delegates to akasha).
    """
    if "--legacy" in args:
        return _akasha(["health"] + [a for a in args if a != "--legacy"])
    from omb.vault_ops import health_strict
    return health_strict()


def cmd_capsule(args: List[str]) -> int:
    """Access the read-only capsule bundle view."""
    return _capsule(args)


def cmd_supersede(args: List[str]) -> int:
    """Enforce P0.1 Truth singularity: move old entries to superseded/.

    Usage: omb supersede <new-id> --replaces <old-id-1> [<old-id-2> ...]
    """
    import argparse
    parser = argparse.ArgumentParser(prog="omb supersede", add_help=False)
    parser.add_argument("new_id")
    parser.add_argument("--replaces", nargs="+", required=True)
    try:
        parsed = parser.parse_args(args)
    except SystemExit:
        print("  usage: omb supersede <new-id> --replaces <old-id-1> [<old-id-2> ...]", file=sys.stderr)
        return 2
    from omb.vault_ops import supersede
    return supersede(parsed.new_id, parsed.replaces)


def cmd_audit(args: List[str]) -> int:
    """Emit AUDIT.md (default) or JSON (--json). Tier 0/1 violations. No mutation."""
    from omb.vault_ops import audit, audit_json
    if "--json" in args:
        import json as _json
        result = audit_json()
        print(_json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    return audit()


def cmd_validate(args: List[str]) -> int:
    """T1-A: contract v2 validation (C1..C6). Report only, no mutation.

    Usage:
        omb validate                    # all entries
        omb validate --entry <id>       # single
        omb validate --json
    """
    import argparse
    parser = argparse.ArgumentParser(prog="omb validate", add_help=False)
    parser.add_argument("--entry")
    parser.add_argument("--json", action="store_true")
    parsed, _ = parser.parse_known_args(args)
    from omb.validator import validate_vault, format_report, validate_to_json
    report = validate_vault(entry_id=parsed.entry)
    if parsed.json:
        import json as _json
        print(_json.dumps(validate_to_json(report), indent=2, ensure_ascii=False))
    else:
        print(format_report(report))
    return 1 if report.critical_count() > 0 else 0


def cmd_rebuild(args: List[str]) -> int:
    """T1-C: rebuild rc vault from ~/omb/source/. Skeleton.

    Usage:
        omb rebuild --dry-run       # show plan
        omb rebuild --apply         # create akasha-rc1 (or specified) from source
    """
    from omb.vault_ops import rebuild_plan, rebuild_apply
    if "--apply" in args:
        return rebuild_apply()
    return rebuild_plan()


def cmd_import(args: List[str]) -> int:
    """I-A: import external knowledge files through normalize gate.

    Usage:
        omb import <path> [--normalize]     # reject unless normalized
    """
    from omb.vault_ops import import_normalize
    if not args:
        print("usage: omb import <path> [--normalize]", file=sys.stderr)
        return 2
    path = args[0]
    normalize = "--normalize" in args
    return import_normalize(path, normalize)


# ── command dispatch ──────────────────────────────────────────────────────────

def cmd_akasha(args: List[str]) -> int:
    """INACTIVE 백업 레이어 — `omb akasha <sub>` 로만 명시 접근. Re:Zero 2026-04-18."""
    if not args:
        print("omb akasha: INACTIVE backup layer. Explicit access only.", file=sys.stderr)
        print("  subcommands: status / search / ingest / health / audit / validate", file=sys.stderr)
        print("               supersede / rebuild / import", file=sys.stderr)
        return 2
    sub = args[0]
    rest = args[1:]
    if sub == "health":
        return cmd_health(rest)
    if sub == "audit":
        return cmd_audit(rest)
    if sub == "validate":
        return cmd_validate(rest)
    if sub == "rebuild":
        return cmd_rebuild(rest)
    if sub == "import":
        return cmd_import(rest)
    if sub == "supersede":
        return cmd_supersede(rest)
    # fallthrough to akasha CLI
    return _akasha([sub] + rest)


COMMANDS = {
    "status": cmd_status,
    "search": cmd_search,
    "ingest": cmd_ingest,
    "capsule": cmd_capsule,
    "akasha": cmd_akasha,
}

_deprecated: dict[str, str] = {}


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
    print("  status                omb 현황 (지식 · 제품번들)")
    print("  search <query>        지식 검색 (관련 제품번들 자동 첨부)")
    print("    --limit N             결과 개수 (기본 10)")
    print("    --no-capsule          제품번들 첨부 비활성")
    print("  ingest <유형> <이름>  새 페이지 뼈대 생성 후 내용은 LLM 이 채움")
    print("                        유형: 개체 / 개념 / 원본요약 / 합성")
    print("  capsule ...           제품 번들 (build / search / status)")
