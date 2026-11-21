Vendored copy of `br/` from branch `holdem-br` (git show holdem-br:br/*.py). ManiacBR is the exact best
response to the maniac baseline (87.55 percent over 2000 arena matches). Needs numba (`pip install numba`) and
the table `data/maniac_k25.npz`. Used only as a training-time teacher by `rl/teacher.py`, never deployed.
