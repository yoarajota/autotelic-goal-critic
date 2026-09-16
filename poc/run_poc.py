"""Proof of concept: does critic-guided goal selection buy competence over uniform sampling?

Critical function under test, in one sentence: **a critic that rates goal-space regions by
absolute learning progress, estimated from the achievement outcomes the environment reported,
raises the learner's held-out success rate over reachable goals above uniform random goal
sampling at a matched interaction budget.**

Prediction from the theory pass (P1), fixed before this file existed:

* distractor-rich goal space — the critic is ahead: >= 20 percentage points at the matched budget,
  or equal competence in at most half the transitions;
* all-learnable goal space — the advantage is smaller or absent, because uniform sampling is
  reported as competitive where there are no distractors.

Usage:

    python poc/run_poc.py --budget 60000 --eval-every 5000 --seeds 0 1 2 3 4

What this is not: it is not the P5 benchmark. One gridworld, one budget range, a distance-ring
region parameterisation, no baseline tuning. It exists to show the critical function runs and to
report the direction and rough size of the effect, which the P5 pass then measures properly.
"""

from __future__ import annotations

import argparse
import json
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from random import Random
from typing import Any

from gridworld import Cell, GoalClass, GridWorld
from learner import RelativeGoalQ, run_episode, success_rate
from selection import CriticSelection, GoalSelector, UniformSelection

GRID_SIZE = 21
# The horizon is tight relative to the reachable distances: a goal at the far end of the reachable
# set needs a near-optimal path to be reached at all, so held-out success measures the quality of
# what was learned rather than merely whether the agent drifted into the goal.
HORIZON = 12
ALPHA = 0.2
GAMMA = 0.99
ACTION_EPSILON = 0.1
RELABEL_COUNT = 1
CRITIC_WINDOW = 4
CRITIC_MIN_SAMPLES = 8
CRITIC_CANDIDATES = 8
CRITIC_EPSILON = 0.4
TRIVIAL_CEILING = 0.95
EVAL_SEED = 20260916
EVAL_GOALS = 30
SEEDS = (0, 1, 2, 3, 4)
CONDITIONS = ("distractor-rich", "all-learnable")
ARMS = ("uniform", "critic")
PREDICTED_MARGIN_PP = 20.0
TARGET_RATE = 0.90


@dataclass
class Run:
    condition: str
    arm: str
    seed: int
    # (checkpoint target, held-out success rate). The checkpoint target is the intended budget,
    # not the exact transition count reached: episodes overshoot it by up to the horizon, and
    # keying on the exact count would put each seed in its own column and make the median a
    # median of one sample.
    curve: list[tuple[int, float]]
    steps: int
    episodes: int
    episodes_per_region: dict[int, int] = field(default_factory=dict)


@dataclass(frozen=True)
class World:
    """The grid plus the goal sets, assembled once so every run sees the same problem."""

    grid: GridWorld
    evaluation: list[Cell]

    def training_goals(self, condition: str) -> list[Cell]:
        if condition == "distractor-rich":
            goals = self.grid.goals(GoalClass.TRIVIAL, GoalClass.REACHABLE, GoalClass.IMPOSSIBLE)
        elif condition == "all-learnable":
            goals = self.grid.goals(GoalClass.REACHABLE)
        else:
            raise ValueError(f"unknown condition {condition!r}")
        held_out = set(self.evaluation)
        return [goal for goal in goals if goal not in held_out]

    def region(self, goal: Cell) -> int:
        return self.grid.distance(self.grid.start, goal)

    def practice_region(self, region: int) -> bool:
        """Regions whose practice can produce progress: reachable, and not satisfied at once."""
        return 2 <= region <= self.grid.horizon


def build_world() -> World:
    grid = GridWorld(size=GRID_SIZE, horizon=HORIZON)
    reachable = grid.goals(GoalClass.REACHABLE)
    held_out = sorted(Random(EVAL_SEED).sample(reachable, EVAL_GOALS))
    return World(grid=grid, evaluation=held_out)


def make_selector(arm: str, goals: list[Cell], world: World) -> GoalSelector:
    if arm == "uniform":
        return UniformSelection(goals=goals)
    if arm == "critic":
        return CriticSelection(
            goals=goals,
            region_of=world.region,
            window=CRITIC_WINDOW,
            min_samples=CRITIC_MIN_SAMPLES,
            trivial_ceiling=TRIVIAL_CEILING,
            candidates=CRITIC_CANDIDATES,
            epsilon=CRITIC_EPSILON,
        )
    raise ValueError(f"unknown arm {arm!r}")


def train(world: World, condition: str, arm: str, seed: int, budget: int,
          eval_every: int) -> Run:
    rng = Random(seed)
    learner = RelativeGoalQ(world=world.grid, rng=rng, alpha=ALPHA, gamma=GAMMA,
                            epsilon=ACTION_EPSILON, relabel_count=RELABEL_COUNT)
    goals = world.training_goals(condition)
    selector = make_selector(arm, goals, world)
    curve = [(0, success_rate(world.grid, learner, world.evaluation))]
    steps = 0
    episodes = 0
    per_region: dict[int, int] = {}
    next_eval = eval_every
    while steps < budget:
        goal = selector.choose(rng)
        arrived, _, trajectory = run_episode(world.grid, learner, goal, explore=True)
        selector.observe(goal, arrived)
        learner.train_on(trajectory, goal)
        steps += max(len(trajectory), 1)
        episodes += 1
        region = world.region(goal)
        per_region[region] = per_region.get(region, 0) + 1
        while steps >= next_eval and next_eval <= budget:
            curve.append((next_eval, success_rate(world.grid, learner, world.evaluation)))
            next_eval += eval_every
    return Run(condition=condition, arm=arm, seed=seed, curve=curve, steps=steps,
               episodes=episodes, episodes_per_region=per_region)


def run_matrix(world: World, budget: int, eval_every: int,
               seeds: list[int]) -> dict[str, dict[str, list[Run]]]:
    return {
        condition: {
            arm: [train(world, condition, arm, seed, budget, eval_every) for seed in seeds]
            for arm in ARMS
        }
        for condition in CONDITIONS
    }


def median_curve(runs: list[Run]) -> list[tuple[int, float]]:
    points: dict[int, list[float]] = {}
    for run in runs:
        for spent, rate in run.curve:
            points.setdefault(spent, []).append(rate)
    return sorted((spent, statistics.median(rates)) for spent, rates in points.items())


def transitions_to_reach(curve: list[tuple[int, float]], target: float) -> int | None:
    for spent, rate in curve:
        if rate >= target:
            return spent
    return None


def pct(value: float) -> str:
    return f"{value * 100:5.1f}%"


def practice_share(runs: list[Run], world: World) -> float:
    """Share of episodes spent on regions where practice can produce progress."""
    shares = [
        sum(count for region, count in run.episodes_per_region.items()
            if world.practice_region(region)) / max(run.episodes, 1)
        for run in runs
    ]
    return statistics.median(shares)


def arm_lines(arm: str, curves: dict[str, list[tuple[int, float]]],
              finals: dict[str, list[float]]) -> list[str]:
    return [
        f"  {arm:8s} held-out success: " + "  ".join(
            f"{spent // 1000}k={pct(rate)}" for spent, rate in curves[arm]
        ),
        f"  {'':8s} final median {pct(statistics.median(finals[arm]))} "
        f"(min {pct(min(finals[arm]))}, max {pct(max(finals[arm]))}) over {len(finals[arm])} seeds",
    ]


def summarise_condition(world: World, condition: str, runs: dict[str, list[Run]],
                        args: argparse.Namespace) -> tuple[dict[str, Any], list[str]]:
    finals = {arm: [run.curve[-1][1] for run in runs[arm]] for arm in ARMS}
    curves = {arm: median_curve(runs[arm]) for arm in ARMS}
    baseline_final = statistics.median(finals["uniform"])
    margin = statistics.median(finals["critic"]) - baseline_final
    probe = train(world, condition, "uniform", args.seeds[0], args.saturation_budget,
                  args.eval_every)

    lines = [condition]
    for arm in ARMS:
        lines += arm_lines(arm, curves, finals)
    lines.append(f"  baseline at {args.saturation_budget // 1000}k transitions "
                 f"(ceiling probe, seed {args.seeds[0]}): {pct(probe.curve[-1][1])}")
    lines.append(f"  critic margin at matched budget: {margin * 100:+5.1f} pp "
                 f"(predicted: {args.prediction[condition]})")
    lines.append(
        f"  transitions to reach the baseline's final competence of {pct(baseline_final)}: "
        f"uniform {transitions_to_reach(curves['uniform'], baseline_final)}, "
        f"critic {transitions_to_reach(curves['critic'], baseline_final)}"
    )
    lines.append(f"  transitions to {pct(TARGET_RATE).strip()} held-out success, median of seeds "
                 f"(not pre-registered at P1): "
                 f"uniform {transitions_to_reach(curves['uniform'], TARGET_RATE)}, "
                 f"critic {transitions_to_reach(curves['critic'], TARGET_RATE)}")
    for arm in ARMS:
        lines.append(f"  {arm:8s} episodes spent on reachable-with-practice regions: "
                     f"{pct(practice_share(runs[arm], world))}")
    lines.append("")

    summary = {
        "median_final": {arm: statistics.median(finals[arm]) for arm in ARMS},
        "min_final": {arm: min(finals[arm]) for arm in ARMS},
        "max_final": {arm: max(finals[arm]) for arm in ARMS},
        "margin_pp": margin * 100,
        "transitions_to_baseline_final": {
            "uniform": transitions_to_reach(curves["uniform"], baseline_final),
            "critic": transitions_to_reach(curves["critic"], baseline_final),
        },
        "transitions_to_90pct": {
            "uniform": transitions_to_reach(curves["uniform"], TARGET_RATE),
            "critic": transitions_to_reach(curves["critic"], TARGET_RATE),
        },
        "saturation_probe_rate": probe.curve[-1][1],
        "episode_share_reachable_regions": {arm: practice_share(runs[arm], world) for arm in ARMS},
    }
    return summary, lines


def config_payload(world: World, args: argparse.Namespace) -> dict[str, Any]:
    return {
        "grid_size": GRID_SIZE, "horizon": HORIZON, "alpha": ALPHA, "gamma": GAMMA,
        "action_epsilon": ACTION_EPSILON, "relabel_count": RELABEL_COUNT,
        "critic_window": CRITIC_WINDOW, "critic_min_samples": CRITIC_MIN_SAMPLES,
        "critic_candidates": CRITIC_CANDIDATES, "critic_epsilon": CRITIC_EPSILON,
        "trivial_ceiling": TRIVIAL_CEILING, "budget": args.budget,
        "eval_every": args.eval_every, "seeds": list(args.seeds),
        "held_out_eval_goals": len(world.evaluation), "eval_seed": EVAL_SEED,
    }


def goal_space_payload(world: World) -> dict[str, Any]:
    return {
        condition: {
            "training_goals": len(world.training_goals(condition)),
            "goals_per_region": {
                str(region): sum(1 for goal in world.training_goals(condition)
                                 if world.region(goal) == region)
                for region in sorted({world.region(goal)
                                      for goal in world.training_goals(condition)})
            },
        }
        for condition in CONDITIONS
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--budget", type=int, default=60_000,
                        help="environment transitions per arm per seed")
    parser.add_argument("--eval-every", type=int, default=5_000)
    parser.add_argument("--seeds", type=int, nargs="+", default=list(SEEDS))
    parser.add_argument("--saturation-budget", type=int, default=200_000,
                        help="budget for the single-seed ceiling probe on the baseline arm")
    parser.add_argument("--out", type=Path, default=Path("evidence-data/E-002-poc-runs.json"))
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    args.prediction = {
        "distractor-rich": f"critic ahead by >= {PREDICTED_MARGIN_PP:.0f} pp at matched budget",
        "all-learnable": "advantage smaller or absent",
    }
    world = build_world()
    runs = run_matrix(world, args.budget, args.eval_every, list(args.seeds))

    print(f"grid {GRID_SIZE}x{GRID_SIZE}, horizon {HORIZON}, "
          f"{len(world.evaluation)} held-out reachable goals, budget {args.budget} transitions")
    for condition in CONDITIONS:
        goals = world.training_goals(condition)
        share = sum(1 for goal in goals if world.practice_region(world.region(goal))) / len(goals)
        print(f"  {condition}: {len(goals)} training goals, "
              f"{pct(share)} of them reachable-with-practice")
    print()

    summary: dict[str, Any] = {}
    for condition in CONDITIONS:
        condition_summary, lines = summarise_condition(world, condition, runs[condition], args)
        summary[condition] = condition_summary
        print("\n".join(lines))

    payload: dict[str, Any] = {
        "config": config_payload(world, args),
        "goal_space": goal_space_payload(world),
        "prediction": args.prediction,
        "runs": {
            condition: {
                arm: [
                    {"seed": run.seed, "curve": run.curve, "steps": run.steps,
                     "episodes": run.episodes, "episodes_per_region": run.episodes_per_region}
                    for run in runs[condition][arm]
                ]
                for arm in ARMS
            }
            for condition in CONDITIONS
        },
        "saturation_probe": {
            condition: summary[condition]["saturation_probe_rate"] for condition in CONDITIONS
        },
        "summary": summary,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
