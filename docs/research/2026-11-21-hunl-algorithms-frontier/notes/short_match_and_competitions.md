# Short winner-take-all HUNL matches with rising blinds, and bot-competition lessons (fetch date 2026-11-21)

Method note: about 17 search and fetch calls. Many searches returned thin results. chipzen.ai was not visited. Items marked UNVERIFIED rest on a search snippet or a single weak source.

## 1. Chip EV vs win probability heads-up; how a skill edge should change risk-taking as blinds rise

### Takeaway
Primary literature I could retrieve treats heads-up tournament value as win probability, not chip count, and the Miltersen and Sorensen work shows win probability is not simply chip share once blinds are large relative to stacks. I found no citable quantitative model of "edge erodes as blinds rise" or of skill-adjusted declining marginal all-ins. Those parts are inference only.

### Cited Findings
- Miltersen and Sorensen (AAMAS 2007) model the heads-up endgame with 300/600 blinds and 8000 chips in play (the PartyPoker $5 to $30 SNG endgame). They compute a strategy with a rigorous near-optimality guarantee. A player holding 2500 of 8000 chips gets a guaranteed win probability strictly above 2500/8000. The value of each game state is the probability of winning the tournament under optimal play. Source: search result summary of the paper, not read in full; the PDF URL returned 404 on fetch. [itu.dk PDF](https://www.itu.dk/~trbj/papers/poker.pdf), [researchr](https://researchr.org/publication/MiltersenS07)
- A secondary snippet says the computed strategy is within about 1.4 percentage points of optimal win probability. UNVERIFIED (not confirmed against the paper text). [itu.dk PDF](https://www.itu.dk/~trbj/papers/poker.pdf)
- The strategy analysis first restricts the strategy-playing side to all-in bets only, and computations indicate it holds up in the unrestricted game. Ganzfried and Sandholm (AAMAS 2008) cite this and say jam/fold strategies are near-optimal in the two-player case. [Ganzfried and Sandholm AAMAS08 (via search summary)](https://aamas.csc.liv.ac.uk/Proceedings/aamas08/proceedings/pdf/paper/AAMAS08_0313.pdf); [kilthub record](https://kilthub.cmu.edu/articles/journal_contribution/Computing_an_Approximate_Jam_Fold_Equilibrium_for_3-player_No-Limit_Texas_Hold_em_Tournaments/6604343)
- Generic poker-education statement: maximizing chip EV is a fair tournament approximation but breaks down with fixed payouts (big stacks have money EV below chip EV). This is the ICM argument and applies to multi-payout events, not to a pure winner-take-all heads-up match. [PokerNews SNG heads-up tips](https://www.pokernews.com/strategy/10-tips-for-sit-go-success-how-to-play-heads-up-28040.htm)
- Empirical ICM test (arXiv 2506.00180, 2025, Juho Kim, over 10,000 live events): ICM beats a rank-based baseline (MSE 4.30e-3 vs 6.77e-3). Top-quartile stacks outperformed ICM (residual +5.59e-3, p=0.004) and bottom-quartile stacks underperformed (-4.44e-3, p<0.001). ICM ignores skill, position and blind level. A cited prior study (Scott et al. 2024) found small stacks near ICM expectations. Multiway data with at most 10 players, not heads-up. [arXiv 2506.00180v2](https://arxiv.org/html/2506.00180v2)
- Low-stakes SNG regular ROI of 3 to 8 percent and mid-stakes 2 to 5 percent was reported by a strategy site, which implies skill edges per match are small. Weak source. [PokerNews](https://www.pokernews.com/strategy/10-tips-for-sit-go-success-how-to-play-heads-up-28040.htm)

### Inferences
- In a winner-take-all heads-up match, utility is 1 if you win, 0 if you lose, so utility is the win probability. Chip share maps to win probability monotonically but not linearly. Linearity (chip EV = win probability) holds only for a martingale chip process with no blind pressure; with blinds that are large versus stacks, the Miltersen and Sorensen guarantee (win prob above chip share for the short stack at 2500/8000) shows the mapping is not identity. So "chip EV equals win probability" is an approximation that is poorest at shallow stacks.
- Escalating blinds shorten the horizon, so fewer hands for a skill edge to compound. With a 44-hand median match, luck weight is high. A stronger player loses relatively little by variance-seeking, but standard reasoning says the favorite should avoid coin-flip all-ins while deep and the underdog should seek variance. This is reasoning, not sourced.
- Against a field of loose-passive or highly aggressive amateurs, the available edge per hand is large, so the favorite benefits from lengthening effective match (not jamming early) until stacks reach push/fold depth; after that, blinds force variance regardless. UNSOURCED.

### Gaps
- No source found for a skill-adjusted win probability formula or for quantified "edge erodes as blinds rise." HoldemResources and academic SNG-skill literature not retrieved.
- Miltersen and Sorensen paper text not read; key numbers rely on snippets.

## 2. Heads-up push/fold Nash ranges by stack depth

### Takeaway
Published Nash heads-up shove (SB) and call (BB) ranges are available as a table by effective stack: SB shove falls from about 74 percent at 5 BB to about 41 percent at 20 BB, BB call from about 69 to 22 percent. Against non-Nash opponents the guidance is to tighten shoves against loose callers and widen against tight callers.

### Cited Findings
- Table below (PokerStrategy, no ante, ES is the smaller stack in BB before blinds posted; NPR is SB shove range and NCR is BB call range; the article's ICM calculator uses 0 percent edge). Source: [PokerStrategy Nash ranges](https://www.pokerstrategy.com/strategy/sit-and-go/1779/)

| ES (BB) | SB shove | BB call |
|---|---|---|
| 5 | 74.1% | 68.6% |
| 6 | 70.1% | 59.6% |
| 8 | 62.6% | 48.4% |
| 10 | 56.6% | 38.5% |
| 12 | 51.4% | 33.0% |
| 15 | 45.7% | 28.4% |
| 18 | 42.1% | 23.8% |
| 20 | 40.9% | 21.7% |

  Other rows (1 to 20 BB) are on the page. A 10 percent BB ante widens ranges (ES 9: 65.6 percent shove, 49.6 percent call).
- Opponent-adjustment guidance from the same page at ES 9 (EV in BB): if the opponent calls too loosely, stop shoving your weakest hands (a weak Nash-range hand goes from +0.76 BB vs a 20 percent caller to -0.64 BB vs a 70 percent caller). If the opponent calls too tightly, add hands outside the range. If the opponent shoves too loosely, add stronger hands to the calling range. For unknown opponents, shove about Nash and call slightly tighter than Nash. [PokerStrategy](https://www.pokerstrategy.com/strategy/sit-and-go/1779/)
- Other pages that appeared (matchpoker, deucescracked, netlify mirrors) gave inconsistent or low-quality numbers (a button shove of "35 percent at 15 BB", "42.5 percent at 10 BB"); I do not rely on them. They disagree with the PokerStrategy table at 15 BB (45.7 percent). Treat all as unreliable versus the PokerStrategy table.

### Inferences
- With blinds 400/600 for the later levels and 10000 chip stacks, effective stacks fall to roughly 17 to 25 BB at BB 400 to 600 for even-stack starts, and a short stack goes to push/fold depth (under 10 BB) quickly. The table is the reference for those spots.
- The table is chip-EV Nash with no ICM; in winner-take-all heads-up this is close to the right objective (see section 1) but is not exact.
- Because amateur BBs defend about 55 percent while the Nash call at 10 BB is 38.5 percent, an SB shove is profitable with fewer hands against a loose caller (weak shoves lose EV per the table above); against loose BB the shove range should be narrower than Nash.

### Gaps
- HoldemResources source was not fetched directly. No numbers for non-zero-ante structures matching our blind schedule or for stack depths above 20 BB (open-raise/fold zones).

## 3. Lessons from bot-vs-bot competitions 2015 to 2026

### Takeaway
The ACPC ran 2006 to 2018 and I found no successor; HUNL winners were equilibrium-approximation bots (Hyperborean, Tartanian, Slumbot, Baby Tartanian8). I found almost no reported numbers on how exploitation or simple rule-based bots fared against heterogeneous amateur fields, and no MIT Pokerbots 2025/2026 winner write-ups.

### Cited Findings
- ACPC ran from 2006 to 2018 (Wikipedia), with two winners per event: Total Bankroll and Bankroll Instant Run-off (most matches won). HUNL winners 2010 to 2014: Tartanian4/HyperboreanNL (2010), Lucky7/Hyperborean (2011), Little Rock/Hyperborean (2012), Slumbot NL/Hyperborean (2013), Tartanian7 both (2014). [Wikipedia Computer poker player](https://www.wikipedia.org/wiki/Computer_poker_player) Conflict: an archived mailing list shows a 2017 call for participation and a fragment saying 2015 was not held ("due to AAAI"), unreconciled. [Google Groups computer-poker](https://groups.google.com/g/computer-poker) Wikipedia is a tertiary source; the official ACPC site failed (self-signed certificate).
- 2016: Baby Tartanian8 (CMU, Brown and Sandholm) won HUNL total bankroll among 11 entrants. The first AAAI announcement was erroneous (extra matches run to separate top four) and a corrected results list put Baby Tartanian8 first in Bankroll Instant Runoff. Slumbot was reported to narrowly beat it at 95 percent significance in the uncorrected March 2016 report. [IJCAI 2016](https://ijcai.org/proceedings/2016/639); [ACPC 2016 Results Amendment](https://groups.google.com/g/computer-poker/c/yOS44TbK0ao); [PokerNews 2016](https://www.pokernews.com/news/2016/03/the-perfect-poker-bot-is-almost-here-24212.htm)
- Libratus beat four pros in 2017, a gap of about $1.8 million in simulated money. Pluribus (6-player, 2019) is out of scope. [Wikipedia](https://www.wikipedia.org/wiki/Computer_poker_player)
- MIT Pokerbots: 2024 variant was Auction Hold'em (30 s per 1000 hands, 1 GB RAM). A GTO Wizard team entry used depth-limited subgame solving with an equity heuristic in place of a value network, a custom evaluator (about 400M hands/s on one thread), and a precomputed auction-bid equity table (1.8x multiplier best in simulation). No placement stated. [gtowizard-ai/mitpoker-2024](https://github.com/gtowizard-ai/mitpoker-2024)
- Older MIT entries: 2017 entry tracked opponent stats to adjust aggression and looseness (no big lookup tables); 2021 entry precomputed hand strength by simulation, tight-aggressive with randomization. Both from search snippets of personal pages. [MIT Rubin page](https://www.mit.edu/~jlrubin/projects/pokerbots); [python_AutonomousPokerbot](https://github.com/ngnnah/python_AutonomousPokerbot)
- UNVERIFIED: Digg summary of Sequoia says a solo MIT entrant (@artemsaraiev) won the No Limit grand prize ($100,000) at a San Francisco final after placing fifth at the Boston regional; this may be a Sequoia competition, not MIT Pokerbots, and no strategy or date is given. [Digg](https://digg.com/ai/j8g1n1p2)
- UNVERIFIED: a UK Fullhouse Hackathon 2026 finalist described a GTO baseline plus opponent modeling that folded too often against strong opponents. [LinkedIn](https://www.linkedin.com/in/akbw)
- LLM-era arenas, 2025 to 2026: GTO Wizard agent beat leading LLMs in 5,000-hand heads-up matches (best LLM about -16 bb/100, a GPT-5.3 variant) [PokerNews April 2026](https://www.pokernews.com/news/2026/04/gto-wizard-ai-outperforms-gpt-5-and-grok-4-in-new-benchmark-51020.htm); GTO Wizard Benchmark API (arXiv, March 2026) [arXiv 2603.23660](https://arxiv.org/html/2603.23660); PokerSkill (arXiv 2605.30094, May 2026) LLM agents with a rule engine lose -57 to -87 mbb/hand to GTOWizard (default prompts -132 to -204), and a rules-only library scored -132 mbb/hand, similar to default LLMs [arXiv 2605.30094](https://arxiv.org/html/2605.30094v1). A January 2026 LLM Poker Arena report says frontier LLMs played far looser than professional ranges. [LLM Poker Arena](https://mattohan567.github.io/AI-Poker-Arena/)
- Yi and Yi (arXiv 2509.23747, Sept 2025): pure GTO does not maximize profit against weak opponents; self-play baseline then opponent-modeling adjustment; MCCFR best in heads-up. Abstract only, no win rates. [arXiv 2509.23747](https://arxiv.org/abs/2509.23747v1)

### Inferences
- Across ACPC and MIT sources, winning structure is a strong equilibrium baseline plus (sometimes) opponent adaptation; ACPC ranked by both bankroll and matches won, mirroring our "match wins then hands per win" ranking, and the two metrics produced different winners several years (2010 to 2013).
- No source gives numbers for beating heterogeneous amateur rule-based fields; designing for that field needs our own simulation of the observed population (75 percent button raise, 55 percent BB defend).

### Gaps
- No MIT Pokerbots 2025 or 2026 official winner write-up found. No Kaggle poker-bot competition evidence found. No ACPC 2017 or 2018 result pages retrieved (official site unreachable). No data on online bot arenas with amateur rule-based fields beyond the LLM benchmarks.

## 4. Optimizing match win probability (tournament utility) in CFR or RL, 2024 to 2026

### Takeaway
I found no 2024 to 2026 paper that trains CFR or RL on match win probability for heads-up matches. The relevant older line is the jam/fold tournament work (2007, 2008), which uses win probability or ICM as value.

### Cited Findings
- Miltersen and Sorensen (2007) compute strategies whose game values are tournament win probabilities (see section 1). [researchr](https://researchr.org/publication/MiltersenS07)
- Ganzfried and Sandholm (AAMAS 2008) compute approximate 3-player jam/fold equilibria using fictitious play, a value-iteration-like method for stochastic games and the ICM heuristic. [kilthub](https://kilthub.cmu.edu/articles/journal_contribution/Computing_an_Approximate_Jam_Fold_Equilibrium_for_3-player_No-Limit_Texas_Hold_em_Tournaments/6604343)
- UNVERIFIED, may be a course project: a Technion page proposes a learnable neural ICM module with a DQN. Authors and date not seen. [Technion CRML](https://crml.eelabs.technion.ac.il/?p=5615)
- SpinGPT (arXiv 2509.22387, 2025) targets 3-player Spin & Go with SFT then RL; no ICM objective seen in snippet. [arXiv 2509.22387](https://arxiv.org/pdf/2509.22387v2)

### Inferences
- A practical route is dynamic programming over (stack, blind level) states with the heads-up win probability as terminal value (the Miltersen and Sorensen structure), solving push/fold nodes by Nash, instead of RL.

### Gaps
- No 2024 to 2026 evidence located; search tool weak on arXiv. A targeted arXiv listing search ("tournament equity", "match win probability", "risk-sensitive CFR") was not done.
