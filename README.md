# Autotelic goal generation: generator + independent Goldilocks critic

> Does generator + Goldilocks critic produce measurably more learning progress than uniform random goal sampling at matched interaction budget?

**Concept** `C-006` · **archetype** `implementation` · **status** `falsified`

**No.** The one measurement in this repository found no advantage, and the run that failed to find
one also explains why in this configuration there was nothing to find. The concept is published as
a probe: hypothesis falsified, evidence in [E-002](docs/05-evidence.md#e-002), stopped at TRL 3.

## What the concept is

A goal-conditioned learner that has to decide for itself what to practise next. A **generator**
proposes candidate goals; an **independent critic** rates each one by how much learning progress it
is likely to produce, estimated from the achievement outcomes the environment reported rather than
from the learner's own value estimates; selection then rejects the two ends of the difficulty
range, goals already mastered and goals that cannot be reached. The appeal of the idea is that
uniform sampling is supposed to waste budget on goals that cannot be learned. The question was
whether the rating pays for itself at the same number of environment interactions.

## Claim

**H-001** — Under a deterministic discrete gridworld whose goal space mixes reachable, trivially
satisfied and unreachable goals, with a tabular goal-conditioned learner and hindsight relabelling
shared by both arms, a pinned seed set and a matched total environment-transition budget,
generator + independent Goldilocks critic goal selection reaches a held-out success rate over
reachable goals at least 20 percentage points higher than uniform random goal sampling at the same
budget; at the cost of the critic's competence estimation, which needs recorded outcome samples
before any goal can be rated, adds a minimum-sample threshold below which a goal is unrated rather
than rejected, and adds per-candidate scoring compute to every selection step.

→ ***verdict: falsified*** by [E-002](docs/05-evidence.md#e-002), on the condition written into the
selection screen before any code existed: at a matched budget over 5 pinned seeds, a median
advantage of zero or less in held-out success over reachable goals. Measured: **+0.0 percentage
points** with distractors present, **-3.3 points** in the all-learnable control, and the critic
arm behind the baseline on both time-to-competence readings. The pre-registered margin was 20
points; the effect was not merely smaller, it was absent.

## What the measurement showed

The mechanism worked. It moved **71.0%** of episodes onto regions where progress was possible,
against **63.9%** for uniform sampling — the reallocation the design calls for is plainly visible
in the run's own data (E-002). It bought no competence.

The reason is in the same data, and it attacks the premise rather than the implementation. The
*distractor-rich uniform* arm, which spends about a third of its episodes on trivial or unreachable
goals, reached its plateau at least as early as the all-learnable arm did at equal budget (96.7%
against 86.7% at 20k transitions, E-002). The learner's value function is indexed by goal minus
position, so an episode aimed at an unreachable goal still trains the values that a reachable far
goal needs. **Where a learner transfers across goals, practice on an unlearnable goal is not
waste** — and the waste this mechanism exists to remove was therefore not there to remove.

That is the useful result of this repository. It is a bound on an argument that is usually stated
without one: the case for learning-progress goal selection assumes practice is goal-specific, and
that assumption needs testing before the second component is paid for (R5).

Readiness, scenario status and audience for this result: [docs/scorecard.md](docs/scorecard.md) — machine-generated.

## Try it

```bash
# setup — works from a clean checkout; requires uv (https://docs.astral.sh/uv/) and gitleaks
make setup

# the checks this repository holds itself to
make quality
make test

# the whole comparison: both arms, both conditions, 5 seeds, one command (~6 s)
make poc
```

`make poc` prints the held-out success curves for all four arm/condition pairs and writes
`evidence-data/E-002-poc-runs.json`. A re-run produces a byte-identical file, so the harness is
deterministic; the summary in E-002 is checkable against the raw curves it came from.

## How it works

Competence on a goal-space region is the mean achievement rate over a sliding window of recent
outcomes; learning progress is the **absolute** change in competence between consecutive windows,
so a skill that is decaying is selected back into attention instead of being filtered out. The
critic scores the region, rejects the trivial and the unreachable ends, treats regions with too few
recorded outcomes as *unrated* rather than impossible, and the choice among proposals keeps a
non-zero random floor — pure progress-greedy selection is not what any reported system does.
[`docs/01-theory.md`](docs/01-theory.md) has the sourced version, the conditions the mechanism
requires (including the one this run refined), and the eight failure modes; the implementation is
[poc/](poc/) — a gridworld, a tabular learner indexed by goal-relative offset, and the two
selection policies behind one interface.

## Evidence

What each claim was checked against, and when it was last re-verified:
[docs/verification.md](docs/verification.md) — machine-generated by `make verify`, which executes
every entry's declared checks and recomputes the headline numbers from the committed data.

Full ledger, with the commands and the raw results: [docs/05-evidence.md](docs/05-evidence.md).

## Limitations

**Where the incumbent wins.** Everywhere that was measured. Uniform random goal sampling with
hindsight relabelling (HER, arXiv:1707.01495v3) matched the critic arm in the distractor-rich
condition (+0.0 pp) and was ahead of it in the all-learnable control (-3.3 pp) at a matched budget
over 5 seeds, and on the timing readings it was never the critic that clearly gained: in the
distractor-rich condition the baseline reached its own plateau in 20k transitions against the
critic's 30k, and in the control the baseline reached 90% held-out success in 15k against the
critic's 25k, with the one reading that does favour the critic (35k against 40k to the baseline's
plateau level) being the same quantity read at a threshold the curves had already stopped moving
around (E-002). A competent engineer loses nothing
by using the incumbent here — that is the substitution answer, obtained by measurement rather than
by architectural review, because no ATAM pass and no adversarial review were run (G4 is waived for
this probe).

**What is untested.** Everything that would make the falsification interesting rather than merely
local:

- **Whether the null is the mechanism's or the instrument's.** The learner in the proof of concept
  transfers freely across goals, which is precisely the condition the run identified as removing
  the waste the mechanism exists to remove. A learner with bounded cross-goal transfer — limited
  capacity, or a goal representation the agent must acquire, as the settings in the sources have —
  was never tried (E-002, and open question 8 in `docs/01-theory.md`).
- **The published effect sizes.** The IMGEP ablation reports progress-based selection ahead on one
  goal space and not another, and a hand-written curriculum not separable from the active condition
  (E-001). Nothing here reproduces or refutes those numbers; this repository measured a different
  and much smaller configuration.
- **Threshold sensitivity.** The window, the minimum-sample count and the triviality ceiling were
  fixed, not tuned, and no source reports a sensitivity analysis for any of them (E-001). Whether
  the effect exists only in a narrow band of these values is unknown.
- **Whether the critic's independence matters at all** — the justification for having two
  components instead of one. It is filed as a separate candidate concept rather than measured here.
- **Non-enumerable goal spaces.** The problem class that motivated the concept was a goal space too
  large to enumerate; the proof of concept enumerates its goal space by construction, so it cannot
  speak to the scale that made the question interesting.

**What would move it up a level.** Not more of the same run. TRL 4 needs components integrated with
each other, an explicit public interface, conformance and failure-mode tests, and a green ISO 5055
gate — the artefacts waived here — and TRL 5 needs a relevant environment. Re-entering at P3 would
mean clearing those waivers; the credible version of that work also swaps in a learner whose
practice is goal-specific, since otherwise it re-measures the finding above.

### What we tried that didn't work

- **The mechanism, in the only configuration it was tried in.** Detailed above; the entry that
  matters is E-002.
- **A recalled source list.** Three identifiers written from memory as plausible arXiv IDs resolved
  to a nuclear-reactor physics paper and a quantum-cryptography paper, and a fourth URL returned
  HTTP 404. Every identifier is now located by title and checked against the document it serves
  before it can enter the ledger (`docs/03-log.md` L-001, E-001).
- **A quality gate that could not fail.** The idiomatic complexity report (`radon cc -n C`) prints a
  rank-C block and still exits 0, so the declared cyclomatic threshold was decorative. The runner
  now enforces the thresholds in `tools/complexity_gate.py`, and a test fails if the enforced and
  declared values drift apart.
- **A summary line that flattered the mechanism.** The first version of the comparison summary
  measured the critic's transitions-to-competence against the end of the run rather than against the
  baseline's own time to the same competence, turning a slowdown into an apparent speedup. It was
  caught by reading the baseline's curve instead of the summary; the corrected reading is what E-002
  reports (`docs/03-log.md` L-002).

## Documents

| Document | Contents |
| :--- | :--- |
| [docs/01-theory.md](docs/01-theory.md) | What the literature establishes, with the `SRC-###` source ledger. |
| [docs/03-log.md](docs/03-log.md) | Append-only working log: what was tried, including what failed. |
| [docs/04-tradeoffs.md](docs/04-tradeoffs.md) | ATAM-lite: not run — gate waived for this probe; the file still holds its template. |
| [docs/05-evidence.md](docs/05-evidence.md) | Every claim, its command, environment, and observed result. |
| [docs/adr/](docs/adr/) | Decisions and the options rejected: not yet written — gate waived for this probe. |
| [.sota/](.sota/) | Machine-readable readiness and quality data. |

## Setup requirements

`make setup` installs the toolchain into a project-local virtual environment with `uv`; nothing is
installed globally. `make quality` additionally requires **gitleaks** on the host (it is a Go
binary, so it is not covered by `uv sync`); the quality runner fails loudly if it is missing rather
than skipping the secret scan.

## License

MIT — see [LICENSE](LICENSE).
