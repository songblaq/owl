from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from capsule.buildcmd import bundle_summary
from capsule.registry import PRODUCTS, default_vault_root, get_product


def run_status(product_name: Optional[str], vault_root: Optional[str], json_out: bool) -> int:
    root = Path(vault_root).expanduser().resolve() if vault_root else default_vault_root(Path.home())

    if product_name:
        summary = bundle_summary(product_name, str(root))
        if json_out:
            print(json.dumps(summary, ensure_ascii=False, indent=2))
            return 0
        print(f"제품 번들 — {summary['label']}")
        print("━" * 32)
        print(f"  상태: {'준비됨' if summary['exists'] else '없음'}")
        print(f"  페이지: {summary['pagesCount']}")
        print(f"  컨텍스트 파트: {summary['ctxCount']}")
        return 0

    summaries = [bundle_summary(product.key, str(root)) for product in PRODUCTS.values()]
    if json_out:
        print(json.dumps({"vaultRoot": str(root), "products": summaries}, ensure_ascii=False, indent=2))
        return 0

    print("제품 번들")
    print("━" * 32)
    for summary in summaries:
        built = "준비됨" if summary["exists"] else "없음"
        print(f"  {summary['product']}: {built} (페이지 {summary['pagesCount']})")
    return 0
