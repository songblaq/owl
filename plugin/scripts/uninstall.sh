#!/usr/bin/env bash
# oh-my-brain plugin uninstaller

set -euo pipefail

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()    { echo -e "${BLUE}[omb]${NC} $*"; }
success() { echo -e "${GREEN}[omb]${NC} $*"; }
warn()    { echo -e "${YELLOW}[omb]${NC} $*"; }

CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"
AGENTS_SKILLS_DIR="$HOME/.agents/skills"
OMB_CONFIG_DIR="$HOME/.config/omb"

echo ""
echo -e "${BLUE}oh-my-brain plugin uninstaller${NC}"
echo "────────────────────────────────────────"
echo ""
echo "This will remove:"
echo "  - skills from $AGENTS_SKILLS_DIR/omb-*"
echo "  - OMB block from $CLAUDE_MD"
echo "  - $OMB_CONFIG_DIR/plugin.json"
echo "  - pipx packages: omb, akasha"
echo "  - Gemini/OpenClaw/Hermes integrations (if installed)"
echo ""
echo "Vault data (~/omb/) will NOT be removed."
echo ""

if [ -t 0 ]; then
  read -p "Continue? (y/N) " -n 1 -r
  echo
else
  if [ -c /dev/tty ]; then
    echo -n "Continue? (y/N) " >&2
    read -n 1 -r < /dev/tty
    echo
  else
    warn "Non-interactive mode. Skipping confirmation."
    REPLY="y"
  fi
fi

if [[ ! ${REPLY:-n} =~ ^[Yy]$ ]]; then
  echo "Cancelled."
  exit 0
fi

# ── remove skills (Claude Code / Codex / OpenCode) ───────────────────────────
info "Removing skills..."
for skill in omb-search omb-ingest omb-health omb-compile omb-setup omb-update; do
  target="$AGENTS_SKILLS_DIR/$skill"
  if [ -e "$target" ] || [ -L "$target" ]; then
    rm -rf "$target"
    echo "    removed: $AGENTS_SKILLS_DIR/$skill"
  fi
done
success "skills removed"

# ── remove Hermes skills (symlinks) ──────────────────────────────────────────
HERMES_SKILLS_DIR="$HOME/.hermes/skills"
HERMES_CATEGORY="knowledge"
if [ -d "$HERMES_SKILLS_DIR/$HERMES_CATEGORY" ]; then
  info "Removing Hermes skills..."
  for skill in omb-search omb-ingest omb-health omb-compile omb-setup omb-update; do
    target="$HERMES_SKILLS_DIR/$HERMES_CATEGORY/$skill"
    if [ -e "$target" ] || [ -L "$target" ]; then
      rm -rf "$target"
      echo "    removed: $target"
    fi
  done
  # Remove category dir if empty
  rmdir "$HERMES_SKILLS_DIR/$HERMES_CATEGORY" 2>/dev/null || true
  success "Hermes skills removed"
fi

# ── remove Gemini extension ──────────────────────────────────────────────────
if command -v gemini &>/dev/null; then
  info "Removing Gemini extension..."
  gemini extensions uninstall oh-my-brain 2>/dev/null && success "Gemini extension removed" || warn "Gemini extension not found (skip)"
fi

# ── remove OpenClaw plugin ───────────────────────────────────────────────────
if command -v openclaw &>/dev/null; then
  info "Removing OpenClaw plugin..."
  openclaw plugins uninstall oh-my-brain-openclaw 2>/dev/null && success "OpenClaw plugin removed" || warn "OpenClaw plugin not found (skip)"
fi

# ── remove CLAUDE.md block ────────────────────────────────────────────────────
if [ -f "$CLAUDE_MD" ] && grep -q "<!-- OMB:START -->" "$CLAUDE_MD"; then
  info "Removing OMB block from CLAUDE.md..."
  python3 - <<PYEOF
import re

with open('$CLAUDE_MD', 'r', encoding='utf-8') as f:
    content = f.read()

result = re.sub(
    r'\n*<!-- OMB:START -->.*?<!-- OMB:END -->\n*',
    '\n',
    content,
    flags=re.DOTALL
)

with open('$CLAUDE_MD', 'w', encoding='utf-8') as f:
    f.write(result)
PYEOF
  success "CLAUDE.md OMB block removed"
fi

# ── remove config ─────────────────────────────────────────────────────────────
if [ -f "$OMB_CONFIG_DIR/plugin.json" ]; then
  rm -f "$OMB_CONFIG_DIR/plugin.json"
  success "plugin.json removed"
fi

# ── uninstall pipx packages ───────────────────────────────────────────────────
info "Uninstalling pipx packages..."
pipx uninstall omb 2>/dev/null && echo "    removed: omb" || warn "omb not installed via pipx"
pipx uninstall akasha 2>/dev/null && echo "    removed: akasha" || warn "akasha not installed via pipx"

echo ""
echo -e "${GREEN}✓ oh-my-brain plugin uninstalled${NC}"
echo ""
echo "  Vault data preserved at ~/omb/"
echo "  To remove vault: rm -rf ~/omb/"
echo ""
