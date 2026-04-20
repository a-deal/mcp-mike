---
title: Mike's Bridge from Claude Desktop to Claude Code CLI
audience: Mike
cadence: one week per tier
companion: `quiz me on cli` (spaced repetition deck in mcp-mike)
last_updated: 2026-04-19
---

# Mike's CLI Bridge

Four weeks, five tiers, fifteen concepts. Each tier is a week of practice,
not a week of reading. You already know Claude Desktop. This gets you fluent
in Claude Code — the CLI that works directly on your filesystem — so you can
run the same agent workflows on real projects, not just in chats.

**How to use this doc:**
1. Read the week's section. Ten minutes max.
2. Run `quiz me on cli` in Claude Desktop. Answer the questions. Mark
   correct or wrong honestly.
3. Do the week's practice task. Keep it under an hour.
4. `save a note to learning: [what clicked this week]`
5. Move to the next week when you can demo the tier's skills without help.

If a week feels easy, skip to the practice and move on. If it feels hard,
stay another week. The spaced-repetition deck in `mcp-mike` covers the same
15 concepts so your knowledge compounds without re-reading.

---

## Week 1: Foundations (Tier 1)

**Goal:** you can open a terminal, navigate to a project, and start a Claude
Code session without asking anyone for help.

Concepts (all in the `cli` track, quizzed by the tool):
- **Claude Code vs. Claude Desktop** — Desktop is a briefing room. CLI is a
  teammate on the ground.
- **Terminal Basics** — five commands carry 90% of your CLI work: `cd`,
  `ls`, `pwd`, `cat`, Cmd+T.
- **Installing Claude Code** — `npm install -g @anthropic-ai/claude-code`,
  verified with `claude --version`.
- **Your First Claude Code Session** — run `claude` inside a project
  directory, talk in plain English, exit with Ctrl+C twice.

Practice (one hour, end-to-end):
1. Open Terminal.
2. `cd ~/src/mcp-mike`
3. `claude`
4. Ask: "What does this project do? Summarize it in 3 sentences."
5. Ask: "Which file is the biggest? Show me its first 20 lines."
6. Exit with Ctrl+C twice.
7. Save a note: `save a note to learning: first claude code session felt like...`

**Milestone to clear Week 1:** you can go from "I want to use Claude Code"
to a running session in under 60 seconds.

---

## Week 2: Working with the Agent (Tier 2)

**Goal:** you understand the safety rails. Claude asks before it touches
anything. You know what it's asking and when to say yes vs. no.

Concepts:
- **The Tools Claude Uses** — Read, Edit, Write, Bash, Grep, Glob. You
  describe the job; Claude picks the tool.
- **Permission Prompts** — Yes / Yes, always / No. Reading is free; editing
  and running shell commands cost you a nod.
- **Permission Modes** — Default (ask first), Plan (no actions, just plan),
  Accept Edits (auto-approve edits, still ask bash), Bypass (no prompts).
  Shift+Tab to switch.
- **CLAUDE.md** — project-level standing order. Drop a CLAUDE.md at the
  root; Claude reads it every session.

Practice (one hour):
1. Run `claude` in any project.
2. Ask: "Add a new heading to README.md called 'Notes' with one line under it."
3. Watch the permission prompt. Approve with Yes (not Yes, always).
4. Hit Shift+Tab to cycle through permission modes. Stop at Plan mode.
5. Ask for something ambitious ("refactor the project to be cleaner"). Read
   the plan. Don't execute. Exit plan mode.
6. Look at `~/.claude/CLAUDE.md` on Andrew's machine. Read the "Testing" section.
   Imagine what you'd put in a CLAUDE.md for your own projects.

**Milestone to clear Week 2:** you can explain to someone non-technical why
"Yes, always" is dangerous for `rm -rf` and safe for `ls`.

---

## Week 3: Workflow (Tier 3)

**Goal:** your long sessions stay crisp. You know how to reset context, run
common actions fast, and plan before you act.

Concepts:
- **Slash Commands** — `/help`, `/clear`, `/compact`, `/model`, `/init`.
  Fast hotkeys for common actions.
- **Context Management** — `/clear` wipes. `/compact` keeps a summary.
  New terminal window = fresh everything. Watch for the signal: Claude
  repeating or forgetting.
- **Plan Mode** — always plan before anything multi-file or risky. Read
  the plan, cut the parts you don't want, then execute.

Practice (one hour):
1. Run `claude`. Type `/help`. Read the slash commands list once.
2. Start a session. Do 5 back-and-forth turns. Run `/compact`. Read the
   summary it keeps.
3. Start another session. Shift+Tab to Plan Mode. Ask Claude to "refactor
   the largest file." Read the plan. Identify one step you'd cut. Exit plan mode.
4. Try `/clear` mid-session and feel the freshness.

**Milestone to clear Week 3:** you can recognize context decay and run the
right reset command within 10 seconds.

---

## Week 4: Extending the Agent (Tier 4)

**Goal:** your Desktop workflow (mcp-mike tools, personas) works in Claude Code
too. One toolkit, two surfaces.

Concepts:
- **Skills** — Andrew's personas (Duke, Nexus, K) are skills. Invoke with
  `/duke`, `/k`. In Desktop you pasted personas; in CLI they're always available.
- **MCP Servers in Claude Code** — the same mcp-mike server you use in
  Desktop works in Claude Code. Run `quiz me on cli` inside a CLI session.
  One server, two surfaces.

Practice (one hour):
1. Run `claude` in any directory.
2. Type `/` and scroll through the available skills. Try `/duke` with a
   sample message to review.
3. Still in CLI, ask: "quiz me on cli." If mcp-mike is connected, you get
   a real quiz. If not, Andrew will fix the config.
4. Save a note: `save a note to learning: desktop and cli now feel like...`

**Milestone to clear Week 4:** you can do a complete learning loop (hub
search → quiz → save note) from a Claude Code terminal session.

---

## Week 5+: Advanced (Tier 5) — optional, when you're ready

**Goal:** automate repetitive patterns and parallelize work.

Concepts:
- **Hooks** — run a shell command when Claude does specific things
  (before a tool runs, after a file edit, when a session stops). Configured
  in `~/.claude/settings.json`. Start simple: play a sound when Claude
  finishes. Graduate to auto-run tests after every edit.
- **Subagents** — spawn a focused Claude to handle one task in parallel
  while your main session stays clean. Good for research, review, experiments.

No practice here until you feel friction that hooks or subagents would solve.
Don't build automation you don't need yet.

---

## How to know you're done with the bridge

You should be able to:
1. Run Claude Code on your LearnAIR repo and ask it to propose changes.
2. Switch permission modes based on the task.
3. Drop a CLAUDE.md in a project and know what to put in it.
4. Use mcp-mike tools from both Desktop and CLI.
5. Know when to start fresh vs. compact vs. keep going.

At that point, you're not "using Claude Code." You're running agent workflows
on real code. That's the capstone of the curriculum.

---

## Refreshing this doc

Andrew updates this doc and the `cli` track in `concepts.json` when:
- Claude Code ships a major new feature worth teaching
- Mike reports a confusion point that isn't covered

If you hit a friction point that isn't here, text Andrew. He adds it.
