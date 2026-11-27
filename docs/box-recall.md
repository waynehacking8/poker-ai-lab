# Box recall inventory (2026-11-27 01:40 UTC)

The four test boxes (gb10-a to gb10-d) are on vendor loan and may be taken back on a date not yet known. This file records what on them is
not on GitHub and what would take long to produce again. Nothing has been moved yet.

## 1. Code on gb10-d that is in no pushed commit

Method: every code or small text file under the box home folders (`.py .sh .rs .toml .json .md ...`, at most 2 MB, skipping venv, cache,
logs, out, data and models folders) was hashed as a git blob and looked up in two lists: the blobs of every commit on
`origin` (github.com/waynehacking8/poker-ai-lab) and the blobs of every local branch on the PC checkout. The `poker-ai-lab-*` folders on the
box are `git archive` copies, so a matching blob means the file is in a commit; no path match is needed.

| Status | Files | Where it is now |
|---|---|---|
| In a pushed commit | 20,449 | GitHub, poker-ai-lab |
| Only in a local PC branch | 2,754 | PC checkout, 35 local branches with no remote plus 5 commits on holdem-league and 25 on holdem-rl |
| In no commit (box only) | 318 code and small result files, plus data | **pushed** to the private repo github.com/waynehacking8/poker-ai-lab-archive, branch `box-d-snapshot`, folder `box-d/` (read back: 318 files) |

The box-only set is small scripts and result summaries from the run folders (`ad0-run`, `c1v5-run`, `g0b-run`, `v5b-run`, `x3b-verify`,
`verify-h4`, `poker-ai-lab-x2a`, ...). Left out of the snapshot on purpose: `chipzen-replays` and `verify-holdem-data` (data, listed below),
`bp-src` (an unmodified copy of the open-source github.com/matteo-psnt/poker-solver v0.1.0, MIT), `poker-ai-lab-sim/.cache` and
`d2_timing/gen_*` (generated). No secret pattern (HF, OpenAI, GitHub, AWS tokens, private keys, bearer tokens) was found in the snapshot or
in the unpushed local commits.

Open: pushing the local branches to the private archive repo was refused by the session's permission classifier. The command, for Wayne
to run: `git -C C:/Users/WEI-CHENG/Desktop/poker-ai-lab push https://github.com/waynehacking8/poker-ai-lab-archive.git 'refs/heads/*:refs/heads/*'`.
They go to the private repo, not the public one, because they carry models still unpublished during Season 16 (`rl/models/gs50.npz`,
`s2_it1800.npz`, `b1.npz`, `blueprints/d*.bp`). The local branches sit on the PC, so the box recall alone does not lose them.

Other git repos on gb10-d (`claude-code-config`, `loop-eng`, `oss`) are clean with nothing unpushed. `~/gb10-agent` on the box is a deploy
copy, not a git checkout.

## 2. Results that are slow to produce again (gb10-d unless noted)

| What | Path | Size | Cost to redo |
|---|---|---|---|
| Blueprint 100bb | `~/bp-data/blueprint-100bb.tar` (+ `.sha256`) | 1.9 GB | the blueprint solve run; recorded in the research roadmap |
| Blueprint abstraction and runs | `~/bp-data/data` (`combo_abstraction`, `runs`) | 1.9 GB | same run |
| Blueprint training logs | `~/bp-logs` | 324 MB | same run |
| RL checkpoints | `~/poker-ai-lab-rl/ckpt` (68 runs: fb1, fb2, s2, s2b, br_*, spec_*, probe_*, ...) | 2.8 GB | hours each; fb2 holds the PPO value head that is not in the deployed npz |
| RL logs | `~/poker-ai-lab-rl/logs` | 173 MB | same runs |
| Other RL checkpoints | `~/d0-run/ckpt` 20 MB, `~/poker-ai-lab-x2r/ckpt` 30 MB, `~/b1-build/rl/ckpt` 11 MB, `~/poker-ai-lab-x2b/ckpt` 4 MB | 65 MB | |
| Packaged bots | `~/build-rl/*.tar.gz` (v5-c1v5, fb2-900-allin, h4-300, fb1-900, fb2-900, distill1) | 372 MB | rebuilt from commits in minutes |
| D2s2 data | `~/poker-ai-lab-d2s2/data/g1` (+ `g1_2a` 10 MB) | 2.9 GB | |
| D2s2 logs | `~/poker-ai-lab-d2s2/logs` | 938 MB | |
| AD0 and V5b fit data | `~/ad0-run/data.npz` + `data`, `~/v5b-run/data.npz` + `data` | 1.0 GB + 1.0 GB | about 97 min each (AD0 data, measured) |
| Chipzen replays | `~/chipzen-replays` (44,169 match files) | 4.1 GB | about 54 h of paced fetching (43,497 public matches at about 4.5 s, plus the 900 s rate-limit blocks) |
| League results | `~/poker-ai-lab-league/out` | 89 MB | |
| X2r logs (C1v5 rows live here) | `~/poker-ai-lab-x2r/logs` | 225 MB | C1v5 alone is about 4 h |
| gb10-agent desks | `~/gb10-agent/desks` (12: wayne, user2 to user10, full-user2, bench) | 534 MB | user state, cannot be redone |
| gb10-agent logs | `~/gb10-agent/logs` (166 files) | 304 MB | cannot be redone |
| gb10-agent data backups | `~/gb10-agent/data-bak-20261118.tgz`, `data-bak-20261119.tgz` | 5 KB | small |
| gb10-agent models | `~/gb10-agent/models` (Qwen3.6, Holo, Qwen3.8 NVFP4) | 125 GB | download again from Hugging Face |
| Eval data | `~/gb10-eval-data` (src-harvey-labs, financebench, legalbench-rag) | 4.0 GB | download again |
| TensorRT probe | `~/perf-probe/trt-oci` | 14 GB | image pull |

Other boxes, home folders only: gb10-c holds `~/.cache` 457 GB (model cache), `~/gb10-agent` 86 GB (models only, no desks) and `~/oss`
72 GB; gb10-a holds `~/workspce` and `~/fedgpt_data` (84 GB each, not from this project); gb10-b is empty.
