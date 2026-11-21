# HUNL equilibrium-finding and search algorithms, 2024-2026 frontier

All sources fetched 2026-11-21. Source dates are the arXiv/venue dates stated. Anything not fetched in full is marked unverified. chipzen.ai was not visited.

## Q1. Successors to ReBeL / Student of Games (Obscuro, equilibrium refinements, learned-value or depth-limited search, lab output)

### Takeaway
No 2024-2026 paper I found shows a new search method evaluated on full HUNL that beats the classic stack. Obscuro (Zhang and Sandholm, 2025) is a Fog of War chess paper, not a poker paper, and the 2026 equilibrium-refinements paper tests only small benchmark games. The nearest HUNL-relevant new work is EVPA (ICLR 2025) and the learned-value/CFR-schedule line.

### Cited Findings
- Obscuro is "the first superhuman AI for FoW chess", by Brian Hu Zhang and Tuomas Sandholm, arXiv 2506.01242, v1 2025-06-02, v2 2026-02-28. No code link and no poker experiments. Poker is only background. — [arXiv abs](https://arxiv.org/abs/2506.01242)
- Obscuro mechanics: samples a few hundred of the consistent positions each turn, drops positions irrelevant at higher orders of mutual knowledge (method named KLUSS), solves the subgame with PCFR+ and plays the last iterate. Tree growth uses "one-sided GT-CFR": on alternating iterations only one player explores (current strategy mixed with PUCT) while the other follows its equilibrium strategy. Leaves are scored by Stockfish 14 at depth 11, not by a learned net. Learning an evaluation net by deep RL is listed as future work. — [arXiv HTML v2](https://arxiv.org/html/2506.01242v2) (only first ~100k of 135k chars read; appendix on hardware/per-move stats not read)
- Obscuro results: 85.1% vs the prior SOTA ZS21 over 1,000 games; 97% vs humans rated 1450-2006; 80% (16-4) vs the top human (2318). Ablation: disabling one-sided GT-CFR alone scored 53.3% against full Obscuro over 10,000 games. Each doubling of thinking time gave about 52-57% head-to-head. — [same](https://arxiv.org/html/2506.01242v2)
- Obscuro compute: human games on a 6-core Intel i5 desktop at 3 min + 2 s/move; ablations 5 s/move on 10 cores of a 64-core EPYC; 3 threads (1 equilibrium solver, 2 expansion). — [same](https://arxiv.org/html/2506.01242v2)
- Authors state the methods are general-purpose and note HU hold'em common-knowledge sets are small enough to hold in memory; no poker numbers reported. — [same](https://arxiv.org/html/2506.01242v2)
- "Equilibrium Refinements Improve Subgame Solving in Imperfect-Information Games" (Kubicek, Lisy, Sandholm), arXiv 2601.17131, 2026-01-23, also listed in IJCAI 2026 proceedings (search listing; page not opened). Proposes "gadget game sequential equilibria", modifies sequence-form LP and CFR, claims >50% exploitability reduction vs vanilla. — [arXiv abs](https://arxiv.org/abs/2601.17131), [IJCAI 2026 listing](https://www.ijcai.org/proceedings/2026/384)
- That paper's tested games: Goofspiel 5, Leduc hold'em, Liar's dice 1,4, nested depth-limited on Goofspiel 7 and Liar's dice 2,4 (with 10 learned value functions). No HUNL; Texas hold'em named as future work. Cost described as "mild", no hardware or timings; no code link found. — [arXiv HTML v1](https://arxiv.org/html/2601.17131v1) (last ~12k chars unread)
- Student of Games (DeepMind, arXiv 2112.03178; Science Advances 2023): wins about 7 ± 3 mbb/hand vs Slumbot over 3.1M matches; table lists Modicum 11 ± 5 and ReBeL 45 ± 5 vs Slumbot. Poker uses randomized betting abstractions (about 20,000 actions cut to 4-5), trained up to 1.1M steps; no poker hardware stated; no code release statement found. — [ar5iv SoG](https://ar5iv.labs.arxiv.org/html/2112.03178) (last ~68k chars unread)
- ReBeL HUNL: 45 ± 5 mbb vs Slumbot, 9 ± 4 vs BabyTartanian8, 165 ± 69 vs Dong Kim (variance reduced). Data generation used 90 DGX-1 machines with 8 V100 each (720 GPUs); 6x1536 MLP value net, 2,660 inputs; under 2 s per hand average, never above 5 s; solves to end of the current betting round. — [ar5iv ReBeL](https://ar5iv.labs.arxiv.org/html/2007.13544)
- ReBeL code: github.com/facebookresearch/rebel, 702 stars, Apache-2.0, archived (read-only) 2024-11-01, last push 2024-03-20 per GitHub API; Liar's Dice only, no poker. — [repo page](https://github.com/facebookresearch/rebel), GitHub API fetched 2026-11-21
- EVPA (Li and Huang, ICLR 2025): online pruning plus abstraction for large IIEFGs; expected-value estimation via a set of M=10 independently trained nets (third-party summary), minimax pruning before CFR, online info-set merging. Abstract claims it beats DeepStack's replication and Slumbot in HUNL with significant win-rate margins. The PDF text could not be extracted, so numbers are unverified. — [ICLR abstract](https://proceedings.iclr.cc/paper_files/paper/2025/hash/8c1b5863a6b0f925617b917bb2f55be0-Abstract-Conference.html), [ICLR poster](https://iclr.cc/virtual/2025/poster/29930)
- Two 2026 arXiv papers (2605.19928 "Real-Time Parallel CFR", 2605.10900) were surfaced by search as citing EVPA; I did not open them. Unverified. — [search result](https://arxiv.org/pdf/2605.19928)
- Perfect Bayesian Equilibrium computation paper (Konicki, Chakraborty, Wellman, arXiv 2602.15233, AAMAS 2026) is tangential (empirical game theory). — [arXiv](https://arxiv.org/pdf/2602.15233v3)

### Inferences
- Obscuro's one-sided GT-CFR is the key transferable idea (cheap tree growth, no common-knowledge set), but it was shown only with a hand-coded Stockfish leaf evaluator in chess. Direct use in HUNL needs a leaf value function, which is exactly what ReBeL/SoG trained at large cost.
- For a 0.5 vCPU / 256 MB / 1 s deployment, none of ReBeL (720 GPU data gen, 6x1536 MLP, about 2 s/hand on GPU-class hardware), SoG, or Obscuro (3 threads, multi-second) fits as published. A runtime-lite variant would need a distilled leaf net and small subgames.

### Gaps
- No Meta FAIR, Alberta, or Lisy poker-search paper from 2024-2026 was found by my searches (searches were limited, about 14 calls). Absence is not proven.
- No Tencent/NetEase/AlphaHoldem-successor 2024-2026 paper found; only the 2022 AlphaHoldem and DecisionHoldem appeared. Unverified whether any exist.
- Zhang and Sandholm 2026 work cited by the refinements paper was not located.
- Obscuro appendix D (hardware, per-move stats) and SoG supplementary (poker compute) not read.

## Q2. Model-free deep CFR family and regret-minimization variants

### Takeaway
The best recent, evidence-backed gain is not a new net but training-free hyperparameter schedules on DCFR/PCFR+ (AAAI 2026), and Deep DCFR+/PDCFR+ (AAAI 2026) is the newest model-free neural CFR with a poker (flop hold'em) test. ESCHER and DREAM have not been tested on HUNL.

### Cited Findings
- "Faster Game Solving via Hyperparameter Schedules" (Zhang, McAleer, Sandholm), arXiv 2404.09097, v1 2024-04-13, v2 2026-02-08, AAAI-26. Training-free schedules derived on 3 small games, generalizing to 17 games. — [arXiv](https://arxiv.org/abs/2404.09097)
- Schedule formulas (n = total iterations): HS-DCFR alpha(t)=1+3t/n, beta(t)=-1-2t/n, gamma(t)=30-5t/n (or 15-5t/n); DCFR baseline fixed alpha=1.5, beta=0, gamma=2; HS-PCFR+ schedules only gamma. — [arXiv HTML v2](https://arxiv.org/html/2404.09097v2)
- Reported gains are orders of magnitude in minimum exploitability at fixed iterations: HS-PCFR+(30) about 12.5 OoM average vs prior SOTA over 10 games; HS-DCFR(30) about 3.1 OoM vs DDCFR. No wall-clock numbers. Poker tests are Kuhn, Leduc and two Libratus-generated HUNL endgames (endgame-1, -3; only DCFR variants plotted because PCFR+ was not reproduced for large poker games). Used OpenSpiel v1.2 and PokerRL; run on a single Apple M2 with 16 GB; no code repo stated. DDCFR (the RL-learned schedule) needed 24 h on 200 CPU cores. — [same](https://arxiv.org/html/2404.09097v2)
- Deep (Predictive) Discounted CFR (VR-DeepDCFR+ / VR-DeepPDCFR+), Xu, Li, Fu, Fu, Xing, Cheng, arXiv 2511.08174, 2025-11-11, AAAI 2026. Value-net variance-reduced advantages, bootstrapped cumulative-advantage fit, discounting and clipping. — [arXiv abs](https://arxiv.org/abs/2511.08174)
- Its poker test is Flop Hold'em (FHP), not HUNL: 20,000 matches vs five rule-based styles, avg chips VR-DeepDCFR+ 11.6 ± 1.2, VR-DeepPDCFR+ 11.3 ± 0.9, DREAM -2.0 ± 3.1, OS-DeepCFR -7.8 ± 1.4. Nets 3x64 (FHP 128 wide), 10^8 episodes, 10^7 buffer; run on a 64-core EPYC 7702, 256 GB RAM, no GPU; runtime about equal to DREAM. ESCHER was not benchmarked there. Authors (Chinese Academy of Sciences/Tencent-affiliated names; affiliation not verified). — [arXiv HTML](https://arxiv.org/html/2511.08174)
- Code: github.com/rpSebastian/DeepPDCFR, 20 stars, no license field, last push 2026-03-01. — GitHub API 2026-11-21
- ESCHER (McAleer, Farina, Lanctot, Sandholm, ICLR 2023, arXiv 2206.04122): history value function, no importance sampling; tested on phantom tic-tac-toe, dark hex, dark chess, beating DREAM and NFSP over 90% head-to-head in dark chess. Repo Sandholm-Lab/ESCHER: 16 stars, no license, last push 2022-07-13. — [arXiv](https://arxiv.org/abs/2206.04122), GitHub API
- DREAM (Steinberger, Lerer, Brown, 2020): evaluated on Leduc and Flop Hold'em. Repo EricSteinberger/DREAM: 122 stars, MIT, last push 2024-07-25. PokerRL: 548 stars, MIT, last push 2023-03-31. Deep-CFR repo: 336 stars, MIT, last push 2020-05-06. — [DREAM arXiv](https://ar5iv.arxiv.org/html/2006.10410), GitHub API
- A Sept 2025 study benchmarks MCCFR variants on heads-up and multiway NLHE and finds MCCFR strongest heads-up (arXiv 2509.23747); I did not open it, details unverified. — [arXiv PDF](https://arxiv.org/pdf/2509.23747v1)
- OpenSpiel: 5,601 stars, Apache-2.0, last push 2026-11-14. — GitHub API 2026-11-21
- "Dynamic Discounted CFR" (DDCFR): referenced as the RL-learned discounting predecessor (about 24 h on 200 CPU cores per HS paper). A standalone DDCFR paper was not fetched. — [HS paper](https://arxiv.org/html/2404.09097v2)

### Inferences
- Best convergence per compute on poker with evidence: HS-PCFR+/HS-DCFR for tabular solving (essentially free, runs on a laptop CPU), and Deep PDCFR+ for neural model-free. The neural methods have only been shown on small or flop-only games, not HUNL.
- The tabular schedule trick fits an offline trainer on the 20-core aarch64 box and any online subgame resolve in numpy. A model-free net is a poor fit for HUNL given no HUNL evidence.

### Gaps
- No head-to-head of ESCHER vs Deep PDCFR+ on poker; no HUNL result for any model-free deep CFR variant found.
- HS paper code location unverified; whether PCFR+ schedules were verified on HUNL subgames is not established (only DCFR plotted).

## Q3. Open code, compute, artifact size, inference cost, fit to 0.5 vCPU / 256 MB / 1 s

### Takeaway
Only the tabular family (abstracted MCCFR blueprint plus table lookup, schedules to train it) plausibly ships under the limits. ReBeL, SoG, Obscuro and Deep CFR style nets are out of budget as published; a heavily distilled net might fit but nothing published demonstrates that.

### Cited Findings
- ReBeL: 6x1536 MLP (about 6 hidden layers x 1536; roughly 12-15M parameters is my estimate from layer sizes, not stated), 720 V100 for data generation, under 2 s/hand avg on its hardware. — [ReBeL](https://ar5iv.labs.arxiv.org/html/2007.13544)
- AlphaHoldem: per-decision time about 2.9 ms on a single GPU, trained three days on one PC. — [AAAI listing](https://ojs.aaai.org/index.php/AAAI/article/view/20394)
- Slumbot2019 code: ericgjackson/slumbot2019, 178 stars, MIT, last push 2023-09-18 (abstracted CFR blueprint, no subgame solving per one source). — GitHub API; [search summary](https://arxiv.org/pdf/2201.11580)
- RLCard: 3,589 stars, MIT, last push 2024-06-26. — GitHub API
- Student of Games and Obscuro: no public code found. — see Q1

### Inferences
- Constraint check: 0.5 vCPU numpy at 1 s allows roughly a few thousand to tens of thousands of simple vector ops; a river subgame solve with 1,326-wide ranges for even a few hundred CFR iterations is borderline, a 12M-parameter MLP forward pass (about 25 MFLOP) is fine in compute but 50+ MB in float32 (4-8 MB in int8) and plausible within 256 MB. The real limit is subgame solve cost, not the net.
- 48 h on a GB10 is far below ReBeL's 720-GPU data generation, so ReBeL-style training would need a drastically reduced game (smaller ranges/bet set). Unverified by experiment.

### Gaps
- Artifact sizes for SoG, EVPA, and Deep PDCFR+ not stated in what I read. No measurement of numpy inference time was done.

## Q4. Measured HUNL strength reported 2024-2026

### Takeaway
Very few 2024-2026 papers report Slumbot numbers; the new standard is the GTO Wizard Benchmark (March 2026). Classic Slumbot figures come from 2020-2023 papers.

### Cited Findings
- GTO Wizard Benchmark (Provost et al., arXiv 2603.23660, 2026-03-24): public HUNL API using AIVAT; GTO Wizard AI beat Slumbot by 19.4 ± 4.1 bb/100 (= 194 mbb/hand); frontier LLMs zero-shot (GPT-5.4, Claude Opus 4.6, Gemini 3.1 Pro, Grok 4) far below baseline. — [arXiv](https://arxiv.org/abs/2603.23660)
- PokerSkill (arXiv 2605.30094, May 2026): scaffolded LLMs lose 57 ± 21 to 87 ± 64 mbb/hand vs the GTO Wizard benchmark; defaults lost 160-204. — [arXiv](https://arxiv.org/pdf/2605.30094) (snippet-level; unopened)
- Slumbot has no AIVAT, so Slumbot results are raw chip results with wide CIs. — search summary of [GTO Wizard Benchmark](https://arxiv.org/html/2603.23660)
- Older reference points: AlphaHoldem +111.56 mbb/h vs Slumbot (AAAI 2022); DecisionHoldem >730 mbb/h vs Slumbot over about 20k games (arXiv 2201.11580, 2022, as summarized by search, number unverified against the paper); ReBeL +45, SoG +7, Modicum +11 (above). Libratus 147 mbb/hand vs top humans (CMU lecture slide). — [AAAI](https://ojs.aaai.org/index.php/AAAI/article/view/20394), [arXiv 2201.11580](https://web3.arxiv.org/pdf/2201.11580), [Sandholm lecture](https://www.cs.cmu.edu/~sandholm/cs15-888F26/Lecture_17_Libratus_and_subgame_solving.pdf)
- Slumbot sample sizes and match rules differ across papers (e.g. 3.1M matches for SoG vs 100k hands for AlphaHoldem), so mbb numbers are not directly comparable.

### Inferences
- Slumbot margins are a weak strength proxy (abstraction-only bot). Use the GTO Wizard Benchmark with AIVAT if a comparable number is wanted.

### Gaps
- EVPA's actual Slumbot margins, Deep PDCFR+ on HUNL, and any 2024-2025 paper reporting a fresh Slumbot number were not found. One snippet cites a 13.5 ± 36.7 mbb/hand over 900k hands vs Slumbot without a verifiable source; treat as unverified.
