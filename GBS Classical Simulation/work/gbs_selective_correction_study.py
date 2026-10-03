"""Predeclared, small-system selective GBS correction study.

Every model's target moments come from local Gaussian vacuum determinants.
The full held-out distribution is constructed only after all models are fit.
Enumerated partition functions and iid table sampling are deliberately bounded
to small systems; this is not a scalable replacement for a published sampler.
"""
import os
for _key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[_key] = '1'
import argparse
import hashlib
import itertools
import json
import math
import platform
import time
import tracemalloc
from pathlib import Path
import numpy as np
import scipy
from scipy.optimize import minimize
from scipy.special import logsumexp
from threadpoolctl import threadpool_limits, threadpool_info
from gbs_projection_probe import haar_unitary, exact_click_probs

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs' / 'selective_correction_v1'
PROTOCOL = {
    'version': 1, 'declared_date': '2026-10-02',
    'eventual_experiment': 'Jiuzhang 2.0 threshold-click task; no hardware data in this run',
    'published_reference': 'Villalonga et al. arXiv:2109.11525v2, Eqs. 4-5 as printed',
    'modes': [6, 8, 10], 'source_fractions': [0.5, 1.0],
    'squeezing': [0.4, 0.8], 'transmission': [0.4, 0.7, 0.95],
    'development_replicates_per_cell': 1, 'heldout_replicates_per_cell': 3,
    'seed_base': 2026100200, 'added_triple_fraction': 0.25,
    'shortlist_triple_fraction': 0.5,
    'pair_rule': 'Rank triples by sum of absolute normalized pair covariances; deterministic lexicographic ties.',
    'residual_rule': 'Shortlist top half by pair score; rank by absolute local spin-triple target minus Q2 prediction, divided by sqrt(max(1-Q2_prediction^2,1e-12)).',
    'random_control': 'Same pair shortlist, same local-statistic queries, random quarter of all triples retained; independent fixed seed per instance.',
    'architecture': 'Enumerated normalized exponential family: all one/pair spin features plus selected triple features, fitted by L-BFGS-B.',
    'development_choice': 'Choose pair or residual by smaller mean development full TVD; freeze before held-out run; no other tuning.',
    'baselines': ['independent', 'tap_printed', 'pair_maxent', 'uniform_triples', 'random_shortlist'],
    'primary_endpoint': 'Exact unconditional full-distribution TVD; paired comparisons on held-out instances.',
    'secondary': ['click-count TVD', 'spin-moment RMS by order 1-4', 'click-cumulant RMS orders 3-4', 'conditional fixed-click TVD where target mass >=0.01', 'metric ranking disagreements'],
    'resources': 'Instrumented single-thread wall time, traced allocation peak (not complete native RSS), local determinant queries, fitted features, retained table bytes, iid table sampling time for 100000 shots (3 repeats). Shared pair preparation charged to every corrected method.',
    'fit_tolerance': 1e-6, 'max_iterations': 3000,
    'failure_policy': 'Retain all rows. No clipping of invalid TAP discriminants. Report fit failures and moment violations separately.',
    'inference': 'Paired bootstrap means with 2000 resamples across equally weighted held-out instances; descriptive, not experimental-population guarantees.',
    'success_gate': 'Report strict per-instance dominance vs pair_maxent and uniform_triples: TVD lower by >1e-8, measured preprocessing time <= comparator, traced peak <= comparator. Feature/query budgets are separate from measured-cost claims.',
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def subsets(m, k):
    return list(itertools.combinations(range(m), k))

def covariance(r, u, eta):
    m = len(r)
    sym = np.block([[u.real, -u.imag], [u.imag, u.real]])
    vin = np.diag(np.r_[np.exp(-2*r)/2, np.exp(2*r)/2])
    return eta * sym @ vin @ sym.T + (1-eta) * np.eye(2*m)/2

class LocalMoments:
    """Only requested small-subsystem determinants, never a full P table."""
    def __init__(self, v):
        self.v = v
        self.m = len(v)//2
        self.vac = {(): 1.0}
        self.cache = {(): 1.0}
    def vacuum(self, group):
        group = tuple(sorted(group))
        if group not in self.vac:
            inds = list(group) + [i+self.m for i in group]
            sign, logdet = np.linalg.slogdet(self.v[np.ix_(inds, inds)] + np.eye(len(inds))/2)
            if sign <= 0:
                raise ValueError('nonpositive Gaussian vacuum determinant')
            self.vac[group] = float(np.exp(-logdet/2))
        return self.vac[group]
    def spin(self, group):
        group = tuple(sorted(group))
        if group not in self.cache:
            # s_i = 1-2*indicator(vacuum_i).
            self.cache[group] = sum((-2)**k * self.vacuum(t)
                                    for k in range(len(group)+1)
                                    for t in itertools.combinations(group, k))
        return self.cache[group]

def spins_and_features(m, groups):
    bits = (np.arange(1 << m)[:, None] >> np.arange(m)) & 1
    spins = 2*bits-1
    f = np.column_stack([np.prod(spins[:, t], axis=1) for t in groups]).astype(float)
    return spins, f

def fit(f, target, initial=None):
    def obj(theta):
        logits = f @ theta
        z = logsumexp(logits)
        q = np.exp(logits-z)
        return z-theta@target, f.T@q-target
    start = np.zeros(len(target)) if initial is None else initial
    opt = minimize(obj, start, jac=True, method='L-BFGS-B',
                   options={'maxiter': PROTOCOL['max_iterations'], 'gtol': 1e-10, 'ftol': 1e-15, 'maxls': 40})
    q = np.exp(f@opt.x-logsumexp(f@opt.x))
    err = float(np.max(np.abs(q@f-target)))
    return q, opt.x, {'optimizer_success': bool(opt.success), 'message': str(opt.message),
                      'iterations': int(opt.nit), 'max_matched_moment_error': err,
                      'valid_fit': bool(opt.success and err <= PROTOCOL['fit_tolerance'])}

def measured(fn):
    tracemalloc.start()
    start = time.perf_counter()
    val = fn()
    elapsed = time.perf_counter()-start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return val, elapsed, peak

def pair_targets(v):
    loc = LocalMoments(v)
    m = loc.m
    groups = subsets(m, 1)+subsets(m, 2)
    target = np.array([loc.spin(t) for t in groups])
    spins, f = spins_and_features(m, groups)
    mu = target[:m]
    c = np.eye(m)
    for t, value in zip(groups[m:], target[m:]):
        a,b = t
        c[a,b] = c[b,a] = value
    c -= np.outer(mu, mu)
    return loc, groups, target, spins, f, mu, c

def build_models(v, seed):
    m = len(v)//2
    shared, common_time, common_peak = measured(lambda: pair_targets(v))
    loc0, g2, target2, spins, f2, mu, c = shared
    models = {}
    def store(name, q, stats, sec, peak, loc, groups):
        if q is not None:
            if not np.all(np.isfinite(q)) or q.min() < 0 or abs(q.sum()-1) > 1e-10:
                raise ValueError('invalid normalized model')
        models[name] = {'q': q, 'stats': dict(stats, preprocessing_seconds=sec+common_time,
                    traced_peak_bytes=int(peak+common_peak), fitted_features=len(groups),
                    determinant_queries=len(loc.vac)-1, moment_queries=len(loc.cache)-1,
                    selected_triples=[list(t) for t in groups if len(t)==3],
                    retained_probability_table_bytes=0 if q is None else int(q.nbytes)),
                    'groups': groups}
    def independent():
        q = np.prod((1+spins*mu)/2, axis=1)
        return q, {'valid_fit': True}
    (q,info),sec,peak = measured(independent)
    # Independent genuinely requires only the one-mode targets, so queries and
    # common cost are measured separately rather than charged the pair stage.
    def independent_local():
        loc = LocalMoments(v)
        means = np.array([loc.spin((i,)) for i in range(m)])
        sb,_ = spins_and_features(m, subsets(m,1))
        return np.prod((1+sb*means)/2,axis=1),loc
    (q,loc),sec,peak = measured(independent_local)
    store('independent',q,info,sec-common_time,peak-common_peak,loc,subsets(m,1))
    def tap():
        inv = np.linalg.inv(c)
        disc = 1-8*inv*np.outer(mu,mu)
        off = ~np.eye(m,dtype=bool)
        if np.min(disc[off]) < 0:
            return None, {'valid_fit': False, 'unsupported_reason': 'negative printed TAP square-root discriminant', 'min_discriminant': float(np.min(disc[off]))}
        j = -2*inv/(1+np.sqrt(np.where(off,disc,1)))
        np.fill_diagonal(j,0)
        # Literal arXiv v2 Eq. 5. Do not silently substitute a different
        # conventional TAP field equation when evaluating the printed model.
        h = np.arctanh(mu) - j@mu - (j*j)@(1-mu*mu)
        logits = spins@h + np.array([np.einsum('i,ij,j',s,j,s)/2 for s in spins])
        q = np.exp(logits-logsumexp(logits))
        return q, {'valid_fit': True, 'max_pair_moment_error': float(np.max(np.abs(q@f2-target2))), 'minimum_discriminant': float(np.min(disc[off])), 'sampling_scope': 'exact stationary distribution, not published Gibbs trajectory'}
    (q,info),sec,peak = measured(tap)
    store('tap_printed',q,info,sec,peak,loc0,g2)
    (q2,theta2,info2),pair_fit_time,pair_fit_peak = measured(lambda: fit(f2,target2))
    store('pair_maxent',q2,info2,pair_fit_time,pair_fit_peak,loc0,g2)
    triples = subsets(m,3)
    budget = math.ceil(len(triples)*PROTOCOL['added_triple_fraction'])
    shortlist_size = math.ceil(len(triples)*PROTOCOL['shortlist_triple_fraction'])
    for name in ['pair_selected','residual_selected','random_shortlist','uniform_triples']:
        def corrected():
            loc = LocalMoments(v)
            # Charge the common local moments to all models; compute only new
            # determinants below. The fresh cache cannot see other models' data.
            loc.vac = dict(loc0.vac)
            loc.cache = dict(loc0.cache)
            rho = c/np.sqrt(np.outer(np.diag(c),np.diag(c)))
            ranked = sorted(triples,key=lambda t: (-sum(abs(rho[a,b]) for a,b in itertools.combinations(t,2)),t))
            if name == 'uniform_triples':
                chosen = triples
            elif name == 'pair_selected':
                chosen = ranked[:budget]
            else:
                shortlist = ranked[:shortlist_size]
                targets = {t:loc.spin(t) for t in shortlist}
                if name == 'random_shortlist':
                    rng = np.random.default_rng(seed+800000)
                    chosen = sorted(shortlist[i] for i in rng.choice(len(shortlist),budget,replace=False))
                else:
                    scores = {}
                    for t in shortlist:
                        pred = float(q2@np.prod(spins[:,t],axis=1))
                        scores[t] = abs(targets[t]-pred)/math.sqrt(max(1-pred*pred,1e-12))
                    chosen = sorted(shortlist,key=lambda t:(-scores[t],t))[:budget]
            groups = g2+sorted(chosen)
            _,f = spins_and_features(m,groups)
            target = np.array([loc.spin(t) for t in groups])
            q,theta,info = fit(f,target,np.r_[theta2,np.zeros(len(chosen))])
            info['candidate_triples_queried'] = len([t for t in loc.cache if len(t)==3])
            return q,info,loc,groups
        (q,info,loc,groups),sec,peak = measured(corrected)
        store(name,q,info,sec+pair_fit_time,peak+pair_fit_peak,loc,groups)
    return models

def partitions(items):
    if not items:
        yield []
        return
    first,*rest = items
    for part in partitions(rest):
        yield [(first,)]+part
        for i in range(len(part)):
            yield part[:i]+[(first,)+part[i]]+part[i+1:]

def cumulants(q, bits, groups):
    cache = {():1.0}
    def moment(t):
        t=tuple(sorted(t))
        if t not in cache:
            cache[t]=float(q@np.prod(bits[:,t],axis=1))
        return cache[t]
    return np.array([sum(math.factorial(len(p)-1)*(-1)**(len(p)-1)*math.prod(moment(t) for t in p)
                         for p in partitions(list(g))) for g in groups])

def evaluate(p, models, m, seed):
    bits = (np.arange(1<<m)[:,None]>>np.arange(m))&1
    count = bits.sum(axis=1)
    pc = np.bincount(count,weights=p,minlength=m+1)
    fs = {k:spins_and_features(m,subsets(m,k))[1] for k in range(1,5)}
    pm = {k:p@f for k,f in fs.items()}
    pk = {k:cumulants(p,bits,subsets(m,k)) for k in (3,4)}
    rows={}
    for name,model in models.items():
        q=model['q']
        row=dict(model['stats'])
        if q is None:
            rows[name]=row
            continue
        qc=np.bincount(count,weights=q,minlength=m+1)
        row.update(full_tvd=float(abs(p-q).sum()/2), click_count_tvd=float(abs(pc-qc).sum()/2),
                   mean_clicks=float(q@count), spin_moment_rms={str(k):float(np.sqrt(np.mean((pm[k]-q@f)**2))) for k,f in fs.items()},
                   click_cumulant_rms={str(k):float(np.sqrt(np.mean((pk[k]-cumulants(q,bits,subsets(m,k)))**2))) for k in (3,4)})
        sectors=[]
        for k in range(m+1):
            if pc[k]>=0.01:
                idx=count==k
                sectors.append({'clicks':k,'target_mass':float(pc[k]),'model_mass':float(qc[k]),
                                'conditional_tvd':float(abs(p[idx]/pc[k]-q[idx]/qc[k]).sum()/2)})
        row['fixed_click_sectors']=sectors
        rng=np.random.default_rng(seed+900000)
        cdf=np.cumsum(q);cdf[-1]=1
        samples=None;times=[]
        for _ in range(3):
            start=time.perf_counter()
            samples=np.searchsorted(cdf,rng.random(100000))
            times.append(time.perf_counter()-start)
        emp=np.bincount(samples,minlength=len(q))/len(samples)
        # A sample-to-Q discrepancy measures the sampler implementation, not
        # approximation accuracy against P. No noisy sample TVD replaces exact TVD.
        row['iid_table_sampling_seconds_100k']=float(np.median(times))
        row['sample_to_model_tvd_100k']=float(abs(emp-q).sum()/2)
        row['sample_mean_click_error']=float(abs(count[samples].mean()-q@count))
        rows[name]=row
    return rows,pc

def selftests():
    errors={}
    for name,r,eta in [('vacuum',np.zeros(4),.8),('zero_transmission',np.ones(4)*.8,0),('independent_squeezed',np.array([.2,.4,.6,.8]),1)]:
        u=np.eye(4,dtype=complex)
        p,p0=exact_click_probs(r,u,eta)
        v=covariance(r,u,eta)
        loc=LocalMoments(v)
        single=np.array([loc.vacuum((i,)) for i in range(4)])
        if eta==1:
            assert np.max(abs(single-1/np.cosh(r)))<1e-12
        bits=(np.arange(16)[:,None]>>np.arange(4))&1
        expected=np.prod(np.where(bits,1-single,single),axis=1)
        error=float(np.max(abs(expected-p)))
        assert error<1e-12
        errors[name]=error
    # Same optical input under an arbitrary interferometer must conserve total
    # photon expectation before loss; covariance provides a separate check.
    rng=np.random.default_rng(781)
    r=np.array([.8,.4,.1,0.]);u=haar_unitary(4,rng);v=covariance(r,u,.7)
    err=abs((np.trace(v)-4)/2-.7*np.sinh(r).dot(np.sinh(r)))
    assert err<1e-12
    errors['mean_photon_conservation_error']=float(err)
    return errors

def suite():
    cells=list(itertools.product(PROTOCOL['modes'],PROTOCOL['source_fractions'],PROTOCOL['squeezing'],PROTOCOL['transmission']))
    for split,nrep,offset in [('development',1,0),('heldout',3,100000)]:
        for cell,(m,frac,r,eta) in enumerate(cells):
            for rep in range(nrep):
                seed=PROTOCOL['seed_base']+offset+cell*100+rep
                yield dict(id=f'{split}_m{m}_f{frac}_r{r}_eta{eta}_rep{rep}',split=split,
                           modes=m,source_fraction=frac,squeezing=r,transmission=eta,seed=seed)

def run(limit=None):
    OUT.mkdir(parents=True,exist_ok=True)
    protocol_path=OUT/'protocol.json'
    if not protocol_path.exists():
        raise RuntimeError('Declare protocol with --declare before running.')
    if json.loads(protocol_path.read_text())!=PROTOCOL:
        raise RuntimeError('Declared protocol changed; use a new version.')
    checks=selftests()
    rows=[];decision=None
    artifacts=OUT/'distributions';artifacts.mkdir(exist_ok=True)
    started=time.perf_counter()
    for i,case in enumerate(suite()):
        if limit is not None and i>=limit:
            break
        if case['split']=='heldout' and decision is None:
            dev={name:float(np.mean([x['methods'][name]['full_tvd'] for x in rows])) for name in ['pair_selected','residual_selected']}
            chosen=min(dev,key=lambda name:(dev[name],name))
            decision={'chosen_method':chosen,'development_mean_tvd':dev,'frozen_before_heldout':True,'protocol_sha256':sha(protocol_path)}
            (OUT/'frozen_selection.json').write_text(json.dumps(decision,indent=2))
        m=case['modes'];rng=np.random.default_rng(case['seed'])
        r=np.zeros(m);r[:int(m*case['source_fraction'])]=case['squeezing']
        u=haar_unitary(m,rng);v=covariance(r,u,case['transmission'])
        models=build_models(v,case['seed'])
        # Full reference is unavailable until every model is finalized.
        t=time.perf_counter();p,p0=exact_click_probs(r,u,case['transmission']);exact_time=time.perf_counter()-t
        raw_min=float(p.min());raw_sum=float(p.sum())
        if raw_min < -1e-10 or abs(raw_sum-1)>1e-10:
            raise ValueError('Exact reference failed probability checks')
        p=np.maximum(p,0);p/=p.sum()
        # Validate local moments vs an independently computed full inclusion-
        # exclusion table, including all third-order statistics.
        loc=LocalMoments(v);groups=sum([subsets(m,k) for k in range(1,4)],[])
        _,f=spins_and_features(m,groups)
        local_error=float(np.max(abs(p@f-np.array([loc.spin(t) for t in groups]))))
        assert local_error<1e-9
        methods,pc=evaluate(p,models,m,case['seed'])
        record=dict(case,methods=methods,exact_generation_seconds=exact_time,
                    exact_raw_min_probability=raw_min,exact_raw_sum=raw_sum,
                    local_vs_full_moment_error=local_error,exact_mean_clicks=float(np.arange(m+1)@pc))
        rows.append(record)
        save={'p':p,'covariance':v,'unitary':u,'squeezing':r}
        save.update({f'q_{name}':model['q'] for name,model in models.items() if model['q'] is not None})
        np.savez_compressed(artifacts/f'{case["id"]}.npz',**save)
        (OUT/'results.json').write_text(json.dumps({'protocol_sha256':sha(protocol_path),'selection':decision,'checks':checks,'rows':rows},indent=2))
        print(f'{i+1}: {case["id"]}: Q2={methods["pair_maxent"]["full_tvd"]:.5f}, pair={methods["pair_selected"]["full_tvd"]:.5f}, residual={methods["residual_selected"]["full_tvd"]:.5f}, Q3={methods["uniform_triples"]["full_tvd"]:.5f}',flush=True)
    env={'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,
         'platform':platform.platform(),'processor':platform.processor(),'threadpools':threadpool_info(),
         'script_sha256':sha(Path(__file__)),'helper_sha256':sha(Path(__file__).with_name('gbs_projection_probe.py')),
         'total_run_seconds':time.perf_counter()-started,'completed_cases':len(rows)}
    (OUT/'environment.json').write_text(json.dumps(env,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--declare',action='store_true');parser.add_argument('--limit',type=int)
    args=parser.parse_args()
    if args.declare:
        OUT.mkdir(parents=True,exist_ok=True)
        path=OUT/'protocol.json'
        if path.exists() and json.loads(path.read_text())!=PROTOCOL:
            raise RuntimeError('Do not overwrite a declared protocol')
        path.write_text(json.dumps(PROTOCOL,indent=2))
        print(path,sha(path))
    else:
        with threadpool_limits(limits=1):
            run(args.limit)
