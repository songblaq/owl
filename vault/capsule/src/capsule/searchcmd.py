from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable, List, Optional

from capsule.registry import default_vault_root, get_product


def _candidate_files(bundle_root: Path) -> Iterable[Path]:
    pages = bundle_root / "pages"
    if pages.exists():
        yield from pages.rglob("*.md")
    for name in [
        "ATLAS.md",
        "ATLAS_FULL.md",
        "llms.txt",
        "llms_FULL.txt",
        "INDEX_CONFIG_KEYS.md",
        "INDEX_CLI_COMMANDS.md",
    ]:
        path = bundle_root / name
        if path.exists():
            yield path


def _score_text(path: Path, text: str, terms: List[str]) -> tuple[int, Optional[str]]:
    lowered_path = str(path).lower()
    lowered_text = text.lower()
    score = 0
    snippet = None

    for term in terms:
        path_hits = lowered_path.count(term)
        body_hits = lowered_text.count(term)
        if path_hits:
            score += path_hits * 8
        if body_hits:
            score += body_hits
        if snippet is None and body_hits:
            for line in text.splitlines():
                if term in line.lower():
                    snippet = line.strip()
                    break

    if text.startswith("# "):
        title_line = text.splitlines()[0].lower()
        for term in terms:
            if term in title_line:
                score += 5

    return score, snippet


def run_search(product_name: str, query: str, limit: int, vault_root: Optional[str], json_out: bool) -> int:
    product = get_product(product_name)
    root = Path(vault_root).expanduser().resolve() if vault_root else default_vault_root(Path.home())
    bundle_root = root / product.key
    if not bundle_root.exists():
        print(f"capsule search: bundle does not exist: {bundle_root}")
        print("  Run: capsule build <product>")
        return 2

    terms = [t.lower() for t in re.split(r"\s+", query.strip()) if t.strip()]
    if not terms:
        print("capsule search: query required", flush=True)
        return 2

    hits = []
    for path in _candidate_files(bundle_root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        score, snippet = _score_text(path, text, terms)
        if score <= 0:
            continue
        hits.append(
            {
                "path": str(path.relative_to(bundle_root)),
                "score": score,
                "snippet": snippet,
            }
        )

    hits.sort(key=lambda item: (-item["score"], item["path"]))
    hits = hits[:limit]

    if json_out:
        print(json.dumps({"product": product.key, "query": query, "hits": hits}, ensure_ascii=False, indent=2))
        return 0

    print(f"Capsule search — {product.label}")
    print("━" * 32)
    if not hits:
        print("No matches.")
        return 0

    for idx, hit in enumerate(hits, start=1):
        print(f"[{idx}] {hit['path']}  (score: {hit['score']})")
        if hit["snippet"]:
            print(f"    {hit['snippet']}")
    return 0
