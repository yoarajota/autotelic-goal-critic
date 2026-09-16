"""Goal-conditioned learner: tabular Q over goal-relative offsets, with hindsight relabelling.

The value function is indexed by (goal − position) rather than by (position, goal). That choice is
what makes held-out evaluation meaningful: a goal that is never practised still benefits from
practice on other goals, so the held-out success rate measures competence rather than how much
budget each goal happened to receive. A per-goal table would report 0% on every unpractised goal
for both arms, and the comparison would degenerate into an allocation score.

Hindsight relabelling is shared by both arms: after each episode the states actually visited are
also used as training signal for the goal that was reached. Relabelled achievements are
deliberately *not* fed to the selection statistic — an agent that was somewhere is not an agent
that can get there, and scoring that as competence is the chance-achievement failure mode.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from random import Random

from gridworld import ACTION_COUNT, ACTION_DELTAS, Cell, GridWorld

Offset = tuple[int, int]


@dataclass
class RelativeGoalQ:
    world: GridWorld
    rng: Random
    alpha: float = 0.2
    gamma: float = 0.99
    epsilon: float = 0.1
    relabel_count: int = 1
    values: dict[tuple[int, int, int], float] = field(default_factory=dict)

    def offset(self, position: Cell, goal: Cell) -> Offset:
        return (goal[0] - position[0], goal[1] - position[1])

    def value(self, offset: Offset, action: int) -> float:
        return self.values.get((offset[0], offset[1], action), 0.0)

    def best_value(self, offset: Offset) -> float:
        return max(self.value(offset, action) for action in range(ACTION_COUNT))

    def act(self, position: Cell, goal: Cell, *, explore: bool) -> int:
        if explore and self.rng.random() < self.epsilon:
            return self.rng.randrange(ACTION_COUNT)
        offset = self.offset(position, goal)
        best = self.best_value(offset)
        # max() over a list keeps the tie-break order deterministic; a generator does not.
        candidates = [a for a in range(ACTION_COUNT) if self.value(offset, a) == best]
        if len(candidates) == 1:
            return candidates[0]
        return candidates[self.rng.randrange(len(candidates))]

    def update(self, position: Cell, goal: Cell, action: int, next_position: Cell,
               arrived: bool) -> None:
        offset = self.offset(position, goal)
        reward = 1.0 if arrived else 0.0
        bootstrap = (0.0 if arrived
                     else self.gamma * self.best_value(self.offset(next_position, goal)))
        key = (offset[0], offset[1], action)
        self.values[key] = self.value(offset, action) + self.alpha * (
            reward + bootstrap - self.value(offset, action)
        )

    def learn_from(self, trajectory: list[tuple[Cell, int]], goal: Cell) -> None:
        """One Q-learning pass over an episode, as if `goal` had been the pursued goal."""
        for position, action in trajectory:
            next_position = self.world.step(position, action)
            self.update(position, goal, action, next_position, arrived=next_position == goal)

    def train_on(self, trajectory: list[tuple[Cell, int]], pursued_goal: Cell) -> None:
        self.learn_from(trajectory, pursued_goal)
        for relabelled in self.relabelled_goals(trajectory):
            self.learn_from(trajectory, relabelled)

    def relabelled_goals(self, trajectory: list[tuple[Cell, int]]) -> list[Cell]:
        """The HER 'final' strategy: the position the episode ended on."""
        if not trajectory or self.relabel_count <= 0:
            return []
        last_position, last_action = trajectory[-1]
        achieved = self.world.step(last_position, last_action)
        return [achieved] * self.relabel_count


def run_episode(world: GridWorld, learner: RelativeGoalQ, goal: Cell, *, explore: bool,
                collect: bool = True) -> tuple[bool, int, list[tuple[Cell, int]]]:
    """Return (arrived, steps, trajectory).

    A goal already satisfied at the start cell is satisfied: it costs zero steps and produces no
    trajectory. Without that check the start cell's goal would need the agent to walk away and
    return, which would make a trivial goal look like a real one to every measurement here.
    """
    position = world.start
    trajectory: list[tuple[Cell, int]] = []
    if position == goal:
        return True, 0, trajectory
    for step in range(1, world.horizon + 1):
        action = learner.act(position, goal, explore=explore)
        if collect:
            trajectory.append((position, action))
        next_position = world.step(position, action)
        if next_position == goal:
            return True, step, trajectory
        position = next_position
    return False, world.horizon, trajectory


def success_rate(world: GridWorld, learner: RelativeGoalQ, goals: Iterable[Cell]) -> float:
    """Greedy evaluation. No learning, no exploration noise."""
    goals = list(goals)
    if not goals:
        raise ValueError("cannot evaluate on an empty goal set")
    successes = sum(
        1 for goal in goals if run_episode(world, learner, goal, explore=False, collect=False)[0]
    )
    return successes / len(goals)


__all__ = ["ACTION_DELTAS", "RelativeGoalQ", "run_episode", "success_rate"]
