---
title: Thinker sources for Mike's workstation
last_refreshed: 2026-04-19
refresh_cadence: monthly
---

# Thinker Sources

Mike's top 5 thinkers (Apr 17, 2026), each mapped to a frame in his workstation.
This file is the curated source corpus Andrew maintains. When these thinkers
publish new work, Andrew updates this file and pushes. Mike pulls.

The `ng`, `brynjolfsson`, `nadella`, `mattis`, and `priestley` MCP tools return
frameworks inspired by these sources. To change the advice the tools give,
curate this file AND edit the corresponding function in `mcp_mike/tools.py`.

## Refresh cadence

Monthly, or sooner when a named thinker ships something major (new book, keynote,
long-form essay, consequential podcast appearance).

Refresh checklist:
1. Scan each thinker's canonical channel (below) for anything new since
   `last_refreshed`.
2. If relevant to Mike's frame, add it under the thinker's section below.
3. If the new work changes the guidance, edit the tool function in
   `mcp_mike/tools.py` and update the test that pins the change.
4. Run `bash refresh-thinkers.sh` to bump `last_refreshed` and commit.
5. Push. Mike pulls.

## Ng — SKILL (execution-first, output-based training)

**Canonical channels:**
- deeplearning.ai (The Batch newsletter)
- Stanford CS229, CS230 (archived lectures)
- YouTube: Stanford Online, DeepLearning.AI
- Twitter: @AndrewYNg

**Core works feeding the tool:**
- *Machine Learning Yearning* (free ebook)
- *AI for Everyone* (Coursera)
- "AI is the new electricity" (keynote, multiple venues)
- DeepLearning.AI Specializations (project-based pedagogy reference)

**Key patterns baked into the tool:**
- Error analysis > accuracy metric worship
- Data > algorithm (especially for small/specialized domains)
- Weekly hands-on projects as the teaching unit
- Decompose jobs into observable behaviors

## Brynjolfsson — MARKET (target roles with economic upside)

**Canonical channels:**
- Stanford Digital Economy Lab (digitaleconomy.stanford.edu)
- NBER working papers (search "Brynjolfsson")
- Twitter: @erikbryn

**Core works feeding the tool:**
- *The Second Machine Age* (w/ Andrew McAfee)
- *Machine, Platform, Crowd* (w/ McAfee)
- "The Turing Trap" (Daedalus essay, 2022)
- 2023 call-center study: Brynjolfsson, Li, Raymond — "Generative AI at Work"

**Key patterns baked into the tool:**
- Complement > substitute framing
- Task decomposition (O*NET approach)
- Bottom-up market sizing, not top-down
- J-curve: productivity gains lag tech investment

## Nadella — ENVIRONMENT (train inside real workflows)

**Canonical channels:**
- Microsoft CEO annual letter
- LinkedIn (his posts specifically)
- Stanford GSB / MIT Sloan talks on YouTube
- Microsoft Build keynotes

**Core works feeding the tool:**
- *Hit Refresh* (memoir)
- Microsoft annual letters (2014–present)
- Copilot launch keynote (2023 Build)
- Commentary on growth mindset / Carol Dweck

**Key patterns baked into the tool:**
- Empathy as strategy, not soft skill
- Meet work where it already happens (Copilot pattern)
- Platform over product; partner where not differentiated
- Learn-it-all > know-it-all

## Mattis — LEADERSHIP (clear intent under ambiguity)

**Canonical channels:**
- Hoover Institution talks
- Military history journals (Proceedings, Marine Corps Gazette)
- *Warriors and Citizens* podcast appearances

**Core works feeding the tool:**
- *Call Sign Chaos* (memoir, w/ Bing West)
- *Warriors and Citizens* (edited volume, Hoover)
- "Reading" interview (various venues) — the functional-illiteracy quote
- Commander's Intent doctrine (Marine Corps Doctrinal Publication 1)

**Key patterns baked into the tool:**
- Commander's Intent: purpose / key tasks / end state
- 70% rule for decisions under uncertainty
- OODA loop for crisis tempo
- Reading as leadership discipline
- Unit fights the way it trains

## Priestley — POSITIONING (scarcity and demand)

**Canonical channels:**
- Dent Global (dent.global)
- YouTube: Daniel Priestley channel
- LinkedIn (his posts specifically)
- Podcast appearances (Diary of a CEO, etc.)

**Core works feeding the tool:**
- *Key Person of Influence* (the 5 P's book)
- *Oversubscribed* (scarcity by design)
- *24 Assets* (category-builder)
- *Entrepreneur Revolution*

**Key patterns baked into the tool:**
- Oversubscribed > full (11 for 10, not 10 for 11)
- 5 P's: Pitch, Publish, Product, Profile, Partnership
- Ascending transaction ladder (free → low → mid → high ticket)
- Niche discipline (narrow who/what/how)

## How to add a new thinker

1. Add a section here with canonical channels, core works, key patterns.
2. Add a function to `mcp_mike/tools.py` following the `ng/brynjolfsson/nadella/mattis/priestley` shape.
3. Register it in `mcp_mike/server.py` (import + `mcp.tool()(name)`).
4. Add tests in `tests/test_tools.py` that pin the key patterns.
5. Run pytest. Green → commit → push.
