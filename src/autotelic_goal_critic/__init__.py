"""Goal generator and independent Goldilocks critic for a goal-conditioned learner.

The mechanism is specified in `docs/01-theory.md`: a generator proposes goals, an independent
critic rates each candidate by absolute learning progress estimated from recorded environment
outcomes, and selection rejects goals that are already mastered or out of reach. Nothing is
implemented here yet — the executable form of the mechanism lands as the proof of concept in
`poc/`, and the components it is built from land in this package.
"""
