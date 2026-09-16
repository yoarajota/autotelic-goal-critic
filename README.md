# Autotelic goal generation: generator + independent Goldilocks critic

> Does generator + Goldilocks critic produce measurably more learning progress than uniform random goal sampling at matched interaction budget?

**Concept** `C-006` · **archetype** `implementation`.

A goal-conditioned learner that has to decide for itself what to practise next. A **generator**
proposes candidate goals; an **independent critic** rates each one by how much learning progress
it is likely to produce, estimated from the achievement outcomes the environment reported — not
from the learner's own value estimates — and selection rejects the two ends of the difficulty
range: goals already mastered and goals that cannot be reached. The question is whether that
rating buys anything over drawing goals uniformly. The concept lives in a discrete gridworld whose
goal space deliberately mixes reachable, trivially satisfied and unreachable goals, because the
reported advantage of progress-based selection is conditional on distractors being present.

## Claim

**H-001** — Under a deterministic discrete gridworld whose goal space mixes reachable, trivially
satisfied and unreachable goals, with a tabular goal-conditioned learner and hindsight relabelling
shared by both arms, a pinned seed set and a matched total environment-transition budget,
generator + independent Goldilocks critic goal selection reaches a held-out success rate over
reachable goals at least 20 percentage points higher than uniform random goal sampling at the same
budget; at the cost of the critic's competence estimation, which needs recorded outcome samples
before any goal can be rated, adds a minimum-sample threshold below which a goal is unrated rather
than rejected, and adds per-candidate scoring compute to every selection step.
→ *verdict: untested* — the pre-registered comparison has not run. A proof-of-concept surrogate has,
and **it does not support the claim**: over 5 pinned seeds at a matched 60k-transition budget, the
critic arm ended level with uniform sampling in the distractor-rich condition (+0.0 pp) and behind
it in the all-learnable control (-3.3 pp), and it was slower on both time-to-competence readings
(E-002). The margin was fixed before any code exists (E-001). The proof of concept is a throwaway
instrument — one small domain, an untuned baseline — so it bounds what that configuration shows
rather than deciding the hypothesis; but it is a negative signal, and it identified the condition
that P5 has to answer: a learner that transfers freely across goals makes practice on any goal
partly useful for every goal, which removes the waste the mechanism exists to remove (E-002).

## Baseline

Compared against **uniform random goal sampling with hindsight relabelling** (HER,
arXiv:1707.01495v3) because that is what goal-conditioned practice runs and what the
intrinsic-motivation literature itself compares against: one arm draws goals uniformly, the other
draws them from the critic, and nothing else differs. It is not a strawman — hindsight relabelling
is already an automatic curriculum, and the published random-selection condition is reported as
competitive wherever the goal space contains no distractors (E-001).

Reproduce the comparison: `uv run python poc/run_poc.py --budget 60000 --eval-every 5000 --seeds 0 1 2 3 4`,
which writes the raw curve data behind [E-002](docs/05-evidence.md#e-002) — a proof of concept, not the
pre-registered benchmark, which lands at P5 and is the only run that can decide H-001.

<!-- scorecard:start -->

### Readiness scorecard

_Generated from `.sota/` — do not hand-edit._

| Measure | Value | Meaning |
| :--- | :--- | :--- |
| **TRL** | **3** | Critical function proof of concept |
| **SRL**  | **4** | Performance specifications and constraints defined and allocated — seams only |
| Composite SRL | 0.333 | aggregate over all components (0–1) |
| Weakest component | core (0.3333) | lowest component-level SRL |
| Weakest seam | n/a | lowest-scoring integration pair |
| Suitable for | not assessed | audience for which this result is ready |

| Component | Role | TRL | Component SRL |
| :--- | :--- | :-: | :-: |
| `core` | concept | 3 | 0.333 |

| Scenario | Characteristic | Priority | Status |
| :--- | :--- | :--- | :--- |
| S-001 | performance-efficiency | high | unverified |
| S-002 | reliability | high | unverified |
| S-003 | maintainability | medium | unverified |

<!-- scorecard:end -->

## Try it

```bash
# setup — works from a clean checkout; requires uv (https://docs.astral.sh/uv/) and gitleaks
make setup

# the checks this repository holds itself to
make quality
make test

# the proof of concept: both arms, both conditions, 5 seeds, one command (~6 s)
make poc
```

`make poc` prints the held-out success curves and writes `evidence-data/E-002-poc-runs.json`.
A re-run produces a byte-identical file, so the harness is deterministic.

## How it works

Competence on a goal region is the mean achievement rate over a sliding window of recent
outcomes; learning progress is the **absolute** change in competence between windows, so a
skill that is decaying is selected back into attention rather than filtered out. The critic scores
candidate regions by that quantity and rejects the trivial and the unreachable ends; candidates
with too few recorded outcomes are treated as *unrated*, not impossible, and are explored. Which
goal to practise is then chosen from the scores with a non-zero random floor, since pure
progress-greedy selection is not what the reported systems do. See
[docs/01-theory.md](docs/01-theory.md) for the sourced version, including the conditions the
mechanism requires and the eight failure modes that become tests, and
[docs/04-tradeoffs.md](docs/04-tradeoffs.md) for the architecture (written at integration).

## Evidence

| ID | Claim | Command | Result |
| :--- | :--- | :--- | :--- |
| E-001 | The mechanism, its operating conditions, its failure modes, the incumbent and every published number quoted in this repository come from 12 primary sources, all read and all resolved | `docs/05-evidence.md → E-001` | 12 sources at `Access: full-text`, all 12 URLs HTTP 200; three recalled identifiers that resolved to unrelated papers were discarded before use |
| E-002 | The proof of concept runs the critical function end to end, and the mechanism does not buy competence in it | `make poc` | 20 runs, 5 seeds per arm, both conditions; critic margin +0.0 pp (distractor-rich) and -3.3 pp (all-learnable); byte-identical data on re-run |

Full ledger: [docs/05-evidence.md](docs/05-evidence.md).

## Limitations

- **No measurement supports the concept.** The one experiment in this repository fails to support
  it: at a matched budget the critic arm was level with uniform sampling where the mechanism should
  have its advantage and behind it in the control, over 5 seeds (E-002). Every other comparative
  statement here comes from the published sources, in their environments, at budgets three to four
  orders of magnitude larger than this gridworld's — none of it is this repository's result.
- **The mechanism's premise failed in the configuration that was measured.** Uniform sampling is
  supposed to waste budget on goals that cannot be learned. In the proof of concept it did not: the
  arm spending a third of its episodes on trivial or unreachable goals reached its plateau at least
  as early as the arm practising only learnable goals, because the learner shares value estimates
  across goals and therefore learns something useful from any episode (E-002). If that reading holds
  in the settings the sources used, the second component is unpaid complexity there too (R5).
- **The published evidence for the mechanism is mixed, and the incumbent is strong.** In the
  ablation that comes closest to this question, progress-based selection is reported ahead of
  random selection on one goal space and not on another, and a hand-written fixed curriculum is
  described as not separable from the progress-based condition (E-001). Uniform selection is
  reported as competitive where there are no distractors (E-001). A positive result here would be
  narrow; a negative result would be consistent with part of the literature.
- **The domain is chosen for cost, not for fidelity.** A discrete deterministic gridworld with an
  enumerable goal space is not the problem class that motivated the concept ("too large to
  enumerate"), and the critic's competence estimate is drawn from a setting without the stochastic
  reachability the sources report as the trap for difficulty-based selection (E-001). That
  difference favours the critic arm, which is why a positive result here would not transfer to the
  continuous, stochastic environments those sources use.
- **The critic's thresholds are choices, not results.** The minimum-sample count that separates
  "unrated" from "unreachable", the window length, and the triviality ceiling have no reported
  sensitivity analysis (E-001); if the effect exists only in a narrow band of them, the mechanism
  costs more than its papers price.
- **The two-part structure is this repository's design, not a tested finding.** Whether an
  independent raters buys anything over a single network that both proposes and rates goals is not
  measured here, and no source in the ledger settles it.
- **The disengagement structure is borrowed across fields.** The pairing of dropping an
  unattainable goal with committing to a new one is a design analogy from human self-regulation
  research, which measures those two capacities in people; no source establishes the transfer.

### What we tried that didn't work

- **A recalled source list.** Three identifiers written from memory as plausible arXiv IDs
  resolved to a nuclear-reactor physics paper and a quantum-cryptography paper, and a fourth URL
  returned HTTP 404. Every identifier is now located by title and verified against the document it
  serves before it can enter the ledger; the discarded ones are recorded in E-001 so the failure
  stays visible.
- **A quality gate that cannot fail.** The idiomatic complexity report (`radon cc -n C`) prints a
  rank-C block and still exits 0, so the declared cyclomatic threshold was decorative. The runner
  now enforces the thresholds in `tools/complexity_gate.py` and a test fails if the enforced and
  declared values drift apart.

<!-- The source-identifier failure is log entry L-001; the gate that could not fail is recorded as
     friction F-003 in .sota/feedback.yaml. Neither belongs in this list until it is promoted to a
     stated limitation, which is what this section is. -->

## Documents

| Document | Contents |
| :--- | :--- |
| [docs/01-theory.md](docs/01-theory.md) | What the literature establishes, with the `SRC-###` source ledger. |
| [docs/03-log.md](docs/03-log.md) | Append-only working log: what was tried, including what failed. |
| [docs/04-tradeoffs.md](docs/04-tradeoffs.md) | ATAM-lite: drivers, scenarios, sensitivity and tradeoff points, risks. |
| [docs/05-evidence.md](docs/05-evidence.md) | Every claim, its command, environment, and observed result. |
| [docs/adr/](docs/adr/) | Decisions and the options rejected. |
| [.sota/](.sota/) | Machine-readable readiness and quality data. |

## Setup requirements

`make setup` installs the toolchain into a project-local virtual environment with `uv`; nothing
is installed globally. `make quality` additionally requires **gitleaks** on the host (it is a Go
binary, so it is not covered by `uv sync`); the quality runner fails loudly if it is missing
rather than skipping the secret scan.

## License

MIT — see [LICENSE](LICENSE).
