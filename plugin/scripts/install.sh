#!/usr/bin/env bash
# oh-my-brain plugin installer
# Usage: bash plugin/scripts/install.sh [--skills-only] [--claude-only]
#
# Supported runtimes:
#   Claude Code / Codex / OpenCode  → ~/.agents/skills/ symlinks + CLAUDE.md patch
#   Gemini CLI                      → gemini extensions install
#   OpenClaw                        → openclaw plugins install
#   Hermes                          → hermes skills install (per-skill)

set -euo pipefail

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# ── flags ─────────────────────────────────────────────────────────────────────
SKILLS_ONLY=false
CLAUDE_ONLY=false
for arg in "$@"; do
  case "$arg" in
    --skills-only) SKILLS_ONLY=true ;;
    --claude-only) CLAUDE_ONLY=true ;;
  esac
done

# ── paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PLUGIN_DIR="$REPO_ROOT/plugin"
SKILLS_SRC="$REPO_ROOT/skills"
PLUGIN_CLAUDE="$PLUGIN_DIR/CLAUDE.md"

CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"
AGENTS_SKILLS_DIR="$HOME/.agents/skills"
OMB_CONFIG_DIR="$HOME/.config/omb"

# ── helpers ───────────────────────────────────────────────────────────────────
info()    { echo -e "${BLUE}[omb]${NC} $*"; }
success() { echo -e "${GREEN}[omb]${NC} $*"; }
warn()    { echo -e "${YELLOW}[omb]${NC} $*"; }
error()   { echo -e "${RED}[omb]${NC} $*" >&2; }

# ── version ───────────────────────────────────────────────────────────────────
VERSION=$(python3 -c "import json; print(json.load(open('$REPO_ROOT/package.json'))['version'])")

echo ""
echo -e "${BLUE}oh-my-brain plugin installer v${VERSION}${NC}"
echo "────────────────────────────────────────"
echo ""

# ── step 1: pipx packages ─────────────────────────────────────────────────────
if ! $SKILLS_ONLY && ! $CLAUDE_ONLY; then
  info "Installing pipx packages..."

  if ! command -v pipx &>/dev/null; then
    error "pipx not found. Install with: brew install pipx"
    exit 1
  fi

  (cd "$REPO_ROOT/vault/akasha" && pipx install -e . --force -q)
  success "akasha installed"

  (cd "$REPO_ROOT/vault/omb" && pipx install -e . --force -q)
  success "omb installed"

  # ── step 2: vault init ───────────────────────────────────────────────────
  info "Checking vault..."
  VAULT_DIR="$HOME/omb/vault/akasha"
  if [ ! -d "$VAULT_DIR" ] || [ ! -f "$VAULT_DIR/.akasha-vault" ]; then
    info "Initializing vault at $VAULT_DIR..."
    akasha init "$VAULT_DIR"
    success "vault initialized"
  else
    success "vault exists ($VAULT_DIR)"
  fi
fi

# ── step 3: Claude Code / Codex / OpenCode skills (shared ~/.agents/skills) ───
if ! $CLAUDE_ONLY; then
  info "Syncing skills (Claude Code / Codex / OpenCode)..."

  mkdir -p "$AGENTS_SKILLS_DIR"
  for skill_dir in "$SKILLS_SRC"/*/; do
    skill_name="$(basename "$skill_dir")"
    rm -rf "$AGENTS_SKILLS_DIR/$skill_name"
    ln -sfn "$skill_dir" "$AGENTS_SKILLS_DIR/$skill_name"
  done
  success "skills → $AGENTS_SKILLS_DIR"

  # ── Gemini CLI ─────────────────────────────────────────────────────────────
  if command -v gemini &>/dev/null; then
    info "Installing Gemini CLI extension..."
    GEMINI_PLUGIN_DIR="$REPO_ROOT/plugins/gemini"
    if gemini extensions install "$GEMINI_PLUGIN_DIR" --force 2>/dev/null; then
      success "Gemini extension installed"
    else
      warn "Gemini extension install failed (non-fatal). Manual: gemini extensions install $GEMINI_PLUGIN_DIR"
    fi
  fi

  # ── OpenClaw ───────────────────────────────────────────────────────────────
  if command -v openclaw &>/dev/null; then
    info "Installing OpenClaw plugin..."
    OPENCLAW_PLUGIN_DIR="$REPO_ROOT/plugins/openclaw"
    if openclaw plugins install "$OPENCLAW_PLUGIN_DIR" 2>/dev/null; then
      success "OpenClaw plugin installed"
    else
      warn "OpenClaw plugin install failed (non-fatal). Manual: openclaw plugins install $OPENCLAW_PLUGIN_DIR"
    fi
  fi

  # ── Hermes ─────────────────────────────────────────────────────────────────
  if command -v hermes &>/dev/null; then
    info "Installing Hermes skills..."
    HERMES_SKILLS_DIR="$REPO_ROOT/plugins/hermes/skills"
    installed=0
    for skill_dir in "$HERMES_SKILLS_DIR"/*/; do
      skill_name="$(basename "$skill_dir")"
      if hermes skills install "$skill_dir" 2>/dev/null; then
        installed=$((installed + 1))
      else
        warn "  hermes skill install failed: $skill_name (non-fatal)"
      fi
    done
    [ "$installed" -gt 0 ] && success "Hermes: $installed skills installed"
  fi
fi

# ── step 4: CLAUDE.md upsert ─────────────────────────────────────────────────
if ! $SKILLS_ONLY; then
  info "Updating CLAUDE.md..."
  touch "$CLAUDE_MD"

  NEW_BLOCK="$(cat "$PLUGIN_CLAUDE")"

  if grep -q "<!-- OMB:START -->" "$CLAUDE_MD"; then
    # Replace existing OMB block
    python3 - <<PYEOF
import re, sys

with open('$CLAUDE_MD', 'r', encoding='utf-8') as f:
    content = f.read()

new_block = open('$PLUGIN_CLAUDE', encoding='utf-8').read()

result = re.sub(
    r'<!-- OMB:START -->.*?<!-- OMB:END -->',
    new_block.strip(),
    content,
    flags=re.DOTALL
)

with open('$CLAUDE_MD', 'w', encoding='utf-8') as f:
    f.write(result)
PYEOF
    success "CLAUDE.md OMB block updated (v${VERSION})"
  else
    # Append new OMB block
    printf '\n\n' >> "$CLAUDE_MD"
    cat "$PLUGIN_CLAUDE" >> "$CLAUDE_MD"
    success "CLAUDE.md OMB block added (v${VERSION})"
  fi
fi

# ── step 5: save repo path ────────────────────────────────────────────────────
if ! $SKILLS_ONLY && ! $CLAUDE_ONLY; then
  mkdir -p "$OMB_CONFIG_DIR"
  python3 - <<PYEOF
import json, os
config_path = '$OMB_CONFIG_DIR/plugin.json'
config = {}
if os.path.exists(config_path):
    with open(config_path) as f:
        config = json.load(f)
config['repoRoot'] = '$REPO_ROOT'
config['version'] = '$VERSION'
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)
PYEOF
  success "repo path saved → $OMB_CONFIG_DIR/plugin.json"
fi

# ── done ─────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}✓ oh-my-brain plugin v${VERSION} installed${NC}"
echo ""
echo "  omb status        # verify vault"
echo "  omb search \"...\"  # search knowledge"
echo ""
