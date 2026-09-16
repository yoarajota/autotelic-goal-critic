# Theory — Autotelic goal generation: generator + independent Goldilocks critic

Written at P1. Establishes what is already known, from primary sources only. Every source in
the ledger at the bottom was fetched and read in full (or in the relevant sections) during this
pass; the numbers quoted below were read out of those documents, not recalled. Where a claim
reaches this document only through another paper's report of it, that is said explicitly and the
work lands in § Open questions.

## The mechanism

The claim under test is narrow: **the choice of which goal to practise next buys learning
progress, and an explicit generator/critic pair is what makes that choice**, rather than sampling
goals uniformly. This section states the mechanism precisely enough to implement, then the
criterion the critic applies.

**Setting.** A goal-conditioned learner interacts with an environment and receives, for each
episode, a goal `g` drawn from a goal space `G`. Achievement is decided by the environment:
`R_g(s) = 1` iff the state satisfies the goal's condition. A goal-conditioned policy `π(a | s, g)`
is trained on the transitions collected, and hindsight relabelling turns states reached during
an episode into additional goals for that same episode — so every episode yields outcome samples
for more than the goal it was launched with (E-001).

**Competence and learning progress.** Competence on a goal or goal region `R ⊆ G` is the mean
achievement rate over a sliding window of the most recent `l` outcomes, `C(R)`. Learning
progress is the change in that competence across windows,

```
LP(R) = |C(R; window n) − C(R; window n−1)|
```

The absolute value is deliberate and is what the sources use: a negative change is a real signal
(a skill is decaying, or a perturbation moved the goal) and must be selected back into attention,
not filtered out. In the multi-goal formulation this is written `LP_M = dC_M / dt` with competence
the probability of success (E-001).

**The criterion.** Schmidhuber's formal theory makes interestingness the *progress of the
observer's compression*, not surprise or novelty as such: data that is arbitrary and data that
is fully predictable both fail to be interesting, because neither admits further compression
progress — "Neither the arbitrary nor the fully predictable is truly novel or surprising"
(E-001). Oudeyer, Kaplan and Hafner operationalise the same criterion for a robot as maximising
learning progress, which drives it toward situations "which are neither too predictable nor too
unpredictable" (E-001). The developmental-psychology name for a preference for intermediate
difficulty is the Goldilocks effect, measured as infants looking away most from sequences whose
complexity was very low or very high (E-001).

The operational form of the criterion, which is what this repository tests, is therefore: a
candidate goal is worth practising when its recent competence is **partially** acquired — above
zero (so the goal is evidently reachable) and below mastery (so there is something left to
learn). The three rejections the criterion implies are: trivial goals (competence at the ceiling),
verifiably impossible goals (competence at zero over enough recorded outcomes), and — the case the
sources single out — goals that are achieved *by chance* and therefore look like intermediate
difficulty while carrying no progress (E-001).

**Two-part structure.** The pair under test is:

- a **generator** that proposes candidate goals (in the sources, by sampling a goal-space region
  or module weighted by learning progress, or by a learned proposal distribution); and
- an **independent critic** that rates each candidate by absolute learning progress estimated from
  **recorded outcomes**, and selects among them with an exploration mixture.

"Independent" is a structural claim with a testable meaning: the critic's rating function does not
read the parameters the learner is optimising. It reads the achievement outcomes the environment
produced (success/failure per goal). The sources do this explicitly — an autotelic agent "is not
externally provided its true competence or LP, it needs to approximate them", and it approximates
them from dedicated self-evaluation episodes whose success/failure results are queued per module,
separately from the Q-value network being trained (E-001). A rating derived instead from the
learner's own value estimates is produced by the function whose improvement is being measured, and
nothing stops it from rating a goal high because it has mis-estimated it high.

**Selection rule.** Scores over regions with enough outcomes, plus a minimum-sample rule: a goal
with fewer than `n_min` recorded outcomes is *unrated*, not *impossible*, and is explored. Without
that rule the critic cannot distinguish "hard" from "not yet tried", which is the distinction the
whole mechanism depends on. Ties are broken toward the candidate with higher estimated
controllability (empowerment — the mutual information between the agent's actions and future
states (E-001)), which prefers goals the agent can actually influence over goals that move for
reasons of their own. Neither the exploration mixture nor the tie-break is decoration: both
reported LP-based systems mix in random selection rather than following LP greedily (E-001), and no
source reports pure LP selection.

**Termination and re-engagement.** A critic that only abandons goals stalls: the plateau case is
exactly that all remaining goals have `LP ≈ 0`. The human self-regulation literature used for this
design separates two capacities that are measured independently — disengaging from an unattainable
goal, and re-engaging with a new one — and finds different correlates for each (E-001). The
mechanism here is the same shape: rejection of a goal must be paired with the generation of a
replacement, or the candidate pool empties. This is a design analogy borrowed across fields; no
source in the ledger establishes that the transfer to an artificial agent holds, and it is listed
as an open question.

## Conditions under which it holds

Each of these is a condition on the claim, not a caveat on the code. The pre-registered experiment
in § Hypothesis manipulates condition 1 directly.

1. **The goal space must contain distractors.** The reported advantage of learning-progress
   selection over random goal-space selection is conditional. The IMGEP paper's own ablation
   between active model babbling (learning-progress goal-space choice) and random model babbling
   (uniform goal-space choice) reports the random condition as competitive except in the presence
   of distracting goal spaces: random model babbling "can perform surprisingly well, especially
   when all goal spaces are relevant, i.e. when there are no distractors" (E-001). A world in which
   every goal is learnable is therefore a world in which the critic has little to buy, and the
   experiment must contain trivial and unreachable goals for the mechanism to have a chance of
   showing an effect at all.

   **Refined by measurement (E-002).** The condition above is necessary but not sufficient: the
algorithmic premise — that uniform sampling *wastes* budget on unlearnable goals — also requires
that practice be goal-specific. In the proof of concept the distractor-rich uniform arm, which
spent roughly a third of its episodes on trivial or unreachable goals, reached its plateau at
least as early as the arm practising only reachable goals at the same budget (E-002). An episode
aimed at an unreachable goal still trains the offset values a reachable far goal needs, so
nothing was wasted. Where a learner transfers freely across goals, the waste the mechanism exists
to remove is not there to remove — which is the sharpest bound this repository has on the claim.

2. **Achievement must be judged outside the learner.** The critic's signal is the environment's
   verdict. If the rating is derived from the same estimates the learner is improving, the
   measurement is self-confirming and the mechanism degenerates into optimism.

3. **The competence estimate must be paid for, out of the budget being compared.** CURIOUS spends
   `p_eval = 0.1` of its episodes on noise-free self-evaluation rollouts, i.e. a tenth of the
   interaction budget is consumed by the rating apparatus rather than by the policy (E-001). Any
   comparison at matched budget must therefore state whether the critic's estimation cost is
   deducted from the learner's budget or added on top; the first is the honest reading of "matched"
   and is what this repository pre-registers.

4. **The environment must be stationary enough for a windowed estimate to mean something.** Both
   reported failure modes below depend on this: under drift or stochastic reachability, an
   increase in measured competence need not correspond to anything the agent learned (E-001).

5. **A learnable zone must exist and must be reachable from current competence.** The criterion is
   silent when all goals are already mastered or all are impossible: progress is zero everywhere
   (E-001). Cases where "some goals might be reachable only after the agent mastered more basic
   skills" are the interesting ones, because they require the criterion to prefer the stepping
   stone (E-001).

6. **The exploration mixture must be non-zero.** The reported systems mix randomness into
   selection — `ε = 0.35` in the IAC robot experiments (E-001) and `ε = 0.4` in CURIOUS (E-001) —
   so the honest form of the claim is about LP-weighted selection *with* a random floor, not pure
   LP selection. The baseline shares the same floor in this repository's experiment.

## Known failure modes

Each row becomes a property or edge test at component level; the trigger is the condition that
makes it appear.

| Failure mode | Trigger condition | Source |
| :--- | :--- | :--- |
| **Self-confirmed rating.** The critic rates a goal by the same estimates the learner optimises, so a mis-estimated goal is rated high because it is mis-estimated high. | Rating function reads the learner's value/competence estimates instead of environment outcomes. | (E-001) |
| **Chance-achievement trap (aleatoric difficulty mistaken for learnable difficulty).** Goals that are sometimes reached by chance are scored as intermediate difficulty and attract attention, although no progress is available on them. The sources name this directly and recommend estimating medium-term progress to separate it from newly-learned competence. | Stochastic environment, or goals reachable only by accident. | (E-001) |
| **No-distractor null.** The critic's advantage disappears when every goal is learnable; random selection is then reported to be competitive. | Environment with no trivial and no unreachable goals. | (E-001) |
| **Rating overhead.** Competence estimation consumes interaction budget (a tenth of episodes in CURIOUS), so a matched-budget comparison that ignores it flatters the critic. | Dedicated self-evaluation rollouts; or scoring that requires environment interaction. | (E-001) |
| **Catastrophic forgetting under a shifting goal distribution.** Narrowing practice to a high-progress region decays competence on regions left behind; the absolute value of LP is the reported mitigation, and the reported ablation is a perturbation-recovery test rather than a learning curve. | Long training concentrated on a subset of goals; or a change in the body/sensors. | (E-001) |
| **Plateau (boredom).** Once every reachable goal is mastered, learning progress is zero everywhere and the criterion has no preference left. Schmidhuber's formulation makes this inevitable by construction: after the pattern is learned it is no longer interesting, so the drive must be pointed at new material rather than turned up. | Fully mastered reachable goal set, no new goals entering. | (E-001) |
| **Disengagement without re-engagement.** A rule that drops goals with zero progress but has no replacement generator empties the candidate pool rather than redirecting it. | Rejection implemented without a paired proposal step. | (E-001) |
| **Mistaking "not yet tried" for "impossible".** With too few samples per goal, an unrated goal is rejected as unreachable, and the critic prunes the frontier it was supposed to find. | `n_min` too small, or no unrated state distinct from zero competence. | (E-001) |

The literature's own record on whether the mechanism beats the baseline is mixed and is worth
stating in full, because it is the reason this repository measures rather than assumes:

- The IMGEP ablation reports active model babbling ahead of random model babbling on the pickaxe
  goal space (Welch's t-test, p < 0.01) but **not** on the cart space (p = 0.09), and a
  hand-written fixed curriculum was not separable from the active condition on either space
  (E-001). Exploration-coverage medians in the same paper vary by goal space from near-parity to
  roughly an order of magnitude apart across conditions (E-001).
- An earlier attempt to derive learning progress from Bellman errors is reported by the CURIOUS
  paper as failing to beat random goal selection (E-001). That primary was not read for this pass
  and is listed as an open question.
- CURIOUS's own comparison of LP-based module selection against random module selection is
  reported over 10 trials and is significant for *recovery after an injected sensory perturbation*;
  its learning-curve demonstration of the curriculum is a single run (E-001). Both of those are
  weaker than a matched-budget learning-curve comparison over seeds.
- A fixed, hand-designed curriculum was not separable from the active condition in the IMGEP
  comparison (E-001), which is the result that most directly threatens the incumbent's criticism:
  if hand-staging is as good as the critic, the critic's complexity is unpaid.

## The incumbent

**Baseline: uniform random goal sampling with hindsight relabelling** — the HER construction of
Andrychowicz et al. (arXiv:1707.01495v3), goal states sampled uniformly from the task's goal
distribution and achieved states relabelled as goals per episode (E-001).

This is the honest incumbent for three reasons, and the choice is deliberately not a strawman:

1. **It is what the field actually runs.** In UVFA, HER and UNICORN "the next goal to target is
   selected at random" (E-001). Hindsight relabelling is itself an automatic curriculum: an
   episode that fails its intended goal still supplies training signal for the goals it did reach,
   which is a large part of why the method works at all. The baseline is not "no curriculum".
2. **It is strong.** The IMGEP ablation reports uniform goal-space selection as competitive
   wherever there are no distractors (E-001), and the CURIOUS paper takes the efficiency of
   hindsight relabelling as already established rather than re-testing it (E-001).
3. **It is the comparison the prior work makes.** Both CURIOUS (random module choice) and IMGEP
   (random model babbling) define their intrinsic-motivation contribution against exactly this
   random-selection condition (E-001), so a comparison against anything else would not be
   commensurable with the literature.

And it is genuinely limited: sampled uniformly, the goal distribution does not adapt, so budget
goes to goals that are already mastered or unattainable, and the reported remedy in the literature
is precisely the selection mechanism under test here (E-001). HER's own motivating experiment
shows the shape of the problem it solves — a standard algorithm fails the bit-flipping task for
`n > 40` while HER solves it, by making easy goals available through relabelling (E-001) — which is
also the reason the baseline is strong: relabelling is already an automatic difficulty filter.

**Tuning the baseline fairly.** Both arms share one implementation of the environment, the learner,
the relabelling strategy and the exploration floor; only the goal-selection policy differs. The
shared hyperparameters — tabular update rate, episode horizon, relabelling count `k`, exploration
rate `ε`, evaluation cadence — are tuned **once, on the baseline**, and the critic's own
parameters (`n_min`, window length `l`, the triviality ceiling) are pre-declared rather than tuned
on the outcome. If the critic arm needs tuning that the baseline does not, that asymmetry is
reported as a cost of the mechanism. The confound this guards against is measured in the
unsupervised-RL benchmark: implementation differences alone can move results more than the
algorithmic difference under test, which is why the benchmark provides one code path for every
method it compares (E-001).

**Incomparability to the published numbers.** The reported IMGEP, CURIOUS and HER figures come
from robotic, 3D and simulated manipulation environments whose budgets are three to four orders of
magnitude larger than a tabular gridworld's (E-001). Nothing here reproduces their effect sizes;
this repository measures the *direction and the size of the selection effect* in a small,
fully-enumerable domain that can be run and re-checked cheaply, and the transfer of its result to
those environments is explicitly not claimed.

## Hypothesis

**H-001** — Under a deterministic discrete gridworld whose goal space mixes reachable, trivially
satisfied and unreachable goals, with a tabular goal-conditioned learner and hindsight relabelling
shared by both arms, a pinned seed set and a matched total environment-transition budget,
generator + independent Goldilocks critic goal selection reaches a held-out success rate over
reachable goals at least **20 percentage points higher** than uniform random goal sampling at the
same budget; at the cost of the critic's competence estimation, which needs recorded outcome
samples before any goal can be rated, adds a minimum-sample threshold below which a goal is
unrated rather than rejected, and adds per-candidate scoring compute to every selection step.

*Measured by:* the held-out success rate over reachable goals — goals never sampled during
training — evaluated identically for both arms at the same total budget, over ≥ 5 pinned seeds,
with the difference reported as median and min/max across seeds rather than a single run.

*Pre-registered margin.* Two outcomes count as interesting, both fixed before any code exists (E-001
records the same margin as it was written in the concept's selection screen):
(a) at a matched budget, ≥ 20 percentage points higher held-out success rate; or
(b) equal held-out competence reached in at most half the environment transitions.

*Decision rule.* **Supported** if the critic arm's median advantage is ≥ +20 percentage points and
the advantage is positive on at least 4 of 5 seeds. **Partially supported** if the advantage is
positive but below the margin — a real effect too small to pay for the second component.
**Falsified** if the median advantage is ≤ 0. Interaction budget means total environment
transitions, so any evaluation rollouts the critic performs are deducted from the learner's share;
the critic arm pays its own overhead inside the same budget.

*Second condition, pre-registered.* The same comparison is run in a world where every goal is
reachable and none is trivial. The prediction, stated before the run, is that the advantage there
is **smaller or absent**, per the reported no-distractor result (E-001). A null result in this
condition is a confirmation of the mechanism's stated condition, not a falsification of H-001;
it is reported separately and never pooled with the primary condition. With two conditions and one
primary metric there is no multiple-comparison correction to hide behind: the primary condition
decides H-001 and the second is a mechanism check.

*What would move the claim up.* A run in a non-enumerable goal space, and a budget large enough to
compare against a published effect size, would both be needed before anything here generalises to
the environments the sources used. This hypothesis is about a small domain; it is falsifiable
there and only there.

## Prior implementations

| Implementation | Maturity | What it does differently |
| :--- | :--- | :--- |
| **IMGEP with active model babbling** (Forestier, Portelas, Mollard & Oudeyer, JMLR 23, 2022) | Published method with an explicit random-selection control, from 16 to 100 seeds depending on environment, and released research code (E-001) | Chooses goal *spaces* by learning progress over a modular, object-centred representation, with stepping-stone-preserving mutations; its published active-versus-random contrast is partial across goal spaces, and its random control is described as competitive without distractors (E-001). This repository keeps the selection question and drops the population, the mutation operator and the modular goal representation. |
| **CURIOUS** (Colas, Fournier, Sigaud, Chetouani & Oudeyer, ICML 2019) | Published algorithm, 10 trials per condition, reported significance tests (E-001) | Non-stationary multi-armed bandit over *modules* with absolute LP as arm value, competence estimated from self-evaluation rollouts, mixed with random selection at `ε = 0.4` (E-001). Its LP-versus-random comparison is a perturbation-recovery test, and its curriculum demonstration is a single run (E-001). This repository tests the same selection idea as a learning curve at matched budget. |
| **GoalGAN and successors** (Florensa et al. 2018; Racanière et al. 2019) | Reported by the survey; primaries not read here (see § Open questions) | Trains a generator to emit goals of intermediate feasibility, without an explicit learning-progress estimate; a variant samples difficulty uniformly (E-001). |
| **Active-learning goal proposal** (Sukhbaatar et al. 2018; Campero et al. 2021) | Reported by the survey; primaries not read here | Rewards the goal policy for setting goals that are neither too easy nor impossible — the generator and the critic are both learned (E-001). |
| **Powerplay-style value-disagreement selection** (Zhang et al. 2020) | Reported by the survey; primaries not read here | Selects goals that maximise disagreement across an ensemble of value functions, on the grounds that agreement means too easy or too hard (E-001). |
| **This repository** | Not implemented yet; hypothesis and design only | Measures the selection effect at a matched interaction budget with a pre-registered margin, ≥ 5 pinned seeds, an explicit distractor condition and a published negative result if the effect is absent. It does not contribute a new algorithm: the mechanism is IMGEP/CURIOUS's, simplified to the smallest form that keeps the rating independent of the learner. |

## Open questions

1. **Does the critic's independence change the outcome, or is an outcome-based estimate alone
   sufficient?** The literature's two-part structures differ in how the rating is produced (bandit,
   GAN discriminator, ensemble disagreement) and this repository implements only one. Whether a
   single network that both proposes and rates goals is sufficient is the mechanism's core
   justification and is not measured here.
2. **How sensitive is the mechanism to the Goldilocks band?** No source in the ledger reports a
   sensitivity analysis of the minimum-sample threshold, the window length, or the triviality
   ceiling. If the effect exists only in a narrow band of these, the mechanism is expensive in a way
   the papers do not price.
3. **Learning progress from Bellman errors failing to beat random** is reported second-hand by the
   CURIOUS paper (E-001) and the primary was not read. It is the closest published negative result
   to this hypothesis and should be read before P5.
4. **The goal-proposal papers** cited in § Prior implementations reach this document only through
   the survey's report (E-001); their methods, baselines and budgets were not verified here. Any
   comparison against their numbers would need those primaries.
5. **Goal disengagement and re-engagement are measured in humans**, as separable capacities with
   different correlates (E-001), and the transfer of that structure to an artificial agent's
   selection rule is an analogy with no experimental support in the ledger.
6. **Non-enumerable goal spaces.** Every source either enumerates goal-space regions or learns a
   density model over them (E-001); the problem class in the selection screen is a goal space too
   large to enumerate, and a tabular gridworld is enumerable by construction. The experiment
   therefore cannot speak to the scale that motivated the concept.
7. **Threshold on "verifiably impossible".** No source establishes how many failed attempts make a
   goal unreachable; the criterion "yes, impossible" is not decidable from finite samples (E-001),
   so any implementation chooses a sample count. This repository's choice is a design decision, not
   a derived result.
8. **How much does goal selection matter when the learner transfers across goals?** The proof of
   concept says: less than the concept assumed. Its distractor-rich uniform arm was not slowed by
   spending a third of its episodes on unreachable goals (E-002), which is consistent with transfer
   making practice on any goal partly useful for every goal. The P5 design has to separate two
   readings that the PoC cannot: the mechanism genuinely buys nothing in small enumerable domains,
   or it buys nothing *for this learner*. A learner with bounded cross-goal transfer — limited
   capacity, or a goal representation the agent must acquire, as the sources' settings have — is
   the configuration in which this question is still open.

## Sources

Every entry below was fetched and read during this pass. `Access: full-text` means the document
itself was read (in full, or in the sections the claim rests on); no entry here is `secondary` or
`unreachable`, and nothing is cited from memory. Three arXiv-looking identifiers that were recalled
rather than looked up resolved to unrelated papers when fetched and were discarded before reaching
this ledger — which is why every URL here was checked against the document it served (E-001).

### SRC-001 — Schmidhuber, *A Possibility for Implementing Curiosity and Boredom in Model-Building Neural Controllers*, Proc. From Animals to Animats (SAB), MIT Press/Bradford Books, 1991, pp. 222–227

- **URL:** https://people.idsia.ch/~juergen/curiositysab/curiositysab.html
- **Access:** full-text
- **Establishes:** the original curiosity formulation this line of work descends from: an adaptive
  world model plus a controller, augmented by "dynamic curiosity and boredom" through delayed
  reinforcement for actions that increase the model's knowledge of the world; and the precondition
  that curiosity makes sense only for systems that can dynamically influence what they learn, in
  on-line learning situations with some form of dynamic attention. Curiosity is tied to what the
  system already knows — a system becomes curious when it believes there is something it does not
  know — which is the ancestor of the intermediate-difficulty criterion rather than a novelty or
  surprise drive.

### SRC-002 — Schmidhuber, *Formal Theory of Creativity, Fun, and Intrinsic Motivation (1990–2010)*, author's preprint, people.idsia.ch

- **URL:** https://people.idsia.ch/~juergen/ieeecreative.pdf
- **Access:** full-text
- **Establishes:** the formal criterion the concept's "novel but learnable" rule reduces to:
  interestingness is the progress of the observer's compression (or prediction), not surprise. It
  states that arbitrary data and fully predictable data are both unsurprising and boring because
  neither permits further compression progress, and that only data with still unknown algorithmic
  regularities carry value. The criterion is defined relative to a subjective observer's prior
  knowledge and its limited compression algorithm, not to a property of the data.

### SRC-003 — Oudeyer, Kaplan & Hafner, *Intrinsic Motivation Systems for Autonomous Mental Development*, IEEE Transactions on Evolutionary Computation 11(2), 2007, pp. 265–286

- **URL:** https://www.pyoudeyer.com/ims.pdf
- **Access:** full-text
- **Establishes:** Intelligent Adaptive Curiosity and the operational form of the criterion for a
  robot: a module monitors the derivative of a predictor's errors as learning progress, the system
  selects actions by the learning progress it expects from them, and the drive pushes the robot
  toward situations "which are neither too predictable nor too unpredictable". Reports the
  stage-like ordering observed in the experiments — first the easy-to-learn situations, then
  progressively harder ones, while regions where nothing can be learned are avoided — and the
  implementation detail that selection is `ε`-greedy with `ε = 0.35` rather than pure
  progress-greedy. Also separates two groups of architectures by whether learning progress is
  measured over recent situations generally or over situations that are similar but not necessarily
  close in time.

### SRC-004 — Colas, Karch, Sigaud & Oudeyer, *Autotelic Agents with Intrinsically Motivated Goal-Conditioned Reinforcement Learning: A Short Survey*, Journal of Artificial Intelligence Research 74, 2022, pp. 1159–1199

- **URL:** https://arxiv.org/abs/2012.09830
- **Access:** full-text
- **Establishes:** the framing and the failure analysis. Defines the goal construct as a
  (goal embedding, goal-achievement function) pair and the IMGEP family as the autotelic algorithms
  that generate and pursue their own goals; states the exact problem this concept's screen claims —
  goal spaces can be too large to master, "some goals might be trivial, others impossible", some
  "might be reached by chance sometimes, although the agent cannot make any progress on them", and
  some are reachable only after more basic skills; and states the counter-argument too — measures of
  intermediate difficulty are sensitive to environment stochasticity, because intermediate-looking
  difficulty can mean either not-yet-mastered or impossible-sometimes, and medium-term learning
  progress is what separates the two. Reports the LP-based family as bandit selection over
  goal-space regions using absolute learning progress, notes that absolute value brings attention
  back to goals whose performance is decreasing, and records that one form of LP derived from
  Bellman errors did not improve over random goal selection. Also records that empowerment-style
  methods maximise the mutual information between goals and states, rewritable as maximising the
  entropy of the goal distribution while minimising it given experienced states. This source is a
  survey: the primary works it reports (GoalGAN, Sukhbaatar et al., Campero et al., Stooke et al.,
  Zhang et al., Racanière et al., ALP-GMM) are not claimed as read here.

### SRC-005 — Forestier, Portelas, Mollard & Oudeyer, *Intrinsically Motivated Goal Exploration Processes with Automatic Curriculum Learning*, Journal of Machine Learning Research 23, 2022, pp. 1–41

- **URL:** https://arxiv.org/abs/1708.02190
- **Access:** full-text
- **Establishes:** the IMGEP architecture in modular, population-based form and — the load-bearing
  result for this repository — its own active-versus-random ablation. Active Model Babbling selects
  goal spaces with learning-progress estimates; Random Model Babbling selects them uniformly with
  everything else held equal, and the paper states that the random condition "can perform
  surprisingly well, especially when all goal spaces are relevant, i.e. when there are no
  distractors". In the competence tests, AMB is reported ahead of RMB on the pickaxe goal space
  (Welch's t-tests, p < 0.01) but not on the cart space (p = 0.09, attributed to environment
  stochasticity), and the hand-designed Fixed Curriculum condition is not separable from AMB on
  either. Also reports exploration-coverage medians with quartiles for each condition (for example,
  cart coverage medians of 5 for RMB against 56 for AMB with interquartile ranges of 162–409 and
  360–886 respectively) and the per-condition seed counts (100 seeds in the 2D simulated
  environment, 20 to 42 runs in Minecraft, 16 RMB against 23 AMB in the robotic environment), which
  is the scale a matched-budget comparison has to reach before its numbers mean anything.

### SRC-006 — Colas, Fournier, Sigaud, Chetouani & Oudeyer, *CURIOUS: Intrinsically Motivated Modular Multi-Goal Reinforcement Learning*, Proceedings of the 36th International Conference on Machine Learning, PMLR 97, 2019

- **URL:** https://arxiv.org/abs/1810.06284
- **Access:** full-text
- **Establishes:** the learning-progress estimator and its cost, in implementable detail.
  Learning progress is the derivative of competence, `LP = dC/dt`, with competence the probability
  of success; module selection is a non-stationary multi-armed bandit whose arm value is the
  current **absolute** LP, so modules being forgotten are re-selected; competence is not available
  externally, so the agent approximates its "subjective competence" from self-evaluation rollouts
  taken with `p_eval = 0.1` and no exploration noise, over a window of `l = 300` episodes, with
  selection mixed against random at `ε = 0.4`. The active-versus-random ablation is an
  architecture-matched pair: M-UVFA uses the same modular goal-parameterised policy with random
  module choice, while CURIOUS uses LP-based module choice; the reported significance test between
  them is on recovery after a time-locked sensory perturbation, over 10 trials, and the
  developmental curriculum itself is displayed as a single run. Also records that a flat goal space
  fails badly here — none of the goals in the full product space correspond to a real situation, so
  the HER-equivalent baseline's learning curve stays flat — and that learning progress remains small
  both for solved modules and for modules that are too hard, which is the empirical shape of the
  criterion.

### SRC-007 — Andrychowicz, Wolski, Ray, Schneider, Fong, Welinder, McGrew, Tobin, Abbeel & Zaremba, *Hindsight Experience Replay*, 31st Conference on Neural Information Processing Systems (NIPS 2017); arXiv:1707.01495v3, 2018

- **URL:** https://arxiv.org/abs/1707.01495
- **Access:** full-text
- **Establishes:** the incumbent, precisely. The goal-conditioned formulation with a goal sampled
  per episode, and the relabelling trick that turns a failed episode into training signal for the
  goals it did reach — the automatic curriculum that makes the baseline strong. Its motivating
  bit-flipping experiment shows a standard algorithm failing for `n > 40` while the
  hindsight-relabelling variant solves it, i.e. the baseline's advantage comes from making easy
  goals available, not from choosing goals by difficulty. Goal states are sampled uniformly from
  the task's goal distribution (for pushing, from the same square as the box position; for
  pick-and-place, uniformly in the horizontal square with height sampled uniformly in a range),
  and initial state–goal pairs are discarded when the goal is already satisfied — the trivial-goal
  filter the baseline gets for free, and one this repository's critic must also implement.

### SRC-008 — Oudeyer & Kaplan, *What is intrinsic motivation? A typology of computational approaches*, Frontiers in Neurorobotics 1, 2007

- **URL:** https://www.frontiersin.org/journals/neurorobotics/articles/10.3389/neuro.12.006.2007/full
- **Access:** full-text
- **Establishes:** the typology this concept's branch sits in — knowledge-based models of intrinsic
  motivation (dissonance between experienced situations and the agent's predictions),
  competence-based models (measures of competence at achieving self-determined goals) and
  morphological models (properties of the sensorimotor flow irrespective of what the agent predicts
  or masters, i.e. novelty/surprise-style drives). It sets out the competence-based architecture
  with goal-reaching episodes, a mis-achievement measure compared against the goal, and an internal
  reward used to judge the interestingness of the associated goal, with a module selecting goals for
  maximal reward. It also records the state of the field at the time: the competence-based approach
  is presented as containing high potential and as not yet studied in the computational literature.

### SRC-009 — Kidd, Piantadosi & Aslin, *The Goldilocks Effect: Human Infants Allocate Attention to Visual Sequences That Are Neither Too Simple Nor Too Complex*, PLoS ONE 7(5): e36399, 2012, doi:10.1371/journal.pone.0036399

- **URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC3359326/
- **Access:** full-text
- **Establishes:** the provenance of the *name* used throughout this repository. It measures
  infants' visual attention to event sequences varying in complexity under an ideal-learner model
  and reports that the probability of looking away was greatest for items of very low or very high
  complexity, concluding that infants seek intermediate rates of information absorption and avoid
  wasting resources on material that is already known or unknowable. The "Goldilocks" label for
  the intermediate-difficulty preference comes from this literature; it is not the terminology the
  curiosity/intrinsic-motivation papers use, and the concept's selection screen attributes the rule
  to Schmidhuber, whose contribution is the formal criterion in SRC-002 rather than the name.

### SRC-010 — Wrosch, Scheier & Miller, *Goal Adjustment Capacities, Subjective Well-Being, and Physical Health*, Social and Personality Psychology Compass 7(12), 2013, pp. 847–860

- **URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC4145404/
- **Access:** full-text
- **Establishes:** the disengagement/re-engagement structure borrowed for the critic's end-of-goal
  behaviour, from the self-regulation literature on unattainable goals: goal **disengagement**
  capacity (dropping goals that cannot be attained) and goal **re-engagement** capacity (committing
  to new goals) are generalised individual differences measured separately, with different
  correlates — disengagement is associated with reduced distress and with physical and biological
  health outcomes recorded as improved, while re-engagement is associated with positive well-being
  indicators but rarely predicts distress or health (E-001). The transfer of this two-capacity
  structure to an artificial agent's selection rule is this repository's design analogy, not a
  finding of the source.

### SRC-011 — Laskin, Yarats, Liu, Lee, Zhan, Lu, Cang, Pinto & Abbeel, *URLB: Unsupervised Reinforcement Learning Benchmark*, arXiv:2110.15191

- **URL:** https://arxiv.org/abs/2110.15191
- **Access:** full-text
- **Establishes:** the methodology standard this repository's comparison has to meet, and a sober
  reading of what unsupervised methods currently achieve. Its stated motivation is that results are
  hard to compare when methods rely on different optimisation algorithms, because "small differences
  in implementation can result in large performance differences that are independent of the
  pre-training algorithm", and its main contribution is one unified code path with identical
  implementations of the optimisation algorithm for every baseline. It also reports that the
  implemented baselines make progress but are unable to solve the benchmark. Read here for
  methodology, not for goal-selection evidence: it benchmarks reward-free pre-training, which is a
  different setting from the goal-generation question this repository asks.

### SRC-012 — Mohamed & Rezende, *Variational Information Maximisation for Intrinsically Motivated Reinforcement Learning*, arXiv:1509.08731

- **URL:** https://arxiv.org/abs/1509.08731
- **Access:** full-text
- **Establishes:** the definition behind the empowerment tie-break — the mutual information is the
  definition of the internal drive known as empowerment in intrinsically-motivated reinforcement
  learning, with a variational lower bound used to estimate it, and the mutual information (channel
  capacity) between actions and future states as the quantity an agent can maximise without external
  reward. Used here only to pin what "prefer the more controllable goal" means when two candidates
  have equal learning progress.
