# Reproduce the first selective-correction study

This directory contains a bounded computational study, not a calibrated hardware simulator. Read [[First Research Draft]] for results, failures, and publication boundaries.

## Files

- `gbs_selective_correction_study.py`: predeclared development/held-out sweep; local Gaussian moments; normalized selected-feature models; exact evaluation; iid sample generation.
- `gbs_selective_cost_audit.py`: independent pipeline rebuilds, three randomized-order timing repeats, isolated traced allocation peaks, recovery and permutation checks.
- `gbs_selective_report.py`: regenerate the summary, research draft, and scientific figures from raw results.
- `gbs_projection_probe.py`: existing exact-probability and Haar-interferometer helper. Its separate phase-space experiment is not executed by this study.

Run these from a checkout/copy of the GBS Classical Simulation folder with Python 3.11 and the recorded dependencies. The commands use paths relative to that folder:

```powershell
python -m pip install -r work/requirements-selective-study.txt
python -X utf8 work/gbs_selective_correction_study.py --declare
python -X utf8 work/gbs_selective_correction_study.py
python -X utf8 work/gbs_selective_cost_audit.py
python -X utf8 work/gbs_selective_report.py
```

The declared grid is 36 development instances and 108 held-out instances. All random seeds are explicit. The programs use one numerical-library thread. On the recorded machine the main sweep took about 63 seconds; the isolated audit runs additional fits. Timing will vary by machine and load. All model probabilities were reproduced exactly in the audit on the original environment.

Reruns replace files in `outputs/selective_correction_v1/`. Use a separate checkout/copy to preserve the original measured timings. `--limit` is a development smoke-run option; it produces an incomplete result set and is not the reported study.

## Evidence locations

- `outputs/selective_correction_v1/protocol.json`: hypotheses, exact grid, budgets, endpoints, strict failure and success gates.
- `frozen_selection.json`: development means and the rule chosen before held-out evaluation.
- `results.json`: every instance, every method, optimizer flags, physical/reference checks, primary and secondary errors, selected detector groups and original instrumented costs.
- `distributions/*.npz`: all 144 exact/reference and approximate probability tables plus interferometers, covariance matrices, and squeezing vectors.
- `cost_audit.json`: repeated untraced wall times, isolated whole-pipeline traced memory, query/feature counts, and exact rebuild agreement.
- `verification.json`: artifact completeness, probability rebuild, full-order recovery, output-permutation and protocol-hash checks.
- `environment.json`: environment, numerical-thread details and main-study source hashes.
- `summary.json`: aggregate and paired descriptive results, full cell grid, all flagged cases, metric ranking reversals, and sensitivity results.
- `accuracy_cost.png` and `.pdf`: plot for the draft.

## Interpretation constraints

The fitting and iid table-sampling architecture enumerates all `2**M` bit strings. It is suitable for small exact tests and supplies no large-system runtime claim. Full held-out reference distributions are constructed only after fitting and never used to select features. Local Gaussian marginal information is allowed on every instance and is charged to preprocessing.

The TAP comparison implements arXiv:2109.11525v2 Eqs. 4–5 literally, with the stationary distribution enumerated. It does not reproduce the paper's Gibbs chains or its measured experimental performance. Negative off-diagonal square-root discriminants are flagged unsupported rather than clipped.

The initial `traced_peak_bytes` field sums phase allocation peaks and is a conservative proxy. Use the isolated whole-pipeline peaks in `cost_audit.json` for memory comparisons. Python-traced allocation is not total native process memory. Keep optimizer abnormal terminations in primary results; the draft includes a separate strict-validity sensitivity analysis.

The supplementary scripts are also captured in `artifact_manifest.json` with file hashes so report and audit provenance remain inspectable.
