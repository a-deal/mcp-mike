"""Core tool implementations for Mike's MCP server.

Five tools:
  load_persona  - load a persona from workspace/personas/
  hub           - search hub docs by keyword
  quiz_me       - spaced repetition quiz on Claude concepts
  mark_concept  - record quiz result, adjust interval
  whats_next    - find TODOs across all projects
  save_note     - append a timestamped note to a project
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# --- Paths ---

def _workspace() -> Path:
    """Workspace root. Override with MIKE_WORKSPACE env var."""
    return Path(os.environ.get("MIKE_WORKSPACE", os.path.expanduser("~/Documents/claude-workspace")))


def _concepts_path() -> Path:
    """Path to the concepts JSON file."""
    return Path(__file__).parent.parent / "concepts.json"


def _progress_path() -> Path:
    return _workspace() / ".progress.json"


# --- Concepts ---

def _load_concepts() -> list[dict]:
    path = _concepts_path()
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


CONCEPTS = _load_concepts()


def _get_progress(workspace: Path | None = None) -> dict:
    path = (workspace or _workspace()) / ".progress.json"
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _save_progress(progress: dict, workspace: Path | None = None):
    path = (workspace or _workspace()) / ".progress.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(progress, f, indent=2, default=str)


# --- Tool: load_persona ---

def load_persona(name: str) -> str:
    """Load a persona by name from workspace/personas/.

    Args:
        name: Persona name (e.g. 'nexus', 'mens-work'). Case-insensitive.
    """
    personas_dir = _workspace() / "personas"
    if not personas_dir.exists():
        return f"Personas directory not found at {personas_dir}. Create it and add .md files."

    # Case-insensitive match
    target = name.lower().strip()
    available = []
    for f in sorted(personas_dir.glob("*.md")):
        available.append(f.stem)
        if f.stem.lower() == target:
            return f.read_text()

    available_str = ", ".join(available) if available else "(none)"
    return f"Persona '{name}' not found. Available personas: {available_str}"


# --- Tool: hub ---

def hub(query: str) -> str:
    """Search hub docs for a keyword. Returns matching passages.

    Args:
        query: Search term (case-insensitive).
    """
    hub_dir = _workspace() / "hub"
    if not hub_dir.exists():
        return f"Hub directory not found at {hub_dir}."

    query_lower = query.lower()
    results = []

    for md_file in sorted(hub_dir.rglob("*.md")):
        lines = md_file.read_text().splitlines()
        for i, line in enumerate(lines):
            if query_lower in line.lower():
                # Grab surrounding context (2 lines before, 2 after)
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                snippet = "\n".join(lines[start:end])
                rel_path = md_file.relative_to(hub_dir)
                results.append(f"**{rel_path}** (line {i + 1}):\n{snippet}")

    if not results:
        return f"Nothing found for '{query}' in hub docs."

    # Cap at 5 results to keep output manageable
    output = results[:5]
    header = f"Found {len(results)} match(es) for '{query}':\n\n"
    return header + "\n\n---\n\n".join(output)


# --- Tool: quiz_me ---

def quiz_me(track: str = "") -> str:
    """Pick the next concept due for review and ask the quiz question.

    Uses spaced repetition: concepts due for review come first,
    then new concepts in tier order.

    Args:
        track: Optional filter. 'claude' for Claude usage, 'learnair' for
               domain knowledge, 'internet' for technical foundations.
               Empty string returns concepts from all tracks.
    """
    progress = _get_progress()
    now = datetime.now()

    # Filter concepts by track
    track_lower = track.lower().strip()
    if track_lower == "claude":
        pool = [c for c in CONCEPTS if "track" not in c]
    elif track_lower:
        pool = [c for c in CONCEPTS if c.get("track") == track_lower]
    else:
        pool = CONCEPTS

    if not pool:
        return f"No concepts found for track '{track}'. Available tracks: claude, learnair, internet (or leave empty for all)."

    track_label = f" [{track_lower}]" if track_lower else ""

    # Find concepts due for review (past their next_review date)
    due = []
    for concept in pool:
        cid = concept["id"]
        if cid in progress:
            next_review = datetime.fromisoformat(progress[cid]["next_review"])
            if now >= next_review:
                due.append((next_review, concept))

    # Sort by most overdue first
    due.sort(key=lambda x: x[0])

    if due:
        concept = due[0][1]
        times_reviewed = progress[concept["id"]]["times_correct"]
        confused = ""
        if "confused" in concept:
            confused = f"\n\n_If this is fuzzy, say 'I'm confused' and I'll explain it differently._"
        return (
            f"**Review{track_label}: {concept['name']}** (Tier {concept['tier']}, reviewed {times_reviewed}x)\n\n"
            f"{concept['quiz']}\n\n"
            f"_When you're ready, use `mark_concept('{concept['id']}', 'correct')` or "
            f"`mark_concept('{concept['id']}', 'wrong')` to record your answer._"
            f"{confused}"
        )

    # No reviews due, introduce a new concept
    learned_ids = set(progress.keys())
    for concept in pool:
        if concept["id"] not in learned_ids:
            confused = ""
            if "confused" in concept:
                confused = f"\n\n**Still confused?** {concept['confused']}"
            return (
                f"**New concept{track_label}: {concept['name']}** (Tier {concept['tier']})\n\n"
                f"{concept['summary']}\n\n"
                f"**Practice:** {concept['practice']}\n\n"
                f"**Quiz:** {concept['quiz']}\n\n"
                f"_When you're ready, use `mark_concept('{concept['id']}', 'correct')` or "
                f"`mark_concept('{concept['id']}', 'wrong')` to record your answer._"
                f"{confused}"
            )

    total = len(pool)
    return f"You've reviewed all {total} concepts{track_label}. Keep practicing the ones that come up for review."


# --- Tool: mark_concept ---

def mark_concept(concept_id: str, result: str) -> str:
    """Record a quiz result and adjust the review interval.

    Args:
        concept_id: The concept ID (e.g. 'context-window').
        result: 'correct' or 'wrong'.
    """
    # Validate concept exists
    concept = None
    for c in CONCEPTS:
        if c["id"] == concept_id:
            concept = c
            break
    if not concept:
        valid_ids = [c["id"] for c in CONCEPTS[:5]]
        return f"Concept '{concept_id}' not found. Examples: {', '.join(valid_ids)}"

    progress = _get_progress()
    now = datetime.now()

    if concept_id not in progress:
        progress[concept_id] = {
            "times_correct": 0,
            "times_wrong": 0,
            "interval_days": 1,
            "next_review": now.isoformat(),
            "first_seen": now.isoformat(),
        }

    entry = progress[concept_id]

    if result.lower().startswith("c"):
        entry["times_correct"] = entry.get("times_correct", 0) + 1
        # Double the interval on correct (1 -> 2 -> 4 -> 8 -> 16 -> 30 max)
        entry["interval_days"] = min(entry["interval_days"] * 2, 30)
        entry["next_review"] = (now + timedelta(days=entry["interval_days"])).isoformat()
        _save_progress(progress)
        return (
            f"Got it. '{concept['name']}' marked correct. "
            f"Next review in {entry['interval_days']} day(s). "
            f"({entry['times_correct']} correct, {entry['times_wrong']} wrong total)"
        )
    else:
        entry["times_wrong"] = entry.get("times_wrong", 0) + 1
        # Reset interval to 1 day on wrong
        entry["interval_days"] = 1
        entry["next_review"] = (now + timedelta(days=1)).isoformat()
        _save_progress(progress)
        confused = ""
        if "confused" in concept:
            confused = f"\n\n**Think of it this way:** {concept['confused']}"
        return (
            f"No worries. Let's review '{concept['name']}'.\n\n"
            f"**Summary:** {concept['summary']}\n\n"
            f"**Practice:** {concept['practice']}"
            f"{confused}\n\n"
            f"Next review tomorrow."
        )


# --- Tool: progress ---

def progress(track: str = "") -> str:
    """Show learning progress across all tracks or a specific track.

    Args:
        track: Optional filter. 'claude', 'learnair', 'internet', or empty for all.
    """
    prog = _get_progress()
    track_lower = track.lower().strip()

    # Group concepts by track
    tracks: dict[str, list[dict]] = {"claude": [], "learnair": [], "internet": [], "capstone": []}
    for c in CONCEPTS:
        t = c.get("track", "claude")
        if t not in tracks:
            tracks[t] = []
        tracks[t].append(c)

    if track_lower and track_lower not in tracks:
        return f"Unknown track '{track}'. Available: claude, learnair, internet."

    target_tracks = {track_lower: tracks[track_lower]} if track_lower else tracks
    lines = []

    for tname, concepts in target_tracks.items():
        total = len(concepts)
        started = sum(1 for c in concepts if c["id"] in prog)
        mastered = sum(
            1 for c in concepts
            if c["id"] in prog and prog[c["id"]].get("interval_days", 1) >= 8
        )
        lines.append(
            f"**{tname.upper()}** — {started}/{total} started, {mastered}/{total} mastered (8+ day interval)"
        )

    return "**Learning Progress**\n\n" + "\n".join(lines)


# --- Tool: whats_next ---

def whats_next() -> str:
    """Scan all projects for TODOs and action items.

    Looks for lines containing TODO, action item markers, or
    checkbox patterns in notes.md files across the workspace.
    """
    ws = _workspace()
    markers = ["todo", "- [ ]", "action:", "next step"]
    results = []

    for project_dir in sorted(ws.iterdir()):
        if not project_dir.is_dir() or project_dir.name.startswith("."):
            continue

        notes_file = project_dir / "notes.md"
        if not notes_file.exists():
            continue

        lines = notes_file.read_text().splitlines()
        todos = []
        for line in lines:
            line_lower = line.lower().strip()
            if any(m in line_lower for m in markers):
                todos.append(line.strip())

        if todos:
            results.append(f"**{project_dir.name}:**\n" + "\n".join(f"  {t}" for t in todos))

    if not results:
        return "No TODOs found across your projects. Either you're caught up or your notes need TODO markers."

    return "**Action items across projects:**\n\n" + "\n\n".join(results)


# --- Tool: save_note ---

def save_note(project: str, content: str) -> str:
    """Append a timestamped note to a project's notes file.

    Args:
        project: Project folder name (e.g. 'learnair').
        content: The note to save.
    """
    project_dir = _workspace() / project.lower().strip()
    project_dir.mkdir(parents=True, exist_ok=True)

    notes_file = project_dir / "notes.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    entry = f"\n- [{timestamp}] {content}\n"

    if notes_file.exists():
        with open(notes_file, "a") as f:
            f.write(entry)
    else:
        with open(notes_file, "w") as f:
            f.write(f"# {project} Notes\n{entry}")

    return f"Saved to {project}/notes.md."
