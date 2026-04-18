from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict


@dataclass(frozen=True)
class ProductConfig:
    key: str
    label: str
    source_subdir: str
    source_flag: str
    build_script: str
    verify_script: str


PRODUCTS: Dict[str, ProductConfig] = {
    "openclaw": ProductConfig(
        key="openclaw",
        label="OpenClaw",
        source_subdir="openclaw",
        source_flag="--openclaw",
        build_script="build-openclaw.mjs",
        verify_script="verify-openclaw.mjs",
    ),
    "hermes-agent": ProductConfig(
        key="hermes-agent",
        label="Hermes Agent",
        source_subdir="hermes-agent",
        source_flag="--source",
        build_script="build-hermes.mjs",
        verify_script="verify-hermes.mjs",
    ),
}


def get_product(product: str) -> ProductConfig:
    key = product.strip().lower()
    if key not in PRODUCTS:
        known = ", ".join(sorted(PRODUCTS))
        raise KeyError(f"unknown capsule product '{product}'. Known products: {known}")
    return PRODUCTS[key]


def default_source_path(home: Path, product: ProductConfig) -> Path:
    return home / "omb" / "input" / product.source_subdir


def default_vault_root(home: Path) -> Path:
    return home / "omb" / "brain" / "readonly"
