# FlashCFR Phase 1 Design — Vanilla CFR on Kuhn Poker (GPU)

Required pre-implementation deliverable from `docs/flashcfr-spec.md`
("Starting point"). This document defines kernel signatures, memory
layout, and the kernel-by-kernel work order **before any `.cu` file is
written**. The intent is to allow review of the algorithmic decisions
in isolation of CUDA implementation details.

This is a paper design produced on a GPU-less environment (macOS
Darwin). Kernel implementation is gated on review of this document and
on a machine with CUDA 12.x + an Ampere-class or newer GPU.

---

## 1. Scope of Phase 1

- **Game:** Kuhn Poker only. 12 information sets total, 6 chance
  outcomes (`(card_p0, card_p1)` permutations of `{J, Q, K}`).
- **Algorithm:** vanilla CFR with chance sampling — the same variant
  the CPU baseline (`cfr/algorithms/vanilla_cfr.py`) implements. CFR+
  and MCCFR variants come in later phases.
- **Goal:** GPU-learned average strategies match the CPU baseline up
  to seed-dependent noise, and iterations / second on Kuhn is ≥ 10× the
  CPU baseline at the same iteration count.
- **Non-goals for Phase 1:** Leduc, multi-GPU sharding, regret-table
  swapping to host memory, tensor cores. Kuhn is intentionally tiny so
  the design focus is "does the kernel pipeline give correct results",
  not "does it scale".

### CPU baseline numbers to beat

From `docs/roadmap.md` / `tests/test_kuhn_cfr.py`:

  iterations    expl    wall time (single-thread Python+NumPy)
       2 000   0.45      0.3 s
      20 000   0.012     2.4 s
     200 000   0.004    24 s

These set the validation thresholds. Phase 1 GPU run at 200k iterations
must reproduce expl ≤ 0.005 and finish in ≤ 2.4 s.

---

## 2. Why Kuhn first if it is "too small for GPU"

Kuhn fits in shared memory on a single SM. That is the *point*. A
correctness-bound Phase 1 wants the smallest game where every CFR step
is exercised — chance sampling, regret update, strategy averaging,
exploitability check — and where the GPU output can be **byte-for-byte
compared** to the CPU reference. Kuhn at 12 info sets × 2 actions =
24-element regret table is the smallest such game. Leduc (528 info
sets, variable action counts) is left for Phase 2 because its added
complexity does not stress different parts of the kernel design.

---

## 3. Tree representation

Pre-computed flat arrays, indexed by **(deal_idx, history_idx)** pairs.
The Kuhn tree expanded per deal has 5 terminal histories and 7
non-terminal histories (`'', 'p', 'b', 'pb', 'pp', 'pbp', 'pbb', 'bp',
'bb'`); deduplicated against the 6 deals there are at most
`6 × 12 = 72` reachable nodes. We materialize them at host startup and
copy to constant memory:

```c++
struct KuhnNode {
    int8_t  history_id;       // 0..11, index into histories[]
    int8_t  player;           // -1 terminal, 0 P0, 1 P1
    int8_t  info_set_id;      // -1 terminal, else 0..11 (per-player keys)
    int8_t  num_actions;      // always 2 for Kuhn
    int16_t child[2];         // node ids of children (or -1)
    float   terminal_util_p1; // valid iff player == -1
};
```

`KuhnNode tree[72]` lives in **constant memory** (read-only, broadcast
to all SMs). 72 * 12 bytes = 864 bytes — well under the 64 KB constant
budget.

The 12 information sets per player are enumerated upfront:

```
info_set_id  description
  0  "J:"     P0 at root with J
  1  "Q:"     P0 at root with Q
  2  "K:"     P0 at root with K
  3  "J:p"    P1 facing P0 check, holds J
  ...
 11  "K:pb"   P0 holds K, facing P1 bet after P0 check
```

A second constant array `int8_t info_set_owner[12]` records which
player owns each info set — needed for the cf-reach update.

---

## 4. Regret-table memory layout (struct-of-arrays)

Two **float32 arrays**, length 24 each (12 info sets × 2 actions),
device-resident in global memory:

```c++
float regret_sum[12 * 2];        // cumulative counterfactual regret
float strategy_sum[12 * 2];      // cumulative own-reach-weighted strategy
```

Indexing: `idx(info_set_id, action) = info_set_id * 2 + action`.

Two further arrays support reductions within a single iteration:

```c++
float current_strategy[12 * 2];  // regret matching output for this iter
float node_util[72];             // expected utility per traversed node
```

`node_util` is laid out per node-index so post-order updates can read
children directly. All four arrays start zero-initialized.

### Why SoA, not AoS

Vectorized regret matching loads `regret_sum[info_set_id, 0]` and
`regret_sum[info_set_id, 1]` for every info set simultaneously. In SoA
those two values are at `idx` and `idx + 1` — coalesced. AoS would
interleave them with `strategy_sum` and break the load pattern.

For Kuhn at 24 floats this is overkill — the arrays fit in a single
warp. The SoA discipline matters because the **same layout is reused
verbatim in Phase 2 for Leduc** (1056 floats), where coalescing does
start to dominate.

### Why FP32 throughout (not FP16/FP32 mixed)

Per `flashcfr-spec.md` Key Design Decisions §2 the spec recommends
mixed precision. For Phase 1 we **defer** that recommendation: FP32
throughout. Reasons:

1. The CPU reference is FP32 (NumPy float64 is overkill but matches).
   Comparing GPU FP32 to CPU FP32 is a straight equality check up to
   seed noise.
2. Kuhn fits in 24 floats. The memory savings of FP16 are irrelevant.
3. Numerical comparison against the CPU baseline is one of the Phase 1
   acceptance gates (exploitability within 0.005). Mixed precision
   introduces an extra source of divergence that confounds bug hunting.

Mixed precision belongs in Phase 2/3, where memory bandwidth dominates.
Record this as a new design decision (proposed `D10` in
`docs/design-decisions.md` after review).

---

## 5. Kernel-by-kernel work order

A single CFR iteration is decomposed into four kernels launched in
sequence. **One thread block per iteration** at Phase 1 — Kuhn is too
small to parallelize across info sets within an iteration without idle
warps. Iterations themselves are launched in a host loop; the CUDA
graphs capture path is a Phase 1.x optimization, not Phase 1.0.

### Kernel A: `regret_matching`

Compute `current_strategy[i]` from `regret_sum[i]` for all 12 info sets.

```c++
__global__ void regret_matching(
    const float* __restrict__ regret_sum,    // [24]
    float*       __restrict__ current_strategy  // [24]
);
```

- Grid: 1 block, 12 threads. Each thread handles one info set.
- Per-thread work: read `regret_sum[2*i]` and `regret_sum[2*i+1]`, max
  with 0, sum; if sum > 0 normalize, else write 0.5 / 0.5.
- No shared memory needed at this scale.

### Kernel B: `sample_chance`

Pick one of the 6 Kuhn deals uniformly at random.

```c++
__global__ void sample_chance(
    curandState* __restrict__ rng_state,
    int*         __restrict__ chosen_deal       // [1]
);
```

- Grid: 1 block, 1 thread. cuRAND XORWOW.
- Deal index also implies the root node index in the precomputed tree
  (we materialize one tree per deal at startup, see §3). The kernel
  writes `chosen_deal` for downstream kernels to read.

### Kernel C: `traverse_and_accumulate`

The CFR recursion, unrolled. Computes `node_util[]` post-order for the
12 nodes reachable from the chosen deal's root, and accumulates regrets
and strategy sums.

```c++
__global__ void traverse_and_accumulate(
    const int*   __restrict__ chosen_deal,        // [1]
    const float* __restrict__ current_strategy,   // [24]
    float*       __restrict__ regret_sum,         // [24]
    float*       __restrict__ strategy_sum,       // [24]
    float*       __restrict__ node_util_scratch   // [72]
);
```

- Grid: 1 block, 16 threads (32 threads/warp; padding wasted lanes).
- The Kuhn tree per deal has depth ≤ 3 (root → response → response).
  Threads are mapped to leaves first, then walk up in two reduction
  steps.
- Reach probabilities are FP32, threaded through registers — no shared
  memory. Each thread holds its own `(reach_p0, reach_p1)` pair.
- Regret and strategy_sum updates use `atomicAdd` on the global arrays.
  At Kuhn scale conflicts are rare; correctness still requires atomics
  because multiple threads can target the same info set (post-order
  reduction visits sibling subtrees).

### Kernel D: `iteration_done`

Synthetic barrier kernel — no compute. Exists so the host can stream
iterations without `cudaDeviceSynchronize()` after each. Replaces with
CUDA Graphs in Phase 1.x.

### Per-iteration cost (estimate)

72 nodes × FP32 work ≪ 1 µs of compute. Launch overhead (3 × ~5 µs ≈
15 µs/iter) dominates. The single-block design accepts that on Kuhn —
the win comes from running 10 000+ iterations as one CUDA graph
launch in Phase 1.x.

---

## 6. Exploitability check (off-iteration)

Reuses the CPU two-pass best-response (`cfr.evaluate.exploitability
.best_response_value`) for validation: download `strategy_sum` to host,
normalize to `policy: dict[info_set, np.ndarray]`, run the CPU
evaluator. Phase 1 does not implement a GPU best-response; the CPU
evaluator on Kuhn runs in milliseconds and is the reference oracle.

A GPU best-response is a Phase 2/3 deliverable, after the algorithm
shape stabilizes on Leduc.

---

## 7. Host-side driver and Python API

A thin pybind11 module exposes `flashcfr.train_kuhn(iterations, seed)`,
returning a host-side dict matching `cfr.algorithms._state.policy_table`
output shape. The drop-in compatibility with the CPU baseline is what
makes regression testing trivial:

```python
from cfr.games import kuhn
from cfr.evaluate.exploitability import exploitability
import flashcfr  # built C++ extension

policy = flashcfr.train_kuhn(iterations=200_000, seed=0)
assert exploitability(kuhn, policy) < 0.005
```

The CPU CFR convention (current-player-perspective return + per-call
sign-flip — see `vanilla_cfr.py:54-94`) **must be preserved in the GPU
implementation**. This is the only way GPU and CPU policies are
directly comparable info-set by info-set.

---

## 8. Work order (when implementation begins)

When implementation begins on a CUDA-equipped machine, the proposed
sequence is:

1. **Build skeleton** — pybind11 extension, empty kernels, CMake. Goal:
   `flashcfr.train_kuhn(0, 0)` returns the zero-strategy policy and
   tests run end-to-end with no CUDA errors.
2. **Tree materialization on host** — port the Kuhn game module's
   `is_terminal` / `current_player` / `next_history` / `info_set_key`
   into a host-side function that emits the `KuhnNode tree[]` array.
   Unit test: golden file comparing the emitted tree to a hand-checked
   reference.
3. **Kernel A in isolation** — regret matching only. Seed
   `regret_sum[]` with known values, call the kernel, compare
   `current_strategy[]` to a NumPy implementation. Reproducible on
   small data.
4. **Kernel C in isolation** — traversal + accumulation. Seed
   `current_strategy[]` to uniform, run a single iteration, compare
   `regret_sum[]` and `strategy_sum[]` to the CPU baseline (one
   recursive call, same seed).
5. **Full driver** — host loop over 200k iterations, verify final
   policy against CPU baseline. Acceptance: exploitability ≤ 0.005.
6. **Performance pass** — CUDA Graphs over the 4-kernel sequence,
   measure iterations / sec, target 10× CPU.

Each step has an isolated acceptance criterion. Diverging from the CPU
baseline at any step is a stop-the-line bug — do not paper over it by
loosening tolerances.

---

## 9. Open questions to resolve at implementation time

These are deferred to when CUDA hardware is available; recording them
here so they are not silently re-litigated:

1. **cuRAND state placement.** Per-thread state in registers vs.
   per-block in shared memory vs. global. For Phase 1 (1 RNG draw per
   iteration) any of the three works. Default proposal: global, sized
   to one state per CUDA stream — see `flashcfr-spec.md` Key Design
   Decisions §3.
2. **CUDA Graph capture timing.** Phase 1.0 launches kernels
   individually; Phase 1.1 captures the per-iteration sequence as a
   graph. Open question: capture once and replay, or recapture each
   iteration to allow exploitability probes mid-training? Initial
   stance: capture once, probe out-of-graph at preset checkpoints (the
   same pattern `scripts/plot_convergence_kuhn.py` uses on the CPU).
3. **Atomic contention measurement.** Phase 1.0 uses naive `atomicAdd`.
   If profiling on Phase 2 (Leduc, 528 info sets) shows contention, we
   move to warp-level reductions then a single `atomicAdd` per warp.
   Defer the optimization until profiling justifies it.

---

## 10. Relation to the CPU reference

The CPU code path remains the ground-truth validator. Every Phase 1
test in this design's §8 work order compares against the CPU baseline
defined in `cfr/algorithms/vanilla_cfr.py`. Do not modify the CPU code
to accommodate the GPU port.

If the GPU and CPU disagree at any acceptance gate, the GPU is wrong
until proven otherwise — the CPU baseline already matches the published
Kuhn Nash equilibrium and Lanctot 2013's Leduc reference value.

---

## 11. Status

This document **is** the Phase 1 pause point requested by
`flashcfr-spec.md` §"Starting point" and `HANDOFF.md` §"Where to start".

Implementation begins after:

  - Review of this document, and
  - Recording any deviations from §3-5 (tree layout, FP32 default,
    kernel decomposition) as new `D{n}` entries in
    `docs/design-decisions.md`, and
  - Verification that the implementation environment provides CUDA
    12.x and an Ampere-or-newer GPU.

No CUDA source code exists yet by intent. Do not start writing kernels
without first updating this design with whatever review notes come
back.
