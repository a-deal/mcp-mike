#!/usr/bin/env python3
"""Generate learnair/workstation.html from concepts.json.

Reads mcp-mike/concepts.json and emits a standalone HTML page with:
  - 5 (track) x 6 (tier) concept map grid
  - Per-track detail sections with quiz prompts
  - Gate script + design tokens matching the existing learnair site

Output: ~/src/a-deal.github.io/learnair/workstation.html
"""
from __future__ import annotations

import html
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONCEPTS = ROOT / "concepts.json"
OUT = Path.home() / "src/a-deal.github.io/learnair/workstation.html"

TRACKS = [
    ("claude", "Claude Desktop", "Foundations. How the model thinks, how context works, where it breaks."),
    ("cli", "Claude Code / CLI", "Bridge from the browser to the terminal. Agents, permissions, tool use."),
    ("internet", "Internet & Computing", "Technical substrate. HTTP, cloud, APIs, deployment."),
    ("learnair", "LearnAIR Domain", "The thesis. Mission command, supervision patterns, veteran-operator pedagogy."),
    ("capstone", "Capstone Project", "Your job-search agent. Five tools, commander's intent, end-to-end."),
]

TRACK_COLORS = {
    "claude":   "#b44a2d",
    "cli":      "#2d6a4f",
    "internet": "#1e40af",
    "learnair": "#a06c23",
    "capstone": "#6d28d9",
}


def load_concepts() -> list[dict]:
    return json.loads(CONCEPTS.read_text())


def normalize_track(c: dict) -> str:
    return c.get("track") or "claude"


def build_grid(concepts: list[dict]) -> dict[tuple[str, int], list[dict]]:
    grid: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for c in concepts:
        key = (normalize_track(c), c.get("tier", 0))
        grid[key].append(c)
    for key in grid:
        grid[key].sort(key=lambda c: c["name"])
    return grid


def pill(c: dict) -> str:
    track = normalize_track(c)
    return (
        f'<a class="chip chip-{track}" href="#c-{html.escape(c["id"])}" '
        f'title="{html.escape(c["summary"])}">'
        f'{html.escape(c["name"])}</a>'
    )


def render_grid(grid: dict) -> str:
    rows = []
    # Header row
    header = ['<div class="map-cell map-header map-corner"><span>tier ↓ · track →</span></div>']
    for tid, tname, _ in TRACKS:
        header.append(
            f'<div class="map-cell map-header map-track-{tid}">'
            f'<span class="dot"></span>{html.escape(tname)}</div>'
        )
    rows.append("".join(header))
    # Tier rows
    for tier in range(1, 7):
        row = [f'<div class="map-cell map-header map-tier">Tier {tier}</div>']
        for tid, _, _ in TRACKS:
            cell_concepts = grid.get((tid, tier), [])
            if not cell_concepts:
                row.append('<div class="map-cell map-empty">—</div>')
                continue
            chips = "".join(pill(c) for c in cell_concepts)
            row.append(f'<div class="map-cell">{chips}</div>')
        rows.append("".join(row))
    return '<div class="map-grid">' + "".join(rows) + "</div>"


def render_track_section(track_id: str, title: str, blurb: str, concepts: list[dict]) -> str:
    if not concepts:
        return ""
    concepts = sorted(concepts, key=lambda c: (c.get("tier", 0), c["name"]))
    cards = []
    for c in concepts:
        tier = c.get("tier", "?")
        cards.append(f"""
      <article class="card" id="c-{html.escape(c['id'])}">
        <div class="card-head">
          <span class="card-tier">T{tier}</span>
          <h4>{html.escape(c['name'])}</h4>
        </div>
        <p class="card-summary">{html.escape(c['summary'])}</p>
        <div class="card-quiz">
          <span class="quiz-label">Quiz</span>
          <p>{html.escape(c.get('quiz', ''))}</p>
        </div>
      </article>""")
    return f"""
    <section class="track-section" id="track-{track_id}">
      <div class="track-head">
        <span class="track-swatch swatch-{track_id}"></span>
        <div>
          <h3>{html.escape(title)}</h3>
          <p class="track-blurb">{html.escape(blurb)}</p>
        </div>
        <span class="track-count">{len(concepts)} concepts</span>
      </div>
      <div class="card-grid">
        {''.join(cards)}
      </div>
    </section>"""


def render_html(concepts: list[dict]) -> str:
    grid = build_grid(concepts)
    track_sections = []
    for tid, name, blurb in TRACKS:
        section_concepts = [c for c in concepts if normalize_track(c) == tid]
        track_sections.append(render_track_section(tid, name, blurb, section_concepts))

    tier_counts = defaultdict(int)
    for c in concepts:
        tier_counts[c.get("tier", 0)] += 1

    track_legend = "".join(
        f'<span class="legend-item"><span class="dot dot-{tid}"></span>{html.escape(name)} '
        f'<span class="legend-count">{sum(1 for c in concepts if normalize_track(c) == tid)}</span></span>'
        for tid, name, _ in TRACKS
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<script>if(localStorage.getItem('learnair_access')!=='granted'){{window.location.href='gate.html?r='+encodeURIComponent(location.pathname.split('/').pop()||'index.html');}}</script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>Mike's Workstation — Concept Map | LearnAIR</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --ink: #0a0a0a; --paper: #f4f1eb; --warm: #e8e3d9; --accent: #b44a2d;
    --accent-soft: rgba(180, 74, 45, 0.08); --muted: #6b6560; --faint: #c9c3b8;
    --white: #fefdfb;
    --claude:   #b44a2d; --claude-soft:   rgba(180, 74, 45, 0.10);
    --cli:      #2d6a4f; --cli-soft:      rgba(45, 106, 79, 0.10);
    --internet: #1e40af; --internet-soft: rgba(30, 64, 175, 0.08);
    --learnair: #a06c23; --learnair-soft: rgba(160, 108, 35, 0.10);
    --capstone: #6d28d9; --capstone-soft: rgba(109, 40, 217, 0.09);
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html {{ font-size: 17px; scroll-behavior: smooth; -webkit-font-smoothing: antialiased; }}
  body {{ font-family: 'Space Grotesk', sans-serif; background: var(--paper); color: var(--ink); line-height: 1.65; }}
  a {{ color: inherit; }}

  nav {{ position: sticky; top: 0; z-index: 100; background: rgba(244, 241, 235, 0.92);
    backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
    border-bottom: 1px solid var(--faint); padding: 0.75rem 1.5rem; }}
  .nav-inner {{ max-width: 1180px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; gap: 1rem; }}
  nav .logo {{ font-family: 'JetBrains Mono', monospace; font-weight: 500; font-size: 0.78rem;
    letter-spacing: 0.15em; text-transform: uppercase; color: var(--accent); text-decoration: none;
    display: flex; align-items: center; gap: 0.6rem; }}
  .doc-badge {{ font-size: 0.55rem; letter-spacing: 0.1em; background: var(--ink); color: var(--paper);
    padding: 2px 7px; font-weight: 500; }}
  .back-link {{ font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; letter-spacing: 0.06em;
    text-decoration: none; color: var(--muted); font-weight: 500; }}
  .back-link:hover {{ color: var(--ink); }}

  .hero {{ max-width: 1180px; margin: 0 auto; padding: 3rem 1.5rem 1.25rem; }}
  .hero .kicker {{ font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; letter-spacing: 0.22em;
    text-transform: uppercase; color: var(--accent); margin-bottom: 0.75rem;
    display: flex; align-items: center; gap: 0.75rem; }}
  .hero .kicker::before {{ content: ''; width: 2rem; height: 1px; background: var(--accent); }}
  .hero h1 {{ font-family: 'Instrument Serif', serif; font-weight: 400; font-size: clamp(2rem, 4.5vw, 2.8rem);
    line-height: 1.1; margin-bottom: 0.9rem; letter-spacing: -0.01em; }}
  .hero h1 em {{ font-style: italic; color: var(--accent); }}
  .hero .subtitle {{ font-size: 0.97rem; color: var(--muted); max-width: 680px; }}
  .hero .subtitle code {{ font-family: 'JetBrains Mono', monospace; font-size: 0.85em;
    background: var(--accent-soft); color: var(--accent); padding: 0.08rem 0.35rem; border-radius: 4px; }}
  .hero .stat-row {{ display: flex; flex-wrap: wrap; gap: 1.25rem; margin-top: 1.25rem;
    font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; letter-spacing: 0.1em;
    text-transform: uppercase; color: var(--muted); }}
  .hero .stat strong {{ color: var(--ink); font-weight: 600; font-size: 0.8rem; margin-right: 0.3rem; }}

  .how {{ max-width: 1180px; margin: 1.5rem auto 2rem; padding: 0 1.5rem; }}
  .how-card {{ background: var(--ink); color: var(--paper); border-radius: 14px; padding: 1.5rem 1.75rem; }}
  .how-card h3 {{ font-family: 'JetBrains Mono', monospace; font-weight: 500; font-size: 0.7rem;
    letter-spacing: 0.2em; text-transform: uppercase; color: var(--accent); margin-bottom: 1rem; }}
  .how-row {{ display: flex; gap: 1.25rem; padding: 0.55rem 0; border-bottom: 1px solid rgba(255,255,255,0.07);
    font-size: 0.88rem; align-items: baseline; }}
  .how-row:last-child {{ border-bottom: none; }}
  .how-label {{ font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: var(--accent);
    min-width: 160px; flex-shrink: 0; }}
  .how-desc {{ color: rgba(250,249,246,0.85); }}
  .how-desc code {{ font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;
    background: rgba(255,255,255,0.09); padding: 0.12rem 0.4rem; border-radius: 4px; color: var(--paper); }}

  .section-title {{ max-width: 1180px; margin: 2.5rem auto 1rem; padding: 0 1.5rem; }}
  .section-title h2 {{ font-family: 'Instrument Serif', serif; font-weight: 400; font-size: 1.75rem;
    letter-spacing: -0.01em; }}
  .section-title p {{ color: var(--muted); font-size: 0.92rem; margin-top: 0.3rem; max-width: 720px; }}

  .legend {{ max-width: 1180px; margin: 0.75rem auto 1rem; padding: 0 1.5rem;
    display: flex; flex-wrap: wrap; gap: 1rem; font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted); }}
  .legend-item {{ display: flex; align-items: center; gap: 0.4rem; }}
  .legend-count {{ color: var(--ink); margin-left: 0.35rem; }}
  .dot {{ display: inline-block; width: 0.55rem; height: 0.55rem; border-radius: 50%; background: var(--muted); }}
  .dot-claude {{ background: var(--claude); }}
  .dot-cli {{ background: var(--cli); }}
  .dot-internet {{ background: var(--internet); }}
  .dot-learnair {{ background: var(--learnair); }}
  .dot-capstone {{ background: var(--capstone); }}

  .map-wrap {{ max-width: 1180px; margin: 0 auto 2rem; padding: 0 1.5rem; }}
  .map-grid {{ display: grid; grid-template-columns: 110px repeat(5, 1fr); gap: 0;
    background: var(--white); border: 1px solid var(--faint); border-radius: 14px; overflow: hidden; }}
  .map-cell {{ padding: 0.75rem 0.75rem; border-right: 1px solid var(--faint);
    border-bottom: 1px solid var(--faint); min-height: 88px;
    display: flex; flex-wrap: wrap; gap: 0.35rem; align-content: flex-start; }}
  .map-cell:nth-child(6n) {{ border-right: none; }}
  .map-grid > .map-cell:nth-last-child(-n+6) {{ border-bottom: none; }}
  .map-header {{ font-family: 'JetBrains Mono', monospace; font-size: 0.68rem;
    letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted); background: var(--warm);
    min-height: auto; padding: 0.75rem; align-items: center; font-weight: 500; }}
  .map-header.map-track-claude {{ color: var(--claude); }}
  .map-header.map-track-cli {{ color: var(--cli); }}
  .map-header.map-track-internet {{ color: var(--internet); }}
  .map-header.map-track-learnair {{ color: var(--learnair); }}
  .map-header.map-track-capstone {{ color: var(--capstone); }}
  .map-header .dot {{ margin-right: 0.45rem; }}
  .map-track-claude .dot {{ background: var(--claude); }}
  .map-track-cli .dot {{ background: var(--cli); }}
  .map-track-internet .dot {{ background: var(--internet); }}
  .map-track-learnair .dot {{ background: var(--learnair); }}
  .map-track-capstone .dot {{ background: var(--capstone); }}
  .map-tier {{ writing-mode: horizontal-tb; font-weight: 600; color: var(--ink); background: var(--warm);
    justify-content: flex-start; }}
  .map-corner {{ background: var(--warm); color: var(--muted); font-size: 0.6rem; }}
  .map-empty {{ color: var(--faint); font-size: 0.9rem; justify-content: center; align-items: center; }}

  .chip {{ display: inline-block; font-size: 0.72rem; line-height: 1.3; padding: 0.3rem 0.55rem;
    border-radius: 6px; text-decoration: none; font-weight: 500; border: 1px solid transparent;
    transition: transform 0.12s ease, box-shadow 0.12s ease; }}
  .chip:hover {{ transform: translateY(-1px); box-shadow: 0 2px 6px rgba(0,0,0,0.08); }}
  .chip-claude {{ background: var(--claude-soft); color: var(--claude); border-color: rgba(180, 74, 45, 0.25); }}
  .chip-cli {{ background: var(--cli-soft); color: var(--cli); border-color: rgba(45, 106, 79, 0.25); }}
  .chip-internet {{ background: var(--internet-soft); color: var(--internet); border-color: rgba(30, 64, 175, 0.25); }}
  .chip-learnair {{ background: var(--learnair-soft); color: var(--learnair); border-color: rgba(160, 108, 35, 0.28); }}
  .chip-capstone {{ background: var(--capstone-soft); color: var(--capstone); border-color: rgba(109, 40, 217, 0.25); }}

  .tracks {{ max-width: 1180px; margin: 0 auto; padding: 0 1.5rem 4rem; }}
  .track-section {{ margin-top: 2.5rem; }}
  .track-head {{ display: flex; align-items: center; gap: 1rem; padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--faint); margin-bottom: 1.25rem; }}
  .track-swatch {{ width: 6px; align-self: stretch; border-radius: 3px; flex-shrink: 0; }}
  .swatch-claude {{ background: var(--claude); }}
  .swatch-cli {{ background: var(--cli); }}
  .swatch-internet {{ background: var(--internet); }}
  .swatch-learnair {{ background: var(--learnair); }}
  .swatch-capstone {{ background: var(--capstone); }}
  .track-head h3 {{ font-family: 'Instrument Serif', serif; font-weight: 400; font-size: 1.45rem; }}
  .track-head p.track-blurb {{ color: var(--muted); font-size: 0.88rem; margin-top: 0.15rem; }}
  .track-count {{ margin-left: auto; font-family: 'JetBrains Mono', monospace; font-size: 0.65rem;
    letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); }}

  .card-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 0.9rem; }}
  .card {{ background: var(--white); border: 1px solid var(--faint); border-radius: 12px;
    padding: 1rem 1.1rem; }}
  .card-head {{ display: flex; align-items: baseline; gap: 0.6rem; margin-bottom: 0.5rem; }}
  .card-tier {{ font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; letter-spacing: 0.1em;
    color: var(--muted); background: var(--warm); padding: 0.1rem 0.4rem; border-radius: 4px; }}
  .card h4 {{ font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 0.95rem; line-height: 1.3; }}
  .card-summary {{ font-size: 0.85rem; color: var(--ink); margin-bottom: 0.7rem; }}
  .card-quiz {{ border-top: 1px dashed var(--faint); padding-top: 0.55rem; }}
  .quiz-label {{ font-family: 'JetBrains Mono', monospace; font-size: 0.58rem; letter-spacing: 0.15em;
    text-transform: uppercase; color: var(--accent); }}
  .card-quiz p {{ font-size: 0.82rem; color: var(--muted); margin-top: 0.25rem; font-style: italic; }}

  footer {{ max-width: 1180px; margin: 0 auto; padding: 1.5rem 1.5rem 3rem;
    border-top: 1px solid var(--faint); font-family: 'JetBrains Mono', monospace;
    font-size: 0.66rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted); }}

  @media (max-width: 900px) {{
    .map-wrap {{ overflow-x: auto; -webkit-overflow-scrolling: touch; }}
    .map-grid {{ grid-template-columns: 72px repeat(5, minmax(140px, 1fr)); min-width: 820px; }}
    .card-grid {{ grid-template-columns: 1fr; }}
    .hero {{ padding: 2rem 1.25rem 1rem; }}
    .hero h1 {{ font-size: 2.1rem; }}
    .hero .subtitle {{ font-size: 0.9rem; line-height: 1.55; }}
    .how {{ padding: 0 1.25rem; }}
    .how-card {{ padding: 1.25rem; }}
    .how-row {{ flex-direction: column; gap: 0.25rem; padding: 0.7rem 0; }}
    .how-label {{ min-width: auto; }}
    .section-title {{ padding: 0 1.25rem; }}
    .legend {{ padding: 0 1.25rem; gap: 0.6rem; font-size: 0.62rem; }}
    .tracks {{ padding: 0 1.25rem 3rem; }}
    .track-head {{ flex-wrap: wrap; }}
    .track-count {{ margin-left: 0; font-size: 0.6rem; }}
  }}
</style>
</head>
<body>
<nav>
  <div class="nav-inner">
    <a href="index.html" class="logo">LearnAIR <span class="doc-badge">Workstation</span></a>
    <a href="index.html" class="back-link">&larr; Back to LearnAIR</a>
  </div>
</nav>

<header class="hero">
  <div class="kicker">Concept Map · {len(concepts)} concepts · 5 tracks · 6 tiers</div>
  <h1>Mike's <em>Workstation</em></h1>
  <p class="subtitle">
    The spaced-rep deck backing the Alpha week. Each chip is a concept in the <code>learning</code> MCP.
    Read the grid left-to-right through a track, top-to-bottom through tier. Click a chip to jump to
    its summary and the quiz prompt Claude will actually ask you.
  </p>
  <div class="stat-row">
    <span class="stat"><strong>T1</strong>{tier_counts[1]}</span>
    <span class="stat"><strong>T2</strong>{tier_counts[2]}</span>
    <span class="stat"><strong>T3</strong>{tier_counts[3]}</span>
    <span class="stat"><strong>T4</strong>{tier_counts[4]}</span>
    <span class="stat"><strong>T5</strong>{tier_counts[5]}</span>
    <span class="stat"><strong>T6</strong>{tier_counts[6]}</span>
  </div>
</header>

<section class="how">
  <div class="how-card">
    <h3>How to use this page</h3>
    <div class="how-row">
      <span class="how-label">Prep</span>
      <span class="how-desc">Scan the grid. Notice the tiers with the most density — those are the backbone weeks.</span>
    </div>
    <div class="how-row">
      <span class="how-label">Drill</span>
      <span class="how-desc">Click any chip to jump to its detail card with the summary and quiz prompt.</span>
    </div>
    <div class="how-row">
      <span class="how-label">Practice</span>
      <span class="how-desc">In Claude Desktop: <code>quiz me on cli</code> (or any track). Mark honestly with <code>mark that correct</code> or <code>mark that wrong</code>.</span>
    </div>
    <div class="how-row">
      <span class="how-label">Checkpoint</span>
      <span class="how-desc"><code>show my progress</code> at the end of each session. <code>share my progress</code> so Andrew can see.</span>
    </div>
  </div>
</section>

<div class="section-title">
  <h2>The map</h2>
  <p>Rows are tiers (difficulty). Columns are tracks. Cells are the concepts sitting at that intersection.</p>
</div>

<div class="legend">
  {track_legend}
</div>

<div class="map-wrap">
{render_grid(grid)}
</div>

<div class="section-title">
  <h2>Concepts by track</h2>
  <p>Every concept in the deck, grouped by track and ordered by tier. The quiz prompt is what the MCP actually asks you.</p>
</div>

<div class="tracks">
{''.join(track_sections)}
</div>

<footer>
  Generated from <a href="https://github.com/a-deal/mcp-mike/blob/main/concepts.json" style="color: var(--accent);">mcp-mike/concepts.json</a>. Regenerate with <code>python3 scripts/gen-workstation-html.py</code>.
</footer>
</body>
</html>
"""


def main() -> None:
    concepts = load_concepts()
    out = render_html(concepts)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(out)
    print(f"wrote {OUT} ({len(out):,} bytes, {len(concepts)} concepts)")


if __name__ == "__main__":
    main()
