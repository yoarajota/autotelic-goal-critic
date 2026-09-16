# Tradeoffs — Autotelic goal generation: generator + independent Goldilocks critic

## ATAM-lite was not run

This pass belongs to G4, and G4 is waived for this repository: the concept stopped at a proof of
concept, published as a probe. The utility tree in [.sota/quality-gates.yaml](../.sota/quality-gates.yaml)
therefore still holds three scenarios with status `unverified`, and there are no sensitivity points,
no tradeoff points and no risk register. That absence is a limitation of this repository, not an
implied clean bill of health, and it is stated in `README.md § Limitations`.

What the architecture analysis would have examined, had it run, is recorded here so the next
person does not have to reconstruct it from the code:

- **The tradeoff the concept actually makes.** The critic buys a reallocation of practice — 71.0% of
  episodes onto regions where progress is possible, against 63.9% for uniform sampling — and pays
  for it with three thresholds that must be chosen before it can rate anything, plus per-candidate
  scoring compute on every selection step. The measurement says the reallocation did not produce
  competence (E-002 in `docs/05-evidence.md`).
- **The sensitive parameters** are the competence window, the minimum-sample count that separates
  "unrated" from "impossible", and the triviality ceiling. No source in the ledger reports a
  sensitivity analysis for any of them (E-001), and the proof of concept fixed rather than tuned
  them, so the mechanism's operating band is unknown.
- **The risk that mattered in practice** was not a seam between components — there are two, and the
  proof of concept exercises both through one interface — but the assumption underneath the whole
  question: that practice on an unlearnable goal is wasted. The run found that for a learner which
  transfers across goals it is not, which is why the second component could not pay for itself in
  that configuration (E-002, and the condition recorded in `docs/01-theory.md`).

Re-entering at P3 means clearing the waiver `not_applicable: [G3, G4, G5]` in
`.sota/readiness.yaml` and supplying the artefacts those gates require: an explicit public
interface, conformance and failure-mode tests, and a green ISO 5055 gate.
