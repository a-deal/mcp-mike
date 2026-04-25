"""Tests for the interactive CLI quiz runner."""
from __future__ import annotations

import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

_tmp = tempfile.mkdtemp()
os.environ["MIKE_WORKSPACE"] = _tmp

from mcp_mike.quiz_cli import (
    _build_pool,
    _pick_concept,
    _apply_result,
    _wrap,
    run_quiz,
)
from mcp_mike.tools import CONCEPTS, _get_progress, _save_progress


@pytest.fixture(autouse=True)
def fresh_workspace(tmp_path):
    os.environ["MIKE_WORKSPACE"] = str(tmp_path)
    yield tmp_path
    os.environ["MIKE_WORKSPACE"] = str(tmp_path)


# ── _build_pool ───────────────────────────────────────────────────────────────

def test_build_pool_cli():
    pool = _build_pool("cli")
    assert len(pool) >= 15
    assert all(c.get("track") == "cli" for c in pool)


def test_build_pool_claude():
    pool = _build_pool("claude")
    assert len(pool) > 0
    assert all("track" not in c for c in pool)


def test_build_pool_learnair():
    pool = _build_pool("learnair")
    assert all(c.get("track") == "learnair" for c in pool)


def test_build_pool_all():
    pool_all = _build_pool("all")
    assert len(pool_all) == len(CONCEPTS)


def test_build_pool_empty_string():
    pool = _build_pool("")
    assert len(pool) == len(CONCEPTS)


def test_build_pool_unknown_track():
    pool = _build_pool("nonexistent")
    assert pool == []


# ── _pick_concept ─────────────────────────────────────────────────────────────

def test_pick_concept_new_when_no_progress():
    pool = _build_pool("cli")
    concept, is_review = _pick_concept(pool, {})
    assert concept in pool
    assert is_review is False


def test_pick_concept_starts_with_tier_1():
    pool = _build_pool("cli")
    concept, is_review = _pick_concept(pool, {})
    assert concept["tier"] == 1
    assert is_review is False


def test_pick_concept_returns_review_when_due(fresh_workspace):
    pool = _build_pool("cli")
    first = pool[0]
    progress = {
        first["id"]: {
            "times_correct": 2,
            "times_wrong": 0,
            "interval_days": 1,
            "next_review": (datetime.now() - timedelta(hours=1)).isoformat(),
            "first_seen": datetime.now().isoformat(),
        }
    }
    concept, is_review = _pick_concept(pool, progress)
    assert concept["id"] == first["id"]
    assert is_review is True


def test_pick_concept_skips_future_review(fresh_workspace):
    pool = _build_pool("cli")
    first = pool[0]
    progress = {
        first["id"]: {
            "times_correct": 1,
            "times_wrong": 0,
            "interval_days": 7,
            "next_review": (datetime.now() + timedelta(days=7)).isoformat(),
            "first_seen": datetime.now().isoformat(),
        }
    }
    concept, is_review = _pick_concept(pool, progress)
    # Should pick the next new concept, not the future review
    assert concept["id"] != first["id"]
    assert is_review is False


# ── _apply_result ─────────────────────────────────────────────────────────────

def test_apply_result_correct_saves_progress(fresh_workspace):
    pool = _build_pool("cli")
    concept = pool[0]
    progress = {}

    feedback = _apply_result(concept, "correct", progress)
    _save_progress(progress)

    assert concept["id"] in progress
    assert progress[concept["id"]]["times_correct"] == 1
    assert progress[concept["id"]]["interval_days"] == 2
    assert "got it" in feedback.lower() or "✓" in feedback


def test_apply_result_wrong_resets_interval(fresh_workspace):
    pool = _build_pool("cli")
    concept = pool[0]
    progress = {
        concept["id"]: {
            "times_correct": 3,
            "times_wrong": 0,
            "interval_days": 8,
            "next_review": datetime.now().isoformat(),
            "first_seen": datetime.now().isoformat(),
        }
    }

    feedback = _apply_result(concept, "wrong", progress)
    assert progress[concept["id"]]["interval_days"] == 1
    assert "✗" in feedback or "no worries" in feedback.lower()


def test_apply_result_wrong_shows_confused(fresh_workspace):
    pool = _build_pool("cli")
    concept = next(c for c in pool if "confused" in c)
    progress = {}

    feedback = _apply_result(concept, "wrong", progress)
    assert concept["confused"][:20].lower() in feedback.lower() or "think of it" in feedback.lower()


def test_apply_result_correct_doubles_interval(fresh_workspace):
    pool = _build_pool("cli")
    concept = pool[0]
    progress = {
        concept["id"]: {
            "times_correct": 1,
            "times_wrong": 0,
            "interval_days": 4,
            "next_review": datetime.now().isoformat(),
            "first_seen": datetime.now().isoformat(),
        }
    }

    _apply_result(concept, "correct", progress)
    assert progress[concept["id"]]["interval_days"] == 8


def test_apply_result_caps_interval_at_30(fresh_workspace):
    pool = _build_pool("cli")
    concept = pool[0]
    progress = {
        concept["id"]: {
            "times_correct": 10,
            "times_wrong": 0,
            "interval_days": 30,
            "next_review": datetime.now().isoformat(),
            "first_seen": datetime.now().isoformat(),
        }
    }

    _apply_result(concept, "correct", progress)
    assert progress[concept["id"]]["interval_days"] == 30


# ── _wrap ─────────────────────────────────────────────────────────────────────

def test_wrap_breaks_long_lines():
    text = "word " * 30
    result = _wrap(text)
    for line in result.splitlines():
        assert len(line) <= 62  # _W + indent wiggle


def test_wrap_preserves_content():
    text = "The quick brown fox jumps over the lazy dog"
    result = _wrap(text)
    assert "quick brown fox" in result


def test_wrap_custom_indent():
    result = _wrap("hello world", indent=4)
    assert result.startswith("    ")


# ── run_quiz (smoke tests with mocked input) ──────────────────────────────────

def test_run_quiz_unknown_track_prints_error(capsys):
    run_quiz("nonexistent")
    out = capsys.readouterr().out
    assert "no concepts found" in out.lower() or "available tracks" in out.lower()


def test_run_quiz_cli_track_exits_on_q(monkeypatch, capsys):
    inputs = iter(["q"])
    monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

    run_quiz("cli")
    out = capsys.readouterr().out
    # Should show concept header before quitting
    assert "cli" in out.lower()


def test_run_quiz_correct_answer_updates_progress(monkeypatch, fresh_workspace, capsys):
    inputs = iter(["", "y", "q"])
    monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

    run_quiz("cli")

    progress = _get_progress()
    assert len(progress) == 1
    cid = list(progress.keys())[0]
    assert progress[cid]["times_correct"] == 1


def test_run_quiz_wrong_answer_updates_progress(monkeypatch, fresh_workspace, capsys):
    inputs = iter(["", "n", "q"])
    monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

    run_quiz("cli")

    progress = _get_progress()
    assert len(progress) == 1
    cid = list(progress.keys())[0]
    assert progress[cid]["times_wrong"] == 1


def test_run_quiz_multiple_rounds(monkeypatch, fresh_workspace, capsys):
    # Answer 3 concepts correctly then quit
    inputs = iter(["", "y", "", "", "y", "", "", "y", "", "q"])
    monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

    run_quiz("cli")

    progress = _get_progress()
    assert len(progress) == 3


def test_run_quiz_shows_session_summary(monkeypatch, fresh_workspace, capsys):
    inputs = iter(["q"])
    monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

    run_quiz("cli")

    out = capsys.readouterr().out
    assert "session done" in out.lower()
