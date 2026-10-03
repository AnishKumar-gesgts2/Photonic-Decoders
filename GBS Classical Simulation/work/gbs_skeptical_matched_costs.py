"""Same-run randomized-order timing of stronger audit controls.

Also optimize the original residual architecture to share the same feature
construction as the new controls, then verify its probabilities are unchanged.
"""
import gc
import json
import math
import time
import tracemalloc
import numpy as np
from scipy.special import logsumexp
from threadpoolctl import threadpool_limits
import gbs_selective_correction_study as s
import gbs_skeptical_audit as a
from gbs_selective_cost_audit import pipeline as original_pipeline

def build(v,kind,seed):
    if kind=='original_residual':
        q,loc,n=original_pipeline(v,seed,'residual_selected')
        np.cumsum(q)
        return q,{'queries':len(loc.vac)-1,'features':n}
    if kind=='optimized_residual':
        loc,g2,t2,f2,theta2,shortlist,tt,ft=a.setup(v)
        q2=np.exp(f2@theta2-logsumexp(f2@theta2))
        scores=[]
        for j,t in enumerate(shortlist):
            pred=float(q2@ft[:,j])
            scores.append(abs(tt[j]-pred)/math.sqrt(max(1-pred*pred,1e-12)))
        m=len(v)//2
        budget=math.ceil(math.comb(m,3)/4)
        chosen=sorted(range(len(shortlist)),key=lambda j:(-scores[j],shortlist[j]))[:budget]
        chosen=sorted(chosen,key=lambda j:shortlist[j])
        f=np.column_stack([f2,ft[:,chosen]]);target=np.r_[t2,tt[chosen]]
        q,_,info=s.fit(f,target,np.r_[theta2,np.zeros(budget)])
        np.cumsum(q)
        return q,dict(info,queries=len(loc.vac)-1,features=len(target))
    return a.pipeline(v,kind,seed)

def main():
    data=json.loads((a.DEST/'results.json').read_text())
    original={r['id']:r for r in json.loads((s.OUT/'results.json').read_text())['rows']}
    names=['original_residual','optimized_residual','all_pair_shortlisted_triples','one_aggregate_shortlist_feature','exact_gaussian_vacuum_plus_mobius']
    spec={'names':names,'cases':108,'repeats':3,'order':'randomized independently in each case and timing round',
          'memory':'one separately measured whole-pipeline Python traced high-water mark',
          'scope':'all start from covariance; CDF included; original residual rebuilt without algorithm changes; optimized residual changes feature construction only'}
    (a.DEST/'matched_cost_spec.json').write_text(json.dumps(spec,indent=2))
    records=[];rng=np.random.default_rng(20027);max_difference=0
    for i,row in enumerate(data['rows']):
        artifact=np.load(s.OUT/'distributions'/f'{row["id"]}.npz')
        v,p=artifact['covariance'],artifact['p']
        times={n:[] for n in names}
        for rep in range(3):
            for name in rng.permutation(names):
                start=time.perf_counter();q,info=build(v,name,original[row['id']]['seed']);times[name].append(time.perf_counter()-start)
                if name in ('original_residual','optimized_residual'):
                    err=float(abs(q-artifact['q_residual_selected']).max());max_difference=max(max_difference,err);assert err<1e-12
        methods={}
        for name in names:
            gc.collect();tracemalloc.start()
            q,info=build(v,name,original[row['id']]['seed'])
            _,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
            methods[name]=dict(info,full_tvd=float(abs(p-q).sum()/2),median_preprocessing_seconds=float(np.median(times[name])),repeated_preprocessing_seconds=times[name],traced_peak_bytes=int(peak))
        records.append({'id':row['id'],'modes':row['modes'],'methods':methods})
        payload={'spec':spec,'max_residual_probability_difference':max_difference,'rows':records}
        (a.DEST/'matched_costs.json').write_text(json.dumps(payload,indent=2))
        print(f'matched costs {i+1}/108',flush=True)
    summary={}
    for name in names:
        vals=[r['methods'][name] for r in records]
        out={'mean_full_tvd':float(np.mean([v['full_tvd'] for v in vals])),
             'median_preprocessing_ms':float(1000*np.median([v['median_preprocessing_seconds'] for v in vals])),
             'median_traced_peak_kib':float(np.median([v['traced_peak_bytes'] for v in vals])/1024)}
        for ref in ['original_residual','optimized_residual']:
            gain=np.array([r['methods'][ref]['full_tvd']-r['methods'][name]['full_tvd'] for r in records])
            ratios=np.array([r['methods'][name]['median_preprocessing_seconds']/r['methods'][ref]['median_preprocessing_seconds'] for r in records])
            memory=np.array([r['methods'][name]['traced_peak_bytes']/r['methods'][ref]['traced_peak_bytes'] for r in records])
            out[f'vs_{ref}']={'tvd_wins':int(sum(gain>1e-8)),'median_paired_time_ratio':float(np.median(ratios)),
                'median_paired_memory_ratio':float(np.median(memory)),
                'strict_dominance':int(sum((gain>1e-8)&(ratios<=1)&(memory<=1)))}
        summary[name]=out
    (a.DEST/'matched_cost_summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    with threadpool_limits(limits=1):main()
