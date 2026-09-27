"""Global four-state joint-fault MAP on the Stim-derived check matrix.

An integer program preserves a simultaneous XX/ZZ error at one fusion as one
categorical event. It minimizes event negative log likelihood subject to every
observed detector parity. This is configuration MAP, not logical-class MAP.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix


def decode(checks: np.ndarray, logicals: np.ndarray, syndrome: np.ndarray,
           priors: np.ndarray, time_limit: float = 10.0) -> tuple[np.ndarray, bool]:
    m, bits = checks.shape
    n = bits // 2
    if (bits % 2 or logicals.shape[1] != bits or syndrome.shape != (m,) or
            priors.shape != (n, 4)):
        raise ValueError("Incompatible joint-MAP dimensions")
    if np.any(priors < 0) or not np.allclose(priors.sum(axis=1), 1):
        raise ValueError("Each local prior must be normalized")
    # x[j,s] is one-hot; k[i] enforces integer parity via sum contributions-2k=s.
    columns = 4*n + m
    matrix = lil_matrix((n + m, columns), dtype=float)
    for j in range(n):
        matrix[j, 4*j:4*j+4] = 1
    states = ((0, 0), (1, 0), (0, 1), (1, 1))
    for i in range(m):
        for j in range(n):
            a, b = int(checks[i, 2*j]), int(checks[i, 2*j+1])
            if a or b:
                for state, (x, z) in enumerate(states):
                    matrix[n+i, 4*j+state] = (a*x) ^ (b*z)
        matrix[n+i, 4*n+i] = -2
    target = np.concatenate((np.ones(n), syndrome.astype(float)))
    upper = np.concatenate((np.ones(4*n), np.full(m, n, dtype=float)))
    costs = np.concatenate((-np.log(np.clip(priors, 1e-12, 1)).reshape(-1),
                            np.zeros(m)))
    result = milp(costs, integrality=np.ones(columns),
                  bounds=Bounds(np.zeros(columns), upper),
                  constraints=LinearConstraint(matrix.tocsr(), target, target),
                  options={"time_limit": time_limit, "mip_rel_gap": 0.0})
    if result.x is None or result.status != 0:
        return np.zeros(logicals.shape[0], dtype=np.uint8), False
    chosen = np.argmax(result.x[:4*n].reshape(n, 4), axis=1)
    errors = np.zeros(bits, dtype=np.uint8)
    errors[::2] = chosen & 1
    errors[1::2] = chosen >> 1
    if not np.array_equal((checks @ errors) & 1, syndrome):
        raise AssertionError("MAP configuration violates detector parity")
    return (logicals @ errors) & 1, True
