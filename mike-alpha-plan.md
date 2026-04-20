---
title: Mike's Alpha Week — How to Run It
audience: Mike
start_date: 2026-04-27 (week after next)
cadence: 90 min/day Mon-Fri + one weekday 1:1 with Andrew
companion_files: mike-cli-bridge.md (curriculum), concepts.json (spaced-rep deck)
last_updated: 2026-04-19
---

# Mike's Alpha Week

## What this is

You said "I'm down" on the Alpha School model Sunday night. This doc is the "yes, here's how" version. It's the structure for the next four weeks, starting the week of **April 27**. The goal is simple: you learn faster, you ship a real thing, and we both see what the model does to adult learning before you try to teach it to anyone else.

## Why this matters (the short version)

Alpha School's research finding is load-bearing: **software alone = 1x velocity. Software + structure + guide + project-based reps = 2.3x velocity.** The workstation I've built you is the software. This doc is the structure. The weekly 1:1 is the guide. Your job-search agent is the project.

Three sentences from the research that set the frame:
1. Compress instruction into 2 focused hours so the rest of the day is application, not lecture.
2. Mastery gates matter: don't advance past something you can't explain back.
3. A human in a guide role (not a teacher role) is the difference between the software being useful and it being transformative.

If you want the deep version, it's in the shared context repo at `learnair-context/` or I'll send it over. Not required reading. This doc is enough to start.

## Your daily 90 minutes

90 min total, Monday through Friday. Pick a time that's actually defensible given the baby and Nikki's schedule. Consistency beats cleverness here.

| Time | What you do | Tool |
|---|---|---|
| 0:00-0:03 | Open Claude Desktop. Ask "what's my progress today?" to orient. | `progress` |
| 0:03-0:20 | Quiz on 5-8 concepts across `cli`, `learnair`, and `capstone`. Be honest when you mark wrong. | `quiz me on cli`, `mark_concept` |
| 0:20-0:25 | For anything marked wrong, take one concrete action to close the gap. Re-read the summary, ask Claude to explain it differently, or save a note to revisit it. | `save a note to learning: ...` |
| 0:25-1:20 | **Project work on your job-search agent.** One concrete step forward per session. Something you can show me. | Claude Code, Claude Desktop, your editor |
| 1:20-1:25 | Supervision log: what worked, what broke, what you changed. One paragraph. | `save a note to learning: today I built X, got stuck on Y, fixed by Z` |
| 1:25-1:30 | Push your progress so I can see it. | `checkpoint` (Claude Desktop will run it when you say "share my progress") |

If 90 min won't work every day, pick 60. Missing a day is fine. Missing three in a row is data — tell me on our weekly and we adjust.

## Our weekly 1:1

30 minutes, weekday (you asked for weekday, Nikki has the weekend). I'll propose a specific day and time in a separate message once I see my week. Shooting for a weekday that's quiet for both of us.

First 1:1: week of April 27 or May 4. Your call on which kickoff fits.

What the 1:1 is for:
- I read your checkpoints before the call, so I show up knowing your state.
- You bring one friction point. Just one. We work through it.
- I bring one framing or one tool change based on what I saw in your checkpoints.
- We close with the one thing you're going to ship next week.

What the 1:1 is NOT:
- Not a status update. Your checkpoints handle that.
- Not LearnAIR strategy. That's a separate thread.
- Not therapy. We both have people for that.

## Your first capstone: the job-search agent

This is the shift from my original plan. I had you building `mcp-module1` (the LearnAIR delivery agent) as your capstone. You told me Sunday your actual first project is the resume-customizer + cover-letter-drafter + LinkedIn-outreach agent for your own job search. That's a better capstone. Here's why:

1. **You'll use it every day.** The thing you build should solve a problem you actually have. Resume-customization for real applications beats a teaching agent you never use.
2. **The skills transfer.** Building an agent that reads a job posting, pulls relevant context from your work history, and produces personalized output is exactly the skillset for `mcp-module1` later. You'll know the shape.
3. **Runway matters more than curriculum right now.** Your job-search agent has direct dollar value. Building it IS the parallel track.
4. **Dogfooding works better when the product serves you.** Alpha kids build food trucks because food is real. Your "food truck" is getting a job.

### The project structure

The four-week arc for this capstone:

**Week 1 (Apr 27-May 3): Foundation + first prototype**
- Get the CLI tier 1 concepts down (you pulled the cli bridge doc already). Goal: run `claude` in your own repo, feel comfortable.
- Build the simplest possible version: paste a job description, get a customized resume back. No LinkedIn, no cover letter yet. One tool, end to end.
- Gate: you can show me the tool working on one real job posting.

**Week 2 (May 4-10): Add cover letter + outreach**
- CLI tier 2 (tools, permissions, CLAUDE.md).
- Extend the agent to also produce a cover letter and 5-7 LinkedIn contacts per posting.
- Gate: end-to-end flow on two real postings.

**Week 3 (May 11-17): Monitor + flag**
- CLI tier 3 (slash commands, context management, plan mode).
- Add the background-monitoring piece: feed it BreakLine, Built.in, whatever job boards you track. It flags fits.
- Gate: agent runs unattended for 24 hours and flags at least one real match.

**Week 4 (May 18-24): Apply + iterate**
- Use the agent on 10 real applications. Track which went through and which didn't.
- Log every friction point. Fix three.
- Gate: you're using your own tool to apply for jobs you actually care about.

At the end of Week 4, you either have a job-search agent that's earning its keep, or you have the most-learned version of "how agents actually get built." Both outcomes are wins. The supervision log you're keeping along the way IS the facilitator guide for LearnAIR Module 1. Nothing gets wasted.

## Day 1 concrete checklist (for when you start)

Don't try to do this the day you start. Do this the day BEFORE. Sunday April 26.

- [ ] `cd ~/src/mcp-mike && git pull && bash onboard.sh` — gets you the latest tools and thinkers
- [ ] Restart Claude Desktop (Cmd+Q, reopen)
- [ ] Open a fresh conversation and say "quiz me on cli" to confirm the new track is live
- [ ] Block the 90-min window on your calendar for Mon-Fri of that week
- [ ] Decide where your job-search agent lives. Suggested: `~/src/job-search-agent` in a new git repo
- [ ] Reply to my Sunday night message with: (1) what time you picked, (2) which weekday works for our 1:1

Day 1 itself (Monday April 27):
- [ ] Run your 90-min block exactly as scheduled. Even if you feel like you don't have enough to do yet, run the full 90 min. The reps matter more than the output on Day 1.
- [ ] At 0:25, open an empty editor window and start your job-search agent. The first version can just be a single Python file with one function: `customize_resume(job_description, my_resume) -> customized_resume`. Doesn't matter if it's bad. Shipping bad on Day 1 beats shipping nothing on Day 7.
- [ ] Run `checkpoint` at the end. I'll see it.

## When things go wrong (FAQ)

**"I don't know what to build on Day 3."** Go to the quiz, mark any wrong answers honestly, then pick one to go deeper on. Ask Claude to build you a tiny scenario where that concept matters. Alpha-style: use what confused you today to drive what you build tomorrow.

**"The agent I'm building isn't working and I'm stuck."** Use the `komoroske` tool and ask: "am I converging or diverging on this?" If you're diverging, you're in a shiny-object loop. Narrow scope. If you're converging, push one more hour.

**"I have a huge energy dip by Wednesday."** Skip the 90 min. Do 30 min of just quiz. Come back full on Thursday. The streak matters less than the honesty.

**"Nikki or the baby needs me mid-block."** Stop the timer, go be present, come back later if you can, or note what happened and pick up tomorrow. The plan does not compete with your family. Full stop.

**"I'm drifting toward the Every rabbit holes again."** Compound engineering, Sparkle, Spiral, Cora — all worth your time eventually. Not during the 90 min. During the 90 min, you're dogfooding Alpha. After, read whatever you want.

## How I'll know it's working

Not by how many concepts you've mastered. By three signals:

1. **You send me a checkpoint every day for a full week.** Streak of 5. That tells me the block is real.
2. **Your job-search agent does one useful thing by end of Week 1.** Customized resume on one real posting. Evidence of shipping.
3. **You come to the first 1:1 with ONE specific friction point**, not "it's going okay." That tells me you're learning, because learners always have friction to name.

If any of those three are missing by end of Week 1, I'll tell you straight: the structure isn't landing, and we adjust. No shame in adjusting. Shame is in pretending it's working when it isn't.

## What I'm doing on my end

Parallel accountability: I'm running my own Alpha week on my own learning (ML internals, portfolio work, the Stanford AI event this Friday). Different subject matter, same structure. If my version works, I'll tell you what I learned. If mine breaks, I'll tell you that too.

## Last thing

You said "I'm down" on Sunday and I took it as a yes. If between now and April 27 it turns into a "not this time" or a "let me start in June," just tell me. The plan lives in the repo regardless. The worst outcome isn't you pausing. The worst outcome is you grinding through a structure that doesn't fit and neither of us saying so.

See you on the kickoff.

Andrew

## Related files in this repo

- `mike-cli-bridge.md` — the 4-week CLI curriculum, tier by tier
- `concepts.json` — the 80-concept spaced-rep deck (`cli`, `learnair`, `internet`, `capstone`, Claude Desktop)
- `thinkers.md` — the source corpus for the 5 thinker tools (Ng, Brynjolfsson, Nadella, Mattis, Priestley)
- `README.md` — start here if something breaks

## Sources (if you want to go deep)

- Alpha School deep-dive (my notes on the model): in `~/src/learnair-context/` after you pull
- Alpha School official: [alpha.school](https://alpha.school/)
- Bloom's 2 Sigma Problem (the 1984 paper this all sits on): searchable term "Bloom 2 sigma"
- MacKenzie Price on Modern Wisdom #981 (podcast, ~1h 11m): direct founder explanation
