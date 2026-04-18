from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Sequence

from capsule.registry import default_source_path, default_vault_root, get_product


def _asset_dir() -> Path:
    return Path(__file__).resolve().parent / "assets"


def _node() -> str:
    path = shutil.which("node")
    if not path:
        raise RuntimeError("capsule: node not found on PATH. Install Node.js to build or verify capsules.")
    return path


def _run_node(script: Path, args: Sequence[str]) -> int:
    return subprocess.call([_node(), str(script), *args])


def _ensure_source_shape(source_root: Path) -> None:
    docs = source_root / "docs"
    if not source_root.exists():
        raise FileNotFoundError(f"capsule: source root does not exist: {source_root}")
    if not docs.is_dir():
        raise FileNotFoundError(f"capsule: expected docs/ under source root: {docs}")


def run_build(
    product_name: str,
    source: Optional[str],
    vault_root: Optional[str],
    include_i18n: bool,
    max_chars_per_part: Optional[int],
    skip_verify: bool,
) -> int:
    product = get_product(product_name)
    home = Path.home()
    source_root = Path(source).expanduser().resolve() if source else default_source_path(home, product)
    resolved_vault_root = Path(vault_root).expanduser().resolve() if vault_root else default_vault_root(home)
    dist_root = resolved_vault_root / product.key

    _ensure_source_shape(source_root)
    dist_root.parent.mkdir(parents=True, exist_ok=True)

    build_script = _asset_dir() / product.build_script
    build_args = [product.source_flag, str(source_root), "--dist", str(dist_root)]
    if include_i18n:
        build_args.append("--include-i18n")
    if max_chars_per_part is not None:
        build_args.extend(["--max-chars-per-part", str(max_chars_per_part)])

    rc = _run_node(build_script, build_args)
    if rc != 0:
        return rc

    if skip_verify:
        print(f"capsule build: built {product.key} → {dist_root}")
        return 0

    verify_script = _asset_dir() / product.verify_script
    verify_args = [product.source_flag, str(source_root), "--dist", str(dist_root)]
    if include_i18n:
        verify_args.append("--include-i18n")
    rc = _run_node(verify_script, verify_args)
    if rc == 0:
        print(f"capsule build: verified {product.key} → {dist_root}")
    return rc


def bundle_summary(product_name: str, vault_root: Optional[str]) -> dict:
    product = get_product(product_name)
    root = Path(vault_root).expanduser().resolve() if vault_root else default_vault_root(Path.home())
    bundle = root / product.key
    manifest = bundle / "manifest.json"
    pages_root = bundle / "pages"
    ctx_root = bundle / "ctx"
    meta_root = bundle / "meta"

    data = {
        "product": product.key,
        "label": product.label,
        "path": str(bundle),
        "exists": bundle.exists(),
        "manifest": str(manifest),
        "pagesCount": 0,
        "ctxCount": 0,
        "metaExists": meta_root.exists(),
        "sourceRoot": None,
    }

    if pages_root.exists():
        data["pagesCount"] = sum(1 for _ in pages_root.rglob("*.md"))
    if ctx_root.exists():
        data["ctxCount"] = sum(1 for _ in ctx_root.glob("*.md"))
    if manifest.exists():
        try:
            manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            manifest_data = None
        if manifest_data:
            inputs = manifest_data.get("inputs", {})
            source_root = inputs.get("docsRoot")
            if source_root:
                data["sourceRoot"] = source_root

    return data
