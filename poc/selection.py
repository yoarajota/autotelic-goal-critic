"""Goal selection policies: uniform sampling, and a generator paired with an independent critic.

The critic rates a goal-space **region** — the Manhattan-distance ring it belongs to — rather than
a single cell, because competence in this world depends on distance and cells in a ring are
interchangeable. Scoring individual cells would estimate learning progress from a handful of
noisy outcomes per cell and select on noise; this is the same region-based estimate the published
systems use, mapped onto the only meaningful region parameterisation this world has.

Independence is structural and is the point: the critic never reads the learner's Q-values. It
reads the success/failure outcomes the environment produced for the goals it was asked to achieve.
A rating derived from the estimates being improved can rate a goal high for the same reason it
mis-estimates it.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from random import Random
from typing import Protocol

from gridworld import Cell

RegionOf = Callable[[Cell], int]

# Signals that a region cannot be scored yet. Kept separate from a low score on purpose: an
# unrated region must be explored, never rejected as unreachable.
UNRATED = float("inf")


class GoalSelector(Protocol):
    """Both arms implement this, so the experiment loop has one code path."""

    def choose(self, rng: Random) -> Cell: ...

    def observe(self, goal: Cell, success: bool) -> None: ...


@dataclass
class UniformSelection:
    """The incumbent: every goal equally likely, forever."""

    goals: list[Cell]

    def choose(self, rng: Random) -> Cell:
        return self.goals[rng.randrange(len(self.goals))]

    def observe(self, goal: Cell, success: bool) -> None:
        """Records nothing: uniform sampling is not a function of past outcomes."""
        return


@dataclass
class CriticSelection:
    """Generator + independent critic: propose candidates, rate them, select."""

    goals: list[Cell]
    region_of: RegionOf
    window: int = 4
    min_samples: int = 8
    trivial_ceiling: float = 0.95
    candidates: int = 8
    epsilon: float = 0.4
    outcomes: dict[int, list[int]] = field(default_factory=dict)

    def observe(self, goal: Cell, success: bool) -> None:
        self.outcomes.setdefault(self.region_of(goal), []).append(1 if success else 0)

    def competence(self, region: int) -> float | None:
        """Mean outcome over the most recent window, or None with too few outcomes."""
        history = self.outcomes.get(region)
        if not history or len(history) < self.min_samples:
            return None
        return sum(history[-self.window :]) / min(self.window, len(history))

    def learning_progress(self, region: int) -> float | None:
        """Absolute change in competence across two consecutive windows."""
        history = self.outcomes.get(region)
        if not history or len(history) < self.min_samples:
            return None
        recent = history[-self.window :]
        previous = history[-2 * self.window : -self.window]
        if len(previous) < self.window:
            return None
        return abs(sum(recent) / len(recent) - sum(previous) / len(previous))

    def score(self, goal: Cell) -> float:
        region = self.region_of(goal)
        competence = self.competence(region)
        if competence is None:
            return UNRATED
        if competence >= self.trivial_ceiling:
            return 0.0
        if competence <= 0.0:
            # Every attempt so far failed. Not provably impossible, but with enough recorded
            # outcomes it is the best available stand-in, and it is retried whenever the region
            # stops being selected (it stays in the candidate pool).
            return 0.0
        progress = self.learning_progress(region)
        return 0.0 if progress is None else progress

    def choose(self, rng: Random) -> Cell:
        if rng.random() < self.epsilon:
            return self.goals[rng.randrange(len(self.goals))]
        proposals = [self.goals[rng.randrange(len(self.goals))] for _ in range(self.candidates)]
        scores = [self.score(goal) for goal in proposals]
        best = max(scores)
        if best <= 0.0:
            # Nothing scored, or every candidate is mastered or unreachable. Falling back to
            # uniform sampling is what keeps the run alive instead of stalling on an empty pool.
            return self.goals[rng.randrange(len(self.goals))]
        winners = [goal for goal, score in zip(proposals, scores, strict=True) if score == best]
        return winners[0] if len(winners) == 1 else winners[rng.randrange(len(winners))]


__all__ = ["CriticSelection", "GoalSelector", "RegionOf", "UNRATED", "UniformSelection"]
