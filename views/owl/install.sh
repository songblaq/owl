#!/usr/bin/env bash
#
# owl — one-shot installer
#
# A personal LLM-maintained wiki. Karpathy LLM Wiki pattern (2026),
# spiritually descended from Vannevar Bush's Memex (1945).
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/songblaq/oh-my-brain/main/views/owl/install.sh | bash
#
# NOTE: Pipe to `bash` (not `sh`). On systems where /bin/sh is dash
# (e.g., Debian/Ubuntu/WSL), piping to `sh` fails because dash doesn't
# support `set -o pipefail`. We re-exec under bash below as a safety net,
# but using `| bash` is the correct invocation.
#
# What it does:
#   1. Clones (or updates) the monorepo to ~/_/projects/agent-brain
#      (override with $OWL_REPO).
#   2. Installs the `owl` CLI via pipx in editable mode.
#   3. Runs `owl setup` to diagnose env, create user-global subagent
#      symlinks, and offer to initialize a vault.
#
# This is intentionally minimal. The interesting work happens in `owl
# setup` (Python, with proper TUI prompts). Bash is just the bootstrap.
#
# Re-runnable. Idempotent. Never modifies vault data.

# Ensure we're running under bash. When invoked via `curl | sh` on a
# system where /bin/sh is dash (Debian/Ubuntu/WSL), `set -o pipefail`
# below would fail. Fall back to POSIX-safe mode in that case, OR
# re-exec under bash if available.
if [ -z "${BASH_VERSION:-}" ]; then
    # Not running under bash. Try to re-exec.
    if command -v bash >/dev/null 2>&1; then
        # Re-exec this script's content under bash. For `curl | sh` we
        # need to re-read stdin; for `bash install.sh` $0 works.
        if [ -f "$0" ] && [ "$0" != "sh" ] && [ "$0" != "-sh" ] && [ "$0" != "dash" ]; then
            exec bash "$0" "$@"
        fi
        # Piped-stdin case: we can't re-exec from a stream easily,
        # so we fall back to POSIX-compatible mode without pipefail.
        # The script is simple enough that pipefail isn't critical.
        set -eu
    else
        # No bash available — run with POSIX-safe flags and hope.
        set -eu
    fi
else
    # Under bash: use the full strict mode.
    set -euo pipefail
fi

REPO_DIR="${OWL_REPO:-${AGENT_BRAIN_REPO:-$HOME/_/projects/agent-brain}}"
REPO_URL="${OWL_REPO_URL:-${AGENT_BRAIN_REPO_URL:-https://github.com/songblaq/oh-my-brain.git}}"
BRANCH="${OWL_BRANCH:-${AGENT_BRAIN_BRANCH:-main}}"

# NOTE: use %b (not %s) so escape sequences like \n in the argument are
# interpreted. Callers use `say "\n2) ..."` to get a blank line before
# each section header. Without %b, the literal "\n" is printed.
say() { printf '\033[1;36m%b\033[0m\n' "$*"; }
warn() { printf '\033[1;33m%b\033[0m\n' "$*" >&2; }
die() { printf '\033[1;31m%b\033[0m\n' "$*" >&2; exit 1; }

say "owl installer"
say "============="
echo

# 1. Sanity check: tools we need
say "1) Checking prerequisites"
if ! command -v git >/dev/null 2>&1; then
    die "  ✗ git not found. Install git first."
fi
echo "  git:    $(command -v git)"

if ! command -v python3 >/dev/null 2>&1; then
    die "  ✗ python3 not found. Install Python 3.9+ first."
fi
echo "  python: $(command -v python3) ($(python3 --version 2>&1))"

if ! command -v pipx >/dev/null 2>&1; then
    warn "  ⚠ pipx not found. Recommended on macOS/Linux:"
    warn "      brew install pipx        (macOS)"
    warn "      sudo apt install pipx    (Debian/Ubuntu)"
    warn "    Falling back to: python3 -m pip install --user --break-system-packages"
    INSTALLER="pip"
else
    echo "  pipx:   $(command -v pipx)"
    INSTALLER="pipx"
fi

# 2. Clone or update the repo
say "\n2) Fetching project repo"
if [ -d "$REPO_DIR/.git" ]; then
    echo "  ↻ updating existing repo at $REPO_DIR"
    git -C "$REPO_DIR" fetch --quiet origin "$BRANCH" || warn "  ⚠ fetch failed; using local state"
    git -C "$REPO_DIR" checkout --quiet "$BRANCH" 2>/dev/null || true
    git -C "$REPO_DIR" pull --quiet --ff-only origin "$BRANCH" 2>/dev/null || warn "  ⚠ pull skipped (local changes?)"
elif [ -d "$REPO_DIR" ]; then
    if [ -f "$REPO_DIR/pyproject.toml" ]; then
        echo "  ↻ found pyproject.toml at $REPO_DIR (assuming local dev checkout)"
    else
        die "  ✗ $REPO_DIR exists but is not a git repo or owl checkout. Set \$OWL_REPO to use a different path."
    fi
else
    mkdir -p "$(dirname "$REPO_DIR")"
    echo "  ↓ cloning $REPO_URL → $REPO_DIR"
    git clone --quiet --branch "$BRANCH" "$REPO_URL" "$REPO_DIR" || die "  ✗ git clone failed"
fi
echo "  ✓ repo at $REPO_DIR"

# 3. Install the CLI
say "\n3) Installing owl CLI"
cd "$REPO_DIR/views/owl"
if [ "$INSTALLER" = "pipx" ]; then
    pipx install --editable . --force >/dev/null 2>&1 || die "  ✗ pipx install failed"
    echo "  ✓ pipx install --editable . (succeeded)"
else
    python3 -m pip install --user --break-system-packages --editable . >/dev/null 2>&1 \
        || die "  ✗ pip install failed"
    echo "  ✓ pip install --user --editable . (succeeded)"
fi

# 4. Verify the CLI is on PATH
say "\n4) Verifying owl on PATH"
if command -v owl >/dev/null 2>&1; then
    OWL_PATH="$(command -v owl)"
    echo "  ✓ owl → $OWL_PATH"
    OWL_VERSION="$(owl --version 2>&1 || echo unknown)"
    echo "  ✓ $OWL_VERSION"
else
    warn "  ⚠ owl CLI not on PATH yet."
    warn "    On macOS/Linux, ~/.local/bin or pipx's bin dir may need to be added to your PATH."
    warn "    Try: echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.zshrc && source ~/.zshrc"
    warn "    Then re-run: owl setup"
    exit 0
fi

# 5. Run owl setup (interactive)
say "\n5) Running owl setup"
echo
owl setup || warn "  ⚠ owl setup exited non-zero — re-run when convenient"

say "\n✨ owl installed."
echo "   Project repo: $REPO_DIR"
echo "   Try:"
echo "     owl status"
echo "     owl search 'wiki'"
echo "     owl health"
