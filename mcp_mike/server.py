"""Mike's MCP server for Claude Desktop.

Tools:
  load_persona  - load a persona from workspace/personas/
  hub           - search hub docs by keyword
  quiz_me       - spaced repetition quiz (tracks: claude, learnair, internet, capstone)
  mark_concept  - record quiz result, adjust interval
  progress      - show learning stats across tracks
  mochary       - meeting prep, difficult conversations, accountability frameworks
  duke          - decision quality, message review, calibration
  komoroske     - systems thinking, sequencing, convergence checks
  ng            - SKILL: execution-first curriculum and practice (Andrew Ng)
  brynjolfsson  - MARKET: role targeting, market sizing, employer ROI (Erik Brynjolfsson)
  nadella       - ENVIRONMENT: real workflows, culture, platforms (Satya Nadella)
  mattis        - LEADERSHIP: commander's intent, decisions, team (Jim Mattis)
  priestley     - POSITIONING: scarcity, 5 P's, ascending ladder (Daniel Priestley)
  whats_next    - find TODOs across all projects
  save_note     - append a timestamped note to a project
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mcp_mike.tools import (
    load_persona,
    hub,
    discover,
    ingest,
    quiz_me,
    mark_concept,
    progress,
    checkpoint,
    mochary,
    duke,
    komoroske,
    ng,
    brynjolfsson,
    nadella,
    mattis,
    priestley,
    whats_next,
    save_note,
)

mcp = FastMCP(
    "Mike's Workspace",
    instructions=(
        "Mike's personal workspace tools. "
        "Use load_persona to load a persona (e.g. 'nexus') instead of Mike pasting it manually. "
        "Use hub to search LearnAIR and strategy docs by keyword. "
        "Use discover to find files and Apple Notes on Mike's machine by keyword. "
        "Use ingest to pull a file or Apple Note into the workspace, organized by project. "
        "Use quiz_me to do a spaced repetition quiz. Three tracks available: "
        "'claude' (how to use Claude), 'learnair' (domain knowledge for the veteran AI supervision curriculum), "
        "'internet' (technical foundations). Leave track empty for all. "
        "Use mark_concept after answering a quiz to track progress. "
        "Use progress to show learning stats across tracks. "
        "When Mike marks a concept wrong, share the 'confused' explanation to help it click. "
        "Use checkpoint to share learning progress with Andrew via the shared context repo. "
        "Suggest running checkpoint at the end of each learning session. "
        "Use mochary for meeting prep, difficult conversations, priorities, and accountability. "
        "Use duke for decision quality checks, message review before sending, and calibrating confidence. "
        "Use komoroske for sequencing priorities, convergence checks, and evening synthesis. "
        "Use ng (Andrew Ng) for Mike's SKILL frame: execution-first, output-based curriculum and practice design. "
        "Use brynjolfsson (Erik Brynjolfsson) for Mike's MARKET frame: role targeting, market sizing, employer ROI. "
        "Use nadella (Satya Nadella) for Mike's ENVIRONMENT frame: training inside real workflows, culture change, platform thinking. "
        "Use mattis (Jim Mattis) for Mike's LEADERSHIP frame: commander's intent, decisions under ambiguity, team cohesion. "
        "Use priestley (Daniel Priestley) for Mike's POSITIONING frame: scarcity, oversubscribed cohorts, the 5 P's. "
        "Use whats_next to see TODOs across all projects. "
        "Use save_note to capture decisions, action items, or thoughts to a project."
    ),
)

mcp.tool()(load_persona)
mcp.tool()(hub)
mcp.tool()(discover)
mcp.tool()(ingest)
mcp.tool()(quiz_me)
mcp.tool()(mark_concept)
mcp.tool()(progress)
mcp.tool()(checkpoint)
mcp.tool()(mochary)
mcp.tool()(duke)
mcp.tool()(komoroske)
mcp.tool()(ng)
mcp.tool()(brynjolfsson)
mcp.tool()(nadella)
mcp.tool()(mattis)
mcp.tool()(priestley)
mcp.tool()(whats_next)
mcp.tool()(save_note)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
