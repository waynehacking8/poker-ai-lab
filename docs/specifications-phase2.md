# Phase 2 Specifications — Synthetic Collusion Detection

Function-level specs for the planned Phase 2 modules. Phase 1
(`docs/cfr-notes.md` and existing CFR code) is the foundation.

---

## 1. Honest player wrapper (`collusion/simulator/honest_player.py`)

### Interface

```python
class HonestPlayer:
    """Wraps a CFR-trained average strategy as a callable agent."""

    def __init__(self, policy: dict[str, np.ndarray], rng: np.random.Generator):
        # policy: info_set -> probability vector (length = num actions).
        # If an info set is missing, default to uniform.
        ...

    def act(self, info_set: str, legal_actions: tuple[str, ...]) -> str:
        # Sample an action according to policy[info_set].
        # Returns the action symbol (e.g., 'p' or 'b').
        ...
```

### Acceptance criteria

- Reproducible given a fixed `rng`.
- Distribution of actions, marginalized over many calls, matches
  `policy[info_set]` within 2% absolute error after 10k samples.

---

## 2. Colluding pair (`collusion/simulator/colluding_pair.py`)

### Behavior model

Two colluding players share hole-card information. Each behaves
normally **against opponents outside the pair**, but applies
"soft-play" rules when seated against the partner:

1. **Soft-play fold**: when the partner is in the pot and the
   colluder's hand is weaker than the partner's known hand, fold
   with probability `soft_fold_prob` (default 0.7).
2. **Chip dump (advanced)**: occasionally check-call to allow the
   partner's value bets to win larger pots (probability
   `chip_dump_prob`, default 0.1).
3. **No bluffing against partner**: when partner is the only
   opponent, never bet from a weak holding.

### Interface

```python
class ColludingPair:
    def __init__(
        self,
        partner_ids: tuple[int, int],
        policy: dict[str, np.ndarray],
        soft_fold_prob: float = 0.7,
        chip_dump_prob: float = 0.1,
        rng: np.random.Generator | None = None,
    ): ...

    def act(
        self,
        seat: int,
        own_card: int,
        partner_card: int | None,        # None if partner not at this table
        info_set: str,
        legal_actions: tuple[str, ...],
    ) -> str: ...
```

### Acceptance criteria

- When playing against the partner, the fold rate at info sets where
  the colluder's card is weaker than the partner's must be at least
  `soft_fold_prob` higher than `HonestPlayer`'s baseline.
- When playing against non-partner opponents, behavior is statistically
  indistinguishable from `HonestPlayer` (chi-square test, p > 0.05).

---

## 3. Game runner (`collusion/simulator/game_runner.py`)

### Interface

```python
def run_session(
    num_players: int,
    num_hands: int,
    colluder_fraction: float,           # e.g., 0.2 means 20% of pairs are colluding
    policy: dict[str, np.ndarray],
    seed: int = 0,
) -> pd.DataFrame:
    """
    Returns a long-format DataFrame with columns:

        hand_id     int
        player_id   int
        seat        int           # 0 .. num_players - 1
        info_set    str
        action      str
        own_card    int
        is_colluder bool
        partner_id  int | None    # for ground-truth labeling

    One row per (player, decision) event.
    """
```

### Acceptance criteria

- For `num_players=4, num_hands=10_000, colluder_fraction=0.25`:
  - Roughly 25,000 to 50,000 rows (each hand produces 2–5 decision
    rows per player).
  - `is_colluder == True` rate is approximately `colluder_fraction`.
- Determinism for fixed seed.

---

## 4. Pairwise feature extractor (`collusion/features/pairwise.py`)

### Per-pair features

For each unordered pair `(i, j)`:

| Feature | Definition |
|---|---|
| `co_table_freq` | Fraction of hands where both i and j are seated. |
| `mutual_fold_rate_i_vs_j` | Fraction of hands where i folded and j was the only remaining bettor. |
| `mutual_fold_rate_j_vs_i` | The symmetric quantity. |
| `simultaneous_fold_rate` | Fraction of hands where i and j both folded in the same round. |
| `chip_flow_i_to_j` | Sum of chips i lost to j minus chips j lost to i, divided by hands played together. |
| `decision_time_corr` | Pearson correlation of decision latency between i and j (placeholder: synthetic latencies). |

### Interface

```python
def compute_pairwise_features(
    log: pd.DataFrame, num_players: int,
) -> pd.DataFrame:
    """
    Returns: DataFrame indexed by (player_i, player_j) with i < j,
             columns = the features listed above.
    """
```

### Acceptance criteria

- For known colluding pairs, `mutual_fold_rate` is at least 2× the
  population mean among non-colluding pairs.
- `co_table_freq` should be near `1.0` for pairs assigned to the
  same table throughout the session.

---

## 5. LightGBM classifier (`collusion/models/lgbm_classifier.py`)

### Interface

```python
def train_lgbm(
    features: pd.DataFrame,           # output of compute_pairwise_features
    labels: pd.Series,                # boolean: True if pair is colluding
    test_size: float = 0.3,
    seed: int = 0,
) -> dict:
    """
    Splits features+labels by PLAYER (not pair) to avoid leakage,
    trains LightGBM with default hyperparameters, and returns:

        {
            "model": booster,
            "auc_test": float,
            "precision_at_recall_50": float,
            "feature_importances": list of (feature_name, importance),
            "roc_curve": (fpr, tpr, thresholds),
        }
    """
```

### Acceptance criteria

- Test-set AUC ≥ 0.85 on a balanced dataset (50/50 colluding /
  non-colluding pairs).
- `mutual_fold_rate` and `chip_flow` rank among the top 3
  feature importances.

---

## 6. Reference benchmarks

| Configuration | Expected metric |
|---|---|
| 4-player Kuhn, 10k hands, 25% colluding pairs | LightGBM AUC ≥ 0.85 |
| Same, with `soft_fold_prob = 0.3` (subtle collusion) | AUC drops to ~0.70 — still above random |
| Same, with `colluder_fraction = 0.05` (rare collusion) | Precision at recall 0.5 ≥ 0.40 |

If you see AUC below 0.7 on the easy 25% / 0.7 setting, suspect
either a feature-engineering bug or label leakage.

---

## 7. Future extensions (Phase 3 stretch)

- **GNN detector**: model players as nodes, behavioral co-occurrence
  as edges; train PyTorch Geometric GraphSAGE; compare AUC to
  LightGBM. Requires GPU.
- **Adversarial colluders**: introduce a "smart colluder" that
  randomizes its soft-fold timing to evade the LightGBM detector;
  measure detector AUC degradation; iterate.
