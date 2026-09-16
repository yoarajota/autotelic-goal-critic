"""Discrete gridworld whose goal space mixes trivial, reachable and impossible goals.

The world is deliberately minimal: an open grid, four moves, a fixed start cell, a fixed
episode horizon. Openness matters — with no interior walls, the shortest path to any cell is its
Manhattan distance, so "cannot be reached within the horizon" is a verifiable impossibility
rather than an empirical guess. That is what makes the impossible goal class honest: a goal
further away than the horizon is not hard, it is unreachable, in every episode, by construction.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

Cell = tuple[int, int]

# up, down, left, right
ACTION_DELTAS: tuple[Cell, ...] = ((-1, 0), (1, 0), (0, -1), (0, 1))
ACTION_COUNT = len(ACTION_DELTAS)


class GoalClass(Enum):
    """Why a goal is or is not worth practising, decided by the environment, not the agent."""

    TRIVIAL = "trivial"  # satisfied within one step of the start cell
    REACHABLE = "reachable"  # needs practice, and practice can succeed
    IMPOSSIBLE = "impossible"  # beyond the horizon: unreachable in every episode


@dataclass(frozen=True)
class GridWorld:
    size: int = 15
    horizon: int = 20

    @property
    def start(self) -> Cell:
        return (self.size // 2, self.size // 2)

    def cells(self) -> list[Cell]:
        return [(x, y) for x in range(self.size) for y in range(self.size)]

    def distance(self, a: Cell, b: Cell) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def classify(self, goal: Cell) -> GoalClass:
        distance = self.distance(self.start, goal)
        if distance <= 1:
            return GoalClass.TRIVIAL
        if distance <= self.horizon:
            return GoalClass.REACHABLE
        return GoalClass.IMPOSSIBLE

    def goals(self, *classes: GoalClass) -> list[Cell]:
        return [cell for cell in self.cells() if self.classify(cell) in classes]

    def step(self, position: Cell, action: int) -> Cell:
        """Move, clamped at the boundary. A blocked move stays in place and still costs a step."""
        dx, dy = ACTION_DELTAS[action]
        x = min(max(position[0] + dx, 0), self.size - 1)
        y = min(max(position[1] + dy, 0), self.size - 1)
        return (x, y)
