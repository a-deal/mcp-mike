#!/bin/bash
# Refresh the thinkers corpus for Mike's workstation.
# Run from mcp-mike/: bash refresh-thinkers.sh
#
# What this does:
# 1. Bumps `last_refreshed` in thinkers.md to today's date.
# 2. Appends a refresh log entry.
# 3. Reminds Andrew to edit tools.py and tests if guidance changed.
#
# What this does NOT do:
# - Auto-scrape new content (intentional: curation is the value).
# - Auto-commit (review before committing).
#
# Cadence: monthly, or sooner when a named thinker ships something major.

set -e

cd "$(dirname "$0")"

TODAY=$(date +%Y-%m-%d)
THINKERS_FILE="thinkers.md"
LOG_FILE=".refresh-log"

if [ ! -f "$THINKERS_FILE" ]; then
    echo "Error: $THINKERS_FILE not found."
    exit 1
fi

# Bump last_refreshed in frontmatter
# macOS sed requires empty string after -i
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/^last_refreshed:.*/last_refreshed: $TODAY/" "$THINKERS_FILE"
else
    sed -i "s/^last_refreshed:.*/last_refreshed: $TODAY/" "$THINKERS_FILE"
fi

# Log the refresh
echo "$TODAY refresh" >> "$LOG_FILE"

echo "Refreshed thinkers corpus: last_refreshed = $TODAY"
echo ""
echo "Did the refresh change the advice in any tool?"
echo "  → Edit mcp_mike/tools.py"
echo "  → Update the corresponding test in tests/test_tools.py"
echo "  → Run pytest (must be green before commit)"
echo ""
echo "When ready:"
echo "  git add thinkers.md mcp_mike/ tests/ .refresh-log"
echo "  git commit -m 'refresh: thinkers $TODAY'"
echo "  git push"
