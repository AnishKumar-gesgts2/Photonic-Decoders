"""Write the audit findings without overwriting the original experiment."""
import hashlib
import json
from pathlib import Path
import gbs_selective_correction_study as s

def main():
    out=s.ROOT/'outputs'/'skeptical_audit_v1'
    summary=json.loads((out/'summary.json').read_text())
    matched=json.loads((out/'matched_cost_summary.json').read_text())
    original=json.loads((s.OUT/'summary.json').read_text())
    aliases={'original_residual':'Original selected correction','optimized_residual':'Same selection, shared feature construction',
        'all_pair_shortlisted_triples':'Keep every queried shortlist triple',
        'one_aggregate_shortlist_feature':'One aggregate triple feature',
        'exact_gaussian_vacuum_plus_mobius':'Exact vacuum + fast inclusion–exclusion'}
    table='| Method | Mean full TVD (lower is better) | Median preprocessing including CDF (ms) | Median traced peak (KiB) |\n|---|---:|---:|---:|\n'
    for name,label in aliases.items():
        v=matched[name]
        err=f'{v["mean_full_tvd"]:.5f}' if name!='exact_gaussian_vacuum_plus_mobius' else f'{v["mean_full_tvd"]:.2e}'
        table+=f'| {label} | {err} | {v["median_preprocessing_ms"]:.2f} | {v["median_traced_peak_kib"]:.1f} |\n'
    exact=matched['exact_gaussian_vacuum_plus_mobius']['vs_optimized_residual']
    small=matched['one_aggregate_shortlist_feature']['vs_optimized_residual']
    minclick,maxclick=summary['mean_target_click_range']
    text=f'''# Skeptical Audit and Stronger Benchmarks

**October 2, 2026 — supersedes the performance interpretation in [[First Research Draft]].** The original study and its artifacts remain preserved. This audit reuses its 108 held-out instances; the new comparisons are retrospective controls, not a newly held-out confirmation.

## Finding

The original TVD numbers are numerically credible, but the benchmark was too weak to justify excitement about a cheaper GBS simulation algorithm. The strongest omitted control is exact calculation: at the tested sizes it obtains essentially zero approximation error, is much cheaper on the typical case, and strictly beats the selected approximation on accuracy, preprocessing time, and traced memory in {exact['strict_dominance']} of 108 cases. The remaining six cases do not pass the time criterion; exact accuracy is better in all 108. This is a **no-go for the current enumerated architecture as a computational improvement**. It remains useful for studying information allocation.

## Why a 37% improvement was plausible

The baseline deliberately matches only one- and two-detector moments. The corrected model receives additional exact three-detector information and fits extra parameters using the complete model output space. Choosing moments the baseline gets wrong is a reasonable optimization heuristic, so improving its fit is expected. The experiment tests which added information helps; it does not solve the large-system sampling problem.

The improvement is relative: TVD decreases from 0.10575 to 0.06641, an absolute reduction of about 0.03933. It is not “37% more accurate than the papers,” a percentage of correctly generated shots, or a 37-point probability improvement. Both numbers are aggregate errors on synthetic small systems.

There are only 64, 256, or 1,024 possible output strings in the 6-, 8-, or 10-mode cases. Target mean click counts range from {minclick:.3f} to {maxclick:.3f}. Fitting sums over every output string, and iid sampling draws from a stored full table. These conveniences remove the central challenge that matters at experimental scale. New interferometer seeds within the same family also do not establish transfer to new circuit structures or noise models.

The previous measured residual-to-pairwise ratios were {original['paired_comparisons']['pair_maxent']['median_time_ratio']:.2f} for time and {original['paired_comparisons']['pair_maxent']['median_traced_peak_ratio']:.2f} for traced memory. Thus the correction bought lower error with more computing resources. It had already failed the predeclared strict dominance gate against both pairwise and all-triple fitting; a positive emphasis on error reduction alone overstated the practical evidence.

## Independent numerical check

All 108 complete reference distributions were checked against **The Walrus 0.22.0 Torontonian implementation**, with the covariance convention explicitly set to $\\hbar=1$. The maximum reference-to-library full TVD was {summary['max_independent_reference_tvd']:.2e}. Matrix preparation and click-pattern indexing were also checked against the public `threshold_detection_prob` API on three patterns per instance. Every covariance passed the library's physical-validity check. This confirms the reference arithmetic independently of our original inclusion–exclusion routine; it does not verify hardware calibration or scalability. [The Walrus sampling and threshold-probability documentation](https://the-walrus.readthedocs.io/en/latest/code/samples.html)

No held-out full probability table supplied the original fitting targets or feature rankings. Its exact local Gaussian marginal targets are legitimate characterized-model information. The issue is comparator adequacy and scope, rather than an identified leakage or probability-formula error.

## Stronger comparisons actually run

{table}

All methods start from the same covariance. The matched run uses three independent timing repetitions in randomized method order for each instance and includes construction of the cumulative sampling table. Traced memory is measured separately over each whole pipeline. It excludes native allocations not visible to Python; these are not total-process memory claims. The exact calculation enumerates all subset vacuum determinants and uses a fast $O(M2^M)$ inclusion–exclusion transform. It still scales exponentially and is not proposed as a large-experiment simulator.

The optimized residual implementation shares feature construction with the new correction controls and produces exactly the same model probabilities as the original. This separates an algorithmic comparison from avoidable matrix-construction overhead. The exact method's median within-instance time ratio to that optimized correction was {exact['median_paired_time_ratio']:.3f}, and its traced-memory ratio was {exact['median_paired_memory_ratio']:.3f}. We did not charge independent reference validation to the exact sampler or the approximations, because that audit is evaluation rather than model preparation.

**Use all the queried information.** The original residual rule calculates half of all triple targets but retains only one quarter of all triple features. Keeping all the queried targets reduces mean TVD to {matched['all_pair_shortlisted_triples']['mean_full_tvd']:.5f}, better on all 108 instances, without any extra local-statistic queries. Fitting more parameters costs additional time and memory relative to the optimized residual pipeline, so this is not strict equal-cost dominance. It shows why local-query savings alone were an inadequate performance argument.

**Simple aggregate correction.** One added feature is the normalized sum of every shortlisted triple's spin product, instead of a separate adjustable parameter for each selected triple. It uses the same queried moments. Mean TVD is {matched['one_aggregate_shortlist_feature']['mean_full_tvd']:.5f}, worse on average than residual selection, but it is more accurate in {small['tvd_wins']} cases and strictly dominates the optimized residual pipeline on error/time/traced memory in {small['strict_dominance']}. Simple controls can challenge parts of the claimed selection benefit.

**Repeated random selection.** We ran 20 independent random selections per instance: 2,160 fits. Their overall mean TVD was {summary['mean_random_20_tvd']:.5f}. Residual selection was better than each instance's random-draw mean in {summary['residual_wins_vs_per_instance_random_mean']} of 108 cases, and better than the best of 20 random draws in {summary['residual_wins_vs_best_of_20_oracle']} cases. The latter is an oracle diagnostic, because choosing the best random draw uses full evaluation answers and is not a deployable comparison. {summary['random_fit_flags']} random fits missed the strict optimizer-status gate; their errors remain included. This supports a real selection effect within this synthetic family, but does not establish novelty or practical superiority.

An additional fairness limitation remains: the original random control deliberately queried the whole half-size shortlist to match the selection rule's query budget, though a practical random sampler could query only the chosen quarter. That makes it an information-allocation control, not the strongest cost-efficient random baseline. Its equal-query advantage cannot be restated as a universal equal-compute advantage.

## What a genuinely stronger published-method benchmark requires

The most directly relevant next comparator is **Dodd et al.'s cumulant-informed chain-rule emulator**. It addresses generating strings without our full-output partition-function enumeration. A fair comparison needs a faithful authors' implementation or carefully validated reproduction, the same covariance/detector model, declared accuracy targets, preprocessing and sampling costs, complete memory accounting, and no silent repairs to negative approximate probabilities. [Dodd et al., A fast and frugal Gaussian Boson Sampling emulator](https://arxiv.org/html/2511.14923)

The current printed-TAP comparison is not a satisfactory primary state-of-the-art benchmark. It evaluates only the small-system stationary distribution defined by printed equations, has unsupported discriminants, and does not reproduce published Gibbs-chain behavior or experimental results. It should remain auxiliary until its implementation and domain are verified against an authoritative source. [Villalonga et al.](https://arxiv.org/html/2109.11525)

I have **not** benchmarked the selected correction against an actual Dodd, tensor-network, or phase-space implementation in this audit. Calling the new controls a reproduction of those papers would be incorrect. Once a non-enumerating correction architecture exists, the next benchmark should include those competitors and new locked instance families, followed by calibrated experimental subsystems. Larger sizes alone will not fix this benchmark if the same exponential fitting method remains in place.

## Revised decision and project scope

1. **Numerical result:** retained; independent reference calculation agrees, and targeted selection usually outperforms random feature choice.
2. **Computational advantage of this implementation:** rejected on the tested small systems; exact calculation is the stronger omitted competitor.
3. **Publication readiness:** not established. The next contribution must be a practical cost improvement over strong methods or a substantively new validation finding. Adding correct correlations and lowering fit error is insufficient by itself.
4. **Next work:** verify published baselines and redesign fitting/sampling so that selected correlations reduce actual costs without enumerating every outcome. Develop and choose on new development instances, then evaluate once on newly locked test families. Stop or pivot if that architecture cannot beat simple controls.

The original first draft is a record of the initial experiment. This audit corrects its positive performance emphasis and supplies a more demanding comparison; it does not erase the original measurements.

## Reproducibility

The audit used an isolated environment with The Walrus 0.22.0, leaving the original environment unchanged. With that library and the original study dependencies installed, run from the GBS project directory:

```powershell
python -X utf8 work/gbs_skeptical_audit.py
python -X utf8 work/gbs_skeptical_matched_costs.py
python -X utf8 work/gbs_skeptical_report.py
```

Audit specs were written before their respective control runs. `outputs/skeptical_audit_v1/` retains all 108 cases, independent-reference discrepancies, every random draw, fit flags, aggregate control results, repeated matched costs, summary tables, and source hashes. The first-stage artifacts in `outputs/selective_correction_v1/` were not replaced. New-control budgets are fixed for this audit; they were not selected from new held-out outcomes.
'''
    report=s.ROOT/'Skeptical Audit and Stronger Benchmarks.md'
    report.write_text(text,encoding='utf-8')
    files=[p for p in out.rglob('*') if p.is_file() and p.name!='artifact_manifest.json']+[report]+list((s.ROOT/'work').glob('gbs_skeptical*.py'))
    manifest={str(p.relative_to(s.ROOT)).replace('\\','/'):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in files}
    (out/'artifact_manifest.json').write_text(json.dumps(manifest,indent=2))
    print(report)

if __name__=='__main__':main()
