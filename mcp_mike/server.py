"""Mike's MCP server for Claude Desktop.

Tools:
  load_persona  - load a persona from workspace/personas/
  hub           - search hub docs by keyword
  quiz_me       - spaced repetition quiz (tracks: claude, learnair, internet)
  mark_concept  - record quiz result, adjust interval
  progress      - show learning stats across tracks
  whats_next    - find TODOs across all projects
  save_note     - append a timestamped note to a project
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mcp_mike.tools import (
    load_persona,
    hub,
    quiz_me,
    mark_concept,
    progress,
    whats_next,
    save_note,
)

mcp = FastMCP(
    "Mike's Workspace",
    instructions=(
        "Mike's personal workspace tools. "
        "Use load_persona to load a persona (e.g. 'nexus') instead of Mike pasting it manually. "
        "Use hub to search LearnAIR and strategy docs by keyword. "
        "Use quiz_me to do a spaced repetition quiz. Three tracks available: "
        "'claude' (how to use Claude), 'learnair' (domain knowledge for the veteran AI supervision curriculum), "
        "'internet' (technical foundations). Leave track empty for all. "
        "Use mark_concept after answering a quiz to track progress. "
        "Use progress to show learning stats across tracks. "
        "When Mike marks a concept wrong, share the 'confused' explanation to help it click. "
        "Use whats_next to see TODOs across all projects. "
        "Use save_note to capture decisions, action items, or thoughts to a project."
    ),
)

mcp.tool()(load_persona)
mcp.tool()(hub)
mcp.tool()(quiz_me)
mcp.tool()(mark_concept)
mcp.tool()(progress)
mcp.tool()(whats_next)
mcp.tool()(save_note)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
