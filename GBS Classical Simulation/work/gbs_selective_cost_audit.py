"""Isolated pipeline costs and independent artifact audit, no rule changes.

The initial study's traced_peak_bytes adds phase peaks and is a conservative
allocation proxy. This supplement measures a whole standalone pipeline's
actual traced high-water mark, and median untraced wall time over three builds.
"""
import gc
import itertools
import json
import math
import time
import tracemalloc
import numpy as np
from threadpoolctl import threadpool_limits
import gbs_selective_correction_study as study

def pipeline(v, seed, name):
    loc,g2,target2,spins,f2,mu,c=study.pair_targets(v)
    q2,theta2,info2=study.fit(f2,target2)
    if name=='pair_maxent':
        return q2,loc,len(g2)
    triples=study.subsets(len(mu),3)
    rho=c/np.sqrt(np.outer(np.diag(c),np.diag(c)))
    ranked=sorted(triples,key=lambda t:(-sum(abs(rho[a,b]) for a,b in itertools.combinations(t,2)),t))
    budget=math.ceil(len(triples)*study.PROTOCOL['added_triple_fraction'])
    if name=='uniform_triples':
        chosen=triples
    else:
        shortlist=ranked[:math.ceil(len(triples)*study.PROTOCOL['shortlist_triple_fraction'])]
        targets={t:loc.spin(t) for t in shortlist}
        if name=='random_shortlist':
            rng=np.random.default_rng(seed+800000)
            chosen=sorted(shortlist[i] for i in rng.choice(len(shortlist),budget,replace=False))
        else:
            scores={}
            for t in shortlist:
                pred=float(q2@np.prod(spins[:,t],axis=1))
                scores[t]=abs(targets[t]-pred)/math.sqrt(max(1-pred*pred,1e-12))
            chosen=sorted(shortlist,key=lambda t:(-scores[t],t))[:budget]
    groups=g2+sorted(chosen)
    _,f=study.spins_and_features(len(mu),groups)
    target=np.array([loc.spin(t) for t in groups])
    q,_,info=study.fit(f,target,np.r_[theta2,np.zeros(len(chosen))])
    return q,loc,len(groups)

def audit():
    root=study.OUT
    data=json.loads((root/'results.json').read_text())
    assert len(data['rows'])==144
    assert sum(x['split']=='heldout' for x in data['rows'])==108
    assert data['selection']['frozen_before_heldout']
    assert data['protocol_sha256']==study.sha(root/'protocol.json')
    out=[]
    max_difference=0.0
    rng=np.random.default_rng(61292)
    for i,row in enumerate(x for x in data['rows'] if x['split']=='heldout'):
        artifact=np.load(root/'distributions'/f'{row["id"]}.npz')
        methods={}
        # Randomized execution order limits systematic warm-up/order timing bias.
        names=['pair_maxent','residual_selected','random_shortlist','uniform_triples']
        times={name:[] for name in names}
        for rep in range(3):
            for name in rng.permutation(names):
                start=time.perf_counter()
                q,loc,nfeatures=pipeline(artifact['covariance'],row['seed'],name)
                times[name].append(time.perf_counter()-start)
                difference=float(np.max(abs(q-artifact[f'q_{name}'])))
                max_difference=max(max_difference,difference)
                assert difference < 1e-12
        for name in names:
            gc.collect()
            tracemalloc.start()
            q,loc,nfeatures=pipeline(artifact['covariance'],row['seed'],name)
            current,peak=tracemalloc.get_traced_memory()
            tracemalloc.stop()
            methods[name]={'median_preprocessing_seconds':float(np.median(times[name])),
                'preprocessing_repeats_seconds':times[name],
                'isolated_traced_peak_bytes':int(peak),
                'determinant_queries':len(loc.vac)-1,'moment_queries':len(loc.cache)-1,
                'fitted_features':nfeatures}
            assert nfeatures==row['methods'][name]['fitted_features']
            assert len(loc.vac)-1==row['methods'][name]['determinant_queries']
        out.append({'id':row['id'],'methods':methods})
        print(f'cost audit {i+1}/108: {row["id"]}',flush=True)
        (root/'cost_audit.json').write_text(json.dumps({'rows':out,
            'max_probability_difference_from_original':max_difference,
            'timing': 'three untraced builds in randomized method order; median',
            'memory': 'one isolated whole-pipeline traced peak; excludes native allocations not traced by Python',
            'scope': 'covariance given; no evaluation costs charged; Q2 training included in corrections; no change in selection rules'},indent=2))
    # Full-order exponential-family recovery is an architecture check independent
    # of selection. A permutation test checks mode ordering in the optical model.
    r=np.array([.3,.5,.7,0.]);u=study.haar_unitary(4,np.random.default_rng(166))
    p,_=study.exact_click_probs(r,u,.65)
    groups=sum([study.subsets(4,k) for k in range(1,5)],[])
    _,f=study.spins_and_features(4,groups)
    q,_,info=study.fit(f,p@f)
    assert abs(q-p).sum()/2 < 1e-6
    perm=np.array([2,0,3,1]);pp,_=study.exact_click_probs(r,u[perm],.65)
    bits=(np.arange(16)[:,None]>>np.arange(4))&1
    mapped=(bits[:,perm]*(1<<np.arange(4))).sum(axis=1)
    perm_error=float(np.max(abs(pp[mapped]-p)))
    assert perm_error<1e-12
    (root/'verification.json').write_text(json.dumps({'all_144_artifacts_present':all((root/'distributions'/f'{x["id"]}.npz').exists() for x in data['rows']),
        'probability_rebuild_max_error':max_difference,'full_order_recovery_tvd':float(abs(q-p).sum()/2),
        'output_mode_permutation_error':perm_error,'declared_protocol_hash_verified':True},indent=2))

if __name__=='__main__':
    with threadpool_limits(limits=1):
        audit()
