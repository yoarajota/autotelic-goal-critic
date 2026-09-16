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

```bash
# Every URL in the source ledger of docs/01-theory.md must resolve. Exits non-zero if any does not.
set -euo pipefail
urls=$(grep -oE 'https?://[^ )>]+' docs/01-theory.md | sort -u | grep -vE 'conventionalcommits|creativecommons')
fail=0
for u in $urls; do
  code=$(curl -sSL -I -o /dev/null -w '%{http_code}' --max-time 30 -A 'evidence-check/1.0' "$u" || echo 000)
  printf '%s  %s\n' "$code" "$u"
  [ "$code" = "200" ] || fail=1
done
echo "checked $(echo "$urls" | wc -l) URL(s)"
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

**Status:** reproducing
**Supports:** H-001, `core` at TRL 2 (mechanism specified, application specified, baseline named),
the pre-registered margin in H-001
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
