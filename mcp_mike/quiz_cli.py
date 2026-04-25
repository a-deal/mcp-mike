"""Interactive CLI quiz runner for Mike's spaced-repetition learning system.

Usage:
    quiz-cli            # quiz on CLI track (default)
    quiz-cli claude     # quiz on Claude Desktop usage
    quiz-cli learnair   # quiz on LearnAIR domain
    quiz-cli internet   # quiz on technical foundations
    quiz-cli all        # mix all tracks
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta

from mcp_mike.tools import CONCEPTS, _get_progress, _save_progress

# ── terminal colours ──────────────────────────────────────────────────────────

_USE_COLOUR = sys.stdout.isatty()


def _c(code: str, text: str) -> str:
    if not _USE_COLOUR:
        return text
    return f"\033[{code}m{text}\033[0m"


def bold(t: str) -> str:   return _c("1", t)
def dim(t: str) -> str:    return _c("2", t)
def cyan(t: str) -> str:   return _c("36", t)
def green(t: str) -> str:  return _c("32", t)
def yellow(t: str) -> str: return _c("33", t)
def red(t: str) -> str:    return _c("31", t)


# ── display helpers ───────────────────────────────────────────────────────────

_W = 60


def _rule(char: str = "─") -> str:
    return dim(char * _W)


def _wrap(text: str, indent: int = 2) -> str:
    """Word-wrap text to _W columns with a leading indent."""
    words = text.split()
    lines: list[str] = []
    line: list[str] = []
    width = _W - indent
    current = 0
    for word in words:
        if current + len(word) + (1 if line else 0) > width:
            lines.append(" " * indent + " ".join(line))
            line = [word]
            current = len(word)
        else:
            if line:
                current += 1
            line.append(word)
            current += len(word)
    if line:
        lines.append(" " * indent + " ".join(line))
    return "\n".join(lines)


def _print_concept(concept: dict, progress: dict, is_review: bool) -> None:
    cid = concept["id"]
    track = concept.get("track", "claude")
    tier = concept["tier"]
    name = concept["name"]

    print()
    print(_rule())

    if is_review:
        times = progress.get(cid, {}).get("times_correct", 0)
        label = f"  REVIEW [{track}] · Tier {tier} · reviewed {times}×"
    else:
        label = f"  NEW [{track}] · Tier {tier}"

    print(bold(cyan(label)))
    print(bold(f"  {name}"))
    print(_rule())

    if not is_review:
        print()
        print(_wrap(concept["summary"]))
        if "practice" in concept:
            print()
            print(bold("  Practice:"))
            print(_wrap(concept["practice"]))

    print()
    print(bold("  Quiz question:"))
    print(_wrap(concept["quiz"]))
    print()


# ── spaced repetition logic ───────────────────────────────────────────────────

def _pick_concept(pool: list[dict], progress: dict) -> tuple[dict, bool]:
    """Return (concept, is_review). Mirrors quiz_me logic."""
    now = datetime.now()

    due = []
    for concept in pool:
        cid = concept["id"]
        if cid in progress:
            next_review = datetime.fromisoformat(progress[cid]["next_review"])
            if now >= next_review:
                due.append((next_review, concept))

    if due:
        due.sort(key=lambda x: x[0])
        return due[0][1], True

    learned_ids = set(progress.keys())
    for concept in pool:
        if concept["id"] not in learned_ids:
            return concept, False

    return pool[0], True  # all done, loop back to oldest


def _apply_result(concept: dict, result: str, progress: dict) -> str:
    """Update progress dict in place. Returns feedback string."""
    cid = concept["id"]
    now = datetime.now()

    if cid not in progress:
        progress[cid] = {
            "times_correct": 0,
            "times_wrong": 0,
            "interval_days": 1,
            "next_review": now.isoformat(),
            "first_seen": now.isoformat(),
        }

    entry = progress[cid]

    if result == "correct":
        entry["times_correct"] = entry.get("times_correct", 0) + 1
        entry["interval_days"] = min(entry["interval_days"] * 2, 30)
        entry["next_review"] = (now + timedelta(days=entry["interval_days"])).isoformat()
        return (
            green(f"  ✓ Got it. Next review in {entry['interval_days']} day(s).")
        )
    else:
        entry["times_wrong"] = entry.get("times_wrong", 0) + 1
        entry["interval_days"] = 1
        entry["next_review"] = (now + timedelta(days=1)).isoformat()
        feedback = red("  ✗ No worries — review it again tomorrow.\n")
        feedback += "\n" + bold("  Summary:")
        feedback += "\n" + _wrap(concept["summary"])
        if "confused" in concept:
            feedback += "\n\n" + bold("  Think of it this way:")
            feedback += "\n" + _wrap(concept["confused"])
        return feedback


# ── main loop ─────────────────────────────────────────────────────────────────

def _build_pool(track: str) -> list[dict]:
    track_lower = track.lower().strip()
    if track_lower in ("all", ""):
        return CONCEPTS
    if track_lower == "claude":
        return [c for c in CONCEPTS if "track" not in c]
    return [c for c in CONCEPTS if c.get("track") == track_lower]


def run_quiz(track: str = "cli") -> None:
    pool = _build_pool(track)
    if not pool:
        print(red(f"No concepts found for track '{track}'."))
        print("Available tracks: cli, claude, learnair, internet, capstone, all")
        return

    track_label = track if track else "all"
    print()
    print(bold(f"  Quiz: {track_label} track  ({len(pool)} concepts)"))
    print(dim("  Type 'q' at any prompt to quit.\n"))

    while True:
        progress = _get_progress()
        concept, is_review = _pick_concept(pool, progress)

        _print_concept(concept, progress, is_review)

        try:
            ans = input(dim("  Press Enter when ready… ")).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if ans == "q":
            break

        # For new concepts, show the answer after the user reflects
        if not is_review:
            print()

        try:
            verdict = input(bold("  Got it? [y/n/q] ")).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if verdict == "q":
            break

        result = "correct" if verdict.startswith("y") else "wrong"
        feedback = _apply_result(concept, result, progress)
        _save_progress(progress)

        print()
        print(feedback)
        print()

        try:
            cont = input(dim("  Next? [Enter/q] ")).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if cont == "q":
            break

    # Session summary
    progress = _get_progress()
    started = sum(1 for c in pool if c["id"] in progress)
    mastered = sum(
        1 for c in pool
        if c["id"] in progress and progress[c["id"]].get("interval_days", 1) >= 8
    )
    print()
    print(_rule())
    print(bold(f"  Session done — {track_label} track"))
    print(f"  {started}/{len(pool)} started · {mastered}/{len(pool)} mastered (8d+ interval)")
    print(_rule())
    print()


def main() -> None:
    track = sys.argv[1] if len(sys.argv) > 1 else "cli"
    run_quiz(track)


if __name__ == "__main__":
    main()
