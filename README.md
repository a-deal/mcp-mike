# Mike's Workspace Tools

Claude Desktop with superpowers. 13 tools that replace your manual workflows: find files anywhere on your machine, organize them into projects, learn with spaced repetition, prep for meetings, check your decisions, and share progress with Andrew.

You don't type commands. You talk to Claude and it uses the tools when relevant. Or ask directly: "quiz me on learnair," "find files about Teresa," "mochary: prep for my call with Justin."

## One-Time Setup (15 minutes)

You need: a Mac, Python 3.10+, and Claude Desktop installed.

**Step 1: Check Python version**
```bash
python3 --version
```
If it says 3.9 or lower, install from python.org first. 3.10+ means you're good.

**Step 2: Run these 4 commands**
```bash
cd ~/src
git clone https://github.com/a-deal/mcp-mike.git
git clone https://github.com/a-deal/learnair-context.git
cd mcp-mike && bash onboard.sh
```

That's it. The onboard script handles everything: workspace creation, server install, config generation, tests. Every step prints PASS or FAIL.

**Step 3: Restart Claude Desktop** (Cmd+Q, reopen)

**Step 4: Verify** -- open a new conversation and say:
```
quiz me on learnair
```
If you get a concept question, you're live.

## What You Can Do

| Say this in Claude Desktop | What happens |
|---|---|
| **Learning** | |
| "quiz me on learnair" | Spaced repetition quiz on LearnAIR domain concepts |
| "quiz me on internet" | Quiz on technical foundations |
| "quiz me on claude" | Quiz on Claude usage |
| "show my progress" | Per-track stats: started, mastered |
| "share my progress" | Checkpoint pushed to shared repo (Andrew can see it) |
| **Finding & Organizing** | |
| "find files about Teresa" | Scans Desktop, Documents, Downloads, Google Drive, Apple Notes |
| "find notes about workshop" | Searches Apple Notes by title |
| "ingest ~/Desktop/handout.pdf into workshops" | Copies file into your organized workspace |
| "ingest note:Teresa Follow-up into learnair" | Pulls Apple Note into workspace |
| **Strategy Docs** | |
| "search the hub for employer signal" | Searches shared context + personal workspace docs |
| **Thinking Frameworks** | |
| "mochary: prep for my call with Justin" | Meeting prep, DRIs, close protocol |
| "mochary: I have too many priorities" | Top Goal, Energy Audit, First 2 Minutes |
| "duke: should we commit to the 90-day pilot" | Decision audit, pre-mortem, backcasting |
| "duke: review this message before I send it" | Proposals not declarations, recipient space |
| "k: am I converging or diverging" | Convergence check, sequencing, systems thinking |
| "k: evening synthesis" | What stood out, what compounds, tomorrow's top 3 |
| **Thinker Workstation (your top 5)** | |
| "ng: designing module 1 practice" | SKILL — execution-first, output-based projects |
| "brynjolfsson: which roles should we target" | MARKET — complement not substitute, employer ROI |
| "nadella: how do we embed this in a workflow" | ENVIRONMENT — meet work where it lives, platforms |
| "mattis: how do I brief on this" | LEADERSHIP — commander's intent, 70% rule, reading |
| "priestley: how do we price the cohort" | POSITIONING — oversubscribed, 5 P's, ladder |
| **Daily Operations** | |
| "load nexus" | Loads a persona from your workspace |
| "what's next" | Scans all projects for TODOs |
| "save a note to learning: context windows clicked today" | Timestamped note to any project |

## The Goal

Everything leads to the capstone: build the Module 1 delivery agent for the LearnAIR curriculum. 65 concepts across 4 tracks prepare you for it. Open the workstation to see the full map:

**[andrewdeal.info/learnair/workstation](https://andrewdeal.info/learnair/workstation)**

## Daily Routine (1 hour)

1. Open the workstation. Read the next concept.
2. Open Claude Desktop. Do the practice exercise.
3. "quiz me on [track]" for spaced review.
4. "save a note to learning: [what clicked]"
5. "share my progress" to checkpoint.

## Updating

When Andrew pushes updates:
```bash
cd ~/src/mcp-mike && git pull
cd ~/src/learnair-context && git pull
```
Restart Claude Desktop.

## Your Workspace

```
~/Documents/claude-workspace/
  personas/       Your persona files
  learnair/       LearnAIR project notes
  workshops/      Workshop materials
  learning/       Learning notes and reflections
  reference/      Ingested files, links, templates
  hub/            Personal docs (hub search also checks shared repo)
  .progress.json  Quiz progress (auto-managed)

~/src/learnair-context/    Shared docs with Andrew (git pull to update)
~/src/mcp-mike/            The tools (git pull to update)
```

## Troubleshooting

**"Tool not found" in Claude Desktop:** Restart Claude Desktop. Run `bash onboard.sh` again.

**discover is slow:** It scans your whole machine. First run takes a few seconds. Say "find files about X" not "find everything."

**Apple Notes not working:** Make sure Notes app exists. The first time, macOS may ask permission.

**Something broke:** Text Andrew, or ask Claude: "Something's wrong with my workspace tools. Here's what happened: [describe]."
