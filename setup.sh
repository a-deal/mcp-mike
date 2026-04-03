#!/bin/bash
# Mike's MCP Server - One-time setup
# Run: bash setup.sh

set -e

echo "Setting up Mike's MCP server..."

# 1. Create workspace if it doesn't exist
WORKSPACE="$HOME/Documents/claude-workspace"
mkdir -p "$WORKSPACE/personas"
mkdir -p "$WORKSPACE/learnair"
mkdir -p "$WORKSPACE/workshops"
mkdir -p "$WORKSPACE/learning"
mkdir -p "$WORKSPACE/reference"
mkdir -p "$WORKSPACE/hub"

echo "  Created workspace at $WORKSPACE"

# 2. Create venv and install
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -q -e .

echo "  Installed MCP server"

# 3. Get the Python path for Claude Desktop config
PYTHON_PATH="$SCRIPT_DIR/.venv/bin/python3"

# 4. Generate the Claude Desktop config snippet
CONFIG_SNIPPET=$(cat <<EOF
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

echo ""
echo "  Setup complete."
echo ""
echo "  Add this to your Claude Desktop config:"
echo "  (Settings > Developer > Edit Config)"
echo ""
echo "$CONFIG_SNIPPET"
echo ""
echo "  Then restart Claude Desktop."
echo ""
echo "  Workspace: $WORKSPACE"
echo "  Add persona files to: $WORKSPACE/personas/"
echo "  Add hub docs to: $WORKSPACE/hub/"
