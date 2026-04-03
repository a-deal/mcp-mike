# Mike's Workspace Tools

This gives Claude Desktop superpowers. Six tools that replace your manual workflows: no more pasting personas from Apple Notes, no more losing track of TODOs, no more forgetting what you learned yesterday.

Once installed, these tools just appear in your Claude conversations. You don't type commands. You just talk to Claude and it uses the tools when relevant. Or you can ask directly: "quiz me," "what's next on my list," "load my nexus persona."

## What You Get

**Load a persona instantly.** Instead of opening Apple Notes, copying Nexus, and pasting it into every chat, just say "load nexus." Claude reads it from your workspace and becomes that persona for the conversation.

**Search your strategy docs.** All the LearnAIR research, the thesis, the arc doc, meeting notes. Say "search the hub for employer signal" and Claude pulls the relevant passages. No more hunting through files.

**Learn Claude with spaced repetition.** 30 concepts organized into weekly tiers. Say "quiz me" and you get the next concept due for review. Answer, mark it correct or wrong, and the system adjusts your review schedule automatically. Correct answers space out (1 day, 2, 4, 8, 16, 30). Wrong answers come back tomorrow.

**Track your TODOs.** Say "what's next" and Claude scans your project notes for action items and TODOs across everything you're working on.

**Save notes without leaving the conversation.** "Save a note to learnair: Teresa confirmed curriculum access." It gets timestamped and appended to your project notes.

## Setup (15 minutes, one time)

You need Python 3.10 or higher. Check with:
```bash
python3 --version
```

If it says 3.9 or lower, we'll install a newer version together. If it says 3.10+, you're good.

### Step 1: Get the code

Open Terminal (it's in Applications > Utilities, or hit Cmd+Space and type "Terminal").

```bash
cd ~/src
git clone https://github.com/a-deal/mcp-mike.git
cd mcp-mike
```

### Step 2: Run setup

```bash
bash setup.sh
```

This creates your workspace folders, installs the server, and prints a config snippet. It looks something like this:

```json
{
  "mcpServers": {
    "mike-workspace": {
      "command": "/Users/mike/src/mcp-mike/.venv/bin/python3",
      "args": ["-m", "mcp_mike.server"],
      "env": {
        "MIKE_WORKSPACE": "/Users/mike/Documents/claude-workspace"
      }
    }
  }
}
```

### Step 3: Add to Claude Desktop

1. Open Claude Desktop
2. Go to Settings (Cmd+,) > Developer > Edit Config
3. Paste the config snippet from Step 2
4. Save and restart Claude Desktop

### Step 4: Seed your docs

```bash
bash sync-hub.sh
```

This copies 20 curated strategy docs into your workspace so the hub search has something to find.

### Step 5: Add your personas

Move your personas from Apple Notes to your workspace:

```
~/Documents/claude-workspace/personas/nexus.md
~/Documents/claude-workspace/personas/mens-work.md
~/Documents/claude-workspace/personas/holotropics.md
```

Each file is just the text of your persona. Plain text, nothing fancy. You can create them in TextEdit (Format > Make Plain Text) or ask Claude to help you format them.

### Step 6: Verify

Open a new conversation in Claude Desktop. Say:

> "Load my nexus persona"

If it responds with your Nexus persona content, you're good. If it says it can't find the tool, restart Claude Desktop.

Then try:

> "Quiz me on the next Claude concept"

> "Search the hub for employer signal"

> "What's next on my TODO list"

## Your Workspace

After setup, your workspace looks like this:

```
~/Documents/claude-workspace/
  personas/          Your persona files (.md)
  learnair/          LearnAIR project notes
  workshops/         Workshop materials
  learning/          Claude learning notes
  reference/         Links, templates, snippets
  hub/               Strategy docs (20 curated files)
  .progress.json     Quiz progress (auto-managed, don't edit)
```

You can add folders for new projects anytime. Just create the folder and drop a `notes.md` in it. The tools will pick it up automatically.

## Tools Reference

| In conversation, say... | What happens |
|---|---|
| "Load my nexus persona" | Reads `personas/nexus.md` and sets it as context |
| "Search the hub for Break Line" | Searches all 20 hub docs for matching passages |
| "Quiz me" | Picks the next concept due for review based on your progress |
| "I got it right" / "Mark context-window as correct" | Records result, pushes review out further |
| "I got it wrong" / "Mark tokens as wrong" | Records result, shows the summary, review comes back tomorrow |
| "What's next" | Scans all project notes for lines with TODO or action items |
| "Save a note to learnair: Teresa wants a follow-up April 21" | Appends timestamped note to `learnair/notes.md` |

## The Learning System

30 concepts across 6 tiers. You don't need to manage the schedule. Just say "quiz me" once a day and the system handles the rest.

**Tier 1 (Week 1):** What Claude is, models, context window, system prompts, tokens, temperature

**Tier 2 (Week 2):** Artifacts, prompt specificity, iterative refinement, file attachments, multi-turn strategy, projects

**Tier 3 (Week 3):** Role assignment, chain of thought, structured extraction, comparison prompting, teaching voice, negative constraints

**Tier 4 (Week 4):** Project instructions, knowledge files, artifact iteration, thread hygiene

**Tier 5 (Week 5-6):** MCP, markdown, file system thinking, context as architecture

**Tier 6 (Ongoing):** Frustration flip, template twice, 80/20 review, summary handoff

Each concept has a definition, why it matters for your specific workflow, a practice exercise, and a quiz question. The full concept map is in `hub/claude-concept-map.md`.

## Updating

When Andrew updates strategy docs:
```bash
cd ~/src/mcp-mike
bash sync-hub.sh
```

That's it. New docs show up in your hub searches immediately.

## Troubleshooting

**"Tool not found" in Claude Desktop:** Restart Claude Desktop. Check that the config path in Step 3 points to the right Python. Run `bash setup.sh` again to verify.

**"Persona not found":** Check that your persona file is in `~/Documents/claude-workspace/personas/` and ends in `.md`. The name is the filename without the extension (e.g., `nexus.md` = "nexus").

**Rate limit hit during quiz:** The quiz tools are lightweight. This is probably from your conversation, not the tools. Take a break and come back.

**Something else broke:** Text Andrew. Or ask Claude: "Something's wrong with my workspace tools. Here's what happened: [describe]." Claude can probably debug it with you.
