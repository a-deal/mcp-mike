#!/bin/bash
# Mike's full onboarding script.
# Run: bash onboard.sh
#
# This does everything: checks prerequisites, installs the server,
# seeds the workspace, generates Claude Desktop config, and validates.
# Each step prints pass/fail so you know exactly where you are.

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

pass() { echo -e "  ${GREEN}PASS${NC} $1"; }
fail() { echo -e "  ${RED}FAIL${NC} $1"; }
info() { echo -e "  ${YELLOW}INFO${NC} $1"; }
step() { echo -e "\n${BOLD}$1${NC}"; }

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="$HOME/Documents/claude-workspace"

echo ""
echo "==========================================="
echo "  Mike's Workstation — Onboarding"
echo "==========================================="
echo ""

# -----------------------------------------------
step "Step 1: Check prerequisites"
# -----------------------------------------------

# Python version
PYTHON_VERSION=$(python3 --version 2>/dev/null | awk '{print $2}')
if [ -z "$PYTHON_VERSION" ]; then
    fail "python3 not found. Install Python 3.10+ from python.org"
    exit 1
fi

MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 10 ]; then
    pass "Python $PYTHON_VERSION (need 3.10+)"
else
    fail "Python $PYTHON_VERSION is too old. Need 3.10+. Install from python.org"
    exit 1
fi

# Git
if command -v git &>/dev/null; then
    pass "git installed"
else
    fail "git not found. Install from git-scm.com"
    exit 1
fi

# Claude Desktop
CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
if [ -d "$CLAUDE_CONFIG_DIR" ]; then
    pass "Claude Desktop detected"
else
    info "Claude Desktop config directory not found at $CLAUDE_CONFIG_DIR"
    info "Install Claude Desktop from claude.ai/download, then re-run this script"
fi

# -----------------------------------------------
step "Step 2: Create workspace"
# -----------------------------------------------

mkdir -p "$WORKSPACE/personas"
mkdir -p "$WORKSPACE/learnair"
mkdir -p "$WORKSPACE/workshops"
mkdir -p "$WORKSPACE/learning"
mkdir -p "$WORKSPACE/reference"
mkdir -p "$WORKSPACE/hub"
pass "Workspace created at $WORKSPACE"

# Seed a starter notes file if it doesn't exist
if [ ! -f "$WORKSPACE/learning/notes.md" ]; then
    cat > "$WORKSPACE/learning/notes.md" << 'NOTES'
# Learning Notes

Notes from your workstation sessions. Add entries with:
  "save a note to learning: [what clicked today]"

NOTES
    pass "Seeded learning/notes.md"
else
    info "learning/notes.md already exists, skipping"
fi

# -----------------------------------------------
step "Step 3: Clone shared context repo"
# -----------------------------------------------

CONTEXT_DIR="$HOME/src/learnair-context"
if [ -d "$CONTEXT_DIR" ]; then
    info "learnair-context already exists at $CONTEXT_DIR"
    cd "$CONTEXT_DIR" && git pull -q 2>/dev/null
    pass "Shared context up to date"
else
    cd "$HOME/src"
    if git clone -q https://github.com/a-deal/learnair-context.git 2>/dev/null; then
        pass "Cloned learnair-context (42 shared docs)"
    else
        info "Could not clone learnair-context. Check internet connection."
        info "You can clone it later: cd ~/src && git clone https://github.com/a-deal/learnair-context.git"
    fi
fi

# -----------------------------------------------
step "Step 4: Install MCP server (pip)"
# -----------------------------------------------

cd "$SCRIPT_DIR"

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    pass "Created virtual environment"
else
    info "Virtual environment already exists"
fi

source .venv/bin/activate
pip install -q -e . 2>&1 | tail -1
pass "MCP server installed"

# -----------------------------------------------
step "Step 5: Verify server loads"
# -----------------------------------------------

# Quick import test
TOOL_CHECK=$(.venv/bin/python3 -c "
from mcp_mike.server import mcp
tools = [t.name for t in mcp._tool_manager._tools.values()]
print(','.join(sorted(tools)))
" 2>&1)

if echo "$TOOL_CHECK" | grep -q "quiz_me"; then
    TOOL_COUNT=$(echo "$TOOL_CHECK" | tr ',' '\n' | wc -l | tr -d ' ')
    pass "Server loads with $TOOL_COUNT tools: $TOOL_CHECK"
else
    fail "Server failed to load. Error: $TOOL_CHECK"
    exit 1
fi

# -----------------------------------------------
step "Step 6: Seed hub docs"
# -----------------------------------------------

# Check if we're on Andrew's machine (has the hub)
if [ -d "$HOME/src/hub/learnair" ]; then
    bash "$SCRIPT_DIR/sync-hub.sh"
    pass "Hub docs synced from Andrew's hub"
else
    # On Mike's machine, check if hub/ has docs from the repo
    if [ -d "$SCRIPT_DIR/workspace-seed/hub" ]; then
        cp "$SCRIPT_DIR/workspace-seed/hub/"*.md "$WORKSPACE/hub/" 2>/dev/null
        pass "Hub docs copied from repo seed"
    else
        info "No hub docs available. Andrew will sync these for you."
        info "Or run: bash sync-hub.sh (from Andrew's machine)"
    fi
fi

HUB_COUNT=$(ls -1 "$WORKSPACE/hub/"*.md 2>/dev/null | wc -l | tr -d ' ')
info "$HUB_COUNT docs in hub"

# -----------------------------------------------
step "Step 7: Generate Claude Desktop config"
# -----------------------------------------------

PYTHON_PATH="$SCRIPT_DIR/.venv/bin/python3"

CONFIG=$(cat <<EOF
{
  "mcpServers": {
    "mike-workspace": {
      "command": "$PYTHON_PATH",
      "args": ["-m", "mcp_mike.server"],
      "env": {
        "MIKE_WORKSPACE": "$WORKSPACE"
      }
    }
  }
}
EOF
)

# Check if config already exists
CLAUDE_CONFIG="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"
if [ -f "$CLAUDE_CONFIG" ]; then
    if grep -q "mike-workspace" "$CLAUDE_CONFIG" 2>/dev/null; then
        pass "Claude Desktop already configured with mike-workspace"
    else
        info "Claude Desktop config exists but doesn't include mike-workspace."
        echo ""
        echo "  Add this to your existing config (Settings > Developer > Edit Config):"
        echo ""
        echo "    \"mike-workspace\": {"
        echo "      \"command\": \"$PYTHON_PATH\","
        echo "      \"args\": [\"-m\", \"mcp_mike.server\"],"
        echo "      \"env\": {"
        echo "        \"MIKE_WORKSPACE\": \"$WORKSPACE\""
        echo "      }"
        echo "    }"
        echo ""
    fi
else
    info "No Claude Desktop config found. Creating one..."
    mkdir -p "$CLAUDE_CONFIG_DIR"
    echo "$CONFIG" > "$CLAUDE_CONFIG"
    pass "Config written to $CLAUDE_CONFIG"
fi

# -----------------------------------------------
step "Step 8: Run tests"
# -----------------------------------------------

cd "$SCRIPT_DIR"
TEST_RESULT=$(.venv/bin/python3 -m pytest tests/ -q 2>&1)
if echo "$TEST_RESULT" | grep -q "passed"; then
    PASSED=$(echo "$TEST_RESULT" | grep -oE '[0-9]+ passed' | head -1)
    pass "All tests pass ($PASSED)"
else
    fail "Tests failed:"
    echo "$TEST_RESULT"
fi

# -----------------------------------------------
echo ""
echo "==========================================="
echo "  Setup complete!"
echo "==========================================="
echo ""
echo "  Next steps:"
echo ""
echo "  1. Restart Claude Desktop (Cmd+Q, then reopen)"
echo ""
echo "  2. Open a new conversation and try:"
echo "     > \"quiz me on learnair\""
echo "     > \"search the hub for employer signal\""
echo "     > \"show my progress\""
echo "     > \"find files about LearnAIR\""
echo "     > \"mochary: prep for my next call\""
echo "     > \"save a note to learning: first session complete\""
echo "     > \"share my progress\""
echo ""
echo "  3. Open the workstation in your browser:"
echo "     https://andrewdeal.info/learnair/workstation"
echo ""
echo "  4. Daily routine: 1 hour."
echo "     Read a concept in the workstation."
echo "     Practice it in Claude Desktop."
echo "     Quiz yourself. Record what clicked."
echo "     Share your progress at the end."
echo ""
echo "  5. To update (when Andrew pushes changes):"
echo "     cd ~/src/mcp-mike && git pull"
echo "     cd ~/src/learnair-context && git pull"
echo "     Restart Claude Desktop."
echo ""
echo "  Workspace: $WORKSPACE"
echo "  Shared context: $HOME/src/learnair-context"
echo "  MCP server: $SCRIPT_DIR"
echo ""
