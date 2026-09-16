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

