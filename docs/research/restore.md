# Restore: continue the research on a clean machine (2026-11-27)

The test boxes are vendor loans and may go back. This page is what a new machine needs to pick up where the work
stopped: where the code, the models and the records are, which data has to be copied off the old box, how the
environment was built, and what comes next. The result record is `experiments.md`, the plan is `roadmap.md`.

## 1. Where everything is

| What | Where | Visibility |
|---|---|---|
| Research records (this folder) | github.com/waynehacking8/poker-ai-lab, branch `research`, `docs/research/` | public |
| Deploy branch and HANDOFF | same repo, branch `holdem-chipzen` (`docs/HANDOFF.md`, `docs/box-recall.md`) | public |
| Every work branch (42) and the box-only files | github.com/waynehacking8/poker-ai-lab-archive (all branches; `box-d-snapshot`; `desktop-leftovers`) | private |
| Training essentials (fb2 run with its value head, the v5 expert teachers `br_bp100`, `br_small_ball`, `br_chipzen`, the T-a teachers `br_ashwing`, `br_autofast`, the gate files, the test styles; 68 MB) | same archive, branch `train-essentials` (`box-d/<old home path>`, `SHA256SUMS`) | private |
| The shipped v5 commit | tag `v5-c1v5` on the archive = `c1v5-root` b14b176 | private |
| v5 package as uploaded | Chipzen bot `poker-ai-lab-v5` (uploaded 2026-11-27), image `holdem-v5-c1v5.tar.gz` sha256 3758ca7f...0840 | account |
| v5 runtime, weights, card, research copy | huggingface.co/waynehacking8/poker-ai-lab-hunl-v5 (private until the Season 16 playoffs end) | private |
| Python package lists, seed registry | `environment/` next to this page | public |

Clone everything with `git clone https://github.com/waynehacking8/poker-ai-lab-archive.git` (all branches come along),
then `git -c core.autocrlf=false` for every `git archive` that goes to a Linux box (CRLF breaks the shell scripts).

## 2. The code lines

Work was split into three trees that live side by side on the box, each an `git archive` copy of one branch:

| Tree on the box | Branch line (latest) | What it holds |
|---|---|---|
| `~/poker-ai-lab-rl` | `holdem-rl` b047c04, then per-slice branches ending in `-rl` (latest `g0b-rl` 9e413f6) | training: `rl/` PPO trainer (torch), `tools/rl_s2.sh`, `t1_run.sh`, `b1_run.sh`, `ckpt/`, `tools/seed_registry.txt` |
| `~/poker-ai-lab-x2r` (and per-run copies `~/<slice>-run/code-*`) | `holdem-x2r` 8be6e38, then per-slice branches without a suffix (latest `c1v5` 4767f28) | evaluation: arena drivers, judges and readers (`tools/*_drive.sh`, `*_judge.sh`, `*_read.py`), fault-plant runners |
| run roots `~/<slice>-run/code-root*` | per-slice branches ending in `-root` (latest `c1v5-root` b14b176) | what gets packaged: `rl/` runtime and bot classes, `deploy/` (Dockerfile, build and parity scripts), the pinned model files |
| `~/poker-ai-lab-league` | `holdem-league` 57a63b8 | the 23-opponent league, candidates, leaderboard (`out/`) |

To continue from v5: start the root tree from `c1v5-root`, the evaluation tree from `c1v5`, and the training tree
from `g0b-rl` (it builds the gate and the experts). Each slice's spec in `roadmap.md` names its branches and the
exact commands.

## 3. Environment

* Python 3.12.3. Training venv (`~/poker-ai-lab-rl/.venv`): `environment/requirements-rl-venv.txt` (torch 2.15.0 with the
  CUDA 13 wheels, numba 0.68.1, numpy 2.5.5, chipzen-bot 0.7.0, pytest 9.2.0). League venv:
  `environment/requirements-league-venv.txt` (numpy, chipzen-bot, pytest). The deployed bot needs numpy only.
* The training trainer picks CUDA when present and falls back to CPU. The old box was a 20-core ARM machine with
  one GPU and 121 GB of memory; arena runs used 6 to 18 worker processes.
* Docker with buildx for the Chipzen image, which is `linux/amd64`: on an ARM box install QEMU binfmt first
  (`docker run --privileged --rm tonistiigi/binfmt --install amd64`, lost at reboot). Build:
  `deploy/build_on_box.sh` and `deploy/remote_build.sh` on the root tree.
* Hosted limits the image must meet: 0.5 vCPU, 256 MB, 5 s per decision, under 200 MB, non-root user.

## 4. Data to copy off the old box (paths on gb10-d)

Code and the training essentials above are on GitHub. These are the larger results that cost hours or days to make again; sizes and the full list are in
`docs/box-recall.md` on `holdem-chipzen`.

| Priority | Path | Size | Needed for |
|---|---|---|---|
| 1 | `~/poker-ai-lab-rl/ckpt/` (68 runs; `fb2/it000900.npz` carries the PPO value head the deployed npz lacks; the v5 experts' teachers are `br_bp100` (T1) and `br_chipzen`) | 2.8 GB | any training that starts from fb2-900 or the experts |
| 1 | `~/poker-ai-lab-rl/tools/seed_registry.txt` (copy in `environment/`) | 4 KB | fresh-seed discipline: the next free seed is 121 |
| 1 | `~/chipzen-replays/` (44,169 public match files) | 4.1 GB | replay clones, the real-arena reads; about 54 h of paced fetching to redo |
| 2 | `~/bp-data/` (`blueprint-100bb.tar` and its abstraction) and `~/bp-logs/` | 4.1 GB | the bp100 opponent (the largest share of the field) |
| 2 | `~/poker-ai-lab-d2s2/data/g1` and `logs/` | 3.8 GB | the G1 per-name fine-tune data |
| 2 | `~/ad0-run/data*`, `~/v5b-run/data*` | 2.0 GB | distillation rows (about 97 min each to redo) |
| 1 | `~/poker-ai-lab-x2r/ckpt/br_small_ball/` (C1, the third v5 teacher) | 30 MB | rebuilding or extending the v5 experts |
| 3 | `~/poker-ai-lab-x2r/logs/`, `~/poker-ai-lab-league/out/` | 0.3 GB | raw rows behind every recorded result |
| 3 | `~/g0b-run/students/`, `~/g0b-run/styles_g0b.json`, `~/c1v5-run/styles_c1v5.json`, `~/v5b-run/styles.json` | small | the gate files and the generated test styles (exclusion lists for new styles) |

Not worth copying: model and Hugging Face caches, venvs, `bp-src` (upstream github.com/matteo-psnt/poker-solver).

## 5. First checks on the new machine

1. Clone the archive, archive `c1v5-root` into a run root and `c1v5` into an evaluation tree (LF endings).
2. Build the venvs from `environment/` and run each tree's slice tests (for the root: `tests/test_c1v5_root.py`,
   `test_g0b_root.py`, `test_rl_*.py`; the repo-wide `pytest` also collects old CFR tests that need pandas). In a
   tree without `.git`, set `C1V5_REF` to an archive of `27773b0` for the parity test. Rehearsed 2026-11-27 from a fresh
   clone of the archive: 80 passed, 5 skipped; the evaluation tree also runs its plant runner
   (`tests/c1v5_plants.py`: 130 of 130 caught on the old box).
3. Rebuild the v5 image from `c1v5-root` and check `rl/models/weights.npz` sha256 f7d22324...91e6 and the 17-file
   list in the image against the Hugging Face copy.
4. Rerun one cheap arena cell (for example `python -m rl.eval_arena --model rl/models/gs50.npz --opp ext:wolf
   --matches 200 --seed <smoke seed> --workers 6`) to confirm the engine and opponents load; use a seed outside the
   registry for smoke runs, so the next read still gets an untouched one.

## 6. Where the research stands and what is next

v5 (GS50: fb2-900 plus three experts behind an open-set opponent gate) passed the full upload gate (14.51) and is
uploaded to the account; Season 16 keeps v4 because the swap window closed on 23 Nov. v5 gains only where the gate
routes (bp100 +18.9, `small_ball` +20.1, `chipzen` +5.9) and plays as fb2-900 elsewhere. The open levers, in the
roadmap's order of evidence:

1. The Ashwing and autodidact families, where v5 equals fb2-900: the T-a experts (`br_ashwing` +16.0 and +15.4,
   `br_autofast` +13.4, 14.45) are trained and kept for later; the gate would need a class for each to route to them.
2. Real-arena measurement of v5 once it plays (Season 17 entry or challenges), since clones overstate (14.3, 14.36).
3. Revision 2's lookahead (14.17 to 14.24), parked until the opponent model at the root is good enough.

**State on 2026-11-27 (update with each read):**

1. E2 Stage 1 done (14.55, CONTINUE both): ashwing family {ext:ashwing, ext:ashwing_search}, autodidact family
   {ext:autodidact, ext:autodidact_fast}; rows in `~/poker-ai-lab-x2r/logs/e2/` on gb10-d, branch `e2` ddd487a.
2. R4R5 done (14.52 to 14.54, branch `r45` 973550f, `~/r45-run`): no evidence that T1 gains on any live name; Blueprint
   (15.4% of entrant-faced seats, T1 on 38.5% of hands) and NashForge (6.1%) go to the default.
3. V6 stage A ran and stopped (14.56, STOP_V6): a solver_live class cannot keep Blueprint off T1 while bp100 keeps
   it; on the gate's 14 terms the two overlap. Branches `v6` e23e5a9, `v6-root` 562cb58, `v6-rl` 79dc09a; box dir
   `~/v6-run`; seed 127 used. The next step is the roadmap agent's call (v6 without T1, other terms, or S1 and live
   play).
4. Box outputs of 14.52 to 14.56 (E2 Stage 1 rows and classes, R3, item 5, R4, the rule table, V6 stage A gates,
   lines and terms including the seed 127 fit-band rows V6b reuses) are on archive branch `train-essentials`,
   `results/results-20261127.tar.gz` (sha256 072e0849...2c2e, paths relative to the box home).
5. V6b was revised and reviewed twice, then STOPPED by Wayne on 2026-11-27 08:23 UTC before any run (roadmap "### V6b." Status): the known-opponent expert line is not a global solution. Partial build parked unverified on `v6-root` e9a9d95 and `v6-rl` 6d56896. Next: the global path plan (roadmap "Where we are", Redirect).
6. To resume on a new machine: ship the branches, copy `code-root` from `c1v5-root` b14b176, and relaunch a stage with
   its driver's restart flag (`E2_RESTART=1`, `R45_RESTART=1`, `V6_RESTART=1`); every driver refuses stale directories.
7. GP0 (roadmap "### GP0.", the global path's first slice, a measurement): its inputs are on `train-essentials` 88df139
   (`box-d/poker-ai-lab-rl/ckpt/s2/it001800.npz`, the G1 base fits `box-d/poker-ai-lab-d2s2/data/g1/*.pt` and
   `slice2k/fit_fold0_*.pt`, the D2a logs as `box-d/poker-ai-lab-d2s2/logs/d2a-<bot>.tar.xz` for ashwing,
   autodidact_fast and wolf; untar into `~/poker-ai-lab-d2s2/logs/d2/`); 18 hashes read back. Plan reviewed (READY),
   built on `gp0` e1424cd (archive only), build verifiers capped and fixed first-hand. Run dir `~/gp0-run` (code in
   `code/`, seeds 128 to 132 `GP0 read`). Stage 0 done (14.57, BASE-FLAT). Stage A done (14.58, A-HIGH, K rule cap; the first launch was lost to a
   reboot and discarded). Stage B done (14.59, NO-CARRY with MODEL-LOSS, GUARD FAIL on `sticky_overbettor`); the
   outcome row is Path C (model work, judged by Stage B again on fresh seeds), GP1 spec next from the roadmap agent.
   Results live in `~/gp0-run/stage{0,A,B}/` on gb10-d; a stage interrupted by a recall is rerun with
   `GP0_RESTART=1` (the old directory is moved aside), e.g.
   `cd ~/gp0-run/code && GP0_RESTART=1 setsid -f bash tools/gp0_drive.sh B > ~/gp0-run/driveB.out 2>&1 < /dev/null`.
8. `origin` (poker-ai-lab) is public: only research and holdem-chipzen go there; code branches with weights and
   `train-essentials` stay on the private archive (Wayne, 2026-11-27).

Process rules that held through the work: a written spec per slice, plan review and outcome verification, fresh
seeds from the registry for every read, counters on every judged run, and a fault-plant runner committed with the
tests.
