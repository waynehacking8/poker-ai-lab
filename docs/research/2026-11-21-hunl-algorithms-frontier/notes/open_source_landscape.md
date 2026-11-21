# Open-source HUNL bots, solvers and blueprints (landscape as of 2026-11-21)

Fetch date: 2026-11-21. Repo stats come from `gh repo view` / `gh search repos` / `gh api` run on that date. chipzen.ai was not visited. Items marked UNVERIFIED rest on search snippets or memory.

## Q1. Which open-source HUNL agents and solvers are maintained in 2025-2026?

### Takeaway
Few real HUNL *bots* are open source and strong. Slumbot is the only public benchmark and it ships code (slumbot2019) but not its blueprint. Actively maintained code is mostly solvers (TexasSolver, GTOpen, DEEPFOLD) or a Rust research stack (robopoker). The only openly reported HUNL bot numbers vs Slumbot are weak or old: robopoker -13.1 bb/100, DecisionHoldem >730 mbb/h (2021, self-reported). Nothing found fits pure Python + numpy + 0.5 vCPU as a drop-in; the reusable parts are algorithms and recipes.

### Cited Findings (inventory; stars/licence/pushed at 2026-11-21)

Bots and blueprint-style stacks
- krukah/robopoker: 235 stars, MIT, Rust, last push 2026-10-28. MCCFR blueprint (linear regret, Pluribus-style sampling and pruning), hierarchical k-means/EMD abstraction, depth-limited and safe subgame re-solve, Deep CFR via candle. Live Slumbot result: world+dirac -13.1 bb/100 +/-14.0 over 86K hands; dirac only -28.4 +/-6.0 over 480K hands. Training spec: 16 vCPU / 120 GB RAM, plus PostgreSQL 8 vCPU / 64 GB; river abstraction table 3.02 GB; a checkpoint at epoch 151.7M had 156K infosets. Litmus suite 34 pass / 6 fail, all failures attributed to flop bucket merging. README states "sampling temperature, not search, is the dominant loss". — [README](https://github.com/krukah/robopoker), [repo](https://github.com/krukah/robopoker)
- AI-Decision/DecisionHoldem: 100 stars, AGPL-3.0, last push 2024-05-29. Blueprint by linear CFR on hand+action abstraction, ~200M iterations on a 48-core CPU workstation for 3-4 days, plus depth-limited real-time search. Self-reported >730 mbb/h vs Slumbot over ~20,000 games (Nov 2021, leaderboard name zqbAgent) and >700 mbb/h vs OpenStack over ~2,000 games. Ships blueprint code and a `blueprint_strategy.dat` training pipeline, C++ `.so` interfaces. The NYU Shanghai 2026 thesis (CEO-Poker) says it does not beat Slumbot but stays near break-even (snippet only). — [README](https://github.com/AI-Decision/DecisionHoldem), [paper](https://arxiv.org/pdf/2201.11580), [thesis](https://cdn.shanghai.nyu.edu/sites/default/files/yuanheng_li_thesis_nyush_honors_2026.pdf)
- ericgjackson/slumbot2019: 178 stars, MIT, C++, last push 2023-09-18. CFR+ and external-sampling MCCFR (ecfr, tcfr), card and betting abstraction builders, endgame resolving, real-game best response, head-to-head tools. Code only; the shipped Slumbot blueprint is not in the repo. — [repo](https://github.com/ericgjackson/slumbot2019)
- Slumbot (hosted bot): 2018 ACPC HUNL champion; plays blinds 50/100 and 200 BB stacks (20,000 chips), stacks reset every hand. API: HTTP POST JSON, endpoints /slumbot/api/login, /new_hand, /act; actions as strings like `b200c/kk/kb400` (k check, c call, f fold, b bet-to-on-street). Free to call. — [sample_api.py](https://slumbot.com/sample_api.py) (fetched directly). Docs page via WebFetch returned HTTP 400.
- GTO Wizard Benchmark / researcher API: client gtowizard-ai/researcher-api-client, 27 stars, no licence field, last push 2026-04-09, Python 3.13+ and uv. Requires an API key by request form; API only plays hands and returns chips won; GTO Wizard AI is proprietary; AIVAT scoring. Paper arXiv 2603.23660 (24 Mar 2026) says GTO Wizard AI beat Slumbot by 19.4 +/-4.1 bb/100. LLMs (GPT-5.4, Claude Opus 4.6, Gemini 3.1 Pro, Grok 4) zero-shot fall well below baseline. — [client README](https://github.com/gtowizard-ai/researcher-api-client), [arXiv](https://arxiv.org/abs/2603.23660)
- bupticybee/AlphaNLHoldem: 110 stars, AGPL-3.0, last push 2023-07-07, TensorFlow + ray, self-play model-free RL (AlphaHoldem-style, not an official release), built on rlcard 50 BB env, not 100 BB ACPC. No Slumbot number reported in README. — [README](https://github.com/bupticybee/AlphaNLHoldem)
- deeptexas-ai/deep-holdem-ai: 33 stars, licence "other", last push 2026-09-28. Python HUNL engine, CFR subgame solver, ReBeL-style recursive solving, value net self-play, supervised StrategyNet. No strength numbers seen; appears promotional (UNVERIFIED quality). Same-org family masterai-top/cfr-poker-ai-masterai (55 stars, "other"). — [README](https://github.com/deeptexas-ai/deep-holdem-ai)
- facebookresearch/rebel: 702 stars, Apache-2.0, C++/PyTorch, last push 2024-03-20 (stale). Official ReBeL code; research-scale (needs large GPU/CPU self-play). — [repo](https://github.com/facebookresearch/rebel)
- fedden/poker_ai (Pluribus-style): 1,584 stars, licence "other", last push 2023-04-03 (stale). zanussbaum/pluribus 109 stars, no licence, 2020. — [repo](https://github.com/fedden/poker_ai)
- Taliwanmli/Talibus-Deep-CFR-Poker-AI: 5 stars, MIT, pushed 2026-11-04, tiny, quality UNVERIFIED.
- lifrordi/DeepStack-Leduc (951 stars, no licence, 2018, Leduc only) and happypepper/DeepHoldem (223 stars, no licence, 2018): stale.
- EricSteinberger/PokerRL 548 stars MIT, last push 2023-03-31; Deep-CFR 336 stars MIT, 2020: stale but the clearest Python Deep CFR / SD-CFR reference.
- google-deepmind/open_spiel: 5,601 stars, Apache-2.0, pushed 2026-11-14. Has universal_poker (ACPC-style, via ACPC game def; limit/no-limit hold'em with abstraction by config) plus CFR, MCCFR, Deep CFR, NFSP in Python and C++. Training full HUNL at scale in it is impractical; useful for algorithms and tests. HUNL support detail from memory, UNVERIFIED this session. — [repo](https://github.com/google-deepmind/open_spiel)
- datamllab/rlcard: 3,589 stars, MIT, pushed 2024-06-26. Has no-limit hold'em env (50 BB, coarse actions, per AlphaNLHoldem README). Environment only; weak for HUNL fidelity.
- LLM agents: PokerSkill (arXiv 2605.30094, 2026) open LLM agent, GPT-5.5 reported -57 +/-21 mbb/hand vs GTO Wizard; needs an LLM call per decision, not usable under our limits. — [arXiv](https://arxiv.org/pdf/2605.30094)

Solvers (postflop/preflop, mostly not bots)
- bupticybee/TexasSolver: 2,622 stars, AGPL-3.0, C++, last push 2026-11-06 (actively maintained). Postflop solver (DCFR). — [repo](https://github.com/bupticybee/TexasSolver)
- b-inary/postflop-solver: 382 stars, AGPL-3.0, Rust, last push 2024-07-09, README: "Development suspended" since Oct 2023 (author went commercial). wasm-postflop: 606 stars, AGPL-3.0, pushed 2023-10-01, suspended. — [repo](https://github.com/b-inary/postflop-solver)
- MatthewPDingle/GTOpen: 93 stars, Apache-2.0, Rust, created 2026-06-13, pushed 2026-11-21. Heads-up postflop DCFR on CPU or CUDA with no card abstraction, preflop 2-9 players, flop-leaf value net trained on exact flop solves, node locking. 1.35M-node flop tree reaches 0.3% pot in 7-11 s on an RTX 3090. A fresh GPU reference relevant to GB10 offline solving. — [README](https://github.com/MatthewPDingle/GTOpen)
- a9876543245/DEEPFOLD-SOLVER: 418 stars, no licence declared, pushed 2026-11-09. Windows desktop GPU/CPU DCFR solver with "2550+ preflop charts"; no licence so charts are not reusable. — [README](https://github.com/a9876543245/DEEPFOLD-SOLVER)
- noambrown/poker_solver: 173 stars, MIT, created 2026-01-05, last push 2026-01-05. River NLHE subgame solver: CFR, CFR+, external-sampling MCCFR, fictitious play, DCFR; Python reference implementation plus C++. Python reference is a clean base for a river solver. — [README](https://github.com/noambrown/poker_solver)
- Stale/small: kmurf1999/HoldemSolver (31, MIT, 2020), hucancode/poker-solver (16, MIT; it is an equity calculator, not a CFR solver).

### Inferences
- A pure-Python numpy blueprint at 256 MB cannot hold a Slumbot-scale blueprint, so the realistic design is a coarse blueprint (tens of MB in float16/uint8) from offline training, plus small real-time solves.
- robopoker is the best current open recipe (abstraction, linear MCCFR, subgame search, Slumbot harness) and also a cautionary data point: a serious Rust effort lands at -13 to -28 bb/100 vs Slumbot at 200 BB. Slumbot is a hard benchmark.
- DecisionHoldem's 3-4 days on 48 cores for ~200M iterations bounds what 48 h on 20 cores can reach; expect a smaller abstraction (UNVERIFIED scaling estimate).
- The 100 BB-or-less stacks of our game are easier than Slumbot's 200 BB; check the actual stack depth.

### Gaps
- No verified blueprint size or bucket counts for DecisionHoldem or robopoker (robopoker's per-street table sizes only partly read; only river 3.02 GB seen).
- No ReBeL or AlphaHoldem open-code Slumbot results found.
- No independently verified per-decision CPU cost for any of these bots.
- Slumbot docs page (slumbot.com/api/documentation) did not load; API facts come from sample_api.py.
- Did not find any 2025-2026 HUNL repo with notable stars beyond those listed; searches by "hunl", "cfr poker", "poker solver", "holdem bot slumbot" returned small repos.

## Q2. Public preflop and push/fold Nash resources for HU, 5-40 BB

### Takeaway
No trustworthy, permissively licensed HU 5-40 BB chart set was found. The best route is to compute our own with a solver (push/fold is a tiny game) and use GTOpen (Apache-2.0) or our own CFR; published chart mirrors are unattributed.

### Cited Findings
- WebSearch for HU push/fold Nash charts returned a C++ equilibrium calculator ("Heads Up Push or Fold", rt500, github.com/rt500/Heads-Up-Push-or-Fold; `gh` could not resolve this repo, so it may be renamed or deleted) and unattributed netlify chart mirrors with no method stated. — [search hit](https://www.github.com/rt500/Heads-Up-Push-or-Fold)
- An academic paper solves a fixed structure (blinds 300/600) with near-optimal HU push/fold, not a stack sweep. — [ITU paper](https://www.itu.dk/~trbj/papers/poker.pdf)
- MIT OCW 15.S50 Poker Theory lecture notes cover preflop/push-fold theory (not downloadable chart data confirmed). — [MIT OCW PDF](https://ocw.mit.edu/courses/15-s50-poker-theory-and-analytics-january-iap-2015/8826933a49d89d788b584cdd41f69182_MIT15_S50IAP15_L4_PreFlop.pdf)
- hasuwini77/push-fold-ranges: 2 stars, CC-BY-4.0, pushed 2026-10-12 (tiny, UNVERIFIED correctness; format and HU coverage not read). Julian-cloud-max/holdemmath-data: 0 stars, licence "other". — [gh search](https://github.com/hasuwini77/push-fold-ranges)
- DEEPFOLD-SOLVER advertises 2,550+ preflop charts but has no declared licence. — [README](https://github.com/a9876543245/DEEPFOLD-SOLVER)
- GTOpen (Apache-2.0) solves preflop for 2-9 players with flop leaves priced by a trained net, so it can generate HU preflop ranges at chosen stacks. — [README](https://github.com/MatthewPDingle/GTOpen)

### Inferences
- HU push/fold at 5-20 BB is a solvable matrix game (169 x 169 hand classes, equity table from an evaluator); computing it ourselves avoids licensing questions and is cheap on the GB10.
- Treat anything above ~12-15 BB as shove-only-model-inaccurate; real solutions include min-raise/limp lines.

### Gaps
- No stack-by-stack HU Nash chart with an explicit permissive licence from a reputable source (GTO Wizard, Simple Postflop, HRC charts are proprietary; not fetched).
- Could not verify correctness of any chart mirror.

## Q3. Fast hand evaluators for Python

### Takeaway
For pure Python, treys/deuces (lookup tables, MIT or unlicensed) and pokerkit (pure Python, MIT, 3.11+) work in a seccomp sandbox. eval7 and phevaluator are fast but C/Cython extensions (wheels, so import needs no compiler but loads a .so). For bulk work use a precomputed numpy lookup table built offline.

### Cited Findings
- eval7 0.1.11 (PyPI, upload 2026-07-29), MIT, wheels for cp310+ including manylinux x86_64; repo JulianAndrews/pyeval7: 73 stars, MIT, pushed 2026-07-29; "performance critical parts implemented in Cython", includes equity calculator. C extension. — [PyPI](https://pypi.org/project/eval7/), [GitHub](https://github.com/JulianAndrews/pyeval7)
- phevaluator 0.6.0 (PyPI, 2026-07-11), Apache-2.0, binary wheels (cp310, cp311...) so C extension; underlying HenryRLee/PokerHandEvaluator: 529 stars, Apache-2.0, pushed 2026-11-15. Perfect-hash, ~100 kB of tables for 7-card. C++ benchmark on random hands: 5-card 1376 ns, 6-card 1550 ns, 7-card 1778 ns (C++ numbers; Python call overhead extra). — [repo](https://github.com/HenryRLee/PokerHandEvaluator), [PyPI](https://pypi.org/project/phevaluator/)
- treys 0.1.8 (2022-06-21), MIT, py3-none-any wheel, "pure Python poker hand evaluation library", lookup tables via bit arithmetic; ihendley/treys 182 stars, pushed 2023-07-15 (stale but stable). — [GitHub](https://github.com/ihendley/treys)
- deuces 0.2.1 (2023-11-29), PyPI licence MIT, worldveil/deuces 625 stars, repo licence field none; pure Python, 5/6/7-card. — [GitHub](https://github.com/worldveil/deuces)
- pokerkit 0.7.8 (2026-11-20), MIT, pure Python, >=3.11, 528 stars, pushed 2026-11-20; "high-speed hand evaluations", also game state engine with HU NLHE support and has a Lattice for bet translation used by robopoker. No speed benchmark in README. — [GitHub](https://github.com/uoftcprg/pokerkit)
- holdem-calc 1.0.0 (MIT, 2019), pure Python odds calculator; slow Monte Carlo/enumeration (UNVERIFIED speed).
- robopoker claims a nanosecond-scale Rust evaluator beating Cactus Kev (Rust, not usable in Python). — [README](https://github.com/krukah/robopoker)

### Inferences
- If seccomp forbids loading compiled extensions or the image must stay small, use treys/deuces code vendored, or build a 7-card rank table (about 133M combos; a perfect-hash like phevaluator's ~100 kB tables ported to numpy) offline.
- At 1 s per decision, evaluator speed matters mainly for real-time equity/range rollouts; numpy vectorized lookups over 1326-combo ranges beat per-hand pure Python by orders of magnitude (inference, not measured).

### Gaps
- No measured Python-level speeds for treys, eval7, phevaluator, pokerkit on this hardware; not benchmarked.
- Not verified whether a seccomp sandbox blocks the specific .so wheels; stated as risk only.
- Licence of deuces repo (none declared) versus PyPI MIT: conflict, read LICENSE before vendoring.
