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
mcp.tool()(whats_next)
mcp.tool()(save_note)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
