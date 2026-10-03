"""Retrospective challenge of v1; preserve all original records.

Run with The Walrus 0.22.0 in an isolated environment. This reuses the v1
held-out suite, so new controls are exploratory, not a new confirmatory test.
"""
import gc
import itertools
import json
import math
import time
import tracemalloc
from pathlib import Path
import numpy as np
from threadpoolctl import threadpool_limits
from thewalrus import tor, threshold_detection_prob
from thewalrus.quantum import Qmat, is_valid_cov
import thewalrus
import gbs_selective_correction_study as s

DEST=s.ROOT/'outputs'/'skeptical_audit_v1'
SPEC={'status':'retrospective controls on original 108 held-out instances; no new held-out claim',
    'controls':['all_pair_shortlisted_triples','one_aggregate_shortlist_feature','20_random_shortlist_draws','exact_gaussian_vacuum_plus_mobius'],
    'independent_reference':'The Walrus 0.22.0 Torontonian, hbar=1; every pattern on 108 instances',
    'budget':'same pair-based shortlist (half of all triples); same local triple queries for new correction controls',
    'random_draws':20,'timing':'three untraced full pipeline builds; one separate traced peak; covariance given; CDF construction included',
    'no_retuning':'Original residual rule/budget unchanged; all new controls reported, including losses.',
    'scope':'Tests numerical correctness, comparator adequacy and small-system cost; does not reproduce Dodd et al.'}

def torontonian_distribution(v):
    m=len(v)//2
    q=Qmat(v,hbar=1)
    o=np.eye(2*m)-np.linalg.inv(q)
    denominator=np.sqrt(np.linalg.det(q)).real
    result=np.empty(1<<m)
    for pattern in range(1<<m):
        sites=[j for j in range(m) if pattern>>j&1]
        inds=sites+[j+m for j in sites]
        result[pattern]=float(np.real(tor(o[np.ix_(inds,inds)])))/denominator
    # Verify matrix preparation/subsetting against the public library API.
    for pattern in (0,1,(1<<m)-1):
        bits=(pattern>>np.arange(m))&1
        api=threshold_detection_prob(np.zeros(2*m),v,bits,hbar=1)
        assert abs(api-result[pattern])<1e-11
    return result

def exact_mobius(v):
    m=len(v)//2
    vacuum=np.ones(1<<m)
    for mask in range(1,1<<m):
        sites=[j for j in range(m) if mask>>j&1]
        inds=sites+[j+m for j in sites]
        sign,ld=np.linalg.slogdet(v[np.ix_(inds,inds)]+np.eye(len(inds))/2)
        assert sign>0
        vacuum[mask]=np.exp(-ld/2)
    p=vacuum[::-1].copy()
    # Fast inclusion-exclusion: O(M 2^M) after determinants rather than 3^M.
    for j in range(m):
        width=1<<j
        blocks=p.reshape(-1,width*2)
        blocks[:,width:]-=blocks[:,:width]
    assert p.min()>-1e-10 and abs(p.sum()-1)<1e-10
    p=np.maximum(p,0);p/=p.sum()
    cdf=np.cumsum(p)
    return p, {'determinant_queries':(1<<m)-1,'cdf_bytes':cdf.nbytes}

def setup(v):
    loc,g2,target2,spins,f2,mu,c=s.pair_targets(v)
    q2,theta2,info=s.fit(f2,target2)
    triples=s.subsets(len(mu),3)
    rho=c/np.sqrt(np.outer(np.diag(c),np.diag(c)))
    ranked=sorted(triples,key=lambda t:(-sum(abs(rho[a,b]) for a,b in itertools.combinations(t,2)),t))
    shortlist=ranked[:math.ceil(len(triples)/2)]
    target=np.array([loc.spin(t) for t in shortlist])
    ft=np.column_stack([np.prod(spins[:,t],axis=1) for t in shortlist]).astype(float)
    return loc,g2,target2,f2,theta2,shortlist,target,ft

def fit_control(setup_data,kind,seed):
    loc,g2,t2,f2,theta2,shortlist,tt,ft=setup_data
    if kind=='one_aggregate_shortlist_feature':
        norm=np.sqrt(len(shortlist))
        extra=ft.sum(axis=1,keepdims=True)/norm
        target_extra=np.array([tt.sum()/norm])
    elif kind=='all_pair_shortlisted_triples':
        extra=ft;target_extra=tt
    elif kind=='random_shortlist':
        m=int((math.sqrt(1+8*len(g2))-1)/2)
        budget=math.ceil(math.comb(m,3)/4)
        idx=np.sort(np.random.default_rng(seed).choice(len(shortlist),budget,replace=False))
        extra=ft[:,idx];target_extra=tt[idx]
    else:
        raise ValueError(kind)
    f=np.column_stack([f2,extra]);target=np.r_[t2,target_extra]
    q,_,info=s.fit(f,target,np.r_[theta2,np.zeros(extra.shape[1])])
    cdf=np.cumsum(q)
    return q,dict(info,fitted_features=len(target),determinant_queries=len(loc.vac)-1,cdf_bytes=cdf.nbytes)

def pipeline(v,kind,seed):
    if kind=='exact_gaussian_vacuum_plus_mobius':
        return exact_mobius(v)
    return fit_control(setup(v),kind,seed)

def measured_pipeline(v,kind,seed,p):
    times=[]
    for _ in range(3):
        t=time.perf_counter();q,info=pipeline(v,kind,seed);times.append(time.perf_counter()-t)
    gc.collect();tracemalloc.start()
    q,info=pipeline(v,kind,seed)
    _,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
    return dict(info,full_tvd=float(abs(p-q).sum()/2),preprocessing_repeats_seconds=times,
                median_preprocessing_seconds=float(np.median(times)),traced_peak_bytes=int(peak))

def main():
    DEST.mkdir(parents=True,exist_ok=True)
    (DEST/'audit_spec.json').write_text(json.dumps(SPEC,indent=2))
    d=json.loads((s.OUT/'results.json').read_text())
    rows=[x for x in d['rows'] if x['split']=='heldout']
    results=[]
    tor(np.zeros((2,2),dtype=complex)) # compile warm-up outside timing
    for i,row in enumerate(rows):
        a=np.load(s.OUT/'distributions'/f'{row["id"]}.npz')
        v,p=a['covariance'],a['p']
        assert is_valid_cov(v,hbar=1)
        start=time.perf_counter();pt=torontonian_distribution(v);tor_sec=time.perf_counter()-start
        error=float(abs(pt-p).sum()/2)
        assert error<1e-9
        controls={}
        kinds=['all_pair_shortlisted_triples','one_aggregate_shortlist_feature','exact_gaussian_vacuum_plus_mobius']
        for kind in kinds:
            controls[kind]=measured_pipeline(v,kind,row['seed'],p)
        sd=setup(v)
        randoms=[];flags=[]
        for rep in range(20):
            q,info=fit_control(sd,'random_shortlist',row['seed']+1000000+rep)
            randoms.append(float(abs(p-q).sum()/2));flags.append(info['valid_fit'])
        record={key:row[key] for key in ['id','modes','source_fraction','squeezing','transmission']}
        record.update(torontonian_reference_tvd=error,max_pattern_probability_error=float(abs(pt-p).max()),
            torontonian_reference_sum=float(pt.sum()),torontonian_generation_seconds=tor_sec,
            target_mean_clicks=row['exact_mean_clicks'],original_residual_tvd=row['methods']['residual_selected']['full_tvd'],
            random_20_tvds=randoms,random_20_valid_fit=flags,controls=controls)
        results.append(record)
        payload={'spec':SPEC,'walrus_version':thewalrus.__version__,'rows':results,'source_sha256':s.sha(Path(__file__))}
        (DEST/'results.json').write_text(json.dumps(payload,indent=2))
        print(f'audit {i+1}/108: {row["id"]}, reference={error:.2e}, residual={record["original_residual_tvd"]:.5f}, shortlist={controls[kinds[0]]["full_tvd"]:.5f}, aggregate={controls[kinds[1]]["full_tvd"]:.5f}',flush=True)
    summarize(payload)

def summarize(data):
    rows=data['rows'];assert len(rows)==108
    original=json.loads((s.OUT/'summary.json').read_text())
    oldcost={x['id']:x['methods']['residual_selected'] for x in json.loads((s.OUT/'cost_audit.json').read_text())['rows']}
    controls={}
    for kind in rows[0]['controls']:
        vals=[r['controls'][kind] for r in rows]
        gain=np.array([r['original_residual_tvd']-r['controls'][kind]['full_tvd'] for r in rows])
        ratio=np.array([r['controls'][kind]['median_preprocessing_seconds']/oldcost[r['id']]['median_preprocessing_seconds'] for r in rows])
        memratio=np.array([r['controls'][kind]['traced_peak_bytes']/oldcost[r['id']]['isolated_traced_peak_bytes'] for r in rows])
        controls[kind]={'mean_full_tvd':float(np.mean([v['full_tvd'] for v in vals])),
            'median_preprocessing_ms':float(1000*np.median([v['median_preprocessing_seconds'] for v in vals])),
            'median_traced_peak_kib':float(np.median([v['traced_peak_bytes'] for v in vals])/1024),
            'wins_vs_original_residual':int(sum(gain>1e-8)), 'ties':int(sum(abs(gain)<=1e-8)), 'losses':int(sum(gain< -1e-8)),
            'median_paired_time_ratio_vs_original':float(np.median(ratio)),
            'median_paired_traced_memory_ratio_vs_original':float(np.median(memratio)),
            'strict_dominance_vs_original':int(sum((gain>1e-8)&(ratio<=1)&(memratio<=1))),
            'flags':[r['id'] for r in rows if not r['controls'][kind].get('valid_fit',True)]}
    selected=np.array([r['original_residual_tvd'] for r in rows])
    random=np.array([r['random_20_tvds'] for r in rows])
    summary={'controls':controls,'original_mean_residual_tvd':float(selected.mean()),
        'mean_random_20_tvd':float(random.mean()),
        'residual_wins_vs_per_instance_random_mean':int(sum(selected<random.mean(axis=1)-1e-8)),
        'residual_wins_vs_best_of_20_oracle':int(sum(selected<random.min(axis=1)-1e-8)),
        'max_independent_reference_tvd':max(r['torontonian_reference_tvd'] for r in rows),
        'mean_target_click_range':[min(r['target_mean_clicks'] for r in rows),max(r['target_mean_clicks'] for r in rows)],
        'random_fit_flags':int(sum(not x for r in rows for x in r['random_20_valid_fit'])),
        'timing_limit':'Compared with saved original timings from a previous run; no claim of simultaneous matched-machine-load measurement.'}
    (DEST/'summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    with threadpool_limits(limits=1):
        main()
