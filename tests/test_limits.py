"""Guards the declared bounds of the experiment.

An experiment whose budget is not pinned is one that can run unbounded, and a pre-registered
margin that can be edited without notice is not pre-registered. These tests read the declaration
files as text and fail if a bound is missing, non-numeric or inconsistent with the thresholds the
structural gate enforces. They are intentionally brittle: changing the margin, the seed count or
a threshold is supposed to be a deliberate edit that also updates this file.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONCEPT = (ROOT / ".sota" / "concept.yaml").read_text(encoding="utf-8")
EVIDENCE = (ROOT / "docs" / "05-evidence.md").read_text(encoding="utf-8")
GATES = (ROOT / ".sota" / "quality-gates.yaml").read_text(encoding="utf-8")
GATE_SCRIPT = (ROOT / "tools" / "complexity_gate.py").read_text(encoding="utf-8")


def test_preregistered_margin_is_intact() -> None:
    assert "20 percentage points" in CONCEPT
    assert "verdict: untested" in CONCEPT


def test_seed_count_is_declared_as_a_finite_number() -> None:
    match = re.search(r"≥ (\d+) seeds per arm", EVIDENCE)
    assert match, "seed count is not declared as a number"
    assert 5 <= int(match.group(1)) <= 1000


def test_budget_is_matched_on_interactions_including_critic_overhead() -> None:
    assert "matched on **total environment transitions**" in EVIDENCE
    assert "deducted from its own arm" in EVIDENCE


def test_both_conditions_are_preregistered() -> None:
    assert "distractor-rich goal space" in EVIDENCE
    assert "never pooled" in EVIDENCE


def test_enforced_thresholds_match_the_declared_ones() -> None:
    for pattern, constant in (
        (r"cyclomatic_complexity_max:\s*(\d+)", "CYCLOMATIC_COMPLEXITY_MAX"),
        (r"function_length_max:\s*(\d+)", "FUNCTION_LENGTH_MAX"),
        (r"file_length_max:\s*(\d+)", "FILE_LENGTH_MAX"),
        (r"max_call_depth:\s*(\d+)", "NESTING_DEPTH_MAX"),
    ):
        declared = re.search(pattern, GATES)
        assert declared, f"{constant} is not declared in .sota/quality-gates.yaml"
        enforced = re.search(rf"^{constant} = (\d+)$", GATE_SCRIPT, re.MULTILINE)
        assert enforced, f"{constant} is not enforced in tools/complexity_gate.py"
        assert declared.group(1) == enforced.group(1), (
            f"{constant}: declared {declared.group(1)}, enforced {enforced.group(1)}"
        )
