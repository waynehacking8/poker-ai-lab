# reports/

Per [`AGENTS.md`](../AGENTS.md): every experiment produces both a
chart and a Markdown report. This directory is the home of those
reports plus any non-PNG artifacts they cite.

| File | Phase | Topic |
|---|---|---|
| [`READING-GUIDE-zh.md`](READING-GUIDE-zh.md) | All | **中文閱讀指南** — how to read each report at 30-second / 3-minute / deep-dive cadence, with red-flag checklists and a concept-to-evidence map. Start here if you are walking a reviewer through the repo. |
| [`phase1-convergence.md`](phase1-convergence.md) | Phase 1 | CFR / MCCFR / CFR+ convergence on Kuhn and Leduc, with calibration sweeps and cross-checks against published Nash values. |
| [`mccfr-scaling.md`](mccfr-scaling.md) | Phase 1 (supplement) | Where MCCFR starts beating enum CFR+ — controlled scaling experiment on N-card Kuhn. Crossover at N ≈ 250-300; MCCFR 5× better at N = 400. |
| [`phase2-collusion-detection.md`](phase2-collusion-detection.md) | Phase 2 | End-to-end synthetic-collusion pipeline, LightGBM AUC, feature importances, ROC — reports both `shared_latency=True` (AUC 0.9995) and `shared_latency=False` (AUC 0.8245). |
| `phase2-metrics.json` | Phase 2 | Combined machine-readable diagnostics keyed by setting name. |
| `phase2-metrics-with_shared_latency.json` | Phase 2 | Diagnostics for the shared-latency-on run. |
| `phase2-metrics-without_shared_latency.json` | Phase 2 | Diagnostics for the adversarial baseline (uncorrelated latencies). |
| `phase2-roc-comparison.png` | Phase 2 | Side-by-side ROC for both settings — headline chart embedded in §4.2. |
| `phase2-roc-with_shared_latency.png` | Phase 2 | ROC for the shared-latency-on run only. |
| `phase2-roc-without_shared_latency.png` | Phase 2 | ROC for the adversarial baseline only. |
| `phase2-roc.png` | Phase 2 | Backwards-compat alias — same as `phase2-roc-with_shared_latency.png`. |

The PNG convergence plots referenced by Phase 1 live in
[`../results/`](../results/) (`convergence_kuhn.png`,
`convergence_leduc.png`) — they were generated first and we kept the
location for backwards compatibility rather than moving them here.

Regenerate everything:

```bash
python -m scripts.plot_convergence_kuhn
python -m scripts.plot_convergence_leduc
python -m scripts.generate_phase2_report_artifacts
```
