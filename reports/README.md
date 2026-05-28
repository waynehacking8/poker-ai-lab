# reports/

Per [`AGENTS.md`](../AGENTS.md): every experiment produces both a
chart and a Markdown report. This directory is the home of those
reports plus any non-PNG artifacts they cite.

| File | Phase | Topic |
|---|---|---|
| [`phase1-convergence.md`](phase1-convergence.md) | Phase 1 | CFR / MCCFR / CFR+ convergence on Kuhn and Leduc, with calibration sweeps and cross-checks against published Nash values. |
| [`phase2-collusion-detection.md`](phase2-collusion-detection.md) | Phase 2 | End-to-end synthetic-collusion pipeline, LightGBM AUC, feature importances, ROC. |
| `phase2-metrics.json` | Phase 2 | Machine-readable diagnostics referenced by the §4 results table. |
| `phase2-roc.png` | Phase 2 | ROC curve embedded in the Phase 2 report. |

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
