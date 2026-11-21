# Clone validation on held-out replays

Held-out: 61 matches, 1930 hands (stable hash split of match ids; clustering, EM fit and size tables use the other matches only).  Tolerance: abs 0.05 or 2 SE of the difference; open size passes within max(0.5 bb, 15%).  Each clone plays the field mix in the real format and its statistics are measured on its own simulated hands; real values come from the held-out hands of the bots in that archetype (or the single bot).

## Match length

Real held-out matches: mean 31.6 hands, median 29, n=61.  Field clones vs field clones (simulated): mean 33.6, median 28.0, n=600.

## A0-opener-aggro-shover

10 of 15 statistics within tolerance.

| statistic | real | clone | within tolerance |
|---|---|---|---|
| btn_open | 0.713 (n=178) | 0.783 (n=7467) | NO |
| btn_limp | 0.039 (n=178) | 0.007 (n=7467) | yes |
| bb_fold_vs_open | 0.205 (n=78) | 0.335 (n=3180) | NO |
| bb_3bet | 0.564 (n=78) | 0.201 (n=3180) | NO |
| btn_fold_vs_3bet | 0.462 (n=13) | 0.493 (n=704) | yes |
| pf_allin_short | 0.085 (n=71) | 0.140 (n=2718) | yes |
| pf_allin_deep | 0.007 (n=299) | 0.017 (n=11932) | yes |
| flop_bet | 0.860 (n=157) | 0.637 (n=6754) | NO |
| turn_bet | 0.576 (n=99) | 0.466 (n=4569) | NO |
| river_bet | 0.434 (n=76) | 0.389 (n=3239) | yes |
| fold_to_bet | 0.477 (n=65) | 0.495 (n=3573) | yes |
| post_agg | 0.862 (n=269) | 0.832 (n=9858) | yes |
| wtsd | 0.387 (n=181) | 0.419 (n=7770) | yes |
| fold_end | 0.311 (n=360) | 0.345 (n=14972) | yes |
| open_size_bb | 2.474 (n=124) | 2.804 (n=5495) | yes |

## A0-opener-aggro-shover [naive]

5 of 15 statistics within tolerance.

| statistic | real | clone | within tolerance |
|---|---|---|---|
| btn_open | 0.713 (n=178) | 0.980 (n=980) | NO |
| btn_limp | 0.039 (n=178) | 0.014 (n=980) | yes |
| bb_fold_vs_open | 0.205 (n=78) | 0.005 (n=380) | NO |
| bb_3bet | 0.564 (n=78) | 0.203 (n=380) | NO |
| btn_fold_vs_3bet | 0.462 (n=13) | 0.064 (n=110) | NO |
| pf_allin_short | 0.085 (n=71) | 0.097 (n=300) | yes |
| pf_allin_deep | 0.007 (n=299) | 0.044 (n=1791) | yes |
| flop_bet | 0.860 (n=157) | 0.527 (n=1578) | NO |
| turn_bet | 0.576 (n=99) | 0.438 (n=1341) | NO |
| river_bet | 0.434 (n=76) | 0.339 (n=1090) | yes |
| fold_to_bet | 0.477 (n=65) | 0.154 (n=877) | NO |
| post_agg | 0.862 (n=269) | 0.771 (n=2747) | NO |
| wtsd | 0.387 (n=181) | 0.775 (n=1765) | NO |
| fold_end | 0.311 (n=360) | 0.116 (n=1948) | NO |
| open_size_bb | 2.474 (n=124) | 2.683 (n=889) | yes |

## A1-mixed-calm

12 of 15 statistics within tolerance.

| statistic | real | clone | within tolerance |
|---|---|---|---|
| btn_open | 0.249 (n=826) | 0.219 (n=8900) | yes |
| btn_limp | 0.616 (n=826) | 0.651 (n=8900) | yes |
| bb_fold_vs_open | 0.426 (n=437) | 0.315 (n=3360) | NO |
| bb_3bet | 0.062 (n=437) | 0.079 (n=3360) | yes |
| btn_fold_vs_3bet | 0.208 (n=53) | 0.088 (n=297) | NO |
| pf_allin_short | 0.003 (n=355) | 0.022 (n=3852) | yes |
| pf_allin_deep | 0.004 (n=1451) | 0.004 (n=14818) | yes |
| flop_bet | 0.326 (n=933) | 0.284 (n=11181) | yes |
| turn_bet | 0.370 (n=826) | 0.329 (n=9535) | yes |
| river_bet | 0.403 (n=698) | 0.355 (n=7991) | yes |
| fold_to_bet | 0.271 (n=656) | 0.257 (n=7751) | yes |
| post_agg | 0.682 (n=1410) | 0.634 (n=15498) | yes |
| wtsd | 0.673 (n=1110) | 0.652 (n=12937) | yes |
| fold_end | 0.317 (n=1650) | 0.258 (n=17816) | NO |
| open_size_bb | 2.711 (n=206) | 2.762 (n=1915) | yes |

## A1-mixed-calm [naive]

5 of 15 statistics within tolerance.

| statistic | real | clone | within tolerance |
|---|---|---|---|
| btn_open | 0.249 (n=826) | 0.201 (n=2144) | yes |
| btn_limp | 0.616 (n=826) | 0.799 (n=2144) | NO |
| bb_fold_vs_open | 0.426 (n=437) | 0.000 (n=636) | NO |
| bb_3bet | 0.062 (n=437) | 0.053 (n=636) | yes |
| btn_fold_vs_3bet | 0.208 (n=53) | 0.000 (n=80) | NO |
| pf_allin_short | 0.003 (n=355) | 0.019 (n=743) | yes |
| pf_allin_deep | 0.004 (n=1451) | 0.005 (n=4039) | yes |
| flop_bet | 0.326 (n=933) | 0.274 (n=3739) | NO |
| turn_bet | 0.370 (n=826) | 0.300 (n=3576) | NO |
| river_bet | 0.403 (n=698) | 0.342 (n=3395) | NO |
| fold_to_bet | 0.271 (n=656) | 0.021 (n=2342) | NO |
| post_agg | 0.682 (n=1410) | 0.604 (n=5868) | NO |
| wtsd | 0.673 (n=1110) | 0.955 (n=4173) | NO |
| fold_end | 0.317 (n=1650) | 0.017 (n=4288) | NO |
| open_size_bb | 2.711 (n=206) | 2.746 (n=423) | yes |

## A2-station

12 of 15 statistics within tolerance.

| statistic | real | clone | within tolerance |
|---|---|---|---|
| btn_open | 0.502 (n=219) | 0.201 (n=9626) | NO |
| btn_limp | 0.498 (n=219) | 0.799 (n=9626) | NO |
| bb_fold_vs_open | 0.000 (n=45) | 0.002 (n=2834) | yes |
| bb_3bet | 0.489 (n=45) | 0.290 (n=2834) | NO |
| btn_fold_vs_3bet | 0.000 (n=9) | 0.041 (n=485) | yes |
| pf_allin_short | 0.000 (n=75) | 0.017 (n=5456) | yes |
| pf_allin_deep | 0.000 (n=361) | 0.003 (n=15462) | yes |
| flop_bet | 0.000 (n=294) | 0.001 (n=14943) | yes |
| turn_bet | 0.000 (n=286) | 0.001 (n=14548) | yes |
| river_bet | 0.000 (n=275) | 0.001 (n=14070) | yes |
| fold_to_bet | 0.000 (n=444) | 0.026 (n=11175) | yes |
| post_agg | 0.000 (n=444) | 0.046 (n=10958) | yes |
| wtsd | 1.000 (n=365) | 0.972 (n=16786) | yes |
| fold_end | 0.000 (n=439) | 0.018 (n=19271) | yes |
| open_size_bb | 2.027 (n=110) | 2.119 (n=1918) | yes |

## A2-station [naive]

12 of 15 statistics within tolerance.

| statistic | real | clone | within tolerance |
|---|---|---|---|
| btn_open | 0.502 (n=219) | 0.188 (n=4614) | NO |
| btn_limp | 0.498 (n=219) | 0.812 (n=4614) | NO |
| bb_fold_vs_open | 0.000 (n=45) | 0.002 (n=1216) | yes |
| bb_3bet | 0.489 (n=45) | 0.266 (n=1216) | NO |
| btn_fold_vs_3bet | 0.000 (n=9) | 0.041 (n=266) | yes |
| pf_allin_short | 0.000 (n=75) | 0.012 (n=2689) | yes |
| pf_allin_deep | 0.000 (n=361) | 0.003 (n=7876) | yes |
| flop_bet | 0.000 (n=294) | 0.000 (n=8236) | yes |
| turn_bet | 0.000 (n=286) | 0.001 (n=8041) | yes |
| river_bet | 0.000 (n=275) | 0.001 (n=7896) | yes |
| fold_to_bet | 0.000 (n=444) | 0.024 (n=4841) | yes |
| post_agg | 0.000 (n=444) | 0.042 (n=4760) | yes |
| wtsd | 1.000 (n=365) | 0.981 (n=8942) | yes |
| fold_end | 0.000 (n=439) | 0.016 (n=9255) | yes |
| open_size_bb | 2.027 (n=110) | 2.112 (n=864) | yes |

## A3-opener-calm

10 of 15 statistics within tolerance.

| statistic | real | clone | within tolerance |
|---|---|---|---|
| btn_open | 0.672 (n=641) | 0.630 (n=10136) | yes |
| btn_limp | 0.231 (n=641) | 0.191 (n=10136) | yes |
| bb_fold_vs_open | 0.338 (n=343) | 0.460 (n=3966) | NO |
| bb_3bet | 0.137 (n=343) | 0.102 (n=3966) | yes |
| btn_fold_vs_3bet | 0.640 (n=75) | 0.680 (n=778) | yes |
| pf_allin_short | 0.069 (n=246) | 0.051 (n=4704) | yes |
| pf_allin_deep | 0.006 (n=1070) | 0.008 (n=15599) | yes |
| flop_bet | 0.406 (n=596) | 0.376 (n=9897) | yes |
| turn_bet | 0.374 (n=425) | 0.342 (n=7506) | yes |
| river_bet | 0.386 (n=306) | 0.334 (n=5770) | yes |
| fold_to_bet | 0.422 (n=495) | 0.515 (n=6036) | NO |
| post_agg | 0.667 (n=837) | 0.748 (n=11614) | NO |
| wtsd | 0.407 (n=703) | 0.489 (n=11310) | NO |
| fold_end | 0.380 (n=1275) | 0.389 (n=20290) | yes |
| open_size_bb | 2.414 (n=428) | 3.101 (n=6231) | NO |

## A3-opener-calm [naive]

5 of 15 statistics within tolerance.

| statistic | real | clone | within tolerance |
|---|---|---|---|
| btn_open | 0.672 (n=641) | 0.687 (n=1516) | yes |
| btn_limp | 0.231 (n=641) | 0.312 (n=1516) | NO |
| bb_fold_vs_open | 0.338 (n=343) | 0.000 (n=551) | NO |
| bb_3bet | 0.137 (n=343) | 0.089 (n=551) | yes |
| btn_fold_vs_3bet | 0.640 (n=75) | 0.089 (n=179) | NO |
| pf_allin_short | 0.069 (n=246) | 0.060 (n=500) | yes |
| pf_allin_deep | 0.006 (n=1070) | 0.014 (n=2839) | yes |
| flop_bet | 0.406 (n=596) | 0.281 (n=2571) | NO |
| turn_bet | 0.374 (n=425) | 0.244 (n=2338) | NO |
| river_bet | 0.386 (n=306) | 0.238 (n=2101) | NO |
| fold_to_bet | 0.422 (n=495) | 0.078 (n=1584) | NO |
| post_agg | 0.667 (n=837) | 0.628 (n=3488) | yes |
| wtsd | 0.407 (n=703) | 0.868 (n=2854) | NO |
| fold_end | 0.380 (n=1275) | 0.073 (n=3012) | NO |
| open_size_bb | 2.414 (n=428) | 3.094 (n=1025) | NO |

## Per-bot clones

Cells are real / clone; `*` marks a miss of the tolerance, `.` an unmeasurable cell (too few held-out decisions).  The bots have only about 100 to 200 held-out hands, so most misses here are real-side noise, which the 2 SE rule already widens.

| statistic | Kimiko | Blueprint | SolvencyCheck | InfernalMonarch | AutodidactInnovations | WSmithSimLab | qwentom-leap | Fabulous | PoetAndCoder | MercuryRetrograde |
|---|---|---|---|---|---|---|---|---|---|---|
| btn_open | 0.09 / 0.08 | 0.60 / 0.56 | 0.03 / 0.09 * | . | 0.20 / 0.23 | . | 0.00 / 0.09 * | 0.71 / 0.73 | 0.28 / 0.25 | 0.06 / 0.11 |
| btn_limp | 0.91 / 0.92 | 0.31 / 0.31 | 0.38 / 0.38 | . | 0.80 / 0.73 * | . | 1.00 / 0.88 * | 0.00 / 0.01 | 0.70 / 0.71 | 0.94 / 0.84 * |
| bb_fold_vs_open | 0.00 / 0.00 | 0.45 / 0.47 | 0.62 / 0.50 | . | 0.67 / 0.56 * | . | 0.00 / 0.18 * | 0.00 / 0.25 * | 0.08 / 0.18 | 0.00 / 0.20 * |
| bb_3bet | 0.25 / 0.17 | 0.13 / 0.10 | 0.07 / 0.07 | . | 0.06 / 0.07 | . | 0.00 / 0.06 * | 0.29 / 0.16 | 0.38 / 0.09 * | 0.00 / 0.06 * |
| btn_fold_vs_3bet | 0.00 / 0.04 | 0.31 / 0.69 * | . | . | 0.25 / 0.13 | . | . | 0.00 / 0.31 * | 0.00 / 0.05 | . |
| pf_allin_short | 0.00 / 0.01 | 0.09 / 0.05 | 0.00 / 0.02 | . | 0.00 / 0.02 | . | 0.00 / 0.02 | 1.00 / 0.13 * | 0.00 / 0.01 | 0.00 / 0.02 |
| pf_allin_deep | 0.00 / 0.00 | 0.01 / 0.01 | 0.01 / 0.00 | . | 0.00 / 0.00 | . | 0.00 / 0.00 | 0.00 / 0.01 | 0.00 / 0.00 | 0.00 / 0.00 |
| flop_bet | 0.00 / 0.00 | 0.32 / 0.31 | 0.44 / 0.36 | . | 0.18 / 0.24 | . | 0.23 / 0.26 | 0.60 / 0.55 | 0.64 / 0.46 * | 0.31 / 0.30 |
| turn_bet | 0.00 / 0.00 | 0.35 / 0.33 | 0.46 / 0.35 * | . | 0.23 / 0.26 | . | 0.17 / 0.29 * | 0.48 / 0.42 | 0.68 / 0.48 * | 0.43 / 0.32 * |
| river_bet | 0.00 / 0.00 | 0.43 / 0.37 | 0.51 / 0.36 * | . | 0.22 / 0.30 | . | 0.32 / 0.37 | 0.42 / 0.37 | 0.62 / 0.48 * | 0.46 / 0.34 * |
| fold_to_bet | 0.00 / 0.03 | 0.43 / 0.49 | 0.17 / 0.25 | . | 0.38 / 0.30 * | . | 0.10 / 0.24 * | 0.50 / 0.50 | 0.30 / 0.29 | 0.00 / 0.20 * |
| post_agg | 0.00 / 0.04 | 0.64 / 0.72 * | 0.91 / 0.66 * | . | 0.49 / 0.62 * | . | 0.39 / 0.60 * | 0.95 / 0.83 * | 0.87 / 0.74 * | 0.90 / 0.62 * |
| wtsd | 1.00 / 0.97 | 0.44 / 0.49 | 0.91 / 0.61 * | . | 0.36 / 0.66 * | . | 0.77 / 0.67 | 0.93 / 0.47 * | 0.79 / 0.57 * | 0.98 / 0.68 * |
| fold_end | 0.00 / 0.02 | 0.41 / 0.39 | 0.49 / 0.45 | . | 0.49 / 0.29 * | . | 0.10 / 0.19 * | 0.17 / 0.34 * | 0.14 / 0.20 | 0.00 / 0.18 * |
| open_size_bb | 2.50 / 2.51 | 2.29 / 2.25 | 2.20 / 2.26 | . | 4.00 / 3.97 | . | . | 2.60 / 2.60 | 2.95 / 2.93 | 2.00 / 2.71 * |

Within tolerance per bot: Kimiko 15/15, Blueprint 13/15, SolvencyCheck 9/14, InfernalMonarch 0/0, AutodidactInnovations 9/15, WSmithSimLab 0/0, qwentom-leap 5/13, Fabulous 9/15, PoetAndCoder 9/15, MercuryRetrograde 4/14

## Censoring effect

Statistics within tolerance (of 15) per archetype with the EM de-censored fit: [10, 12, 12, 10]; with a naive fit that only learns from hands whose cards were shown: [5, 5, 12, 5].  The naive clones almost never fold, since a folded hand never reaches a showdown, which is the overstatement the censoring note warns about.

## Weaknesses of the clones

* Memoryless and non-adaptive: a clone samples from fixed frequencies and never reacts to the
  opponent, so a candidate's opponent model has nothing to learn beyond those frequencies. Real
  bots that adapt, or leak patterns across hands, are not represented.
* Strength is an 8 bucket percentile (all-in equity percentile preflop, board-relative percentile
  with a rough draw bonus postflop) and the context is coarse (street, position, facing class, four
  stack bands). Board texture, blockers, bet history beyond the facing class and exact pot odds are
  invisible, so clones are blunter than the bots they imitate, especially in raised pots.
* The station archetype is only two bots (Kimiko and DeepStack). Both never fold, in training and
  in the held-out matches, and the clone matches that (fold to a button open 0.00 against 0.00, fold
  to a bet 0.03 against 0.00). Its misses are the preflop mix: the two bots differ (Kimiko limps,
  DeepStack raises about 64% of buttons), the clone averages them, and the held-out sample for that
  split is only 219 button decisions. Two bots cannot support a split, so it stays one archetype.
* The folding gap is in the mixed archetype, not the station: held-out real bots fold to a button
  open 43% of the time against 32% for the clone, and end 32% of hands by folding against 26%. The
  archetype mixes bots with different habits (cluster membership of low-data bots comes from shrunk
  statistics), and the pooled table lands in between.
* The per-bot clones use only 150 to 1,400 hand-seats each, shrunk toward their archetype with
  pseudo-count 3 (`--k-bot`, default since the second refit; it was 12 before). Against pseudo-count
  12 the in-tolerance counts moved Blueprint 11 to 13, SolvencyCheck 6 to 9, Autodidact 8 to 9,
  PoetAndCoder 6 to 9, MercuryRetrograde 3 to 4 of about 15, others unchanged. Exact 0 or 1
  frequencies of a real bot (never folds the big blind) still come out above 0 for the thinner
  bots, so treat per-bot results as a sensitivity check, not as a stand-in for that bot.
* Held-out sets are small (61 matches, 1,930 hands), so per-bot and rare-spot comparisons are noisy.
  The archetype count was chosen by silhouette on the training set, and the field weights come from
  how often each archetype appears among rated participants (a participant count, not hands).
* The field was observed between bots that mostly play each other; effects of a stronger opponent
  (for example a candidate that exploits) are extrapolation.
* Match length: the simulated field plays slightly longer matches than the real held-out set (about
  34 against 32 hands on average, medians 28 and 29).

## Uncontaminated prior (`league/data/clones_prior.npz`)

The archetype tables refit without every match that involves one of the 10 per-bot test bots (AutodidactInnovations, Blueprint, DeepStack, InfernalMonarch, Kimiko, MercuryRetrograde, PoetAndCoder, SolvencyCheck, mr_hide, qwentom-leap). Archetype labels, weights and the per-bot clones are copied unchanged from `clones.npz`, so ids stay comparable. 60 of 235 matches (2524 hands) remain.

Hand-seats left per archetype: A0-limper-calm 321, A1-station 0, A2-opener-aggro-shover 1133, A3-opener-aggro-shover 142, A4-bb-folder-calm 126, A5-opener-calm 2862. Every archetype table is shrunk toward the pooled table of the remaining seats with pseudo-count 30; archetypes with under 400 seats (A0-limper-calm, A1-station, A3-opener-aggro-shover, A4-bb-folder-calm) are thin, and an archetype with zero seats is the pooled table, not that archetype. A1-station is Kimiko and DeepStack only, both held-out bots, so it has no clean data at all and the prior's A1 is a generic table: do not use `arch:1` of the prior as a station.

### How far the tables moved (400 simulated matches per archetype and model, same seeds, against the field mix)

Cells are full fit, prior and the change in percentage points.

| statistic | A0-limper-calm | A1-station | A2-opener-aggro-shover | A3-opener-aggro-shover | A4-bb-folder-calm | A5-opener-calm |
|---|---|---|---|---|---|---|
| btn_open | 0.20 / 0.53 (+33) | 0.28 / 0.64 (+36) | 0.80 / 0.72 (-8) | 0.54 / 0.64 (+9) | 0.13 / 0.58 (+44) | 0.65 / 0.64 (-1) |
| btn_limp | 0.79 / 0.29 (-49) | 0.72 / 0.17 (-55) | 0.02 / 0.10 (+8) | 0.35 / 0.15 (-20) | 0.52 / 0.16 (-36) | 0.20 / 0.18 (-3) |
| bb_fold_vs_open | 0.08 / 0.38 (+31) | 0.00 / 0.41 (+41) | 0.34 / 0.37 (+3) | 0.04 / 0.42 (+38) | 0.70 / 0.48 (-22) | 0.42 / 0.45 (+3) |
| bb_3bet | 0.05 / 0.13 (+8) | 0.32 / 0.14 (-18) | 0.27 / 0.22 (-6) | 0.12 / 0.13 (+1) | 0.05 / 0.12 (+7) | 0.10 / 0.11 (+1) |
| btn_fold_vs_3bet | 0.31 / 0.66 (+36) | 0.04 / 0.71 (+67) | 0.78 / 0.72 (-6) | 0.04 / 0.67 (+63) | 0.15 / 0.68 (+53) | 0.64 / 0.72 (+8) |
| pf_allin_short | 0.02 / 0.07 (+6) | 0.02 / 0.08 (+6) | 0.13 / 0.10 (-3) | 0.04 / 0.08 (+3) | 0.01 / 0.08 (+7) | 0.06 / 0.07 (+2) |
| pf_allin_deep | 0.01 / 0.01 (+0) | 0.00 / 0.01 (+0) | 0.02 / 0.01 (-2) | 0.01 / 0.01 (-0) | 0.00 / 0.00 (+0) | 0.01 / 0.01 (-0) |
| flop_bet | 0.23 / 0.40 (+17) | 0.00 / 0.45 (+45) | 0.81 / 0.55 (-27) | 0.50 / 0.45 (-5) | 0.33 / 0.46 (+13) | 0.37 / 0.43 (+6) |
| turn_bet | 0.28 / 0.34 (+6) | 0.00 / 0.38 (+38) | 0.61 / 0.43 (-18) | 0.46 / 0.37 (-9) | 0.32 / 0.37 (+4) | 0.33 / 0.34 (+1) |
| river_bet | 0.32 / 0.33 (+1) | 0.00 / 0.34 (+34) | 0.51 / 0.38 (-13) | 0.44 / 0.34 (-9) | 0.33 / 0.36 (+3) | 0.35 / 0.34 (-0) |
| fold_to_bet | 0.22 / 0.49 (+27) | 0.02 / 0.47 (+45) | 0.50 / 0.47 (-3) | 0.38 / 0.47 (+9) | 0.34 / 0.49 (+14) | 0.50 / 0.49 (-1) |
| post_agg | 0.58 / 0.68 (+9) | 0.03 / 0.69 (+66) | 0.87 / 0.73 (-13) | 0.79 / 0.69 (-10) | 0.70 / 0.70 (-0) | 0.72 / 0.68 (-4) |
| wtsd | 0.70 / 0.33 (-38) | 0.98 / 0.33 (-65) | 0.36 / 0.32 (-4) | 0.53 / 0.32 (-21) | 0.60 / 0.31 (-30) | 0.48 / 0.33 (-15) |
| fold_end | 0.16 / 0.42 (+26) | 0.02 / 0.41 (+40) | 0.36 / 0.39 (+3) | 0.22 / 0.41 (+20) | 0.47 / 0.45 (-2) | 0.39 / 0.43 (+4) |
| mean abs change, pp | 20.5 | 39.7 | 8.2 | 15.6 | 16.9 | 3.3 |

### Held-out validation (70/30 split, same held-out matches)

Statistics within tolerance (of 15) per archetype. The base columns are the contaminated train-split fit, the prior columns the same split refit without the test bots' matches. Archetype names come from the split's own clustering.

| archetype | contaminated fit | prior |
|---|---|---|
| A0-opener-aggro-shover | 10 | 8 |
| A1-mixed-calm | 12 | 5 |
| A2-station | 12 | 2 |
| A3-opener-calm | 10 | 11 |

Reading: dropping every match of the 10 test bots leaves 60 matches and 2,524 hands, and the 10 bots
are the high-volume ones, so the prior is close to one pooled table. Only A5-opener-calm (2,862 seats,
mean change 3.3 pp) and, less so, A2-opener-aggro-shover (1,133 seats, 8.2 pp) keep their character.
A0, A3 and A4 move 16 to 21 pp on average and A1 becomes the pooled table (about 40 pp), so those
four no longer behave like their archetypes (for example A0 limps 29% instead of 79%). Held-out
pass counts fall accordingly (A1 12 to 5, A2 12 to 2 in the split's naming). Use the prior to
check that a trained agent does not depend on the test bots, not as a stand-in for the field.
Dropping only the test bots' own seats (keeping their opponents' seats) would leave more data
except for the station, which has no clean data under any rule; that variant was not built.
