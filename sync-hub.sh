#!/bin/bash
# Sync curated hub docs into Mike's workspace.
# Run from mcp-mike/: bash sync-hub.sh
#
# This copies the essential LearnAIR docs from Andrew's hub into
# the workspace/hub/ directory that Mike's MCP server searches.
# Run this whenever docs are updated.

set -e

HUB="$HOME/src/hub"
WORKSPACE="${MIKE_WORKSPACE:-$HOME/Documents/claude-workspace}"
DEST="$WORKSPACE/hub"

mkdir -p "$DEST"

echo "Syncing hub docs to $DEST..."

# --- Anchor doc ---
cp "$HUB/decisions/2026-04-01-learnair-strategic-clarity.md" "$DEST/strategic-clarity.md"

# --- Story arc and call prep ---
cp "$HUB/plans/2026-04-07-story-arc.md" "$DEST/april-7-story-arc.md"
cp "$HUB/plans/2026-04-07-call-arc.md" "$DEST/april-7-call-arc.md"

# --- Research ---
cp "$HUB/research/2026-03-19-learnair-deep-dive.md" "$DEST/learnair-deep-dive.md"
cp "$HUB/research/2026-03-26-learnair-curriculum-analysis.md" "$DEST/curriculum-analysis.md"
cp "$HUB/research/2026-03-23-oregon-employer-readiness.md" "$DEST/oregon-employer-readiness.md"
cp "$HUB/research/2026-03-23-target-contacts.md" "$DEST/target-contacts.md"
cp "$HUB/research/2026-03-26-alpha-school-deep-dive.md" "$DEST/alpha-school-model.md"
cp "$HUB/research/2026-03-22-oregon-landscape.md" "$DEST/oregon-landscape.md"

# --- Strategy ---
cp "$HUB/plans/2026-03-22-learnair-negotiation-strategy.md" "$DEST/negotiation-strategy.md"
cp "$HUB/plans/2026-03-22-strategic-stress-test.md" "$DEST/stress-test.md"
cp "$HUB/plans/2026-03-23-partnership-structure-options.md" "$DEST/partnership-options.md"
cp "$HUB/plans/2026-03-23-steelman-and-plan-of-attack.md" "$DEST/plan-of-attack.md"

# --- Key meetings ---
cp "$HUB/meetings/2026-03-19-learnair-justin-team.md" "$DEST/meeting-justin-team-mar19.md"
cp "$HUB/meetings/2026-03-23-andrew-mike-learnair-recap.md" "$DEST/meeting-mike-recap-mar23.md"
cp "$HUB/meetings/2026-04-02-mike-trisha-coffee.md" "$DEST/meeting-trisha-apr2.md"
cp "$HUB/meetings/2026-04-02-mike-call-full.md" "$DEST/meeting-mike-apr2.md"
cp "$HUB/meetings/2026-04-02-mike-synopsis.md" "$DEST/mike-synopsis-apr2.md"

# --- Mike's guides ---
cp "$HUB/plans/mike-workstation-guide.md" "$DEST/workstation-guide.md"
cp "$HUB/plans/mike-claude-concept-map.md" "$DEST/claude-concept-map.md"

COUNT=$(ls -1 "$DEST"/*.md 2>/dev/null | wc -l | tr -d ' ')
echo "Synced $COUNT docs to $DEST"
echo ""
echo "Mike can search these with: hub(\"employer signal\") or hub(\"competitive\")"
