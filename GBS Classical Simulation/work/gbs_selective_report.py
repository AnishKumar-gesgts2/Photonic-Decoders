"""Generate the first research draft and figures directly from saved outputs."""
import itertools
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from gbs_selective_correction_study import ROOT,OUT,PROTOCOL,sha

LABELS={'independent':'Independent','tap_printed':'Printed TAP stationary model',
        'pair_maxent':'All pairs (Q2)','pair_selected':'Pair-ranked quarter triples',
        'residual_selected':'Residual-ranked quarter triples',
        'random_shortlist':'Random quarter from same shortlist','uniform_triples':'All triples (Q3)'}

def bootstrap(values):
    x=np.asarray(values)
    rng=np.random.default_rng(102026)
    means=x[rng.integers(len(x),size=(2000,len(x)))].mean(axis=1)
    return [float(v) for v in np.quantile(means,[.025,.975])]

def main():
    data=json.loads((OUT/'results.json').read_text())
    audit=json.loads((OUT/'cost_audit.json').read_text())
    assert len(audit['rows'])==108
    rows=[x for x in data['rows'] if x['split']=='heldout']
    costs={x['id']:x['methods'] for x in audit['rows']}
    verification=json.loads((OUT/'verification.json').read_text())
    summary={}
    for name in LABELS:
        vals=[r['methods'][name] for r in rows if 'full_tvd' in r['methods'][name]]
        summary[name]={'evaluated':len(vals),'unsupported':108-len(vals),
            'invalid_gate':sum(not r['methods'][name]['valid_fit'] for r in rows),
            'mean_full_tvd':float(np.mean([v['full_tvd'] for v in vals])),
            'mean_count_tvd':float(np.mean([v['click_count_tvd'] for v in vals])),
            'mean_full_tvd_ci95':bootstrap([v['full_tvd'] for v in vals]),
            'mean_cumulant3_rms':float(np.mean([v['click_cumulant_rms']['3'] for v in vals])),
            'median_iid_sampling_ms_100k':float(1000*np.median([v['iid_table_sampling_seconds_100k'] for v in vals]))}
        if name in costs[rows[0]['id']]:
            cv=[costs[r['id']][name] for r in rows]
            summary[name].update(median_preprocessing_ms=float(1000*np.median([c['median_preprocessing_seconds'] for c in cv])),
                median_traced_peak_kib=float(np.median([c['isolated_traced_peak_bytes'] for c in cv])/1024))
    pairs={}
    for other in ['pair_maxent','pair_selected','random_shortlist','uniform_triples']:
        gain=np.array([r['methods'][other]['full_tvd']-r['methods']['residual_selected']['full_tvd'] for r in rows])
        pairs[other]={'mean_tvd_reduction':float(gain.mean()),'paired_bootstrap_ci95':bootstrap(gain),
                     'wins':int(sum(gain>1e-8)),'ties':int(sum(abs(gain)<=1e-8)),'losses':int(sum(gain < -1e-8))}
        if other in costs[rows[0]['id']]:
            times=np.array([costs[r['id']]['residual_selected']['median_preprocessing_seconds']/costs[r['id']][other]['median_preprocessing_seconds'] for r in rows])
            peaks=np.array([costs[r['id']]['residual_selected']['isolated_traced_peak_bytes']/costs[r['id']][other]['isolated_traced_peak_bytes'] for r in rows])
            pairs[other].update(median_time_ratio=float(np.median(times)),median_traced_peak_ratio=float(np.median(peaks)),
                accuracy_and_time_wins=int(sum((gain>1e-8)&(times<=1))),
                strict_accuracy_time_memory_dominance=int(sum((gain>1e-8)&(times<=1)&(peaks<=1))))
    cells=[]
    for m,f,r,eta in itertools.product(PROTOCOL['modes'],PROTOCOL['source_fractions'],PROTOCOL['squeezing'],PROTOCOL['transmission']):
        cell=[x for x in rows if (x['modes'],x['source_fraction'],x['squeezing'],x['transmission'])==(m,f,r,eta)]
        cells.append({'modes':m,'source_fraction':f,'squeezing':r,'transmission':eta,
            'means':{name:float(np.mean([x['methods'][name]['full_tvd'] for x in cell])) for name in ['pair_maxent','pair_selected','residual_selected','random_shortlist','uniform_triples']}})
    failures=[{'id':r['id'],'method':name,'message':v.get('message',v.get('unsupported_reason')),
               'moment_error':v.get('max_matched_moment_error')} for r in rows for name,v in r['methods'].items() if not v['valid_fit']]
    disagreements={};examples=[]
    core=['pair_maxent','pair_selected','residual_selected','random_shortlist','uniform_triples']
    for metric in ['click_count_tvd','cumulant3_rms']:
        total=0;count=0
        for row in rows:
            for a,b in itertools.combinations(core,2):
                av,bv=row['methods'][a],row['methods'][b]
                d=av['full_tvd']-bv['full_tvd']
                dm=(av['click_count_tvd']-bv['click_count_tvd']) if metric=='click_count_tvd' else (av['click_cumulant_rms']['3']-bv['click_cumulant_rms']['3'])
                if abs(d)>1e-8 and abs(dm)>1e-8:
                    total+=1
                    if d*dm<0:
                        count+=1
                        examples.append({'id':row['id'],'metric':metric,'a':a,'b':b,'a_full':av['full_tvd'],'b_full':bv['full_tvd'],'a_metric':av['click_count_tvd'] if metric=='click_count_tvd' else av['click_cumulant_rms']['3'],'b_metric':bv['click_count_tvd'] if metric=='click_count_tvd' else bv['click_cumulant_rms']['3']})
        disagreements[metric]={'reversals':count,'non_tied_comparisons':total}
    clean=[r for r in rows if all(r['methods'][n]['valid_fit'] for n in core)]
    sensitivity={n:float(np.mean([r['methods'][n]['full_tvd'] for r in clean])) for n in core}
    selection='residual_selected'
    reduction=1-summary[selection]['mean_full_tvd']/summary['pair_maxent']['mean_full_tvd']
    retained=(summary['pair_maxent']['mean_full_tvd']-summary[selection]['mean_full_tvd'])/(summary['pair_maxent']['mean_full_tvd']-summary['uniform_triples']['mean_full_tvd'])
    result={'methods':summary,'paired_comparisons':pairs,'cells':cells,'strict_failures':failures,
        'validation_ranking_disagreements':disagreements,'ranking_disagreement_examples':examples,
        'relative_mean_tvd_reduction_vs_pair':reduction,'aggregate_uniform_gain_retained':retained,
        'all_strict_core_fits_valid_sensitivity':{'cases':len(clean),'means':sensitivity},
        'verification':verification}
    (OUT/'summary.json').write_text(json.dumps(result,indent=2))
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(2,2,figsize=(12,9),layout='constrained')
    colors={'pair_maxent':'#52749c','residual_selected':'#bd541e','random_shortlist':'#888888','uniform_triples':'#347863'}
    for name,color in colors.items():
        means=[];lows=[];highs=[];tim=[];mem=[]
        for m in PROTOCOL['modes']:
            rr=[x for x in rows if x['modes']==m]
            x=[r['methods'][name]['full_tvd'] for r in rr];lo,hi=bootstrap(x)
            means.append(np.mean(x));lows.append(np.mean(x)-lo);highs.append(hi-np.mean(x))
            tim.append(np.median([costs[r['id']][name]['median_preprocessing_seconds'] for r in rr])*1000)
            mem.append(np.median([costs[r['id']][name]['isolated_traced_peak_bytes'] for r in rr])/1024)
        axes[0,0].errorbar(PROTOCOL['modes'],means,yerr=[lows,highs],marker='o',label=LABELS[name],color=color,capsize=3)
        axes[0,1].plot(PROTOCOL['modes'],tim,marker='o',label=LABELS[name],color=color)
        axes[1,0].plot(PROTOCOL['modes'],mem,marker='o',color=color)
    axes[0,0].set(ylabel='Mean full-distribution TVD (lower is better)',title='Held-out accuracy (36 instances per size)')
    axes[0,0].legend(fontsize=8)
    axes[0,1].set(ylabel='Median preprocessing time (ms)',title='Isolated fitting + selection (3 timing repeats)')
    axes[1,0].set(ylabel='Median traced peak allocation (KiB)',title='Whole pipeline; excludes untraced native memory')
    a=np.array([x['methods'][selection]['full_tvd'] for x in rows]);b=np.array([x['methods']['random_shortlist']['full_tvd'] for x in rows])
    for m in PROTOCOL['modes']:
        idx=np.array([x['modes']==m for x in rows]);axes[1,1].scatter(b[idx],a[idx],s=25,label=f'{m} modes',alpha=.8)
    axes[1,1].plot([0,max(b.max(),a.max())],[0,max(b.max(),a.max())],'--',color='#555555')
    axes[1,1].set(xlabel='Random-selection TVD',ylabel='Residual-selection TVD',title='Same shortlist queries and fitted feature budget')
    axes[1,1].legend(fontsize=8)
    for ax in axes.flat:
        ax.grid(alpha=.15)
    for ax in [axes[0,0],axes[0,1],axes[1,0]]:
        ax.set(xlabel='Output modes',xticks=PROTOCOL['modes'])
    fig.suptitle('Selective correlation correction: bounded small-GBS study',fontsize=15)
    fig.savefig(OUT/'accuracy_cost.png',dpi=180)
    fig.savefig(OUT/'accuracy_cost.pdf')
    plt.close(fig)
    table='| Method | Cases | Mean full TVD | Mean click-count TVD | Strict gate failures |\n|---|---:|---:|---:|---:|\n'
    for name,s in summary.items():
        table+=f'| {LABELS[name]} | {s["evaluated"]} | {s["mean_full_tvd"]:.5f} | {s["mean_count_tvd"]:.5f} | {s["invalid_gate"]} |\n'
    cost_table='| Method | Median preprocessing (ms) | Median traced peak (KiB) | Median iid table sampling, 100k shots (ms) |\n|---|---:|---:|---:|\n'
    for name in colors:
        s=summary[name]
        cost_table+=f'| {LABELS[name]} | {s["median_preprocessing_ms"]:.2f} | {s["median_traced_peak_kib"]:.1f} | {s["median_iid_sampling_ms_100k"]:.2f} |\n'
    paired_table='| Comparator | Mean TVD reduction by residual rule | Descriptive paired 95% interval | Wins / ties / losses |\n|---|---:|---|---|\n'
    for name,s in pairs.items():
        lo,hi=s['paired_bootstrap_ci95'];paired_table+=f'| {LABELS[name]} | {s["mean_tvd_reduction"]:.5f} | [{lo:.5f}, {hi:.5f}] | {s["wins"]} / {s["ties"]} / {s["losses"]} |\n'
    cell_table='| Modes | Source fraction | r | Transmission | Q2 TVD | Pair-selected | Residual-selected | Random-selected | Q3 TVD |\n|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n'
    for c in cells:
        cell_table+=f'| {c["modes"]} | {c["source_fraction"]} | {c["squeezing"]} | {c["transmission"]} | '+' | '.join(f'{c["means"][n]:.5f}' for n in core)+' |\n'
    ptime=pairs['uniform_triples']['median_time_ratio'];pmem=pairs['uniform_triples']['median_traced_peak_ratio']
    randomtime=pairs['random_shortlist']['median_time_ratio']
    case_example=next((e for e in examples if e['metric']=='click_count_tvd'),None)
    example_text=''
    if case_example:
        e=case_example
        example_text=f'For example, `{e["id"]}` ranks {LABELS[e["a"]]} and {LABELS[e["b"]]} differently: full TVD is {e["a_full"]:.5f} versus {e["b_full"]:.5f}, while click-count TVD is {e["a_metric"]:.5f} versus {e["b_metric"]:.5f}. This is a diagnostic reversal on a synthetic instance, not an assessment of a published experimental conclusion.'
    text=f'''# Selective Correlation Correction for Small Gaussian Boson Sampling Systems

**First research draft — October 2, 2026.** Completed computational first-stage study; manuscript-development material, not a submission-ready paper.

## Abstract

We tested whether selected three-detector dependencies improve a pairwise classical approximation of threshold Gaussian boson sampling (GBS). The predeclared suite contains 144 synthetic optical instances: 36 for development and 108 held out, spanning 6, 8, and 10 output modes, two source fractions, two squeezing values, and three transmissions. A normalized exponential-family model was fitted using exact local Gaussian moments. A residual-based rule, frozen after development, retained one quarter of all triple features after querying one half. Mean held-out full-distribution total variation distance (TVD) fell from {summary['pair_maxent']['mean_full_tvd']:.5f} for all-pair fitting to {summary[selection]['mean_full_tvd']:.5f}, a {100*reduction:.1f}% reduction. Random selection at the same feature and local-query budgets gave {summary['random_shortlist']['mean_full_tvd']:.5f}; uniform third-order fitting gave {summary['uniform_triples']['mean_full_tvd']:.5f}. Targeted selection preserved {100*retained:.1f}% of the aggregate TVD improvement obtainable by adding every triple. It remained less accurate than uniform third-order fitting on every held-out instance. The study supports selective information allocation at small scale, while its enumerated fitting architecture prevents a scalable-sampler claim.

## 1. Research question and relationship to existing work

The question is which detector groups deserve additional computation when all higher-order dependencies cannot be afforded. Merely showing that lower-order moments do not fix a complete distribution is established background. The testable contribution here is a reproducible comparison of two frozen selection rules with a random control, exact distribution error, and measured costs.

The eventual experimental target is the **Jiuzhang 2.0 threshold-click task**, chosen to connect to a tractable correlation-based reference. Villalonga et al. describe Boltzmann-machine and greedy approximations built from low-order marginals. We implemented the stationary Boltzmann distribution defined by the printed TAP parameter equations, and independent-output sampling. We enumerate those distributions exactly at small scale rather than reproduce their Gibbs chain, implementation speed, or experimental-data analysis. [Villalonga et al.](https://arxiv.org/html/2109.11525)

Dodd et al.'s cumulant-informed chain-rule emulator and Goodman et al.'s phase-space sampler are additional competitors for a future algorithmic claim; neither was implemented in this draft. Jiuzhang 4.0 provides a later, different experimental target. The present result does not measure any of these methods' errors or overturn their claims. [Dodd et al.](https://arxiv.org/html/2511.14923), [Goodman et al.](https://arxiv.org/html/2604.12330), [Jiuzhang 4.0](https://arxiv.org/html/2508.09092)

This is an initial nearest-literature check, not a completed systematic novelty review. No Strikeout List was found in this research vault. Selective feature fitting is not claimed as a new general statistical idea.

## 2. Optical model and locked study design

Each instance starts with independent single-mode squeezed vacuum inputs, a seeded Haar-random complex interferometer, uniform optical transmission, and ideal threshold detection. Modes $M\\in\\{{6,8,10\\}}$, source fraction $f\\in\\{{0.5,1\\}}$, squeezing $r\\in\\{{0.4,0.8\\}}$, and transmission $\\eta\\in\\{{0.4,0.7,0.95\\}}$ form 36 cells. Active sources occupy the first $fM$ inputs. Each cell has one development interferometer and three independent held-out interferometers. No distinguishability, thermalization, dark counts, hardware calibration, or click-number conditioning enters model fitting.

With quadrature vacuum variance $1/2$, the covariance is

$$V=\\eta S(U)V_{{\\mathrm{{in}}}}S(U)^T+(1-\\eta)I/2,$$

where $V_{{\\mathrm{{in}}}}=\\operatorname{{diag}}(e^{{-2r_i}}/2,e^{{2r_i}}/2)$ in all-position/all-momentum ordering. Vacuum probabilities of small mode subsets are computed from $\\det(V_A+I/2)^{{-1/2}}$. Complete threshold-click probabilities are obtained by inclusion–exclusion only after all candidate models have been finalized. Exact threshold detection is the relevant physical reference formalism. [Quesada, Arrazola, and Killoran](https://arxiv.org/abs/1807.01639)

The protocol was saved before results, with SHA-256 `{data['protocol_sha256']}`. Interferometer seeds, physical parameters, optimizer settings, failure rules, budgets, and endpoints are retained in `protocol.json` and `results.json`. Development selected the residual rule by lower mean TVD ({data['selection']['development_mean_tvd']['residual_selected']:.5f} versus {data['selection']['development_mean_tvd']['pair_selected']:.5f}); `frozen_selection.json` records that choice before the held-out stage. Held-out full probabilities never supply fitting targets or feature rankings.

## 3. Selective correction architecture

Let $s_i=2x_i-1$ and $F_S(x)=\\prod_{{i\\in S}}s_i$. For a feature set $\\mathcal F$, we fit

$$Q_{{\\mathcal F}}(x)=Z^{{-1}}\\exp\\left(\\sum_{{S\\in\\mathcal F}}\\theta_S F_S(x)\\right).$$

All one-mode and pair features are retained. L-BFGS-B matches their targets and the selected triple targets using an explicitly summed partition function. Thus $Q$ is nonnegative and normalized, and can generate independent samples from its stored cumulative probability table. The $2^M$ enumeration is intentional for diagnosis and is the principal scaling limitation.

**Pair rule:** rank every triple by the sum of absolute normalized pair covariances within it; retain the top quarter. **Residual rule:** shortlist the top half using that pair score, calculate their local triple targets, and retain a quarter of all triples using $|\\langle F_S\\rangle_P-\\langle F_S\\rangle_{{Q_2}}|/\\sqrt{{\\max(1-\\langle F_S\\rangle_{{Q_2}}^2,10^{{-12}})}}$. Local targets use small-subsystem determinants; the prediction uses the fitted pairwise model. **Random control:** query the identical shortlist, then retain a randomly chosen quarter of all triples from it. The random control matches local-query and fitted-feature budgets; measured wall time and memory are evaluated separately. **Uniform comparator:** retain all triples. All corrected models start from the pairwise fit and pay for that fit.

| Modes | Pair features | Selected triple features | Queried residual/random triples | Uniform triple features |
|---:|---:|---:|---:|---:|
| 6 | 21 | 5 | 10 | 20 |
| 8 | 36 | 14 | 28 | 56 |
| 10 | 55 | 30 | 60 | 120 |

Candidate ranking interactions remain possible: a large individual residual is a heuristic, not an exact additive prediction of TVD improvement. We did not use an oracle full-TVD ranking or exhaustively optimize combinations.

## 4. Held-out results

{table}

The TAP mean uses only its 84 supported cases and must not be compared directly with 108-case means as though the populations matched. Negative square-root discriminants made the printed approximation unsupported in 24 held-out instances. This is an applicability boundary in this implementation and synthetic grid, not a disproof of the published experiment. Its table sampler also does not reproduce the paper's Gibbs runtime.

{paired_table}

The residual rule improves on the pairwise model in all 108 cases, and on random selection in 107 with one numerical tie. It loses to uniform third-order fitting in all 108. The ratio of aggregate mean improvements retained is {100*retained:.1f}%; a mean of per-instance retained fractions is a different statistic. Bootstrap intervals use 2,000 paired resamples and describe this heterogeneous synthetic suite; they do not establish transfer to hardware or larger mode counts.

![Accuracy and resource measurements](outputs/selective_correction_v1/accuracy_cost.png)

## 5. Computing costs and the success criterion

{cost_table}

Timing was repeated three times per held-out case in randomized method order with one numerical-library thread. The covariance is given to each pipeline. Costs include local targets, pair fitting, shortlisting, residual calculations, and correction fitting; they exclude exact full-reference generation and evaluation. Memory is an isolated whole-pipeline traced allocation peak, not total process RSS or GPU memory. All methods retain exponentially sized tables, so their small-system iid sampling speeds are not evidence of scalability.

The median within-instance residual-to-uniform preprocessing ratio is {ptime:.3f}, and its traced-memory ratio is {pmem:.3f}. Its residual-to-random time ratio is {randomtime:.3f}. These are medians of paired ratios, not ratios of the summary-table medians. Under the predeclared strict gate of lower TVD with no greater preprocessing time and traced memory, residual selection dominates the pairwise and uniform comparators in **{pairs['pair_maxent']['strict_accuracy_time_memory_dominance']} and {pairs['uniform_triples']['strict_accuracy_time_memory_dominance']} of 108 cases**, respectively. Against the random control, strict dominance occurs in {pairs['random_shortlist']['strict_accuracy_time_memory_dominance']} cases; lower TVD with no greater time occurs in {pairs['random_shortlist']['accuracy_and_time_wins']}.

**Interpretation:** selected triples buy a substantial fraction of third-order accuracy with fewer features and lower measured cost than uniform fitting, but do not establish a general same-accuracy/lower-cost replacement for a published sampler. They cost additional computation relative to Q2. A cheaper intermediate approximation and a strict Pareto improvement over the baseline are different findings.

The first run's `traced_peak_bytes` adds stage allocation peaks and is a conservative proxy, not a true simultaneous high-water mark. This was caught during audit. All memory conclusions above use `cost_audit.json`, which measures an isolated pipeline end to end. `preprocessing_seconds` in the first run is instrumented; the table above uses the repeated untraced audit. Both records are retained.

## 6. Validation, failures, and what summary scores miss

All 144 exact distributions passed probability checks. Analytic vacuum, zero-transmission, and independent squeezed-input checks passed; the largest local-vs-full spin-moment discrepancy was {max(r['local_vs_full_moment_error'] for r in data['rows']):.2e}. Photon-expectation conservation and output-mode permutation checks passed. A full-order four-mode fit recovered its reference with TVD {verification['full_order_recovery_tvd']:.2e}. Isolated pipeline rebuilds reproduced stored probabilities to maximum error {verification['probability_rebuild_max_error']:.2e}.

Every residual-selected held-out fit passed the strict convergence/tolerance gate. One pair-selected fit and two uniform fits ended with an abnormal line-search status even though their maximum matched-moment errors were below $10^{{-6}}$. They remain in the main tables and are flagged in raw results. Excluding all three affected cases leaves {len(clean)} cases and the same method ordering (Q2 {sensitivity['pair_maxent']:.5f}; residual {sensitivity['residual_selected']:.5f}; uniform {sensitivity['uniform_triples']:.5f}). No failed case was silently discarded or replaced.

Across non-tied comparisons among the five core models, click-count TVD reversed the full-TVD ranking in {disagreements['click_count_tvd']['reversals']} of {disagreements['click_count_tvd']['non_tied_comparisons']} comparisons. Third-order click-cumulant RMS reversed it in {disagreements['cumulant3_rms']['reversals']} of {disagreements['cumulant3_rms']['non_tied_comparisons']}. These comparisons share instances and are descriptive counts, not independent significance tests. {example_text}

The raw results also retain spin-moment RMS through order four, click-cumulant RMS at orders three/four, and conditional TVD in every click sector whose target mass is at least 1%. Conditional sector scores do not replace the primary unconditional endpoint. Each method generated 100,000 iid table samples three times; sample-to-model discrepancies validate the generator separately from approximation error to the physical target.

## 7. Where this sits in the complete project

| Stage from the project description | Current status | Remaining evidence |
|---|---|---|
| Define target and published comparison | First choices made | Obtain calibration/samples for Jiuzhang 2.0; verify an authors' implementation |
| Specify selection rules and normalized architecture | Implemented and tested | Replace full enumeration with a practical fitting/sampling method |
| Expand exact cases and lock held-out evaluation | Completed first grid: 144 cases | New locked circuit families, larger sizes, additional noise mechanisms |
| Test selective corrections against uniform order | Completed at 6–10 modes | Matched accuracy targets and time/memory budgets; stronger published comparators |
| Revise the scientific claim from measured results | Completed | Establish novelty and robustness before a submission claim |
| Experimental benchmark and scaling | Not completed | Same calibration, observations, conditioning and validation tests as hardware |
| Publishable contribution | Not established | New method or substantive validation finding beyond known truncation limitations |

We have moved from a nine-instance feasibility probe to a completed first selective-correction benchmark. The full project is still in **small-system algorithm validation**, before scalable algorithm and experimental benchmarking. An overall percent-complete estimate would be misleading because the later algorithmic contribution depends on whether the evidence survives those stages.

## 8. Does a paper require a better algorithm or an analysis of existing papers?

There are two defensible publication routes. **An algorithm paper** needs a specified new method, convincing novelty, and a reproducible accuracy–cost advantage over strong named alternatives on matched tasks. “Better” must mean the same accuracy for less time/memory, or better accuracy within the same measured budget. The current result motivates this route but does not complete it: our solver enumerates every bit string and no Dodd, tensor-network, or phase-space implementation has been beaten.

**A benchmarking/validation paper** can succeed without a superior simulator if it contributes a new, robust finding about a validation metric, a failure regime, a calibration mismatch, or a resource estimate. It would require faithful reproductions and stronger evidence than simply restating papers or confirming that low-order statistics are incomplete. Our ranking reversals and selective-versus-random result are starting findings, not established novelty or experimental refutations.

**Decision:** continue the selective-allocation idea, but do not prepare a submission claiming improved large-scale classical GBS simulation yet. The next decisive step is to port the selection into a method that does not enumerate $2^M$ outcomes, establish fitting/sampling reliability, and compare with at least a faithful cumulant-chain-rule implementation. Reproducing a published implementation and analyzing its results are necessary groundwork; a new algorithm or a new substantiated scientific finding supplies the paper's contribution.

Before extending to the hardware benchmark: (1) complete the nearest-literature and code audit; (2) freeze a second grid including new circuit structures and noise settings; (3) test multiple selection budgets with training separated from evaluation; (4) compare at fixed declared TVD thresholds on exact cases, including full costs and mixing checks if MCMC is used; (5) move to calibrated experimental subsystems and the same published validation tests only after the scalable architecture passes. A failure at stages 2–4 should narrow the claim or trigger a documented pivot to validation analysis, not be hidden.

## 9. Reproducible artifacts

The implementation is `work/gbs_selective_correction_study.py`; isolated cost measurement is `work/gbs_selective_cost_audit.py`; this report is generated by `work/gbs_selective_report.py`. `outputs/selective_correction_v1/` contains the protocol, frozen rule, every per-case result, cost audit, environment and source hashes, verification results, summary, figure PNG/PDF, and 144 compressed optical/probability artifacts. See [the reproduction instructions](work/SELECTIVE_STUDY_README.md).

## Appendix: every predeclared held-out cell

Each entry averages its three independent interferometers. No unfavorable cell is omitted. All per-instance and conditional-sector data remain in the raw artifacts.

{cell_table}
'''
    (ROOT/'First Research Draft.md').write_text(text,encoding='utf-8')
    print(json.dumps({'means':summary,'paired':pairs,'verification':verification,'rank_disagreements':disagreements},indent=2))

if __name__=='__main__':
    main()
