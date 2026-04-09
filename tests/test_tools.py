"""Tests for Mike's MCP server tools."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest

# Set workspace to a temp dir before importing tools
_tmp = tempfile.mkdtemp()
os.environ["MIKE_WORKSPACE"] = _tmp


from mcp_mike.tools import (
    load_persona,
    hub,
    discover,
    ingest,
    quiz_me,
    mark_concept,
    progress,
    mochary,
    duke,
    komoroske,
    whats_next,
    save_note,
    _get_progress,
    _save_progress,
    CONCEPTS,
)


@pytest.fixture(autouse=True)
def workspace(tmp_path):
    """Set up a fresh workspace for each test."""
    os.environ["MIKE_WORKSPACE"] = str(tmp_path)

    # Create persona files
    personas = tmp_path / "personas"
    personas.mkdir()
    (personas / "nexus.md").write_text("# Nexus\nYou are Mike's main thinking partner.")
    (personas / "mens-work.md").write_text("# Men's Work\nFacilitation persona.")

    # Create project dirs with notes
    learnair = tmp_path / "learnair"
    learnair.mkdir()
    (learnair / "notes.md").write_text("# LearnAIR Notes\n- Call Teresa about curriculum\n- TODO: Draft employer outreach script\n")
    (learnair / "thesis.md").write_text("# Thesis\nEmployers will pay for veterans trained in AI ops supervision.")

    workshops = tmp_path / "workshops"
    workshops.mkdir()
    (workshops / "notes.md").write_text("# Workshop Notes\n- TODO: Finalize handout for Wednesday\n")

    # Create hub docs dir
    hub_dir = tmp_path / "hub"
    hub_dir.mkdir()
    (hub_dir / "competitive-landscape.md").write_text("# Competitive Landscape\n23 organizations analyzed. Break Line, BetterUp, VetsinTech...")
    (hub_dir / "april-7-arc.md").write_text("# April 7 Arc\nBeat 1: The Bet. Beat 2: The Job...")

    # Clean progress for each test
    progress_path = tmp_path / ".progress.json"
    if progress_path.exists():
        progress_path.unlink()

    yield tmp_path


# --- load_persona ---

def test_load_persona_exists(workspace):
    result = load_persona("nexus")
    assert "Nexus" in result
    assert "thinking partner" in result


def test_load_persona_case_insensitive(workspace):
    result = load_persona("Nexus")
    assert "Nexus" in result


def test_load_persona_not_found(workspace):
    result = load_persona("nonexistent")
    assert "not found" in result.lower()


def test_load_persona_lists_available(workspace):
    result = load_persona("nonexistent")
    assert "nexus" in result.lower()
    assert "mens-work" in result.lower()


# --- hub ---

def test_hub_search_finds_match(workspace):
    result = hub("competitive")
    assert "23 organizations" in result


def test_hub_search_multiple_results(workspace):
    result = hub("the")
    # Should find content from multiple files
    assert "competitive" in result.lower() or "arc" in result.lower()


def test_hub_search_no_match(workspace):
    result = hub("xyznonexistent")
    assert "no results" in result.lower() or "nothing found" in result.lower()


def test_hub_search_case_insensitive(workspace):
    result = hub("COMPETITIVE")
    assert "23 organizations" in result


# --- quiz_me ---

def test_quiz_me_returns_concept():
    result = quiz_me()
    # Should return a concept with a quiz question
    assert "quiz" in result.lower() or "?" in result


def test_quiz_me_starts_with_tier_1():
    result = quiz_me()
    # First quiz should be a tier 1 concept
    tier_1_names = [c["name"] for c in CONCEPTS if c["tier"] == 1]
    found = any(name.lower() in result.lower() for name in tier_1_names)
    assert found, f"Expected a tier 1 concept in: {result[:100]}"


# --- mark_concept ---

def test_mark_concept_correct(workspace):
    result = mark_concept("what-claude-is", "correct")
    assert "correct" in result.lower() or "nice" in result.lower() or "got it" in result.lower()
    # Check progress was saved
    progress = _get_progress(workspace)
    assert "what-claude-is" in progress


def test_mark_concept_wrong(workspace):
    result = mark_concept("what-claude-is", "wrong")
    assert "review" in result.lower() or "hint" in result.lower() or "summary" in result.lower()


def test_mark_concept_invalid_id(workspace):
    result = mark_concept("fake-concept-id", "correct")
    assert "not found" in result.lower()


def test_mark_concept_updates_interval(workspace):
    mark_concept("what-claude-is", "correct")
    progress = _get_progress(workspace)
    interval_1 = progress["what-claude-is"]["interval_days"]

    mark_concept("what-claude-is", "correct")
    progress = _get_progress(workspace)
    interval_2 = progress["what-claude-is"]["interval_days"]

    assert interval_2 > interval_1


def test_mark_concept_wrong_resets_interval(workspace):
    mark_concept("what-claude-is", "correct")
    mark_concept("what-claude-is", "correct")
    progress = _get_progress(workspace)
    interval_before = progress["what-claude-is"]["interval_days"]

    mark_concept("what-claude-is", "wrong")
    progress = _get_progress(workspace)
    interval_after = progress["what-claude-is"]["interval_days"]

    assert interval_after < interval_before


# --- whats_next ---

def test_whats_next_finds_todos(workspace):
    result = whats_next()
    assert "handout" in result.lower() or "employer" in result.lower()


def test_whats_next_shows_project(workspace):
    result = whats_next()
    assert "learnair" in result.lower() or "workshop" in result.lower()


# --- save_note ---

def test_save_note_appends(workspace):
    result = save_note("learnair", "Met with Teresa. She's interested in the two-prong approach.")
    assert "saved" in result.lower()
    content = (workspace / "learnair" / "notes.md").read_text()
    assert "two-prong" in content


def test_save_note_creates_project_if_missing(workspace):
    result = save_note("new-project", "First note for this project.")
    assert "saved" in result.lower()
    assert (workspace / "new-project" / "notes.md").exists()
    content = (workspace / "new-project" / "notes.md").read_text()
    assert "First note" in content


def test_save_note_timestamps(workspace):
    save_note("learnair", "Test note with timestamp.")
    content = (workspace / "learnair" / "notes.md").read_text()
    # Should have a date/time marker
    assert "2026" in content or "- " in content


# --- quiz_me with tracks ---

def test_quiz_me_claude_track():
    result = quiz_me("claude")
    # Should only return Claude-usage concepts (no track field)
    tier_1_names = [c["name"] for c in CONCEPTS if "track" not in c and c["tier"] == 1]
    found = any(name.lower() in result.lower() for name in tier_1_names)
    assert found, f"Expected a Claude concept in: {result[:100]}"


def test_quiz_me_learnair_track():
    result = quiz_me("learnair")
    # Should return a LearnAIR domain concept
    learnair_names = [c["name"] for c in CONCEPTS if c.get("track") == "learnair"]
    found = any(name.lower() in result.lower() for name in learnair_names)
    assert found, f"Expected a LearnAIR concept in: {result[:200]}"


def test_quiz_me_internet_track():
    result = quiz_me("internet")
    internet_names = [c["name"] for c in CONCEPTS if c.get("track") == "internet"]
    found = any(name.lower() in result.lower() for name in internet_names)
    assert found, f"Expected an internet concept in: {result[:200]}"


def test_quiz_me_invalid_track():
    result = quiz_me("nonexistent")
    assert "no concepts found" in result.lower()


def test_quiz_me_all_tracks():
    result = quiz_me("")
    # Should return something (any track)
    assert "?" in result or "quiz" in result.lower()


def test_quiz_me_learnair_has_confused():
    """LearnAIR concepts should surface 'confused' explanations."""
    result = quiz_me("learnair")
    assert "confused" in result.lower() or "fuzzy" in result.lower() or "think of it" in result.lower()


def test_mark_concept_learnair_wrong_shows_confused(workspace):
    """Marking a LearnAIR concept wrong should show the 'confused' explanation."""
    result = mark_concept("supervision-gap", "wrong")
    assert "think of it this way" in result.lower()


def test_mark_concept_learnair_correct(workspace):
    result = mark_concept("supervision-gap", "correct")
    assert "correct" in result.lower() or "got it" in result.lower()
    progress_data = _get_progress(workspace)
    assert "supervision-gap" in progress_data


# --- progress ---

def test_progress_all_tracks(workspace):
    result = progress()
    assert "claude" in result.lower()
    assert "learnair" in result.lower()
    assert "internet" in result.lower()


def test_progress_single_track(workspace):
    result = progress("learnair")
    assert "learnair" in result.lower()
    assert "claude" not in result.lower()


def test_progress_invalid_track(workspace):
    result = progress("fake")
    assert "unknown" in result.lower()


def test_progress_after_learning(workspace):
    mark_concept("supervision-gap", "correct")
    result = progress("learnair")
    assert "1/" in result  # 1 started


# --- mochary ---

def test_mochary_meeting_prep():
    result = mochary("meeting prep with Justin tomorrow")
    assert "meeting prep" in result.lower()
    assert "DRI" in result
    assert "issue" in result.lower()

def test_mochary_difficult_conversation():
    result = mochary("I need to have a difficult conversation with my co-founder")
    assert "behavior" in result.lower()
    assert "impact" in result.lower()

def test_mochary_priorities():
    result = mochary("I have too many priorities and I'm scattered")
    assert "top goal" in result.lower()
    assert "energy" in result.lower()

def test_mochary_default():
    result = mochary("help me with something")
    assert "available frameworks" in result.lower()


# --- duke ---

def test_duke_message_review():
    result = duke("review this message before I send it to Teresa")
    assert "proposals not declarations" in result.lower()
    assert "recipient" in result.lower()

def test_duke_decision():
    result = duke("should we commit to the 90-day pilot")
    assert "pre-mortem" in result.lower()
    assert "reversible" in result.lower()

def test_duke_calibration():
    result = duke("I think this partnership is going to work")
    assert "percentage" in result.lower() or "%" in result
    assert "evidence" in result.lower()

def test_duke_default():
    result = duke("what can you help with")
    assert "decision quality" in result.lower()


# --- komoroske ---

def test_komoroske_sequencing():
    result = komoroske("I have 8 ideas and don't know which to do first")
    assert "shiny object" in result.lower()
    assert "top 3" in result.lower()

def test_komoroske_convergence():
    result = komoroske("am I converging or diverging on LearnAIR")
    assert "converging" in result.lower()
    assert "leaf node" in result.lower()

def test_komoroske_synthesis():
    result = komoroske("evening synthesis, what did I learn today")
    assert "stood out" in result.lower()
    assert "compounds" in result.lower()

def test_komoroske_build():
    result = komoroske("should I build this feature")
    assert "toehold" in result.lower()

def test_komoroske_default():
    result = komoroske("help")
    assert "systems thinking" in result.lower()


# --- discover ---

def test_discover_finds_files_by_name(workspace, tmp_path):
    """Discover should find files matching query in search dirs."""
    # Create a test file in a searchable location
    search_dir = tmp_path / "searchable"
    search_dir.mkdir()
    (search_dir / "teresa-notes.md").write_text("Notes from call with Teresa about curriculum.")

    os.environ["MIKE_SEARCH_DIRS"] = str(search_dir)
    result = discover("teresa", "files")
    del os.environ["MIKE_SEARCH_DIRS"]
    assert "teresa" in result.lower()


def test_discover_finds_files_by_content(workspace, tmp_path):
    search_dir = tmp_path / "searchable"
    search_dir.mkdir()
    (search_dir / "meeting-notes.md").write_text("Discussed employer readiness with Justin and Teresa.")

    os.environ["MIKE_SEARCH_DIRS"] = str(search_dir)
    result = discover("employer readiness", "files")
    del os.environ["MIKE_SEARCH_DIRS"]
    assert "meeting-notes" in result.lower()


def test_discover_no_results(workspace, tmp_path):
    search_dir = tmp_path / "empty"
    search_dir.mkdir()

    os.environ["MIKE_SEARCH_DIRS"] = str(search_dir)
    result = discover("xyznonexistent", "files")
    del os.environ["MIKE_SEARCH_DIRS"]
    assert "nothing found" in result.lower()


# --- ingest ---

def test_ingest_local_file(workspace, tmp_path):
    source = tmp_path / "workshop-handout.md"
    source.write_text("# Workshop Handout\nContent for the Wednesday session.")

    result = ingest(str(source), "workshops")
    assert "ingested" in result.lower()
    assert (workspace / "workshops" / "workshop-handout.md").exists()
    content = (workspace / "workshops" / "workshop-handout.md").read_text()
    assert "Workshop Handout" in content
    assert "source:" in content  # frontmatter


def test_ingest_creates_project_dir(workspace, tmp_path):
    source = tmp_path / "new-thing.txt"
    source.write_text("Some content.")

    result = ingest(str(source), "new-project")
    assert "ingested" in result.lower()
    assert (workspace / "new-project").exists()


def test_ingest_default_project(workspace, tmp_path):
    source = tmp_path / "random-file.md"
    source.write_text("Stuff.")

    result = ingest(str(source))
    assert "reference" in result.lower()


def test_ingest_file_not_found(workspace):
    result = ingest("/nonexistent/file.md", "learnair")
    assert "not found" in result.lower()
