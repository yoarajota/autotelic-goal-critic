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
→ *verdict: untested* — the experiment has no runnable form yet, so the claim is stated and not
yet measured. It is falsifiable as written: an advantage of zero or less at a matched budget
falsifies it, and an advantage between zero and the margin counts as partial support, not a win.
The margin was fixed before any code exists (E-001).

## Baseline

Compared against **uniform random goal sampling with hindsight relabelling** (HER,
arXiv:1707.01495v3) because that is what goal-conditioned practice runs and what the
intrinsic-motivation literature itself compares against: one arm draws goals uniformly, the other
draws them from the critic, and nothing else differs. It is not a strawman — hindsight relabelling
is already an automatic curriculum, and the published random-selection condition is reported as
competitive wherever the goal space contains no distractors (E-001).

Reproduce the comparison: not yet available. The head-to-head run lands with the proof of concept;
until it exists, this repository contains a hypothesis and the source survey that shaped it, and no
measurement of the concept. See [E-001](docs/05-evidence.md#e-001) for what *is* established.

<!-- scorecard:start -->
<!-- Auto-generated. Do not hand-edit. -->
<!-- scorecard:end -->

## Try it

```bash
# setup — works from a clean checkout; requires uv (https://docs.astral.sh/uv/) and gitleaks
make setup

# the checks this repository holds itself to
make quality
make test

# the headline result in one command — lands with the proof of concept
```

No result command exists yet. What can be run today is the source ledger check recorded as E-001,
which verifies that every URL cited in `docs/01-theory.md` resolves.

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

Full ledger: [docs/05-evidence.md](docs/05-evidence.md).

## Limitations

- **Nothing about the concept has been measured.** The readiness scorecard below reports a
  literature-level claim only. Every comparative statement in this repository comes from the
  published sources, in their environments, at budgets three to four orders of magnitude larger
  than a tabular gridworld's — none of it is this repository's result.
- **The published evidence for the mechanism is mixed, and the incumbent is strong.** In the
  ablation that comes closest to this question, progress-based selection is reported ahead of
  random selection on one goal space and not on another, and a hand-written fixed curriculum is
  described as not separable from the progress-based condition (E-001). Uniform selection is
  reported as competitive where there are no distractors (E-001). A positive result here would be
  narrow; a negative result would be consistent with part of the literature.
- **The domain is chosen for cost, not for fidelity.** A discrete deterministic gridworld with an
  enumerable goal space is not the problem class that motivated the concept ("too large to
  enumerate"), and the critic's estimate is cheaper and less noisy there than in the continuous,
  stochastic environments the sources use. That bias favours the critic arm.
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

<!-- Dispositions of these entries: docs/03-log.md L-001. -->

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
