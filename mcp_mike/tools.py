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
import subprocess
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

def _context_repo() -> Path:
    """Shared context repo. Override with LEARNAIR_CONTEXT env var."""
    return Path(os.environ.get("LEARNAIR_CONTEXT", os.path.expanduser("~/src/learnair-context")))


def hub(query: str) -> str:
    """Search hub docs and shared context for a keyword. Returns matching passages.

    Searches both the personal workspace hub and the shared learnair-context repo.

    Args:
        query: Search term (case-insensitive).
    """
    search_dirs: list[tuple[str, Path]] = []

    hub_dir = _workspace() / "hub"
    if hub_dir.exists():
        search_dirs.append(("hub", hub_dir))

    context_dir = _context_repo()
    if context_dir.exists():
        search_dirs.append(("context", context_dir))

    if not search_dirs:
        return "No hub or context directories found."

    query_lower = query.lower()
    results = []

    for source_name, search_dir in search_dirs:
        for md_file in sorted(search_dir.rglob("*.md")):
            lines = md_file.read_text().splitlines()
            for i, line in enumerate(lines):
                if query_lower in line.lower():
                    # Grab surrounding context (2 lines before, 2 after)
                    start = max(0, i - 2)
                    end = min(len(lines), i + 3)
                    snippet = "\n".join(lines[start:end])
                    rel_path = md_file.relative_to(search_dir)
                    results.append(f"**[{source_name}] {rel_path}** (line {i + 1}):\n{snippet}")

    if not results:
        return f"Nothing found for '{query}' in hub or shared context."

    # Cap at 8 results to keep output manageable
    output = results[:8]
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


# --- Tool: mochary ---

def mochary(situation: str) -> str:
    """Run a Mochary framework on a situation. Meeting prep, difficult conversations, accountability.

    Matt Mochary coached CEOs at Coinbase, Notion, Brex, Plaid, Figma.
    This tool returns the right framework for what Mike is facing.

    Args:
        situation: What you're dealing with. Examples: 'meeting prep with Justin',
                   'difficult conversation with Andrew', 'I have too many priorities',
                   'need to give feedback', 'running a 1:1'.
    """
    sit = situation.lower()

    # Match situation to framework
    if any(w in sit for w in ["meeting", "prep", "agenda", "call"]):
        return (
            "**Mochary: Meeting Prep**\n\n"
            "Before the meeting, answer these:\n\n"
            "1. **What's the one decision this meeting needs to make?** If there's no decision, it's an update and should be an email.\n"
            "2. **Issue/Proposed Solution:** Write down the issue AND your proposed solution before walking in. Never bring a problem without a solution.\n"
            "3. **DRI:** Who owns each action item that comes out of this? Every item gets exactly one owner.\n"
            "4. **Time box:** How long is this meeting? Agree on the end time before you start.\n"
            "5. **Close protocol:** Who closes? When they move to close, everyone supports. No reopening.\n\n"
            "**1:1 Structure (if applicable):**\n"
            "- Personal check-in (2 min)\n"
            "- Review open action items (3 min)\n"
            "- Their issues first, yours last (remaining time)\n"
            "- End with: what did we decide? Who owns what? By when?\n\n"
            "_\"Write first to force clarity. If you can't write it, you haven't thought it through.\"_"
        )

    if any(w in sit for w in ["difficult", "hard conversation", "conflict", "tension", "feedback"]):
        return (
            "**Mochary: Difficult Conversations**\n\n"
            "The framework that actually works:\n\n"
            "1. **State the behavior** (not the person): \"When X happened...\"\n"
            "2. **State the impact**: \"...the effect was Y.\"\n"
            "3. **Ask their perspective**: \"What's your view?\" Then shut up and listen.\n"
            "4. **Agree on next steps**: Specific, owned, time-bound.\n\n"
            "**Before you go in:**\n"
            "- Check your emotional state. Fear and anger give bad advice.\n"
            "- Notice it. Name it. Locate it in your body. Breathe. Then decide.\n"
            "- Are you trying to be right, or trying to solve the problem?\n\n"
            "**The HEARD framework:**\n"
            "Make them feel understood BEFORE solving. Reflect back what they said. "
            "\"What I'm hearing is...\" People can't hear solutions until they feel heard.\n\n"
            "**The 5 A's of Feedback:**\n"
            "Ask (permission) > Acknowledge (their view) > Accept (what's valid) > Act (change) > Attribute (credit them)\n\n"
            "_\"Trust = vulnerability + follow-through. Like = genuine curiosity about the other person.\"_"
        )

    if any(w in sit for w in ["priorit", "too many", "overwhelm", "focus", "scattered"]):
        return (
            "**Mochary: Top Goal + Energy Audit**\n\n"
            "**Top Goal:** You get ONE top goal per day. Not three. One.\n"
            "What is the one thing that, if you did it today, would make today a win?\n\n"
            "**Energy Audit:** List your recurring activities. For each, mark:\n"
            "- Energizing (you'd do it for free)\n"
            "- Draining (you procrastinate on it)\n"
            "- Neutral\n\n"
            "Delegate or eliminate the draining ones. Double down on the energizing ones. "
            "This isn't about productivity. It's about sustainability.\n\n"
            "**First 2 Minutes:** When you commit to something, take the first action within 2 minutes. "
            "Book the meeting. Send the text. Open the doc. Breaking inertia is 80% of the work.\n\n"
            "**I Intend To:** Stop asking permission. Say \"I intend to do X\" instead of \"Can I do X?\" "
            "This shifts you from waiting to leading.\n\n"
            "_\"Separate the decision from the implementation. First decide, then plan.\"_"
        )

    if any(w in sit for w in ["accountab", "follow", "commit", "track"]):
        return (
            "**Mochary: Accountability**\n\n"
            "**DRIs:** Every action item has exactly ONE owner. Not \"we'll figure it out.\" One name.\n\n"
            "**Accountability Partner:** Daily check-in on your top goal. "
            "Text format: \"Yesterday's goal: [X]. Did I do it: [yes/no]. Today's goal: [Y].\"\n\n"
            "**On Time:** Being on time is the simplest trust signal. "
            "If you say 9:00, you're there at 8:55. This isn't about punctuality. It's about \"does this person do what they say?\"\n\n"
            "**Clean Escalate:** When there's a disagreement, both sides present together to the decision-maker. "
            "No back-channel politics. No triangulation.\n\n"
            "_\"Follow-through is the compound interest of trust.\"_"
        )

    # Default: overview of available frameworks
    return (
        "**Mochary: Available Frameworks**\n\n"
        "Tell me more about your situation. I can help with:\n\n"
        "- **Meeting prep** — Issue/Proposed Solution, DRIs, close protocol\n"
        "- **Difficult conversations** — behavior/impact framework, HEARD, feedback\n"
        "- **Priorities** — Top Goal, Energy Audit, First 2 Minutes\n"
        "- **Accountability** — DRIs, daily check-in, clean escalation\n\n"
        "Say something like: \"mochary: I need to prep for my call with Justin\" "
        "or \"mochary: I have too many things on my plate.\"\n\n"
        "_Matt Mochary coached CEOs at Coinbase, Notion, Brex, Plaid, Figma. "
        "His core insight: most leadership problems are process problems, not people problems._"
    )


# --- Tool: duke ---

def duke(decision: str) -> str:
    """Run a Duke decision-quality check. Calibrate confidence, pre-mortem, proposals not declarations.

    Annie Duke's frameworks for making better decisions under uncertainty.

    Args:
        decision: The decision or message you're evaluating. Examples: 'should we commit to the 90-day pilot',
                  'review this message to Justin before I send it', 'I think we should drop the Texas angle'.
    """
    dec = decision.lower()

    if any(w in dec for w in ["review", "message", "send", "email", "draft", "write"]):
        return (
            "**Duke: Message Review**\n\n"
            "Before you send, check:\n\n"
            "1. **Proposals not declarations.** \"I think we should X\" becomes \"What if we tried X? Here's my reasoning...\"\n"
            "   - Declarations close doors. Proposals open them.\n"
            "   - Use questions, not statements. \"And\" not \"but.\"\n\n"
            "2. **Recipient space.** Read it from their perspective.\n"
            "   - What will they feel when they read the first sentence?\n"
            "   - Does this make them defensive or curious?\n"
            "   - Is this about you being right, or about solving the problem together?\n\n"
            "3. **Calibrated confidence.** Replace absolutes with percentages.\n"
            "   - \"This will work\" becomes \"I'm 70% confident because X. The 30% risk is Y.\"\n"
            "   - \"We need to\" becomes \"I'd recommend, because...\"\n\n"
            "4. **The $100 bet.** Would you bet $100 this message improves the relationship? "
            "If not, what would you change?\n\n"
            "_\"Wanna bet? is the most useful phrase in the English language.\"_"
        )

    if any(w in dec for w in ["should", "commit", "decide", "choice", "option"]):
        return (
            "**Duke: Decision Audit**\n\n"
            "Walk through this:\n\n"
            "1. **State the decision clearly.** One sentence. No hedging.\n\n"
            "2. **List outcomes with probabilities.**\n"
            "   - Best case (what % likely?): ___\n"
            "   - Base case (what % likely?): ___\n"
            "   - Worst case (what % likely?): ___\n\n"
            "3. **What information do we have?** What's signal vs. noise?\n\n"
            "4. **What would change our mind?** Name a specific fact that would flip the decision.\n\n"
            "5. **Is this reversible?** One-way door or two-way door?\n"
            "   - Two-way: decide fast, adjust later.\n"
            "   - One-way: slow down, get more info.\n\n"
            "6. **Pre-mortem:** It's 90 days from now and this failed. Why did it fail?\n\n"
            "7. **Backcasting:** It's 90 days from now and this succeeded. What were the 3 steps that mattered?\n\n"
            "8. **State the bet:** \"I'm ___% confident that ___ because ___.\"\n\n"
            "_\"The quality of our lives is the sum of decision quality plus luck. We can only control one of those.\"_"
        )

    if any(w in dec for w in ["think", "believe", "sure", "confident", "right", "wrong"]):
        return (
            "**Duke: Calibration Check**\n\n"
            "You stated a belief. Let's test it:\n\n"
            "1. **How sure are you?** Put a number on it. Not \"pretty sure.\" A percentage.\n\n"
            "2. **What's the evidence?** List 3 data points supporting your belief.\n\n"
            "3. **What's the counter-evidence?** List 2 data points that could prove you wrong.\n\n"
            "4. **Resulting check:** Are you judging this belief by the quality of your reasoning, "
            "or by a recent outcome? Good decisions can have bad outcomes. Bad decisions can have good outcomes. "
            "Don't confuse them.\n\n"
            "5. **The bet frame:** Would you bet $100 on this? $1000? Where does your confidence drop?\n\n"
            "_\"Beliefs are works in progress, not finished products. I'm not sure is the beginning of wisdom.\"_"
        )

    # Default
    return (
        "**Duke: Decision Quality**\n\n"
        "Tell me more. I can help with:\n\n"
        "- **Decision audit** — pre-mortem, backcasting, probability mapping\n"
        "- **Message review** — proposals not declarations, recipient space, calibrated confidence\n"
        "- **Calibration check** — testing your beliefs, bet framing, resulting\n\n"
        "Say something like: \"duke: should we commit to the 90-day pilot?\" "
        "or \"duke: review this message before I send it to Teresa.\"\n\n"
        "_Annie Duke's core insight: separate decision quality from outcome quality. "
        "You can make a great decision and get a bad result. That doesn't make it a bad decision._"
    )


# --- Tool: komoroske ---

def komoroske(question: str) -> str:
    """Run a K (Komoroske) systems-thinking check. Convergence, sequencing, synthesis.

    Alex Komoroske's frameworks for channeling ideas into execution.

    Args:
        question: What you're thinking about. Examples: 'I have 8 ideas and don't know which to do first',
                  'am I converging or diverging', 'is this a real priority or a shiny object'.
    """
    q = question.lower()

    if any(w in q for w in ["priorit", "idea", "which", "first", "sequence", "too many", "scattered"]):
        return (
            "**K: Morning Sequence**\n\n"
            "Brain dump everything. Then answer:\n\n"
            "1. **Which of these are real priorities and which are shiny objects?**\n"
            "   - Real priority: moves the main thing forward. You committed to it.\n"
            "   - Shiny object: feels urgent, is actually avoidance of the hard thing.\n\n"
            "2. **What's the one thing that makes everything else easier?**\n"
            "   Do that first. Not the most urgent. The most leveraged.\n\n"
            "3. **Name your top 3 for the day.** Not 5. Not 8. Three.\n"
            "   Everything else gets parked. Parked doesn't mean abandoned. It means sequenced.\n\n"
            "4. **80/20 split:** 80% execution, 20% synthesis.\n"
            "   The synthesis pass is important but never urgent. Do it anyway.\n\n"
            "_\"Pre-PMF needs convergence, otherwise the entire enterprise diffuses to nothing.\"_"
        )

    if any(w in q for w in ["converg", "diverg", "focus", "diffus", "spread"]):
        return (
            "**K: Convergence Check**\n\n"
            "Ask yourself:\n\n"
            "1. **Is this converging or diverging on its own?**\n"
            "   - Converging: gets tighter with time. Each step narrows options. Good.\n"
            "   - Diverging: gets wider with time. Each step opens new questions. Dangerous pre-PMF.\n\n"
            "2. **Are you optimizing a leaf node?**\n"
            "   If you're polishing something that sits on a branch that might get cut, stop.\n"
            "   Zoom out. Is the branch itself the right one?\n\n"
            "3. **Grubby truffle or gilded turd?**\n"
            "   - Grubby truffle: rough on the surface but compounds underneath. Ship it.\n"
            "   - Gilded turd: looks polished but hollow inside. No amount of polish fixes hollow.\n\n"
            "4. **Pace layers:** Different parts move at different speeds.\n"
            "   Strategy moves slow. Execution moves fast. Don't optimize fast things at the expense of slow things.\n\n"
            "_\"If you go too fast you create hollowness, not resonance.\"_"
        )

    if any(w in q for w in ["learn", "synthes", "reflect", "what did", "evening", "review"]):
        return (
            "**K: Evening Synthesis**\n\n"
            "Five questions, one minute each:\n\n"
            "1. **What stood out today?** (Max 3 positive signals, max 3 negative signals)\n\n"
            "2. **What did I learn?** One thing I know now that I didn't know this morning.\n\n"
            "3. **What compounds?** Something I shipped today that keeps producing value untouched.\n\n"
            "4. **Converging or diverging?** One sentence gut check. Am I getting tighter or wider?\n\n"
            "5. **Tomorrow's top 3.** Not the full list. Just the three that make tomorrow a win.\n\n"
            "_\"The synthesis pass is important but never urgent. Do it anyway. "
            "Every unsolved problem becomes a tool. Convert operating expense to capital expense.\"_"
        )

    if any(w in q for w in ["build", "ship", "product", "start", "launch"]):
        return (
            "**K: Build Check**\n\n"
            "Before you build, answer:\n\n"
            "1. **Get to a toehold product as quickly as possible.**\n"
            "   Not the full vision. The smallest thing that proves the core bet.\n\n"
            "2. **Start from something people love and figure out how to get it to work.**\n"
            "   Not \"build it right, then find users.\" Find the love first.\n\n"
            "3. **Gardener, not builder.**\n"
            "   Create conditions for good things to grow. Don't try to construct exact outcomes.\n\n"
            "4. **Every time an agent can't figure it out on its own, ask: what tool would have helped?**\n"
            "   That's compounding engineering. Convert problems into tools.\n\n"
            "5. **Don't use Claude to think for you. Use it to do cognitive labor for you.**\n"
            "   The friction is the learning process. If you reduce all friction, you reduce all learning.\n\n"
            "_\"What is the highest and best use of burning this marginal token?\"_"
        )

    # Default
    return (
        "**K: Systems Thinking**\n\n"
        "Tell me more. I can help with:\n\n"
        "- **Sequencing** — which of your 8 ideas to do first\n"
        "- **Convergence check** — are you getting tighter or wider?\n"
        "- **Evening synthesis** — extract learning from the day\n"
        "- **Build check** — toehold product, gardener not builder\n\n"
        "Say something like: \"k: I have too many things going on\" "
        "or \"k: am I converging or diverging on LearnAIR?\"\n\n"
        "_Alex Komoroske's core insight: default convergence vs. default divergence. "
        "Some things get tighter on their own. Others spread until there's nothing left. "
        "Know which one you're in._"
    )


# --- Tool: discover ---

def _search_dirs() -> list[Path]:
    """Directories to scan for discover. Broad by default, covers the whole user space."""
    home = Path.home()
    dirs = [
        # Standard user directories
        home / "Desktop",
        home / "Documents",
        home / "Downloads",
        # Google Drive (multiple possible mount points)
        home / "Google Drive",
        home / "Google Drive - My Drive",
        home / "Library" / "CloudStorage" / "GoogleDrive",
        # Common Google Drive Backup & Sync / Drive for Desktop paths
        Path("/Volumes/GoogleDrive"),
        Path("/Volumes/GoogleDrive/My Drive"),
        # iCloud
        home / "Library" / "Mobile Documents" / "com~apple~CloudDocs",
        # Dropbox
        home / "Dropbox",
        # OneDrive
        home / "OneDrive",
        # Projects / source
        home / "src",
        home / "Projects",
        home / "Work",
    ]
    # Also scan any CloudStorage mounts (Google Drive for Desktop shows up here)
    cloud_storage = home / "Library" / "CloudStorage"
    if cloud_storage.exists():
        for child in cloud_storage.iterdir():
            if child.is_dir() and child not in dirs:
                dirs.append(child)

    # Custom paths via env var
    extra = os.environ.get("MIKE_SEARCH_DIRS", "")
    if extra:
        dirs.extend(Path(p.strip()) for p in extra.split(":") if p.strip())

    return [d for d in dirs if d.exists()]


# Directories and extensions to skip during file scanning
_SKIP_DIRS = {
    ".git", ".venv", "node_modules", "__pycache__", ".pytest_cache",
    ".Trash", "Library", "Applications", ".cache", ".npm", ".nvm",
    "venv", "env", ".tox", "build", "dist", ".eggs",
}
_SKIP_EXTENSIONS = {
    ".app", ".dmg", ".pkg", ".zip", ".gz", ".tar", ".bz2", ".xz",
    ".iso", ".img", ".o", ".pyc", ".pyo", ".so", ".dylib", ".exe",
    ".class", ".jar", ".war", ".whl", ".egg",
    ".mp3", ".mp4", ".mov", ".avi", ".mkv", ".wav", ".flac",
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico", ".svg", ".webp",
    ".ttf", ".otf", ".woff", ".woff2", ".eot",
    ".sqlite", ".db", ".sqlite3",
}
_TEXT_EXTENSIONS = {
    ".md", ".txt", ".csv", ".json", ".html", ".htm", ".rtf",
    ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
    ".xml", ".log", ".tex", ".rst", ".org",
    ".py", ".js", ".ts", ".sh", ".bash", ".zsh",
    ".doc", ".docx",  # filename match only, can't read content
    ".pdf",           # filename match only
    ".pptx", ".ppt",  # filename match only
    ".xlsx", ".xls",  # filename match only
}
_CONTENT_READABLE = {
    ".md", ".txt", ".csv", ".json", ".html", ".htm", ".rtf",
    ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
    ".xml", ".log", ".tex", ".rst", ".org",
    ".py", ".js", ".ts", ".sh", ".bash", ".zsh",
}


def discover(query: str, source: str = "") -> str:
    """Find files and Apple Notes matching a keyword across your entire machine.

    Scans Desktop, Documents, Downloads, Google Drive, iCloud, Dropbox,
    OneDrive, src/, and Apple Notes. Finds by filename and text content.

    Args:
        query: What to search for (e.g. 'Teresa', 'workshop handout', 'LearnAIR').
        source: Optional. 'files' for local files only, 'notes' for Apple Notes only.
                Empty searches both.
    """
    query_lower = query.lower()
    source_lower = source.lower().strip()
    results = []
    dirs_searched = []

    # --- Search local files ---
    if source_lower in ("", "files"):
        seen_paths: set[str] = set()
        search_dirs = _search_dirs()
        dirs_searched = [str(d) for d in search_dirs]

        for search_dir in search_dirs:
            try:
                for fpath in search_dir.rglob("*"):
                    if not fpath.is_file():
                        continue
                    if str(fpath) in seen_paths:
                        continue
                    # Skip hidden files and noisy directories
                    parts = fpath.relative_to(search_dir).parts
                    if any(part.startswith(".") or part in _SKIP_DIRS for part in parts):
                        continue
                    if fpath.suffix.lower() in _SKIP_EXTENSIONS:
                        continue

                    # Check filename match
                    name_match = query_lower in fpath.name.lower()
                    # Also check parent folder names for context
                    path_match = not name_match and query_lower in str(fpath).lower()

                    # Check content match for readable text files
                    content_match = False
                    if fpath.suffix.lower() in _CONTENT_READABLE:
                        try:
                            text = fpath.read_text(errors="ignore")[:8000]
                            if query_lower in text.lower():
                                content_match = True
                        except (OSError, UnicodeDecodeError):
                            pass

                    if name_match or path_match or content_match:
                        seen_paths.add(str(fpath))
                        try:
                            stat = fpath.stat()
                            size = stat.st_size
                            size_str = f"{size // 1024}KB" if size >= 1024 else f"{size}B"
                            modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d")
                        except OSError:
                            size_str = "?"
                            modified = "?"

                        if name_match and content_match:
                            match_type = "name+content"
                        elif name_match:
                            match_type = "name"
                        elif content_match:
                            match_type = "content"
                        else:
                            match_type = "path"

                        results.append(f"**{fpath}** ({size_str}, {modified}, {match_type})")

                        if len(results) >= 30:
                            break
            except (PermissionError, OSError):
                continue
            if len(results) >= 30:
                break

    # --- Search Apple Notes ---
    if source_lower in ("", "notes"):
        try:
            script = f'''
            tell application "Notes"
                set matchingNotes to {{}}
                repeat with aNote in every note
                    if name of aNote contains "{query}" then
                        set end of matchingNotes to (name of aNote) & " | " & (modification date of aNote as string)
                    end if
                    if (count of matchingNotes) >= 10 then exit repeat
                end repeat
                set output to ""
                repeat with n in matchingNotes
                    set output to output & n & linefeed
                end repeat
                return output
            end tell
            '''
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0 and result.stdout.strip():
                for line in result.stdout.strip().splitlines():
                    if line.strip():
                        results.append(f"**[Apple Note]** {line.strip()}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    if not results:
        searched = ", ".join(dirs_searched[:5])
        if len(dirs_searched) > 5:
            searched += f" (+{len(dirs_searched) - 5} more)"
        return f"Nothing found for '{query}'. Searched: {searched} + Apple Notes."

    header = f"Found {len(results)} result(s) for '{query}':\n\n"
    return header + "\n".join(results) + "\n\n_To pull something into your workspace, use: ingest('[path or note title]', '[project]')_"


# --- Tool: ingest ---

def ingest(source: str, project: str = "") -> str:
    """Pull a file or Apple Note into your workspace, organized by project.

    Args:
        source: File path or Apple Note title. For Apple Notes, prefix with 'note:' (e.g. 'note:Teresa Follow-up').
        project: Project folder to save into (e.g. 'learnair', 'workshops', 'reference').
                 If empty, saves to 'reference'.
    """
    project_name = project.lower().strip() or "reference"
    project_dir = _workspace() / project_name
    project_dir.mkdir(parents=True, exist_ok=True)

    # --- Apple Note ---
    if source.lower().startswith("note:"):
        note_title = source[5:].strip()
        try:
            script = f'''
            tell application "Notes"
                set matchingNotes to every note whose name contains "{note_title}"
                if (count of matchingNotes) > 0 then
                    set theNote to item 1 of matchingNotes
                    return (name of theNote) & "\\n---\\n" & (plaintext of theNote)
                else
                    return "NOT_FOUND"
                end if
            end tell
            '''
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0 or "NOT_FOUND" in result.stdout:
                return f"Apple Note '{note_title}' not found. Try discover('{note_title}', 'notes') to search."

            content = result.stdout.strip()
            # Clean filename from note title
            safe_name = "".join(c if c.isalnum() or c in " -_" else "" for c in note_title).strip()
            safe_name = safe_name.replace(" ", "-").lower()[:60]
            dest = project_dir / f"{safe_name}.md"

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            header = f"---\nsource: Apple Note\ntitle: {note_title}\ningested: {timestamp}\n---\n\n"
            dest.write_text(header + content)
            return f"Ingested Apple Note '{note_title}' to {project_name}/{dest.name}"

        except (subprocess.TimeoutExpired, FileNotFoundError):
            return "Could not access Apple Notes. Make sure Notes app is available."

    # --- Local file ---
    source_path = Path(os.path.expanduser(source))
    if not source_path.exists():
        return f"File not found: {source}. Use discover() to find files first."

    if not source_path.is_file():
        return f"{source} is a directory, not a file. Point to a specific file."

    # Read and copy
    try:
        if source_path.suffix.lower() in (".md", ".txt", ".csv", ".json", ".html", ".rtf"):
            content = source_path.read_text(errors="ignore")
            dest = project_dir / source_path.name
            if dest.suffix != ".md":
                dest = dest.with_suffix(dest.suffix + ".md")

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            header = f"---\nsource: {source_path}\ningested: {timestamp}\n---\n\n"
            dest.write_text(header + content)
            return f"Ingested {source_path.name} to {project_name}/{dest.name}"
        elif source_path.suffix.lower() == ".pdf":
            # Copy PDF as-is
            dest = project_dir / source_path.name
            import shutil
            shutil.copy2(source_path, dest)
            return f"Copied {source_path.name} to {project_name}/{dest.name} (PDF, not searchable by hub)"
        else:
            dest = project_dir / source_path.name
            import shutil
            shutil.copy2(source_path, dest)
            return f"Copied {source_path.name} to {project_name}/{dest.name}"
    except (OSError, PermissionError) as e:
        return f"Error reading {source}: {e}"


# --- Tool: checkpoint ---

def checkpoint() -> str:
    """Share your learning progress with Andrew via the shared context repo.

    Exports your quiz progress, recent notes, and a summary to
    learnair-context/checkpoints/ so Andrew can see where you are
    and adjust the curriculum.
    """
    context_dir = _context_repo()
    if not context_dir.exists():
        return "Shared context repo not found at ~/src/learnair-context. Clone it first."

    checkpoint_dir = context_dir / "checkpoints"
    checkpoint_dir.mkdir(exist_ok=True)

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")

    # --- Gather progress ---
    prog = _get_progress()
    tracks: dict[str, list[dict]] = {"claude": [], "learnair": [], "internet": [], "capstone": []}
    for c in CONCEPTS:
        t = c.get("track", "claude")
        if t not in tracks:
            tracks[t] = []
        tracks[t].append(c)

    lines = [f"# Checkpoint: {date_str} {time_str}\n"]

    for tname, concepts in tracks.items():
        total = len(concepts)
        started = sum(1 for c in concepts if c["id"] in prog)
        mastered = sum(
            1 for c in concepts
            if c["id"] in prog and prog[c["id"]].get("interval_days", 1) >= 8
        )
        lines.append(f"## {tname.upper()} — {started}/{total} started, {mastered}/{total} mastered")

        # Show per-concept status
        for c in concepts:
            cid = c["id"]
            if cid in prog:
                p = prog[cid]
                correct = p.get("times_correct", 0)
                wrong = p.get("times_wrong", 0)
                interval = p.get("interval_days", 1)
                status = "mastered" if interval >= 8 else "learning"
                lines.append(f"- [{status}] **{c['name']}** ({correct} correct, {wrong} wrong, {interval}d interval)")
            else:
                lines.append(f"- [ ] {c['name']}")
        lines.append("")

    # --- Gather recent notes ---
    notes_file = _workspace() / "learning" / "notes.md"
    if notes_file.exists():
        notes_text = notes_file.read_text()
        # Get last 10 lines of notes
        recent = notes_text.strip().splitlines()[-10:]
        if recent:
            lines.append("## Recent Learning Notes")
            lines.extend(recent)
            lines.append("")

    # --- Stuck concepts (wrong > correct) ---
    stuck = []
    for c in CONCEPTS:
        cid = c["id"]
        if cid in prog:
            p = prog[cid]
            if p.get("times_wrong", 0) > p.get("times_correct", 0):
                stuck.append(c["name"])
    if stuck:
        lines.append("## Stuck On")
        for s in stuck:
            lines.append(f"- {s}")
        lines.append("")

    # Write checkpoint
    checkpoint_file = checkpoint_dir / f"{date_str}.md"
    checkpoint_file.write_text("\n".join(lines))

    # Auto-commit and push if possible
    try:
        subprocess.run(
            ["git", "add", "checkpoints/"],
            cwd=str(context_dir), capture_output=True, timeout=5
        )
        subprocess.run(
            ["git", "commit", "-m", f"checkpoint: {date_str} {time_str}"],
            cwd=str(context_dir), capture_output=True, timeout=5
        )
        push_result = subprocess.run(
            ["git", "push"],
            cwd=str(context_dir), capture_output=True, text=True, timeout=10
        )
        if push_result.returncode == 0:
            return f"Checkpoint saved and shared. Andrew can see your progress by pulling learnair-context."
        else:
            return f"Checkpoint saved to learnair-context/checkpoints/{date_str}.md but couldn't push. Run 'cd ~/src/learnair-context && git push' when you have internet."
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return f"Checkpoint saved to learnair-context/checkpoints/{date_str}.md. Push it when ready: cd ~/src/learnair-context && git push"


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
