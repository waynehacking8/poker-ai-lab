# Model-free self-play RL for heads-up no-limit hold'em and related games, 2022 to November 2026

All fetches and GitHub API reads were done on 2026-11-21. arXiv dates are first-submission dates from the arXiv API (https://export.arxiv.org/api/query). "UNVERIFIED" marks anything I could not confirm from a primary source in this session. "mbb/hand" = milli big blinds per hand; 10 mbb/hand = 1 bb/100.

## 1. AlphaHoldem (AAAI 2022): Trinal-Clip PPO, K-best self-play, state representation, cost, and follow-ups

### Takeaway
AlphaHoldem is PPO with two extra clips, a ConvNet over card and betting tensors, and self-play against an ELO-ranked pool of its own past versions. It reported +111.56 ± 16.06 mbb/hand vs Slumbot (95% CI, 100k hands) from 3 days on 8 TITAN V GPUs and 64 CPU cores, with an 8.6M-parameter net. No official code or weights exist, and the released hand-history repo now returns 404. The only 2026 academic follow-up (AlphaExploitem) was tested only on Kuhn and Leduc. The strongest 2026 PPO-family HUNL results (VRPO, MMPO; see sections 2 and 4) report much smaller Slumbot margins, and their Slumbot versions differ from AlphaHoldem's.

### Cited Findings
* Paper: Zhao, Yan, Li, Li, Xing (Institute of Automation, Chinese Academy of Sciences; Xing also Tsinghua), AAAI 36(4), pages 4689 to 4697, DOI 10.1609/aaai.v36i4.20394. (source: [AAAI paper page](https://aaai.org/papers/04689-alphaholdem-high-performance-artificial-intelligence-for-heads-up-no-limit-poker-via-end-to-end-reinforcement-learning/); [PDF](https://cdn.aaai.org/ojs/20394/20394-13-24407-1-2-20220628.pdf), AAAI-22)
* State representation: two separate 3D tensors fused by the network. The card tensor has 6 channels (two hole cards, three flop cards, turn, river, all public cards, all hole plus public cards), each a 4x13 sparse binary suit-by-rank matrix. The action tensor has 24 channels (at most six actions in each of four rounds), each a 4 x nb binary matrix with rows for player 1's action, player 2's action, the sum of both, and legal actions. nb is the number of betting options. (source: [AlphaHoldem PDF](https://cdn.aaai.org/ojs/20394/20394-13-24407-1-2-20220628.pdf), AAAI-22)
* Action abstraction: the Figure 3 column labels, as extracted from the PDF text layer, read fold, check, call, bet 1/2, 3/4, 1, 3/2, 2 pot, all-in, which is nine options. This is my reading of figure text, not a sentence in the paper. (source: [AlphaHoldem PDF](https://cdn.aaai.org/ojs/20394/20394-13-24407-1-2-20220628.pdf))
* Architecture: a "pseudo-Siamese" design. Two ConvNets with no parameter sharing (one for cards, one for actions) are fused, then fully connected layers produce policy and value. The model has 8.6M parameters (1.8M conv, 6.8M fully connected), and the whole model is under 100 MB (98 MB in Table 1). (source: [AlphaHoldem PDF](https://cdn.aaai.org/ojs/20394/20394-13-24407-1-2-20220628.pdf))
* Trinal-Clip PPO: on top of standard PPO clipping ε, it adds a third clip δ1 on the ratio for negative advantages, L = E[clip(r_t, clip(r_t, 1−ε, 1+ε), δ1) · A_t] with δ1 > 1+ε (δ1 = 3). The value target is also clipped, L = E[(clip(R_t, −δ2, δ3) − V(s_t))²], where δ2 and δ3 are set dynamically to the chips the player and the opponent have put in the pot (range 0 to 20,000). The authors' stated motivation: large ratios on negative-advantage samples add variance, and bluffing makes value losses too large. (source: [AlphaHoldem PDF](https://cdn.aaai.org/ojs/20394/20394-13-24407-1-2-20220628.pdf))
* K-Best Self-Play: one main agent is trained. A pool holds its historical versions, the K best "survivors" by ELO score are kept, and the main agent learns from games against them. The paper does not give K. (source: [AlphaHoldem PDF](https://cdn.aaai.org/ojs/20394/20394-13-24407-1-2-20220628.pdf))
* Hyperparameters: Adam at lr 3e-4; mini-batch 2,048 per GPU, 16,384 total; γ = 0.999; GAE λ = 0.95; 50,000 iterations, each with 8 MPI threads × 128 environments × 128 steps. That totals 6.5 billion training samples, "about 2.7 billion hands". (source: [AlphaHoldem PDF](https://cdn.aaai.org/ojs/20394/20394-13-24407-1-2-20220628.pdf))
* Ablation at equal data (0.65 billion samples), scored by ELO: full AlphaHoldem 1597, Dual-clip PPO 1308, original PPO 1257, naive self-play 1033, best-win self-play 1024, delta-uniform self-play 931, PBT self-play 892, no history information 896, PokerCNN representation 359, Deep CFR-style vector representation 78. (source: [AlphaHoldem PDF](https://cdn.aaai.org/ojs/20394/20394-13-24407-1-2-20220628.pdf), Table 2)
* Training compute: one server with 8 NVIDIA TITAN V GPUs and a 64-core AMD 2.00 GHz CPU, three days. Table 1 lists the GPU version at 4×10³ CPU hours and 580 GPU hours, and a "CPU version" at 5×10⁴ CPU hours and 210 GPU hours that is tested on "a CPU". (source: [AlphaHoldem PDF](https://cdn.aaai.org/ojs/20394/20394-13-24407-1-2-20220628.pdf))
* Inference: 2.9 × 10⁻³ s per decision on one TITAN V GPU, a single forward pass with no search, which the paper calls over 1,000x faster than DeepStack. No CPU latency is given. (source: [AlphaHoldem PDF](https://cdn.aaai.org/ojs/20394/20394-13-24407-1-2-20220628.pdf))
* Results (Table 3, ± is a 95% CI):
  * vs Slumbot: +111.56 ± 16.06 mbb/hand over 100,000 hands.
  * vs OpenStack, their DeepStack reimplementation (3 weeks on 120 GPUs; itself +103.08 mbb/hand vs Slumbot over 100,000 hands): +16.91 ± 22.34 over 100,000 hands.
  * vs four professionals: +10.27 ± 65.13 over 10,000 hands in total, about 2,500 hands each.
  (source: [AlphaHoldem PDF](https://cdn.aaai.org/ojs/20394/20394-13-24407-1-2-20220628.pdf))
* Internal inconsistencies in the paper: the abstract says "100,000 hands" and the introduction says "200,000 hands" (the two matches summed). The introduction also says AlphaHoldem beats DeepStack "with statistical significance", yet Table 3's 16.91 ± 22.34 interval includes zero. (source: [AlphaHoldem PDF](https://cdn.aaai.org/ojs/20394/20394-13-24407-1-2-20220628.pdf))
* Released data: the paper points to github.com/ZhaoEnMin/AlphaHoldem_Data. The GitHub API returns 404 for it on 2026-11-21, and no such repo appears among the author's public repos (DeepHoldem, PokerDeepLearning and a PokerRL fork are listed). No official training code or weights were found. (source: GitHub API, `repos/ZhaoEnMin/AlphaHoldem_Data` and `users/ZhaoEnMin/repos`, 2026-11-21)
* Follow-up, AlphaExploitem (Murgoci, Spaan, Oren; arXiv 2605.09150, 2026-05-09): extends AlphaHoldem with a hierarchical transformer over earlier hands and trains against a pool of exploitable opponents. It was evaluated only on Kuhn poker and Leduc hold'em, simulated with PGX (JAX), with 100-hand episodes. Its AlphaHoldem baseline is the authors' own re-run with standard PPO (clip 0.1, AdamW, lr 1e-4); the extracted text does not mention Trinal-Clip. The K-best league is ELO-based, with size 8 for Kuhn and 5 for Leduc, plus a 25-checkpoint snapshot buffer for Leduc. Compute: one NVIDIA A40, about 12 h per Leduc seed and 4 h per Kuhn seed. (source: [arXiv HTML](https://arxiv.org/html/2605.09150v1), 2026-05-09)
* AlphaExploitem results, in big blinds per hand (seed means, read from text):
  * Leduc, in-distribution opponents: about +1.0 vs about +0.5 for the AlphaHoldem re-run.
  * Kuhn, in-distribution: about +0.38 vs about +0.03.
  * Leduc masking ablation: unmasked +1.10 in-distribution and +1.16 out-of-distribution; masked +0.54 and +0.52.
  * There is no Slumbot or HUNL test.
  * Code: "The code will be publicly released"; no URL.
  (source: [arXiv HTML](https://arxiv.org/html/2605.09150v1))
* Unofficial reimplementation bupticybee/AlphaNLHoldem: 110 stars, AGPL-3.0, last push 2023-07-07, TensorFlow plus ray. It uses RLCard's 50 bb heads-up NL env ("not the standard 100bb ACPC one", with bet sizes slightly different from ACPC). The default config wants 1 GPU and 89 CPU workers, and the bundled opponent "has been trained for about a week". The only reported evaluation is anecdotal: a few professionals played "some dozen games". No Slumbot number. (source: [README via GitHub API](https://github.com/bupticybee/AlphaNLHoldem), 2026-11-21)
* smdesai27/TxhmPokerAgent: 0 stars, MIT, last push 2026-09-05. A PyTorch AlphaHoldem-inspired HUNL agent with PPO plus GAE, a K-best league with rating-weighted sampling plus scripted and exploit opponents, an embedding plus LSTM front end, and a 4-to-5-action curriculum. The README says its win rates are only vs scripted bots and an in-house MCCFR, are "not vs Slumbot/DeepStack", and should not be compared with AlphaHoldem. (source: [README](https://github.com/smdesai27/TxhmPokerAgent), 2026-11-21)
* EircJC/AlphaHoldem-HU: 0 stars, no license, last push 2026-10-10. The Chinese README describes serving an "AlphaHoldem" model (iter330) plus an optional 136 to 138 GB GTO lookup database and an exploit layer that reads opponent VPIP/PFR/AF. NORM=500 normalization covers 20 to 500 bb stacks, and CPU torch inference is described as about milliseconds per step. Its "+56.5" acceptance figure has no stated units or protocol. UNVERIFIED. (source: [README](https://github.com/EircJC/AlphaHoldem-HU), 2026-11-21)
* AlexKashi/AlphaHoldem: 40 stars, no license, last push 2022-05-05; the README is a single line. (source: GitHub API, 2026-11-21)

### Inferences
* An AlphaHoldem-size net (8.6M parameters, about 34 MB at fp32) would fit 256 MB and a numpy forward pass is plausibly in the low tens of ms on 0.5 vCPU. This is my estimate, not measured. The conv layers dominate FLOPs, so a smaller MLP over the same features would be faster.
* AlphaHoldem's published training used about 580 GPU hours plus 64 cores for 3 days. A single GB10 for 48 h is roughly a tenth of the GPU hours, before any per-GPU speed adjustment (not measured). Environment simulation on 20 cores would also be about 3x thinner than their 64 cores.
* AlphaHoldem's Slumbot margin cannot be re-checked: there is no code, no weights, and the hand histories are gone. Later model-free HUNL agents with fuller recipes (VRPO, MMPO) report +33 and +13.5 mbb/hand vs their Slumbot versions, so 111 mbb/hand should be treated as an outlier until reproduced.

### Gaps
* K (the pool size) and the ELO update rule are not in the paper text I extracted.
* The exact network layers of the ConvNets are not given in the text (only parameter counts).
* No independent reproduction of AlphaHoldem on 200 bb HUNL with a Slumbot number was found on arXiv or GitHub.
* AlphaExploitem's exact numbers vs NE opponents are in figures only, so I could not read them from the text.

## 2. R-NaD / DeepNash, Magnetic Mirror Descent, and 2024 to 2026 successors applied to poker

### Takeaway
Regularized policy-gradient methods descended from R-NaD and MMD now have HUNL results. MMPO (MMD plus a Gaussian-mixture bet-size head, Kubíček, Lisý, Sandholm, 2026-09) plays Slumbot to a statistical tie (+13.5 ± 36.7 mbb/hand over 900k hands) with no card or bet abstraction after 4 days on an H200. NashPG (TMLR 2026) beats MMD, R-NaD, NFSP and PSRO head-to-head in its own 100 bb JAX HUNL env. R-NaD itself was removed from OpenSpiel in 2025, and its Stratego successor (Ataraxos, 2025) was not applied to poker.

### Cited Findings
* DeepNash (Perolat et al., arXiv 2206.15378, 2022-06-30; background): R-NaD, model-free, no search. It reached a yearly 2022 and all-time top-3 rank on Gravon in Stratego. (source: [arXiv abs](https://arxiv.org/abs/2206.15378), 2022-06-30)
* DeepNash's compute, as quoted by the Ataraxos paper: 1,024 TPU nodes for 2 to 3 months (TPU v3), an estimated $3,000,000 to $4,500,000, about 5.5 billion games and 5 to 10 trillion training examples. (source: [Ataraxos arXiv HTML](https://arxiv.org/html/2511.07312v2), 2025-11-10, updated 2026-10-04)
* MMD (Sokota et al., arXiv 2206.05825, 2022-06-12, ICLR 2023; background): it was the first standard RL algorithm empirically competitive with CFR in tabular settings, and it performed well as deep self-play RL in 3x3 Dark Hex and Phantom Tic-Tac-Toe. Repo ssokota/mmd: 21 stars, MIT, last push 2023-10-05. OpenSpiel ships a tabular `mmd_dilated.py`. (source: [arXiv abs](https://arxiv.org/abs/2206.05825); GitHub API and OpenSpiel tree, 2026-11-21)
* R-NaD code was removed from OpenSpiel in a commit dated 2025-05-27, "[RNaD] Remove R-NaD codebase from OpenSpiel. (No longer maintained.)". An R-NaD runner survives in nathanlct/IIG-RL-Benchmark (`algorithms/rnad/run_rnad.py`). (source: GitHub API commits on `open_spiel/python/algorithms/rnad/rnad.py`, and code search, 2026-11-21)
* MMPO (Kubíček, Lisý, Sandholm, arXiv 2609.36787, 2026-09-29): magnetic mirror descent with a mixture-of-Gaussians reparametrization for continuous actions, trained by self-play. Per the abstract it outperforms NFSP and matches or beats PSRO's final strategies with 3.5 to 5.5x fewer samples in sequential games (Kuhn, Leduc, Sequential Blotto), and "In heads-up no-limit Texas hold'em, it performs on par with Slumbot." The paper's HTML calls the method MMPO. (source: [arXiv abs](https://arxiv.org/abs/2609.36787); [HTML](https://arxiv.org/html/2609.36787v1), 2026-09-29)
* MMPO HUNL recipe (Appendix E):
  * Game: 400-chip stacks with a 2-chip big blind, which is 200 bb (my arithmetic). No subgame solving, card abstraction or fixed bet abstraction.
  * Actions: fold, call and all-in are discrete. A bet is one continuous pot fraction from 5 Gaussian components, with means initialized geometrically over [1/3, 3]. The sampled bet is rounded to a legal amount, and training uses the rounded bet.
  * Network: MLP with hidden sizes (1024, 1024, 1024, 1024), GELU, LayerNorm, AdamW with weight decay 0.002.
  * Optimization: lr 1e-3 with cosine decay; magnet weights 0.02 (Gaussian head) and 0.2 (categorical head), with the magnet updated every 20,000 steps; entropy decays from 0.03 to 0.003 over 2·10⁶ iterations; batch 4,096; 1 PPO epoch; ε-exploration 0.01; max game length 40.
  * Gradient control: a replicator-style action-clipping rule stops gradients on actions whose logit is far below the max.
  (source: [arXiv HTML](https://arxiv.org/html/2609.36787v1))
* MMPO compute and results:
  * Compute: "trained the strategy for 4 days on H200". The GPU count is not stated, though the introduction says self-play "on a single GPU".
  * vs Slumbot: +13.5 ± 36.7 mbb/hand over 900,000 hands. The interval type is not named in the text, but the figure caption refers to 95% CIs, and the interval spans zero.
  * The paper also reports MMPO scoring 28.2 mbb/hand better than Slumbot would against itself on the same cards.
  * Local best response of the final checkpoint: −1622.7 ± 158.9, as reported. I did not verify the sign convention.
  * Evaluation cost: about 120 CPU hours per Slumbot checkpoint comparison and about 12 CPU hours per LBR run.
  * No inference time and no code URL.
  (source: [arXiv HTML](https://arxiv.org/html/2609.36787v1))
* NashPG (Yu, Liu, Canonne, Wang, Xu, Tran, Albrecht; arXiv 2510.18183, 2025-10-21; TMLR 2026): multi-round regularization. Each block maximizes payoff minus α·KL to a reference policy using PPO (α = 0.2), and the reference resets to the current policy after each block. The abstract claims it "scales to large domains such as Battleship and No-Limit Texas Hold'em". (source: [arXiv abs](https://arxiv.org/abs/2510.18183); [HTML](https://arxiv.org/html/2510.18183v3))
* NashPG HUNL setup:
  * Environment: their own "first JAX implementation" of heads-up NLHE, 200-chip stacks with 1/2 blinds (100 bb), at least 1.3×10²⁰ information states.
  * Actions: the main text says 16 discrete actions (fold, check/call, 12 raise sizes, all-in). Appendix B.2 lists 14 pot fractions (20% to 400%) plus 13 preflop open sizes, so the paper is internally inconsistent.
  * Network: transformer with 2 layers, hidden 512, 4 heads, history length 64, and a 285-dimensional observation.
  * Reward: Δ/stack per hand.
  * Training: 64 environments, rollout length 64, AdamW at 3e-4.
  * Hardware and wall clock: not stated in the parts I read.
  (source: [arXiv HTML](https://arxiv.org/html/2510.18183v3))
* NashPG HUNL head-to-head results (Table 3, "Heads-Up Poker" row; mean ± std over 5 runs, 1,024 games each; positive favors NashPG; units not specified): vs MMD +0.111 ± 0.023, vs NFSP +0.163 ± 0.012, vs PSRO +0.149 ± 0.015, vs R-NaD +0.104 ± 0.064. Section 5.4 reports that swapping NeuRD for PPO inside R-NaD ("RNaD-PPO") substantially improves R-NaD on larger games. There is no external benchmark (no Slumbot). Code: ntu-agents/nashpg, 2 stars, no license, last push 2026-10-14. (source: [arXiv HTML](https://arxiv.org/html/2510.18183v3); GitHub API, 2026-11-21)
* Look-ahead search on policy networks (Kubíček, Burch, Lisý; arXiv 2312.15220, 2023-12-23): adds test-time search to any sampled-trajectory policy-gradient method via an extra critic. It was evaluated when trained along R-NaD on Leduc hold'em, imperfect-information Goofspiel and Battleships, not on HUNL. (source: [arXiv abs](https://arxiv.org/abs/2312.15220))
* Ataraxos (Sokota, Vinitsky, Hu, Fan, Kolter, Farina; arXiv 2511.07312, 2025-11-10), the DeepNash successor for Stratego:
  * Method: "Dynamically Damped Self-Play" with a reverse-KL penalty toward a uniform-random policy, a reverse KL to the data-collection policy, PPO-style ratio clipping, and power-law annealed regularization. MMD appears only in the test-time search step.
  * Compute: RL on 16 H100s for 1 week plus a belief net on 4 H100s for 4 days, under $8,000 at 2025 prices, 163 million games.
  * Result: 15 wins, 1 loss and 4 draws vs Pim Niemeijer. Search costs about 1.26 s per move on an H100.
  * Not tested on poker.
  * Code: AtaraxosAI/stratego (120 stars, MIT, last push 2026-02-18), AtaraxosAI/doudizhu (15 stars, MIT), AtaraxosAI/hanabi (4 stars, MIT).
  (source: [arXiv HTML](https://arxiv.org/html/2511.07312v2); GitHub API, 2026-11-21)
* Equilibrium selection by regularized self-play (Leal; arXiv 2607.17543, 2026-07-20, and 2609.19820, 2026-09-17): R-NaD-style solvers select the maximum-entropy equilibrium. In Kuhn, R-NaD lands at bluff coordinate 0.180 vs the max-entropy 0.201, and anchoring the reference policy steers which equilibrium is selected. The author notes this "matters only against fixed, non-equilibrium opponents". (source: [arXiv 2607.17543](https://arxiv.org/abs/2607.17543); [arXiv 2609.19820](https://arxiv.org/abs/2609.19820))

### Inferences
* MMPO is the closest published match to "small CPU net, no abstraction, HUNL": a 4x1024 MLP is about 3M+ weights (about 12 MB at fp32) and one forward pass, so millisecond numpy inference is plausible. This is an estimate, not measured.
* Leal's steering result suggests that against fixed rule-based opponents, which equilibrium a regularized method lands on can matter, and the reference or magnet policy is a tuning knob for that. This is untested in poker.

### Gaps
* No released code for MMPO; its observation encoding and parameter count were not in the text I read.
* NashPG's payoff units in Table 3 and its compute are not stated in the parts I read. If the units are Δ/stack (100 bb), +0.1 would be about 10 bb/hand, which seems large. UNVERIFIED.
* No DeepNash-style R-NaD run on full HUNL with an external benchmark was found. R-NaD appears in HUNL only as a NashPG baseline.

## 3. NFSP successors, Deep CFR / DREAM / ESCHER / Deep PDCFR+ and other model-free CFR variants: latest HUNL or large-poker evidence

### Takeaway
No model-free neural CFR variant (Deep CFR, DREAM, ESCHER, Deep PDCFR+) has a published full-HUNL result in 2022 to 2026. The newest, VR-Deep(P)DCFR+ (AAAI 2026), was tested on Flop Hold'em vs rule-based bots. In the largest 2025/2026 comparison (ICLR 2026), generic policy gradient (PPO, PPG, MMD) matched or beat NFSP, PSRO, ESCHER and R-NaD, and ESCHER was "uniformly noncompetitive". NFSP appears in 2026 HUNL work only as a losing baseline.

### Cited Findings
* VR-DeepDCFR+ / VR-DeepPDCFR+ (Xu, Li, Fu, Fu, Xing, Cheng; arXiv 2511.08174, 2025-11-11, AAAI 2026): a model-free neural CFR with value-network variance-reduced advantages, bootstrapped cumulative advantages, and discounting plus clipping. Kai Li and Junliang Xing are also AlphaHoldem co-authors. (source: [arXiv abs](https://arxiv.org/abs/2511.08174))
* Its "large poker game" is Flop Hold'em Poker: 20,000 chips, blinds 100/50, fixed 100-chip raises, at most three raises per round. Results vs five rule-based styles over 20,000 matches, in chips (the ± type is not stated): VR-DeepDCFR+ 11.6 ± 1.2, VR-DeepPDCFR+ 11.3 ± 0.9, DREAM −2.0 ± 3.1, OS-DeepCFR −7.8 ± 1.4. Setup: three hidden layers of 128, 10⁸ episodes, a 10⁷ buffer, on an AMD EPYC 7702 64-core CPU with 256 GB RAM. HUNL was not tested. Repo rpSebastian/DeepPDCFR: 20 stars, no license, last push 2026-03-01. (source: [arXiv HTML](https://arxiv.org/html/2511.08174); GitHub API, 2026-11-21)
* ESCHER (McAleer, Farina, Lanctot, Sandholm; arXiv 2206.04122, 2022-06-08, ICLR 2023): removes importance sampling via a history value function and beats DREAM and NFSP head-to-head over 90% of the time in dark chess. No poker beyond small games is named in the abstract. Repo Sandholm-Lab/ESCHER: 16 stars, no license, last push 2022-07-13. OpenSpiel has `pytorch/escher.py`. (source: [arXiv abs](https://arxiv.org/abs/2206.04122); GitHub API, 2026-11-21)
* DREAM (Steinberger, Lerer, Brown; arXiv 2006.10410, 2020; background): model-free regret-based deep RL, claimed state of the art among model-free methods "in popular benchmark games". Repo EricSteinberger/DREAM: 122 stars, MIT, last push 2024-07-25. PokerRL: 548 stars, MIT, last push 2023-03-31. (source: [arXiv abs](https://arxiv.org/abs/2006.10410); GitHub API, 2026-11-21)
* Reevaluating Policy Gradient Methods for Imperfect-Information Games (Rudolph, Lichtlé, Mohammadpour, Bayen, Kolter, Zhang, Farina, Vinitsky, Sokota; arXiv 2502.08938, 2025-02-13, ICLR 2026):
  * Scale: over 7,000 training runs and over 345,000 CPU hours, scored by exact exploitability in five large games (Liar's Dice 2D5F, 3x3 Dark Hex, Abrupt Dark Hex, Phantom TTT, Abrupt Phantom TTT). None is poker.
  * Findings: "The generic PG methods performed the strongest, and were roughly on par with one another". NFSP and R-NaD matched them only in select cases, PSRO was poor, and ESCHER was "uniformly noncompetitive".
  * Setup: every algorithm used a 3-layer, 512-unit MLP, and the generic PG methods got the higher entropy coefficient of Sokota et al. (2023).
  * Code: nathanlct/IIG-RL-Benchmark (30 stars, no license, last push 2025-11-18) and gabrfarina/exp-a-spiel (39 stars, MIT, last push 2025-04-05).
  (source: [arXiv HTML](https://arxiv.org/html/2502.08938v4); GitHub API, 2026-11-21)
* NFSP in 2025/2026 HUNL work:
  * NashPG beats NFSP +0.163 ± 0.012 in HUNL (see section 2).
  * In BluffJAX's Texas Hold'em benchmarks, "PPO-NFSP and PQN-NFSP are typically unable to reach break-even performance" against a self-play ReBeL agent (1e7 training samples, 10 seeds; numbers only in Figure 7).
  (source: [NashPG HTML](https://arxiv.org/html/2510.18183v3); [BluffJAX HTML](https://arxiv.org/html/2610.07686v1), 2026-10-06)
* LUGL (Milec, Samothrakis, Fairbank, Soemers; arXiv 2609.03660, 2026-09-03): fits LightGBM to tabular self-play updates. It reports results competitive with or better than DQN and DeepCFR on Kuhn, Leduc, Liar's Dice, Goofspiel and Flop5 Hold'em. No HUNL. (source: [arXiv abs](https://arxiv.org/abs/2609.03660))
* For contrast, a hybrid that is not model-free at inference: RL-CFR (Li, Fang, Huang; arXiv 2403.04344, 2024-03-07) uses RL to choose action abstractions and CFR to solve at runtime. It reports +64 ± 11 mbb/hand vs a ReBeL replication and +84 ± 17 vs Slumbot in HUNL. (source: [arXiv abs](https://arxiv.org/abs/2403.04344))
* OpenSpiel (5,601 stars, Apache-2.0, last push 2026-11-14) currently ships Deep CFR (JAX and PyTorch), NFSP (JAX), ESCHER (PyTorch), PSRO and tabular MMD. R-NaD is gone (see section 2). (source: GitHub API tree listing, 2026-11-21)

### Inferences
* For a 48 h single-GPU budget and a millisecond CPU policy, model-free neural CFR has no HUNL evidence and is CPU-sampling heavy (Deep PDCFR+ ran on 64 CPU cores). Regularized PPO-family methods have both HUNL evidence and GPU-friendly training.

### Gaps
* No 2022 to 2026 paper reporting Deep CFR, DREAM, ESCHER or Deep PDCFR+ on full HUNL vs Slumbot or another external bot was found in arXiv API searches ("Deep CFR", "ESCHER", "hold'em" plus self-play or RL).
* The DREAM paper's benchmark games were not re-read this session (the abstract does not name them).

## 4. 2024 to 2026 HUNL agents trained with PPO or other policy gradient in self-play, and the tricks that matter

### Takeaway
The strongest published model-free, search-free HUNL policy is VRPO (Fan and Farina, 2026-05, updated 2026-11-09): PPO with a variance-reduced Q-boosted advantage. It scored +33 ± 19 mbb/hand over 1M hands vs the 2022 Slumbot after 63 h on 4 RTX 5090s, with no blueprint bet sizes or search. The recurring tricks are:
1. Variance reduction in the advantage, whether a centralized Q critic, Trinal-Clip or a value clip.
2. Regularization toward a uniform or reference policy (KL or magnet) with decaying entropy.
3. Tiny PPO clip or update sizes.
4. Policy averaging (EMA) or low temperature at evaluation.
5. Fine-grained or continuous bet sizing instead of a coarse abstraction.
6. A pool of past selves or exploitable opponents.

### Cited Findings
* VRPO / Q-boosting (Fan, Farina; arXiv 2605.19235, 2026-05-19, v2 2026-11-09): replaces GAE with an Expected SARSA(λ) trace from a centralized action-value critic, which averages out action-sampling noise. GAE variance "persists even when the critic is exact" in equilibrium self-play. It keeps PPO's clipped objective and on-policy actor updates. It reports over 15% lower exploitability than tuned IPPO, MAPPO, MMD and PPG on mid-sized games, a new state of the art over PerfectDou in Dou Dizhu, and in HUNL "a positive win rate against Slumbot without any blueprint raise sizes, search, or subgame solving". (source: [arXiv abs](https://arxiv.org/abs/2605.19235); [HTML](https://arxiv.org/html/2605.19235v2))
* VRPO HUNL recipe:
  * Game: 200 bb (20,000 chips, 50/100 blinds), with the 5th raise on a street forced all-in to bound trajectories.
  * Actions: fold, call/check, or a raise emitted as three base-16 digit tokens ("Raise to i×16^j×10 chips"), plus an all-in token, so at most 16 actions per step.
  * Reward: in big blinds, max 200.
  * Network: token embeddings of 128 into a 4-layer, 4-head LLaMA-style causal transformer with FFN ratio 2, a 3-layer 256 state MLP, and an action-embedding MLP with dot-product scoring. A separate per-player critic is discarded at execution.
  * Optimization: Muon (lr 4e-4, weight decay 0.01); PPO clip ε = 0.02; KL-to-uniform coefficient α = 0.1; λ = 0.95; γ = 1; 4 actor and 4 critic epochs; 40,000 iterations at batch 8,192 trajectories, about 1.51×10⁹ timesteps.
  * Compute: 4x RTX 5090, about 63 h. HUNL training time is 5.67 s per iteration vs 5.19 s for MAPPO (+9.2%).
  * Evaluation policy: an EMA of weights (β = 0.999) at temperature 0.1.
  (source: [arXiv HTML](https://arxiv.org/html/2605.19235v2))
* VRPO HUNL result: +33 ± 19 mbb/hand vs the 2022 Slumbot over 1,000,000 hands via the Slumbot API, which the authors call "not a decisive win". The ± type is not stated in what I read, and no AIVAT is used for HUNL. For reference, always-fold loses 750 mbb/hand. Dou Dizhu: VRPO peasants vs PerfectDou landlord 0.811 ± 0.011, against PerfectDou-vs-PerfectDou 0.601 ± 0.011. No code URL is in the paper, though its checklist says a codebase is provided. A GitHub search for "VRPO Q-boosting" found nothing. (source: [arXiv HTML](https://arxiv.org/html/2605.19235v2); GitHub search, 2026-11-21)
* MMPO and NashPG are also self-play policy-gradient HUNL agents (details in section 2). MMPO's tricks: continuous pot-fraction bets via 5 Gaussians, a separate magnet strength per head, the magnet replaced by the previous fixed point every 20,000 steps, entropy decayed 10x, and gradient clipping of low-logit actions. NashPG's trick is a periodic KL-reference reset. (source: [MMPO HTML](https://arxiv.org/html/2609.36787v1); [NashPG HTML](https://arxiv.org/html/2510.18183v3))
* AlphaHoldem's own ablation shows Trinal-Clip (ELO 1597) > Dual-clip (1308) > plain PPO (1257), and K-best self-play beat naive, best-win, delta-uniform and PBT self-play at equal samples (section 1). (source: [AlphaHoldem PDF](https://cdn.aaai.org/ojs/20394/20394-13-24407-1-2-20220628.pdf))
* Lightweight-agent study (Kelidari, Haghi, Salmani; arXiv 2607.06854, 2026-07-07), on Gin Rummy with a Leduc check:
  * What helped: trust-region updates, a well-aimed reward, a curriculum of tougher opponents, warm starting and keeping the best checkpoint. Stacked, these lifted self-play from about 30% to 36% vs a fixed expert.
  * What did not help: reward shaping, learned embeddings, imitation/DAgger and an LLM opponent.
  * Capacity: "extra capacity does little to break the ceiling".
  * Code: Nikelroid/adversarial-coevolution (1 star, no license, last push 2026-11-12).
  (source: [arXiv abs](https://arxiv.org/abs/2607.06854); GitHub API, 2026-11-21)
* Data-Augmented Game Starts (Lanier, Monette, Baldi, Fox; arXiv 2605.14379, 2026-05-14): starting regularized-PG rollouts from intermediate states sampled from offline data cuts exploitability under fixed budgets. It can bias equilibria, which the authors mitigate with multi-task observation flags. Tested on long-horizon variants of Kuhn and Goofspiel, not HUNL. (source: [arXiv abs](https://arxiv.org/abs/2605.14379))
* BluffJAX (Reddi, Peters, D'Eramo; arXiv 2610.07686, 2026-10-06):
  * Games: JAX implementations of limit and no-limit Texas hold'em for 2 to 10 players. The NL version has 5 actions (fold, check/call, half pot, pot, all-in) and a 74+n observation.
  * Throughput: the README claims about 2×10⁸ samples/s on one RTX 6000 Ada for the suite. No hold'em-specific number is given in the text.
  * Baselines: CFR, Deep CFR, PPO, PQN, NFSP variants and ReBeL. In hold'em only ReBeL, PPO-NFSP and PQN-NFSP were run.
  * Repo: AryamanReddi99/bluffjax (the paper's github.com/bluffjax/bluffjax resolves there): 17 stars, last push 2026-11-21, JAX 0.7.2. The GitHub API finds no license file, although the paper checklist says MIT.
  (source: [arXiv HTML](https://arxiv.org/html/2610.07686v1); [README](https://github.com/AryamanReddi99/bluffjax), 2026-11-21)
* Evaluation context: GTO Wizard Benchmark (arXiv 2603.23660, 2026-03-24) offers a public HUNL API vs GTO Wizard AI with AIVAT, claiming the same significance with 10x fewer hands. GTO Wizard AI beat Slumbot by 19.4 ± 4.1 bb/100 (194 mbb/hand). (source: [arXiv abs](https://arxiv.org/abs/2603.23660))
* AlphaHoldem-style hobby repos from 2026 (TxhmPokerAgent, AlphaHoldem-HU) exist but report no external-benchmark results (section 1). (source: READMEs above)

### Inferences
* Relative strength vs Slumbot on the published record: AlphaHoldem +111.56 (2022, unreproducible), VRPO +33 ± 19 (2026, 1M hands), MMPO +13.5 ± 36.7 (2026, 900k hands, a tie). GTO Wizard AI's +194 shows that Slumbot is far from unexploitable. The Slumbot versions and stack rules differ across papers, so these numbers are not strictly comparable.
* VRPO's net (128-d, 4 layers) is small, likely around 1 to 2M parameters by my arithmetic (UNVERIFIED; the paper gives no count). But a raise needs three autoregressive steps plus a transformer pass over the history, so numpy CPU latency would need to be measured. An MLP head like MMPO's is simpler to port.
* GPU budgets in published HUNL PPO runs: VRPO about 252 GPU hours on RTX 5090s, MMPO 96+ GPU hours on an H200, AlphaHoldem about 580 GPU hours on TITAN V. A 48 h GB10 run is 0.2 to 0.5x the GPU hours of the smaller two, before per-GPU speed differences (not measured). A GPU-resident env (BluffJAX or NashPG's JAX HUNL) would remove the 20-core CPU sampling bottleneck, but BluffJAX's NL hold'em uses only 3 bet sizes.

### Gaps
* VRPO's HUNL observation details and parameter count, and MMPO's encoding, were not in the text I read; neither has public code.
* No paper reports CPU or numpy inference latency for any of these HUNL policies.
* None of these agents was evaluated against a field of rule-based amateur bots in HUNL. AlphaExploitem's exploitable pools are Kuhn and Leduc only, and Deep PDCFR+ used rule-based bots only in Flop Hold'em.

## 5. Training with a match-level objective (tournament, winner-take-all, rising blinds) instead of chips

### Takeaway
I found no 2022 to 2026 paper or repo that trains a heads-up agent by self-play RL on match win probability with rising blinds. Every HUNL RL paper above optimizes per-hand chips at fixed 50 to 200 bb stacks. The nearest work is SpinGPT (an LLM for 3-player Spin & Go, SFT plus RL on solver hands) and "ICM Out!" (2026-08), which shows that continuation values computed from the tournament model beat ICM for a 3-player jam/fold tournament.

### Cited Findings
* SpinGPT (Maugin, Cazenave; arXiv 2509.22387, 2025-09-26, ACG 2025):
  * Target: the first LLM for 3-player Spin & Go tournaments.
  * Training: SFT on 320k high-stakes expert decisions, then RL on 270k solver-generated hands.
  * Results: matches the solver's action in 78% of decisions (tolerant accuracy). In heads-up with a deep-stack heuristic, +13.4 ± 12.9 BB/100 vs Slumbot over 30,000 hands (95% CI).
  * The authors argue CFR's limits restrict it in tournaments.
  (source: [arXiv abs](https://arxiv.org/abs/2509.22387))
* ICM Out! (Li, Huang; arXiv 2608.09586, 2026-08-10; the same authors as RL-CFR):
  * Method: Strategic-Continuation Optimization prices successor states with continuation values from the finite tournament model instead of ICM.
  * Test: a 3-player jam/fold tournament with a $1M pool. ICM's mean absolute value error is $9,036, and SCO shifts jam frequency by 14.08% on average.
  * Result: SCO earns $214.33 more prize equity per hand and is favored in 2,433 of 2,838 matched units.
  * This is not RL self-play and not heads-up.
  (source: [arXiv abs](https://arxiv.org/abs/2608.09586))
* Empirical Validation of the ICM (Kim; arXiv 2506.00180, 2025-05-30, IEEE CoG 2025): a dataset of over ten thousand tournaments shows ICM underestimates big stacks and overestimates short stacks. (source: [arXiv abs](https://arxiv.org/abs/2506.00180))
* DE-ICM (Inariba; arXiv 2610.06028, 2026-10-05): near-exact ICM placement probabilities for thousands of players. The full matrix for 1,000 players takes 0.2 s on one core. Multi-way tournaments only. (source: [arXiv abs](https://arxiv.org/abs/2610.06028))
* Stack depths in HUNL RL papers:
  * AlphaHoldem: chips up to 20,000 (200 bb).
  * VRPO: 200 bb.
  * MMPO: 200 bb.
  * NashPG: 100 bb.
  * bupticybee/AlphaNLHoldem: 50 bb via RLCard.
  * EircJC/AlphaHoldem-HU: normalizes inputs for 20 to 500 bb stacks, but this is variable depth, not a match objective.
  (source: [AlphaHoldem PDF](https://cdn.aaai.org/ojs/20394/20394-13-24407-1-2-20220628.pdf); [VRPO HTML](https://arxiv.org/html/2605.19235v2); [MMPO HTML](https://arxiv.org/html/2609.36787v1); [NashPG HTML](https://arxiv.org/html/2510.18183v3); [AlphaNLHoldem README](https://github.com/bupticybee/AlphaNLHoldem); [AlphaHoldem-HU README](https://github.com/EircJC/AlphaHoldem-HU))
* Searches run with no relevant hit: arXiv API "sit and go", "push-fold", "tournament AND hold'em", "poker AND win probability", "poker AND stack AND reinforcement", plus a web search for RL with ICM rewards and escalating blinds. (source: arXiv API queries and web search, 2026-11-21)

### Inferences
* Our format starts at 100 bb (10,000 chips, 50/100) and blinds rise every 20 hands, so effective depth falls fast over a median 30 to 44-hand match. Off-the-shelf HUNL RL agents trained at fixed 100 to 200 bb would spend most of a match outside their training distribution. Training over a stack-depth curriculum, with stack and blind level as inputs, is the minimum adaptation. This is inference, not from a paper.
* A match-level reward (+1/−1 at match end) drops straight into a PPO self-play loop because the env already supplies terminal rewards. The cost is credit assignment over about 30 to 44 hands. A per-hand reward equal to the change in estimated match-win probability is the obvious shaping, and the SCO work suggests computing continuation values from the actual blind schedule rather than ICM. Both points are untested in the literature found.

### Gaps
* No primary source on RL self-play for heads-up winner-take-all with escalating blinds. The background literature (Miltersen and Sørensen 2007 and other 2007 to 2008 jam/fold tournament work) is cited in the sibling note `research_notes/HUNL bot algorithms frontier 2026/short_match_and_competitions.md` and was not re-fetched here.

## 6. Which methods fit the Chipzen constraints (0.5 vCPU, 256 MB, numpy only, under 200 ms; 48 h on a 20-core aarch64 GB10)

### Takeaway
On published evidence, the best fit is a regularized PPO-family self-play agent (VRPO-style variance-reduced advantages, or MMD/NashPG-style KL-to-reference regularization) with a small MLP or tiny transformer exported to numpy. It should be trained over varied stack depths and against a pool that includes exploitable rule-based styles. Model-free CFR variants lack HUNL evidence, and AlphaHoldem's exact recipe is unreproducible and compute-heavier than our budget.

### Cited Findings
* Published model-free HUNL agents and their nets:
  * AlphaHoldem: 8.6M-parameter ConvNet plus FC, under 100 MB, 2.9 ms per decision on a GPU.
  * MMPO: 4x1024 MLP.
  * VRPO: 4-layer, 128-d transformer, with the critic discarded at execution.
  * NashPG: 2-layer, 512-d transformer.
  (source: [AlphaHoldem PDF](https://cdn.aaai.org/ojs/20394/20394-13-24407-1-2-20220628.pdf); [MMPO HTML](https://arxiv.org/html/2609.36787v1); [VRPO HTML](https://arxiv.org/html/2605.19235v2); [NashPG HTML](https://arxiv.org/html/2510.18183v3))
* Published training budgets: AlphaHoldem took 3 days on 8 TITAN V plus 64 CPU cores (6.5e9 samples). VRPO took 63 h on 4 RTX 5090 (1.51e9 timesteps). MMPO took 4 days on an H200. (source: same as above)
* The 2026 lightweight-agent study found extra network capacity "does little" and that the curriculum and checkpoint selection mattered more. (source: [arXiv abs](https://arxiv.org/abs/2607.06854))

### Inferences
* All three published nets would fit in 256 MB at fp32, and an MLP of about 3M weights is a few million multiply-adds per decision, far under 200 ms in numpy on 0.5 vCPU. This is an estimate; it must be measured on the target before it is relied on.
* Rough budget fit: 48 GB10-hours is in the range of a scaled-down VRPO or MMPO run (both 96 to 252 GPU hours on faster or more GPUs), not an AlphaHoldem-scale run. With a CPU env on 20 cores, sample throughput, not GPU math, is the likely bottleneck. A JAX GPU env would change that, but no published hold'em throughput figure exists for one.
* Against a field of mostly rule-based amateur bots, the AlphaExploitem pattern (train against a pool of exploitable styles while keeping self-play opponents) is more relevant than shaving mbb/hand off a Slumbot margin, but it is unproven beyond Kuhn and Leduc.

### Gaps
* No measured numpy CPU latency for any published HUNL RL policy.
* No public code or weights for the two strongest 2026 model-free HUNL agents (VRPO, MMPO).
* No published GB10 or aarch64 training throughput for any poker RL setup.
