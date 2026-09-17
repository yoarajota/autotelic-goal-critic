# Evidence ledger — Autotelic goal generation: generator + independent Goldilocks critic

Every claim in this repository resolves to an entry here. An entry without a
reproduction command is a note, not evidence, and fails the repository's own checks.

**Required in every entry:** a fenced command block, an `Environment:` line, a `Result:`
line, and a `Kind:` line (`benchmark | test | survey`). Headings must be exactly
`### E-###  —  <title>` so the tooling can parse them.

**Required for `Kind: benchmark`:** a `Data:` line naming the raw measurement data,
committed under `evidence-data/`, with its sha256 checksum:

```markdown
**Data:** evidence-data/E-012-final.json (sha256: <64 hex chars>)
```

One entry, one dataset; the `Result:` section is the human-readable summary of the
data, and the checksum is what makes the summary checkable.

IDs are never reused. Evidence that stops reproducing is marked `Status: broken` and the
readiness level that depended on it comes down.

---

### E-001 — Source survey: what the primary literature establishes about learning-progress goal selection

**Claim.** Establishes the mechanism, the operating conditions, the failure modes and the
incumbent recorded in `docs/01-theory.md`, and every published number quoted there. Supports the
TRL 1 and TRL 2 claims for the `core` component in `.sota/readiness.yaml`, and the
pre-registered margin in H-001 (`.sota/concept.yaml`).

**Environment:** host (Ubuntu 24.04, x86_64), Python 3.12.3, curl 8.x, network access to
`people.idsia.ch`, `www.pyoudeyer.com`, `arxiv.org`, `www.frontiersin.org` and
`pmc.ncbi.nlm.nih.gov`. No project dependencies: the ledger check below uses curl only.
Fetch date: 2026-09-16.

**Kind:** survey

```sh
# Every URL in the source ledger of docs/01-theory.md must resolve.
# POSIX sh only: the evidence runner executes this block with /bin/sh, which does not
# accept `set -o pipefail`.
urls=$(grep -oE 'https?://[^ )>]+' docs/01-theory.md | sort -u)
fail=0
for u in $urls; do
  code=$(curl -sSL -I -o /dev/null -w '%{http_code}' --max-time 30 -A 'evidence-check/1.0' "$u" || echo 000)
  printf '%s  %s\n' "$code" "$u"
  if [ "$code" != "200" ]; then fail=1; fi
done
echo "checked $(printf '%s\n' "$urls" | wc -l) URL(s)"
exit $fail
```

**Result:** 12 sources fetched, read, and recorded in `docs/01-theory.md`; all 12 URLs returned
HTTP 200 on the verification run. All 12 are `Access: full-text` (the requirement is ≥ 5
reachable with ≥ 3 full-text). Documents were fetched as PDF (extracted locally with pypdf) or as
HTML, and quoted numbers were read out of the extracted text by search, not recalled.

Three candidate identifiers were **recalled rather than looked up, resolved to unrelated
documents, and were discarded before entering the ledger**: arXiv:2202.13349 (recalled as the
unsupervised-RL benchmark) served "Influence of entropy changes on reactor period"; arXiv:2010.11961
(recalled as an unsupervised-RL methods study) served "Are quantum cryptographic security claims
vacuous?"; and `people.idsia.ch/~juergen/curious.html` returned HTTP 404. The correct identifiers
were located by title (arXiv API and the author's own publication page), fetched, and only then
used. This check is the reason the ledger has 12 sources and not 15.

Numbers read out of the sources, with the conditions the source reports them under:

| Quantity | Value as published | Condition it was published under |
| :--- | :--- | :--- |
| Active vs random goal-space selection, pickaxe space | p < 0.01 (Welch's t-test) | Robotic tool-use environment, 23 active runs vs 16 random runs |
| Active vs random goal-space selection, cart space | p = 0.09, no effect detected | Same environment; paper attributes this to environment stochasticity |
| Hand-written fixed curriculum vs active | not separable on either space tested | Same environment |
| Cart-space exploration coverage, median (Q1–Q3) | 5 (162–409) random vs 56 (360–886) active | 2D environment, 100 seeds |
| Seeds/runs per condition | 100 (2D), 20–42 (Minecraft), 16–23 (robotic) | Per environment |
| Competence self-evaluation cost | p_eval = 0.1 of episodes | CURIOUS, four-module robotic manipulation |
| Competence window | l = 300 episodes | CURIOUS |
| Exploration floor in selection | ε = 0.4 (CURIOUS), ε = 0.35 (IAC) | Reported per system |
| CURIOUS vs random module choice | significant on 10 trials, after an injected sensory perturbation | Not a matched-budget learning curve; the curriculum figure is a single run |
| Flat product-space goal (HER-equivalent) | learning curve stays flat | CURIOUS's environment: no goal in the full product space corresponds to a real situation |
| Tabular baseline on bit-flipping | fails for n > 40, hindsight relabelling solves it | HER's motivating experiment |
| Learning progress from Bellman errors | reported as failing to improve over random goal selection | Second-hand report; primary not read |

**Verifies:** exit-zero
**Verifies:** output-contains "checked 12 URL(s)"

**Status:** reproducing
**Supports:** H-001, `core` at TRL 2 (mechanism specified, application specified, baseline named),
the pre-registered margin in H-001
**Recorded:** 2026-09-16

---

### E-002 — Proof of concept: the critic shifts where the budget goes, and that does not buy competence

**Claim.** Establishes the P2 proof-of-concept measurement that bears on H-001, and records a
**negative signal**: at this scale the mechanism reallocates practice as designed but produces no
competence advantage over uniform random goal sampling, and the pre-registered margin is not met.
It also identifies, from its own data, the condition under which the mechanism's premise fails in
this domain — see the confound below, which the P5 design has to answer.

**Environment:** host (Ubuntu 24.04, x86_64), Python 3.13.13 via uv 0.12.15, standard library
only (no numpy, no GPU); single-process, sequential; deterministic environment and seeded RNG.

**Kind:** benchmark

**Data:** evidence-data/E-002-poc-runs.json (sha256: 68b06dba9188b3432cfadfe6a4a9fea246db6106f76c367a7bb1d89366908dfb)

```bash
uv run python poc/run_poc.py --budget 60000 --eval-every 5000 --seeds 0 1 2 3 4 --saturation-budget 200000 --out evidence-data/E-002-poc-runs.json
```

**Result:** Grid 21x21, horizon 12, start at the centre, 30 held-out reachable goals fixed before
training and never sampled. Two conditions: `distractor-rich` (all 441 cells: 5 trivial, 292
reachable, 144 impossible because farther than the horizon, leaving 262 reachable-with-practice
goals in the training pool of 411 once the held-out set is removed, so 63.7% of that pool is worth
practising) and `all-learnable` (262 training goals, all worth practising). Two arms
identical except for goal selection, 5 pinned seeds, 20 runs, matched budget of 60k environment
transitions per run, evaluation every 5k.

| Condition | Arm | Final held-out success (median, min, max) | Episodes on practice regions |
| :--- | :--- | :--- | :--- |
| distractor-rich | uniform | 96.7% (93.3%, 100.0%) | 63.9% |
| distractor-rich | critic | 96.7% (93.3%, 100.0%) | 71.0% |
| all-learnable | uniform | 96.7% (93.3%, 100.0%) | 100% |
| all-learnable | critic | 93.3% (90.0%, 100.0%) | 100% |

- **The critic arm reallocates practice as specified and the reallocation is visible:** in the
distractor-rich condition it spends 71.0% of episodes on regions where progress is possible,
against 63.9% for uniform sampling and 63.7% for a pool sampled uniformly (the wasted remainder
is trivial or unreachable goals).
- **The margin is not met.** Distractor-rich margin at the matched budget: **+0.0 pp** (predicted:
>= 20 pp). All-learnable margin: **-3.3 pp** (predicted: smaller or absent). The two readings
that were not pre-registered agree: transitions to reach the baseline's final competence in the
distractor-rich condition were 30,000 (critic) against 20,000 (uniform), and transitions to 90%
held-out success in the all-learnable condition were 25,000 (critic) against 15,000 (uniform).
Both conditions are ceiling-bound near 97%, so the primary margin had little headroom to show
itself at this budget — but the critic is not ahead on any reading, at any checkpoint, in either
condition.
- **A confound the run itself exposes.** The distractor-rich *uniform* arm, which spends about a
third of its episodes on trivial or unreachable goals, reaches its plateau earlier than the
all-learnable uniform arm at equal budget (96.7% against 86.7% at 20k transitions). Adding
unreachable goals to the goal set did not slow the baseline down; on these curves it appears to
have helped it. The value function is indexed by goal-relative offset, so an episode aimed at an
unreachable goal still trains the offset values that the reachable far goals need. If that reading
holds, the premise this concept rests on — that uniform sampling wastes budget on unlearnable
goals — is false for a learner that transfers across goals, and the mechanism has nothing to buy.
This is the single most important open question the PoC produced, and it is listed as such in
`docs/01-theory.md`; separating it from the mechanism's own effect is P5 work.
- **The critical function itself runs.** One command, exit 0, 20 runs, zero aborted runs, and a
re-run writes a byte-identical data file (same sha256), so the harness is deterministic. The
critic's fallback kept runs alive when every candidate was rejected, which is the behaviour S-002
requires and which `tests/test_goal_selection.py` will have to pin at P3.
- **Prediction compared with observation.** Predicted (P1, from the reported partial effect in the
IMGEP ablation and the no-distractor result): the critic ahead by >= 20 pp with distractors,
advantage smaller or absent without them. Observed: no advantage in either condition, and what
difference exists below the ceiling is negative in the control. The second half of the prediction
is consistent with the observation; the first half is contradicted.
- **Not a decisive test of H-001.** This is a P2 surrogate: one gridworld, an enumerable goal
space, a tabular learner with free cross-goal transfer, one budget range, no baseline tuning, and
a region parameterisation (distance rings) that is the only natural one here. It bounds what this
configuration shows, not what the mechanism is worth in the settings the sources used. What would
make it decisive is P5 as pre-registered.

**Verifies:** data-sha256
**Verifies:** computed-from evidence-data/E-002-poc-runs.json path=summary.distractor-rich.median_final.critic value=0.9667 tolerance=0.0001
**Verifies:** computed-from evidence-data/E-002-poc-runs.json path=summary.distractor-rich.median_final.uniform value=0.9667 tolerance=0.0001
**Verifies:** computed-from evidence-data/E-002-poc-runs.json path=summary.all-learnable.median_final.critic value=0.9333 tolerance=0.0001
**Verifies:** computed-from evidence-data/E-002-poc-runs.json path=summary.distractor-rich.episode_share_reachable_regions.critic value=0.7096 tolerance=0.0001
**Verifies:** repeat-identical --runs 2 evidence-data/E-002-poc-runs.json
**Verifies:** output-contains "critic margin at matched budget:  +0.0 pp"

**Status:** reproducing
**Supports:** H-001 (negative signal at proof-of-concept scale), `core` at TRL 3 (runnable
artefact, one command, exit 0, observed result compared with the analytical prediction)
**Recorded:** 2026-09-16

---

## Benchmark methodology

Pre-registered at P1; applies to every entry with `Kind: benchmark`. The numbers below are
fixed before any comparison is run, so that the outcome cannot be used to choose them.

- **What is measured:** held-out success rate over **reachable** goals, where the held-out goal
  set is fixed before training and never sampled during it. Success is the environment's verdict
  that the goal condition holds at the end of the allocated episode, not the learner's own
  estimate of success.
- **Arms:** (1) uniform random goal sampling with hindsight relabelling; (2) the same learner,
  relabelling and exploration floor, with generator + independent critic goal selection. One code
  path; the goal-selection policy is the only difference between arms, so that implementation
  drift cannot masquerade as an algorithmic effect.
- **Budget:** matched on **total environment transitions**, so any evaluation rollouts the critic
  performs are deducted from its own arm. The absolute budget is fixed at P2 by a timing probe,
  before any comparison is run, and is then written here.
- **Runs:** ≥ 5 seeds per arm per condition, seeds pinned in the repository. Reported as median
  and min/max across seeds; a single run is not a measurement.
- **Held constant:** gridworld layout, goal-space partition, reachable/unreachable classification,
  initial-state distribution, episode horizon, relabelling count, exploration floor, evaluation
  cadence, and evaluation goal set.
- **Baseline configuration:** hyperparameters shared by both arms are tuned once, on the baseline
  arm, before the critic arm exists in the comparison; the critic's own thresholds (minimum-sample
  count, competence window, triviality ceiling) are pre-declared and not tuned against the
  held-out result. Any tuning the critic needs that the baseline does not is reported as a cost.
- **Conditions:** primary = distractor-rich goal space (reachable + trivial + unreachable goals).
  Secondary = all goals reachable and none trivial, with the pre-registered prediction that the
  advantage is smaller or absent there. Reported separately; never pooled.
- **Known measurement bias:** the environment is deterministic and the goal space is enumerable, so
  the critic's competence estimate is cheaper and less noisy than in the continuous, stochastic
  environments the literature uses. That bias favours the critic arm, and is the reason a positive
  result here is not evidence of transfer to those environments.
