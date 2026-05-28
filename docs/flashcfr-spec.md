# FlashCFR Specification

Detailed specification for a CUDA-accelerated CFR library. This is
the primary work order for the GPU environment.

---

## Background and Motivation

Inspired by FlashLib (Berkeley/MIT, 2026) which achieved 20–200×
speedup on classical ML algorithms (KMeans 26×, KNN 19×,
TruncatedSVD 208×, t-SNE 147×) by rewriting CUDA kernels for modern
GPU architectures.

In the LLM era, GPUs are dominated by transformer workloads,
leaving classical algorithms like CFR (Counterfactual Regret
Minimization) without serious GPU optimization. Current mainstream
CFR implementations (OpenSpiel, PokerKit, custom research code)
mostly run on CPU or use NumPy with minimal vectorization.

CFR's workload is actually highly GPU-friendly:

- Massive parallelism across information sets.
- Regular memory access patterns on regret tables.
- Predictable data flow (no dynamic branching at the hot path).
- Data sizes (GB-scale regret tables) match GPU memory hierarchy.

**Goal:** Build "FlashCFR" — a CUDA-accelerated CFR library
targeting 20–100× speedup over existing implementations.

---

## Scope and Deliverables

Build a working prototype with the following components.

### 1. Core CFR engine (CUDA)

- Implement Vanilla CFR and MCCFR (External Sampling variant) on GPU.
- Target test bed:
  - Kuhn Poker (validation).
  - Leduc Hold'em (benchmark).
  - HU Limit Hold'em (scaling).
- Validate convergence by tracking exploitability vs the existing
  CPU implementation in this repo (Phase 1) and against OpenSpiel
  reference numbers.

### 2. GPU-optimized hot-path kernels

Custom CUDA kernels for:

**(a) Hand Strength Evaluation Kernel**
- Input: batch of (hole_cards, board_cards) pairs.
- Output: win probability vs all opponent hand combinations.
- Optimization targets: coalesced memory access, warp-level
  parallelism, shared memory for lookup tables.

**(b) Regret Matching Kernel (fused)**
- Single kernel: `max(0, regret) -> sum -> normalize -> sample`.
- Avoid multiple kernel launches and intermediate global-memory
  writes.
- Target: process millions of infosets in one kernel invocation.

**(c) Counterfactual Value Computation Kernel**
- Batched expected-value computation across opponent hand range.
- Use Tensor Cores where possible (mixed precision: FP16 compute,
  FP32 accumulate).

**(d) Strategy Update Kernel**
- In-place update of cumulative strategy with time-weighting
  (CFR+ style).
- Atomic operations for concurrent infoset updates.

### 3. Memory layout design

- Layout regret table for coalesced access — **struct-of-arrays**,
  not array-of-structs.
- Pin frequently-accessed structures in shared / constant memory.
- Design memory tiling for game trees that exceed single-GPU memory.
- Support gradient checkpointing for the Deep CFR variant.

### 4. Hand bucketing pipeline (FlashLib integration)

- Use FlashLib's GPU KMeans for card abstraction.
- Build EHS (Effective Hand Strength) and OCHS feature vectors on
  the GPU.
- Pipeline: `hand_features (GPU) -> KMeans (FlashLib) -> bucket
  assignment table`.

### 5. Performance prediction interface

Mimic FlashLib's 5-microsecond GPU-runtime predictor:

- Given: game tree size, abstraction parameters, iteration count.
- Predict: GPU memory usage, expected runtime per iteration.
- Use lightweight regression on key kernel parameters.

### 6. Benchmarking suite

Compare against:

- OpenSpiel Python CFR (baseline).
- OpenSpiel C++ CFR (compiled baseline).
- Any existing GPU-CFR research code if available.

Metrics to report:

- Iterations per second.
- Time to reach exploitability threshold (mbb/g).
- GPU utilization (nvprof / Nsight Compute).
- Memory bandwidth achieved vs theoretical peak.

---

## Technical Constraints

- Language: CUDA C++ with PyTorch / Python bindings for usability.
- Target hardware: NVIDIA H100 / A100 / consumer RTX 40 series.
- CUDA version: 12.x.
- Dependencies allowed: cuBLAS, cuRAND, Thrust, CUB, FlashLib.
- Must produce correct results — exploitability matches reference
  implementations within tolerance.

---

## Implementation Phases

### Phase 1 (Validation) — Vanilla CFR on Kuhn Poker

- Pure GPU implementation, verify against this repo's existing CPU
  CFR (which reaches exploitability 0.004 at 200k iterations and
  game value -1/18).
- Establish testing infrastructure and exploitability measurement.

### Phase 2 (Scaling) — MCCFR on Leduc Hold'em

- Add External Sampling.
- Profile with Nsight Compute, identify bottlenecks.
- Optimize top 3 hottest kernels.

### Phase 3 (Realistic) — CFR+ on HU Limit Hold'em

- Add the hand-bucketing pipeline using FlashLib KMeans.
- Implement multi-GPU support for regret-table sharding.
- Benchmark against OpenSpiel and report speedup.

### Phase 4 (Frontier, optional) — Deep CFR

- Replace tabular regret storage with a neural network.
- Integrate PyTorch for the network components.
- Compare sample efficiency vs the tabular version.

---

## Key Design Decisions to Make Upfront

1. **Tree representation**: flat array (GPU-friendly) vs pointer-
   based (flexible)?
   Recommend: flat array with pre-computed traversal order.

2. **Mixed precision**: where to use FP16 vs FP32?
   Recommend: FP16 for regret computation, FP32 for cumulative
   strategy.

3. **Sampling strategy for MCCFR**: deterministic seeded vs cuRAND?
   Recommend: cuRAND for true parallelism, with deterministic
   seeding for reproducibility.

4. **Python API design**: drop-in replacement for OpenSpiel or new
   abstraction?
   Recommend: OpenSpiel-compatible API for easy adoption.

When you commit to one of these, record the rationale as a new
`D{n}` entry in `docs/design-decisions.md`.

---

## Deliverables Format

For each phase, produce:

1. Working code with build instructions.
2. Benchmark results vs reference implementations.
3. Profiling report — memory bandwidth utilization, SM occupancy,
   warp efficiency.
4. Documentation explaining the key design choices.

---

## Stretch Goals

- Subgame solving acceleration (for Libratus-style nested
  re-solving).
- Real-time inference mode for online poker bots (sub-100ms
  decision latency).
- Distributed multi-node training using NCCL.
- Comparison with JAX-based OpenSpiel CFR.

---

## Reference Materials

- Zinkevich et al. 2007 — original CFR paper.
- Tammelin et al. 2014 — CFR+.
- Lanctot et al. 2009 — MCCFR.
- Brown et al. 2019 — Deep CFR.
- FlashLib repo (Berkeley) — kernel design patterns.
- Nsight Compute documentation for GPU profiling.

---

## Starting point

Begin with **Phase 1: Design the data structures and kernel layout
for Kuhn Poker CFR on GPU.** Before writing any CUDA code, produce:

1. Proposed CUDA kernel signatures.
2. Memory layout — specifically the regret-table struct-of-arrays.
3. An implementation plan that lists kernel-by-kernel work order.

Commit this as a design document at `docs/flashcfr-phase1-design.md`
and pause for review. Only after the design is sound should kernel
implementation begin.

---

## Relation to existing repository content

The existing CPU CFR implementation (Phase 1.1–1.3 in
`docs/roadmap.md`) remains in the repository as the **ground-truth
validator** for FlashCFR. Do not delete or rewrite the CPU code;
FlashCFR's correctness will be measured against it on Kuhn Poker.

The CPU code path:

- `cfr/games/kuhn.py` — game tree.
- `cfr/algorithms/vanilla_cfr.py` — Neller & Lanctot 2013 style
  vanilla CFR. **This convention** (cfr returns current-player
  perspective, recursive calls negate) **should be preserved in the
  GPU implementation** so policies are directly comparable.
- `cfr/evaluate/exploitability.py` — brute-force exploitability,
  the ground truth comparator at small game sizes.

Phase 1 of FlashCFR should reproduce identical learned strategies
(up to seed-dependent noise) and identical exploitability curves.
Diverging from the CPU baseline at this scale would indicate a bug.
