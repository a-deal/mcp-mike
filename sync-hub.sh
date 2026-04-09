#!/bin/bash
# Sync curated hub docs into Mike's workspace.
# Run from mcp-mike/: bash sync-hub.sh
#
# This copies essential LearnAIR docs from Andrew's hub into
# the workspace/hub/ directory that Mike's MCP server searches.
# Run this whenever docs are updated.

set -e

HUB="$HOME/src/hub"
WORKSPACE="${MIKE_WORKSPACE:-$HOME/Documents/claude-workspace}"
DEST="$WORKSPACE/hub"

if [ ! -d "$HUB" ]; then
    echo "Hub not found at $HUB. This script runs from Andrew's machine."
    echo "For Mike's machine, Andrew pushes updated docs to the repo."
    exit 1
fi

mkdir -p "$DEST"

echo "Syncing hub docs to $DEST..."

# --- Anchor doc ---
cp "$HUB/learnair/active/strategic-clarity.md" "$DEST/strategic-clarity.md"

# --- Story arc and debrief ---
cp "$HUB/learnair/active/april7-story-arc-v7.md" "$DEST/april-7-story-arc.md"
cp "$HUB/learnair/active/april7-debrief.md" "$DEST/april-7-debrief.md"
cp "$HUB/learnair/active/april7-next-steps.md" "$DEST/april-7-next-steps.md"

# --- Mike-specific ---
cp "$HUB/learnair/active/april2-mike-synopsis.md" "$DEST/mike-synopsis-apr2.md"
cp "$HUB/learnair/active/mike-chamath-insights-v8.md" "$DEST/chamath-insights.md"
cp "$HUB/learnair/active/april8-mike-restructure-proposal.md" "$DEST/restructure-proposal.md"

# --- Intel ---
cp "$HUB/learnair/intel/learnair-deep-dive.md" "$DEST/learnair-deep-dive.md"
cp "$HUB/learnair/intel/curriculum-analysis.md" "$DEST/curriculum-analysis.md"
cp "$HUB/learnair/intel/competitor-hiring-analysis.md" "$DEST/competitor-hiring.md"

# --- Research ---
cp "$HUB/research/2026-03-23-oregon-employer-readiness.md" "$DEST/oregon-employer-readiness.md"
cp "$HUB/research/2026-03-23-target-contacts.md" "$DEST/target-contacts.md"
cp "$HUB/research/2026-03-26-alpha-school-deep-dive.md" "$DEST/alpha-school-model.md"
cp "$HUB/research/2026-03-22-oregon-landscape.md" "$DEST/oregon-landscape.md"

# --- Key meetings ---
cp "$HUB/learnair/meetings/2026-03-19-learnair-justin-team.md" "$DEST/meeting-justin-team-mar19.md"
cp "$HUB/learnair/meetings/2026-04-02-mike-trisha-coffee.md" "$DEST/meeting-trisha-apr2.md"
cp "$HUB/learnair/meetings/2026-04-02-mike-call-full.md" "$DEST/meeting-mike-apr2.md"

COUNT=$(ls -1 "$DEST"/*.md 2>/dev/null | wc -l | tr -d ' ')
echo "Synced $COUNT docs to $DEST"
echo ""
echo "Mike can search these with: \"search the hub for employer signal\""
