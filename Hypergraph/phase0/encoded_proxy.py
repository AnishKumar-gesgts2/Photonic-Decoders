"""Encoded six-ring parity-sector proxy with observable redundancy metadata.

The encoded parity algebra follows the four-fusion (2,2)-Shor construction.
Physical Pauli flip rates are declared sensitivity parameters, not optical
measurements of the boosted analyzer. Diagnostic sectors are not memory LER.
"""
from __future__ import annotations

from collections import defaultdict

import numpy as np
import pymatching

from boosted_encoded import encoded_availability, sample_physical_records
from native_ring_bulk import validate_bulk


def sample_shots(shots: int, efficiency: float, success: float,
                 independent_flip: float, joint_flip: float, seed: int,
                 branch_conditioned: bool = False,
                 photons_per_bsm: int = 4) -> dict:
    if photons_per_bsm not in (2, 4):
        raise ValueError("photons_per_bsm must be 2 or 4")
    if photons_per_bsm == 2 and abs(success - .5) > 1e-12:
        raise ValueError("Ideal two-photon BSM has branch-averaged success 0.5")
    if branch_conditioned and photons_per_bsm != 4:
        raise ValueError("Published branch-conditioned sensitivity is boosted-only")
    rng = np.random.default_rng(seed)
    bulk = validate_bulk(3)
    n = bulk["fusions"]
    clean = bulk["circuit"].compile_sampler(seed=seed + 1).sample(shots)[:, :2*n].astype(np.uint8)
    logical = clean.reshape(shots, n, 2)
    # Four physical Bell outcomes constrained by the encoded stabilizers.
    x = np.zeros((shots, n, 4), dtype=np.uint8)
    z = np.zeros_like(x)
    x[:, :, 0] = rng.integers(0, 2, (shots, n), dtype=np.uint8)
    x[:, :, 2] = x[:, :, 0] ^ logical[:, :, 0]
    x[:, :, 1] = rng.integers(0, 2, (shots, n), dtype=np.uint8)
    x[:, :, 3] = x[:, :, 1] ^ logical[:, :, 0]
    z[:, :, 0] = rng.integers(0, 2, (shots, n), dtype=np.uint8)
    z[:, :, 2] = z[:, :, 0]
    z[:, :, 1] = z[:, :, 0] ^ logical[:, :, 1]
    z[:, :, 3] = z[:, :, 1]
    x ^= (rng.random(x.shape) < independent_flip).astype(np.uint8)
    z ^= (rng.random(z.shape) < independent_flip).astype(np.uint8)
    joint = (rng.random((shots, n)) < joint_flip).astype(np.uint8)
    x[:, :, 0] ^= joint
    z[:, :, 0] ^= joint
    if branch_conditioned:
        # Published correct-identification probabilities by Bell state:
        # Phi+, Phi-, Psi+, Psi-. Used only as a sensitivity model because
        # the full record-conditioned instrument is not available here.
        success_by_branch = np.array([.461, .462, .924, .927])
        survived = rng.random(x.shape) < efficiency**4
        full = rng.random(x.shape) < success_by_branch[2*z+x]
        records = np.where(survived, np.where(full, 2, 1), 0).astype(np.uint8)
    else:
        if photons_per_bsm == 4:
            records = sample_physical_records(shots, n, efficiency, success, rng)
        else:
            # A/C are basis-swapped: their partial records retain X.
            # B/D partial records retain Z. Ideal full/partial is Bell-branch
            # dependent, rather than an independent Bernoulli coin.
            branch_full = np.empty_like(x, dtype=bool)
            branch_full[:, :, (0, 2)] = x[:, :, (0, 2)] == 1
            branch_full[:, :, (1, 3)] = z[:, :, (1, 3)] == 1
            survived = rng.random(x.shape) < efficiency**2
            records = np.where(survived, np.where(branch_full, 2, 1), 0).astype(np.uint8)

    x_known = records > 0
    x_known[:, :, 1] &= records[:, :, 1] == 2
    x_known[:, :, 3] &= records[:, :, 3] == 2
    z_known = records > 0
    z_known[:, :, 0] &= records[:, :, 0] == 2
    z_known[:, :, 2] &= records[:, :, 2] == 2
    known = encoded_availability(records)
    xa = x[:, :, 0] ^ x[:, :, 2]
    xb = x[:, :, 1] ^ x[:, :, 3]
    xa_known = x_known[:, :, 0] & x_known[:, :, 2]
    xb_known = x_known[:, :, 1] & x_known[:, :, 3]
    hard_x = np.where(xa_known, xa, np.where(xb_known, xb, 0)).astype(np.uint8)
    zleft = np.where(z_known[:, :, 0], z[:, :, 0], z[:, :, 2])
    zright = np.where(z_known[:, :, 1], z[:, :, 1], z[:, :, 3])
    hard_z = np.where(known[:, :, 1], zleft ^ zright, 0).astype(np.uint8)
    hard = np.stack((hard_x, hard_z), axis=-1)
    # These comparisons are among already measured physical fusion outcomes.
    flags = np.stack((xa_known & xb_known & (xa != xb),
                      z_known[:, :, 0] & z_known[:, :, 2] & (z[:, :, 0] != z[:, :, 2]),
                      z_known[:, :, 1] & z_known[:, :, 3] & (z[:, :, 1] != z[:, :, 3])),
                     axis=-1)
    if not np.array_equal(known[:, :, 0], xa_known | xb_known):
        raise AssertionError("Encoded XX availability mismatch")
    error = hard ^ logical
    return {"clean": clean, "hard": hard.reshape(shots, 2*n),
            "known": known.reshape(shots, 2*n), "errors": error.reshape(shots, 2*n),
            "records": records, "flags": flags,
            "latent_joint_count": int(joint.sum()),
            "branch_conditioned_success": branch_conditioned,
            "photons_per_bsm": photons_per_bsm}


def feature_key(data: dict, row: int, fusion: int, level: str) -> tuple[int, ...]:
    known = data["known"][row, 2*fusion:2*fusion+2]
    key = tuple(int(v) for v in known)
    if level in ("flags", "all"):
        key += tuple(int(v) for v in data["flags"][row, fusion])
    if level in ("classes", "all"):
        key += tuple(int(v) for v in data["records"][row, fusion])
    return key


def fit_priors(data: dict, level: str, smoothing: float = 2.0) -> dict:
    counts = defaultdict(lambda: np.zeros(4, dtype=float))
    shots, bits = data["errors"].shape
    for row in range(shots):
        for fusion in range(bits // 2):
            e = data["errors"][row, 2*fusion:2*fusion+2]
            counts[feature_key(data, row, fusion, level)][int(e[0]) + 2*int(e[1])] += 1
    return {key: (value + smoothing)/(value.sum() + 4*smoothing)
            for key, value in counts.items()}


def prior_for(data: dict, row: int, fusion: int, level: str,
              fitted: dict, coarse: dict) -> np.ndarray:
    key = feature_key(data, row, fusion, level)
    fallback = feature_key(data, row, fusion, "coarse")
    return fitted.get(key, coarse[fallback])


def contracted_checks(h: np.ndarray, known: np.ndarray) -> np.ndarray:
    """Merge check vertices across missing graph edges to form superchecks."""
    vertices = h.shape[0]
    parent = list(range(vertices))
    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for column in np.flatnonzero(~known):
        endpoints = np.flatnonzero(h[:, column])
        if len(endpoints) != 2:
            raise AssertionError("Expected a two-check fusion-outcome edge")
        a, b = (find(int(v)) for v in endpoints)
        parent[b] = a
    groups = defaultdict(list)
    for vertex in range(vertices):
        groups[find(vertex)].append(vertex)
    rows = [np.bitwise_xor.reduce(h[group], axis=0)
            for group in groups.values()]
    rows = [row for row in rows if np.any(row)]
    result = np.asarray(rows, dtype=np.uint8).reshape((-1, h.shape[1]))
    if np.any(result[:, ~known]) or np.max(result.sum(axis=0), initial=0) > 2:
        raise AssertionError("Invalid erased-edge contraction")
    return result


def deform_sectors(h: np.ndarray, logicals: np.ndarray,
                   known: np.ndarray) -> np.ndarray | None:
    """Move each nonlocal parity by local checks off unavailable outcomes."""
    missing = ~known
    a = h[:, missing].T.copy()
    result = []
    for logical in logicals:
        augmented = np.column_stack((a, logical[missing])).astype(np.uint8)
        rows, variables = a.shape
        pivots = []
        rank = 0
        for column in range(variables):
            found = np.flatnonzero(augmented[rank:, column])
            if len(found) == 0:
                continue
            pivot = rank + int(found[0])
            augmented[[rank, pivot]] = augmented[[pivot, rank]]
            for other in range(rows):
                if other != rank and augmented[other, column]:
                    augmented[other] ^= augmented[rank]
            pivots.append(column)
            rank += 1
            if rank == rows:
                break
        if np.any(augmented[rank:, -1]):
            return None
        coefficients = np.zeros(variables, dtype=np.uint8)
        for row, column in enumerate(pivots):
            coefficients[column] = augmented[row, -1]
        deformed = logical ^ ((coefficients @ h) & 1)
        if np.any(deformed[missing]):
            raise AssertionError("Nonlocal sector deformation failed")
        result.append(deformed)
    return np.asarray(result, dtype=np.uint8)


def matching_prediction(checks: np.ndarray, logicals: np.ndarray,
                        syndrome: np.ndarray, prior: np.ndarray) -> np.ndarray:
    if len(checks) == 0:
        return np.zeros(logicals.shape[0], dtype=np.uint8)
    p_x = prior[:, 1] + prior[:, 3]
    p_z = prior[:, 2] + prior[:, 3]
    probabilities = np.stack((p_x, p_z), axis=1).reshape(-1)
    probabilities = np.clip(probabilities, 1e-6, .499999)
    weights = np.log((1-probabilities)/probabilities)
    matching = pymatching.Matching.from_check_matrix(
        checks, weights=weights, faults_matrix=logicals)
    return np.asarray(matching.decode(syndrome), dtype=np.uint8)


def belief_priors(checks: np.ndarray, syndrome: np.ndarray, prior: np.ndarray,
                  iterations: int = 8) -> np.ndarray:
    """Damped four-state BP; keeps the joint XX/ZZ fault as one variable."""
    m, bits = checks.shape
    n = bits // 2
    if m == 0:
        return prior
    coeff = checks[:, ::2].astype(np.uint8) + 2*checks[:, 1::2].astype(np.uint8)
    state_x = np.array([0, 1, 0, 1], dtype=np.uint8)
    state_z = np.array([0, 0, 1, 1], dtype=np.uint8)
    signs = 1 - 2*((coeff[:, :, None] & 1)*state_x ^
                   ((coeff[:, :, None] >> 1) & 1)*state_z).astype(np.int8)
    active = coeff != 0
    factor = np.ones((m, n, 4), dtype=float)
    log_prior = np.log(np.clip(prior, 1e-12, 1))
    for _ in range(iterations):
        total = log_prior + np.log(np.clip(factor, 1e-12, None)).sum(axis=0)
        cavity = total[None, :, :] - np.log(np.clip(factor, 1e-12, None))
        cavity -= cavity.max(axis=2, keepdims=True)
        q = np.exp(cavity)
        q /= q.sum(axis=2, keepdims=True)
        mean = (q*signs).sum(axis=2)
        mean = np.where(active, np.clip(mean, -0.999999, 0.999999), 1.0)
        # Prefix/suffix avoids division by a near-zero message.
        prefix = np.cumprod(np.concatenate((np.ones((m, 1)), mean[:, :-1]), axis=1), axis=1)
        suffix = np.cumprod(np.concatenate((np.ones((m, 1)), mean[:, :0:-1]), axis=1), axis=1)[:, ::-1]
        product_except = prefix*suffix
        target = np.where(active[:, :, None],
                          1 + signs*((1-2*syndrome.astype(np.int8))[:, None, None]
                                     *product_except[:, :, None]), 1.0)
        factor = .5*factor + .5*np.clip(target, 1e-6, 2)
    posterior = log_prior + np.log(np.clip(factor, 1e-12, None)).sum(axis=0)
    posterior -= posterior.max(axis=1, keepdims=True)
    result = np.exp(posterior)
    return result/result.sum(axis=1, keepdims=True)


def decode_dataset(train: dict, test: dict, level: str, use_belief: bool,
                   max_shots: int | None = None) -> dict:
    bulk = validate_bulk(3)
    h, logicals = bulk["checks"], bulk["logicals"]
    coarse = fit_priors(train, "coarse")
    fitted = coarse if level == "coarse" else fit_priors(train, level)
    shots = len(test["hard"]) if max_shots is None else min(len(test["hard"]), max_shots)
    failures = np.zeros(shots, dtype=bool)
    no_checks = 0
    erased_sectors = 0
    for row in range(shots):
        known = test["known"][row]
        checks = contracted_checks(h, known)
        if len(checks) == 0:
            no_checks += 1
        deformed = deform_sectors(h, logicals, known)
        if deformed is None:
            erased_sectors += 1
            failures[row] = True
            continue
        syndrome = (checks @ test["hard"][row]) & 1
        local = np.asarray([prior_for(test, row, j, level, fitted, coarse)
                            for j in range(bulk["fusions"])])
        if use_belief:
            local = belief_priors(checks, syndrome, local)
        prediction = matching_prediction(checks, deformed, syndrome, local)
        truth = (deformed @ test["errors"][row]) & 1
        failures[row] = np.any(prediction != truth)
    return {"shots": shots, "failures": int(failures.sum()),
            "rate": float(failures.mean()), "no_check_fraction": no_checks/shots,
            "erased_sector_fraction": erased_sectors/shots,
            "failure_bits": failures}
