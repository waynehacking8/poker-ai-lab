# CFR Reading Notes

Reading notes accumulated while implementing this prototype. Intended as a
quick-reference distillation for myself — not a tutorial.

---

## 1. The setup CFR is solving

A two-player **zero-sum extensive-form game with imperfect information**:

- A game tree where some nodes group into **information sets** — collections
  of histories that look identical to the acting player (e.g., all states
  where I hold the King but don't know my opponent's card).
- A **strategy** is a probability distribution over actions at each
  information set.
- The goal: find a **Nash equilibrium** — a strategy pair where neither
  player can improve by unilateral deviation.

For two-player zero-sum, Nash strategies are also **minimax (GTO) strategies**:
they guarantee the best worst-case expected payoff.

---

## 2. Why not Minimax / Alpha-Beta?

Minimax assumes:
- Full observability — fails on poker (hidden cards).
- Small enough tree to enumerate — fails on No-Limit (~10^161 nodes).

CFR solves imperfect-information games via **regret minimization** in the
space of policies, not the space of states.

---

## 3. Regret Matching (the atom)

For a single information set with K actions:

- Track cumulative regret `R[a] = Σ_t [u_t(a) − u_t(σ_t)]`.
- Next strategy: `σ(a) = max(R[a], 0) / Σ_a' max(R[a'], 0)`.
- If all regrets ≤ 0, fall back to uniform.

**Hart & Mas-Colell 2000** showed this converges to coarse correlated
equilibrium in repeated games. CFR extends this to multi-step extensive-form
games.

---

## 4. Counterfactual Regret (the lift)

For a multi-step game, "regret" is computed **per information set**, using:

```
cf_regret(I, a) = Σ_h ∈ I  π^σ_{-i}(h) · [v(σ_{I→a} | h·a) − v(σ | h)]
```

Where:
- `π^σ_{-i}(h)` = **counterfactual reach** — probability of reaching `h`
  assuming the acting player TRIED to (their action probs set to 1), but
  opponent and chance played their actual strategies.
- `v(σ_{I→a} | h·a)` = expected utility if I forced action `a` at this
  info set.

The "counterfactual" framing isolates the acting player's choice at this
node from the path probabilities — making regret a property of the info
set, not the trajectory.

---

## 5. The CFR theorem

The sum of player i's per-info-set counterfactual regrets upper-bounds the
**external regret** for the whole game:

```
external_regret_i(T) ≤ Σ_I cf_regret_i(I, T)
```

Since regret matching gives `cf_regret_i(I, T) = O(√T)` per info set,
total external regret is `O(|I_i| · √T)`.

By the folk theorem, **average strategy with sublinear external regret
converges to Nash equilibrium** in zero-sum games. So:

> **The TIME-AVERAGE of CFR's strategies (not the latest strategy)
> approximates Nash, with exploitability scaling as `O(1/√T)`.**

This is the most-confused point in CFR literature — the last iterate
oscillates; only the running average is the Nash approximation.

---

## 6. CFR+ improvements (Tammelin 2014)

Three changes to vanilla CFR that gave ~1000× speedup on the same hardware,
enabling Heads-Up Limit Hold'em to be essentially solved:

1. **Regret floor at 0**: `R[a] ← max(R[a] + Δ, 0)` after each update.
   Discards "ancient" negative regret so the algorithm responds faster.
2. **Linear averaging**: weight iteration `t`'s strategy by `t` when
   averaging, so later (better) strategies dominate the mix.
3. **Alternating updates**: update player 1 on odd iterations, player 2 on
   even (instead of both simultaneously). Empirically smoother.

---

## 7. Monte Carlo CFR (Lanctot 2009)

Vanilla CFR traverses the full game tree every iteration. For Leduc this is
fine; for No-Limit Hold'em it is impossible. MCCFR samples a subset:

| Variant | What's sampled | What's traversed |
|---|---|---|
| **Outcome Sampling** | A single trajectory | One leaf per iteration |
| **External Sampling** | Opponent + chance | All actions of acting player |
| **Chance Sampling** | Just the deal | Full betting tree |

External Sampling is the most common choice in practice. Variance is higher
than vanilla CFR per iteration, but the constant factor on tree traversal
is so much smaller that wall-clock convergence is far better for large
games.

---

## 8. Deep CFR (Brown et al. 2019)

For games with too many info sets to store tabular regret (No-Limit
Hold'em), replace the regret table with a neural network:

- **Advantage Network**: predicts `cf_regret(I, a)` from a feature
  embedding of `(I, a)`.
- **Strategy Network**: predicts the average strategy.
- **Reservoir Buffer**: store sampled (I, regret) pairs uniformly to avoid
  catastrophic forgetting; sample for training.

Deep CFR brings CFR into the deep-learning ecosystem and is the link
between traditional CFR and modern RL-style training pipelines.

---

## 9. Where this connects to RL

CFR and traditional RL (PPO, Q-learning) attack the same problem — find
good policies — from different angles:

- **RL**: optimize expected return via stochastic gradient on rewards.
  Assumes the environment is stationary from the agent's perspective
  (single-agent setting).
- **CFR**: minimize regret against an adversary in a game tree. Designed
  for non-stationary multi-agent environments.

Hybrid methods (NFSP, Deep CFR, ReBeL, Player of Games) blend the two:
neural function approximation from deep RL + regret/equilibrium reasoning
from CFR.

---

## 10. Common implementation pitfalls

Recording these because I hit (or am still hitting) several of them:

1. **Returning utility from inconsistent perspectives.** Pick one — usually
   P1 — and stick to it in the recursion; flip signs at the player level.
2. **Updating regrets with own reach instead of counterfactual reach.**
   The `(1 − player)` index is non-obvious; easy to swap.
3. **Reporting last-iterate strategy instead of average strategy.** Average
   is what converges to Nash.
4. **Multiple visits to the same info set in one iteration.** When
   enumerating chance outcomes, the same info set can be touched several
   times per iteration. Standard CFR allows in-place updates; some
   variants require snapshotting the strategy at iteration start.
5. **Forgetting chance reach in regret updates.** When chance is enumerated
   outside the recursion (uniform weighting), the chance factor must still
   appear in cf-reach for the math to match the algorithm.

---

*Last updated: 2026-05-28. These notes will evolve as the prototype
matures.*
