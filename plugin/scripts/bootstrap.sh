#!/usr/bin/env bash
# oh-my-brain bootstrap — curl one-liner installer
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/songblaq/oh-my-brain/main/plugin/scripts/bootstrap.sh | bash
#
# What it does:
#   1. Clones oh-my-brain repo to ~/omb/oh-my-brain (or $OMB_REPO_DIR)
#   2. Runs plugin/scripts/install.sh

set -euo pipefail

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()    { echo -e "${BLUE}[omb]${NC} $*"; }
success() { echo -e "${GREEN}[omb]${NC} $*"; }
warn()    { echo -e "${YELLOW}[omb]${NC} $*"; }
error()   { echo -e "${RED}[omb]${NC} $*" >&2; exit 1; }

REPO_URL="https://github.com/songblaq/oh-my-brain.git"
REPO_DIR="${OMB_REPO_DIR:-$HOME/omb/oh-my-brain}"

echo ""
echo -e "${BLUE}oh-my-brain bootstrap${NC}"
echo "────────────────────────────────────────"
echo ""

# ── prereqs ───────────────────────────────────────────────────────────────────
command -v git  &>/dev/null || error "git not found"
command -v pipx &>/dev/null || error "pipx not found. Install: brew install pipx"
command -v python3 &>/dev/null || error "python3 not found"

# ── clone or update repo ──────────────────────────────────────────────────────
if [ -d "$REPO_DIR/.git" ]; then
  info "Repo exists at $REPO_DIR — pulling latest..."
  git -C "$REPO_DIR" pull --ff-only
  success "repo updated"
else
  info "Cloning oh-my-brain → $REPO_DIR"
  mkdir -p "$(dirname "$REPO_DIR")"
  git clone "$REPO_URL" "$REPO_DIR"
  success "repo cloned"
fi

# ── run install ───────────────────────────────────────────────────────────────
bash "$REPO_DIR/plugin/scripts/install.sh"
