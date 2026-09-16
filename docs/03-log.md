# Working log — Autotelic goal generation: generator + independent Goldilocks critic

Append-only. **Never edit an existing entry**; add a new one that supersedes it. This is the
only artefact in the repository that records work *in progress*, and it is deliberately narrow.

Open entries are printed as handoff state to the next session, so this file is how one session
tells the next what was in flight. That is its primary job — write to it before you run out of
context, not after.

## What belongs here — and what does not

Most work-in-progress knowledge already has a home. Use the table before writing an entry:

| What you have | Where it goes |
| :--- | :--- |
| A measurement, even a disappointing one — it has a command and a result | `docs/05-evidence.md` as an `E-###` with the claim it refuted |
| A choice between real alternatives | `docs/adr/D-###` — the rejected options table exists for this |
| A bound on when the concept degrades | `README.md § Limitations` |
| A second concept worth its own repository | a Linear `sota-concept` issue |
| **No decision made and no reproducible command** — a surprise, a blind alley, an abandoned attempt | **here** |
| **Work half-finished right now** | **here, as `Disposition: open`** |

If it fits a row above this file, put it there. A log entry that should have been an ADR
weakens both.

Throwaway scripts and intermediate data are not log entries — those belong in a temp directory,
not the repository. This file records findings, not files.

## Entry format

Headings must be exactly `### L-###  —  YYYY-MM-DD  —  <short title>`, and every entry needs a
`Disposition:` line. Both are parsed by the gate checks.

| Disposition | Means |
| :--- | :--- |
| `open` | Still in flight. Printed by `next` as handoff state. **Blocks the phase gate.** |
| `dead-end` | Tried, did not work, deliberately not pursued. Terminal and legitimate. |
| `promoted: D-###` | Became an architecture decision. |
| `promoted: E-###` | Became evidence. |
| `promoted: README` | Became a stated limitation. |

Every entry must reach a terminal disposition before its phase gate passes. That is the rule
that stops this file becoming a pile — and unlike most promotion rules, it is checked.

---

### L-001 — 2026-09-16 — Recalled source identifiers resolved to unrelated papers

**Context:** assembling the source ledger for the theory pass, starting from a list of candidate
primaries (Schmidhuber 1991 and 2010, Oudeyer–Kaplan–Hafner 2007, the IMGEP paper, the autotelic
survey, HER) plus two works on unsupervised-RL baselines.

**Found:** three of the identifiers were written from memory as plausible arXiv IDs rather than
looked up, and two of them resolved to documents in unrelated fields — arXiv:2202.13349 served a
nuclear-reactor paper on entropy and reactor period, and arXiv:2010.11961 served a
quantum-cryptography paper — while a fourth URL for the 1991 curiosity paper returned HTTP 404.
Nothing about those IDs was obviously wrong: the numbers were in the right range and the
surrounding metadata looked plausible. The failure is only visible if the fetched document's own
title is read, which costs one command per source and would have been skipped had the ledger
been assumed correct. Every identifier was subsequently located by title (arXiv API, the author's
publication page) and checked against the document it served; a per-source URL check now lives in
E-001 so the check is repeatable rather than remembered.

**Disposition:** promoted: E-001

### L-002 — 2026-09-16 — The proof of concept produced a null, and the reason is in its own data

**Context:** building the P2 proof of concept for the selection mechanism — a 21x21 gridworld with
a horizon of 12, a goal space mixing 5 trivial, 292 reachable and 144 unreachable goals, a tabular
learner indexed by goal-relative offset with hindsight relabelling, and two arms differing only in
goal selection. The prediction from P1 was that the critic would be ahead by the pre-registered
20 percentage points with distractors present and level without them.

**Found:** no competence advantage in either condition (distractor-rich margin +0.0 pp, all-learnable
-3.3 pp over 5 seeds, E-002), and the critic arm slower on both time-to-competence readings. The
mechanism
itself worked: it moved 71.0% of episodes onto regions where progress was possible, against 63.9%
for uniform sampling. The reason the movement bought nothing is visible in the same run — the
*distractor-rich uniform* arm, which spends about a third of its episodes on trivial or unreachable
goals, reached its plateau earlier than the all-learnable uniform arm at equal budget (96.7% against
86.7% at 20k transitions). The learner's value function is indexed by goal minus position, so an
episode aimed at an unreachable goal still trains the offset values a reachable far goal needs. The
waste the mechanism exists to remove was not there, because practice transfers across goals. That
is a property of the instrument as much as of the mechanism: a learner with bounded transfer, which
is what the source settings have, would show a different number, and separating the two readings is
P5 work rather than something this PoC can settle.

The other thing worth recording is a reporting bug found before anything was written up: the first
version of the summary compared the critic's transitions-to-competence against *the end of the run*
rather than against the baseline's own transitions-to-the-same-competence, which turned a 1.5x
slowdown into an apparent 2x speedup. It was caught by reading the baseline's own curve instead of
the summary line. Any single number that flatters the mechanism in this repository should be read
against the curve it came from.

**Disposition:** promoted: E-002

