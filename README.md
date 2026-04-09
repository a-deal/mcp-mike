# Mike's Workspace Tools

This gives Claude Desktop superpowers. Seven tools that replace your manual workflows: no more pasting personas from Apple Notes, no more losing track of TODOs, no more forgetting what you learned yesterday.

Once installed, these tools just appear in your Claude conversations. You don't type commands. You just talk to Claude and it uses the tools when relevant. Or you can ask directly: "quiz me on learnair," "what's next on my list," "load my nexus persona."

## What You Get

**Load a persona instantly.** Instead of opening Apple Notes, copying Nexus, and pasting it into every chat, just say "load nexus." Claude reads it from your workspace and becomes that persona for the conversation.

**Search your strategy docs.** All the LearnAIR research, the thesis, the arc doc, meeting notes. Say "search the hub for employer signal" and Claude pulls the relevant passages. No more hunting through files.

**Learn with spaced repetition.** 65 concepts across 4 tracks. Say "quiz me" and you get the next concept due for review. Answer, mark it correct or wrong, and the system adjusts your review schedule automatically. Correct answers space out (1 day, 2, 4, 8, 16, 30). Wrong answers come back tomorrow. When you get one wrong, you get a plain-language analogy to help it click.

**Four learning tracks:**
- **LearnAIR Domain** (17 concepts) - the supervision gap, mission command to AI operators, adversarial collaboration, knowledge systems. What you need to teach.
- **Internet/Technical** (10 concepts) - HTTP, APIs, cloud, CLI, databases, MCP. The foundations.
- **Using Claude** (30 concepts) - prompting, projects, artifacts, context management. How to use the tool.
- **Capstone** (8 concepts) - build the Module 1 delivery agent. The product.

**Check your progress.** Say "show my progress" to see started/mastered counts per track.

**Track your TODOs.** Say "what's next" and Claude scans your project notes for action items.

**Save notes without leaving the conversation.** "Save a note to learning: commander's intent clicked today." It gets timestamped and appended to your project notes.

## The Goal

Everything leads to the capstone: you build the Module 1 delivery agent for the LearnAIR evergreen curriculum. An MCP server with 5 tools that helps a veteran map their military experience to AI supervision concepts. You're not building a school project. You're building the product.

Open the workstation to see the full curriculum map: [andrewdeal.info/learnair/workstation](https://andrewdeal.info/learnair/workstation)

## Setup (15 minutes)

You need Python 3.10 or higher. Check with:
```bash
python3 --version
```

If it says 3.9 or lower, we'll install a newer version together. If it says 3.10+, you're good.

### One command does everything:

```bash
cd ~/src
git clone https://github.com/a-deal/mcp-mike.git
cd mcp-mike
bash onboard.sh
```

The onboard script:
1. Checks prerequisites (Python, git, Claude Desktop)
2. Creates your workspace at `~/Documents/claude-workspace/`
3. Installs the MCP server
4. Verifies all 7 tools load
5. Seeds hub docs (if available)
6. Generates Claude Desktop config
7. Runs all tests

Every step prints PASS/FAIL so you know exactly where you are.

### After onboard.sh:

1. Restart Claude Desktop (Cmd+Q, then reopen)
2. Open a new conversation and try:
   - "quiz me on learnair"
   - "search the hub for employer signal"
   - "show my progress"
   - "save a note to learning: first session complete"

## Your Workspace

```
~/Documents/claude-workspace/
  personas/          Your persona files (.md)
  learnair/          LearnAIR project notes
  workshops/         Workshop materials
  learning/          Learning notes and reflections
  reference/         Links, templates, snippets
  hub/               Strategy docs (17 curated files)
  .progress.json     Quiz progress (auto-managed, don't edit)
```

## Tools Reference

| In conversation, say... | What happens |
|---|---|
| "Load my nexus persona" | Reads `personas/nexus.md` and sets it as context |
| "Search the hub for Break Line" | Searches all hub docs for matching passages |
| "Quiz me" | Picks the next concept due for review from any track |
| "Quiz me on learnair" | Quiz from LearnAIR domain track only |
| "Quiz me on internet" | Quiz from technical foundations track only |
| "Quiz me on claude" | Quiz from Claude usage track only |
| "Quiz me on capstone" | Quiz from capstone build track only |
| "I got it right" / "Mark as correct" | Records result, pushes review out further |
| "I got it wrong" / "Mark as wrong" | Records result, shows analogy, review comes back tomorrow |
| "Show my progress" | Shows started/mastered counts per track |
| "What's next" | Scans all project notes for TODOs and action items |
| "Save a note to learning: ..." | Appends timestamped note to `learning/notes.md` |

## Daily Routine (1 hour)

1. Open the [workstation](https://andrewdeal.info/learnair/workstation). Pick the next concept.
2. Read it. If confused, open the analogy.
3. Open Claude Desktop. Do the practice exercise.
4. Answer the teach-back quiz out loud or in writing.
5. "Quiz me on [track]" for spaced review of past concepts.
6. "Save a note to learning: [what clicked today]."

## Updating

When Andrew updates strategy docs or concepts:
```bash
cd ~/src/mcp-mike
git pull
```

If on Andrew's machine, also sync hub docs:
```bash
bash sync-hub.sh
```

## Troubleshooting

**"Tool not found" in Claude Desktop:** Restart Claude Desktop. Run `bash onboard.sh` again to verify the config.

**"Persona not found":** Check that your persona file is in `~/Documents/claude-workspace/personas/` and ends in `.md`.

**Onboard script fails at a step:** Read the FAIL message. It tells you exactly what's wrong. Fix it and re-run.

**Something else broke:** Text Andrew. Or ask Claude: "Something's wrong with my workspace tools. Here's what happened: [describe]."
