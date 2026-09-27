"""Small periodic bulk of the published rotated six-ring fusion network.

One six-ring graph resource sits at each cubic cell. Its qubits 1,3,5 fuse
with +x,+y,+z neighbors, while 2,4,6 fuse with -x,-y,-z neighbors. This is
the rotated bulk geometry in Bartolucci et al., Supplementary Note V.C.
The finite periodic cell has no planar memory boundaries or declared memory
logical. Three nonlocal parity constraints are held out as diagnostic sectors.
"""
from __future__ import annotations

from itertools import product

import numpy as np
import stim


def ring_bulk(side: int = 2, negative_ports: tuple[int, int, int] = (3, 5, 1)) -> tuple[stim.Circuit, list[tuple[int, int]], np.ndarray]:
    if side < 2:
        raise ValueError("side must be at least 2")
    if sorted(negative_ports) != [1, 3, 5]:
        raise ValueError("negative ports must permute 1,3,5")
    sites = list(product(range(side), repeat=3))
    site_index = {site: i for i, site in enumerate(sites)}
    n = 6 * len(sites)
    qubit = lambda site, port: 6 * site_index[site] + port
    fusions = []
    for site in sites:
        for axis, plus_port in enumerate((0, 2, 4)):
            neighbor = list(site)
            neighbor[axis] = (neighbor[axis] + 1) % side
            fusions.append((qubit(site, plus_port),
                            qubit(tuple(neighbor), negative_ports[axis])))
    if sorted(q for pair in fusions for q in pair) != list(range(n)):
        raise AssertionError("Each resource qubit must have exactly one fusion")
    circuit = stim.Circuit()
    circuit.append("RX", list(range(n)))
    for site in sites:
        for port in range(6):
            circuit.append("CZ", [qubit(site, port), qubit(site, (port + 1) % 6)])
    # Constraints on products of ring graph-state stabilizers K_i=X_i Z_(i-1)Z_(i+1):
    # their X and Z exponents must match on the two qubits of each fusion.
    constraints = np.zeros((2 * len(fusions), n), dtype=np.uint8)
    for j, (a, b) in enumerate(fusions):
        constraints[2*j, [a, b]] = 1
        for q in (a, b):
            base, port = divmod(q, 6)
            constraints[2*j + 1, base*6 + (port - 1) % 6] ^= 1
            constraints[2*j + 1, base*6 + (port + 1) % 6] ^= 1
    return circuit, fusions, constraints


def gf2_nullspace(matrix: np.ndarray) -> list[np.ndarray]:
    a = matrix.copy()
    rows, cols = a.shape
    pivots = []
    row = 0
    for col in range(cols):
        candidates = np.flatnonzero(a[row:, col])
        if len(candidates) == 0:
            continue
        pivot = row + int(candidates[0])
        a[[row, pivot]] = a[[pivot, row]]
        for other in range(rows):
            if other != row and a[other, col]:
                a[other] ^= a[row]
        pivots.append(col)
        row += 1
        if row == rows:
            break
    free = [col for col in range(cols) if col not in pivots]
    basis = []
    for col in free:
        v = np.zeros(cols, dtype=np.uint8)
        v[col] = 1
        for r, pivot in enumerate(pivots):
            v[pivot] = a[r, col]
        if np.any((matrix @ v) % 2):
            raise AssertionError("GF2 nullspace construction failed")
        basis.append(v)
    return basis


def gf2_rank(matrix: np.ndarray) -> int:
    return matrix.shape[1] - len(gf2_nullspace(matrix))


def outcome_check(stabilizer_choice: np.ndarray,
                  fusions: list[tuple[int, int]]) -> np.ndarray:
    """Express a resource-state stabilizer in the fusion XX/ZZ outcome basis."""
    result = np.zeros(2 * len(fusions), dtype=np.uint8)
    for j, (a, b) in enumerate(fusions):
        if stabilizer_choice[a] != stabilizer_choice[b]:
            raise AssertionError("X fusion exponents disagree")
        result[2*j] = stabilizer_choice[a]
        for q in (a, b):
            base, port = divmod(q, 6)
            z = stabilizer_choice[base*6 + (port - 1) % 6] ^ stabilizer_choice[base*6 + (port + 1) % 6]
            if q == a:
                result[2*j + 1] = z
            elif result[2*j + 1] != z:
                raise AssertionError("Z fusion exponents disagree")
    return result


def check_basis(fusions: list[tuple[int, int]], constraints: np.ndarray) -> np.ndarray:
    """Select shortest independent parity checks, avoiding nested-basis artifacts."""
    null_basis = gf2_nullspace(constraints)
    if len(null_basis) > 18:
        raise ValueError("Enumeration is intentionally bounded to a small bulk")
    candidates = []
    for mask in range(1, 1 << len(null_basis)):
        choice = np.zeros(constraints.shape[1], dtype=np.uint8)
        for j, v in enumerate(null_basis):
            if (mask >> j) & 1:
                choice ^= v
        check = outcome_check(choice, fusions)
        if np.any(check):
            candidates.append(check)
    candidates.sort(key=lambda v: (int(v.sum()), tuple(v.tolist())))
    selected = []
    pivots = {}
    for candidate in candidates:
        v = candidate.copy()
        for pivot in sorted(pivots):
            if v[pivot]:
                v ^= pivots[pivot]
        if np.any(v):
            pivot = int(np.flatnonzero(v)[0])
            pivots[pivot] = v
            selected.append(candidate)
    return np.asarray(selected, dtype=np.uint8)


def local_vertex_checks(side: int, fusions: list[tuple[int, int]],
                        constraints: np.ndarray) -> np.ndarray:
    """Derive one local parity check per cubic vertex from R intersect F."""
    if side < 3:
        raise ValueError("Local vertex checks require side >= 3")
    sites = list(product(range(side), repeat=3))
    index = {site: i for i, site in enumerate(sites)}
    n_outcomes = 2 * len(fusions)
    n_qubits = constraints.shape[1]
    transform = np.zeros((n_outcomes, n_qubits), dtype=np.uint8)
    for j, (a, _b) in enumerate(fusions):
        transform[2*j, a] = 1
        base, port = divmod(a, 6)
        transform[2*j+1, base*6 + (port-1) % 6] ^= 1
        transform[2*j+1, base*6 + (port+1) % 6] ^= 1
    checks = []
    for vertex in sites:
        star = set()
        for axis in range(3):
            for other_bits in product((0, 1), repeat=2):
                lower = list(vertex)
                k = 0
                for coord in range(3):
                    if coord != axis:
                        lower[coord] = (vertex[coord] + other_bits[k]) % side
                        k += 1
                star.add(3 * index[tuple(lower)] + axis)
        if len(star) != 12:
            raise AssertionError("Cubic vertex must touch 12 fusion faces")
        outside = [bit for bit in range(n_outcomes) if bit // 2 not in star]
        restricted = np.concatenate((constraints, transform[outside]), axis=0)
        local = gf2_nullspace(restricted)
        candidates = [outcome_check(v, fusions) for v in local]
        candidates = [v for v in candidates if np.any(v)]
        if not candidates:
            raise AssertionError("No local parity check at vertex")
        best = min(candidates, key=lambda v: int(v.sum()))
        checks.append(best)
    return np.asarray(checks, dtype=np.uint8)


def validate_bulk(side: int = 3) -> dict:
    circuit, fusions, constraints = ring_bulk(side)
    checks = (local_vertex_checks(side, fusions, constraints) if side >= 3
              else check_basis(fusions, constraints))
    independent_rank = gf2_rank(checks)
    # The periodic fusion bulk has three nonlocal membrane parities at side 3.
    # They are the quotient (R intersect F) / span(local vertex checks).
    logicals = []  # diagnostic nonlocal sectors, not memory logicals
    span = checks.copy()
    for resource_choice in gf2_nullspace(constraints):
        candidate = outcome_check(resource_choice, fusions)
        if gf2_rank(np.concatenate((span, candidate[None, :]), axis=0)) > gf2_rank(span):
            logicals.append(candidate)
            span = np.concatenate((span, candidate[None, :]), axis=0)
    for a, b in fusions:
        circuit.append("MXX", [a, b])
        circuit.append("MZZ", [a, b])
    n_outcomes = 2 * len(fusions)
    for check in checks:
        circuit.append("DETECTOR", [stim.target_rec(i - n_outcomes)
                                     for i in np.flatnonzero(check)])
    for j, logical in enumerate(logicals):
        circuit.append("OBSERVABLE_INCLUDE", [stim.target_rec(i - n_outcomes)
                                               for i in np.flatnonzero(logical)], j)
    ideal_d, ideal_l = circuit.compile_detector_sampler(seed=91).sample(
        shots=64, separate_observables=True)
    if np.any(ideal_d) or np.any(ideal_l):
        raise AssertionError("Published-resource check was not deterministic")
    support = checks
    per_fusion = []
    for j in range(len(fusions)):
        xx = np.flatnonzero(support[:, 2*j]).tolist()
        zz = np.flatnonzero(support[:, 2*j+1]).tolist()
        both = np.flatnonzero(support[:, 2*j] ^ support[:, 2*j+1]).tolist()
        per_fusion.append({"xx_checks": xx, "zz_checks": zz,
                           "joint_checks": both})
    return {"side": side, "resource_states": side**3,
            "resource_qubits": circuit.num_qubits,
            "fusions": len(fusions), "local_checks": len(checks),
            "independent_check_rank": independent_rank,
            "nonlocal_membrane_observables": len(logicals),
            "local_check_weights": sorted(set(int(x) for x in checks.sum(axis=1))),
            "max_joint_outcome_detector_weight": max(len(x["joint_checks"]) for x in per_fusion),
            "min_joint_outcome_detector_weight": min(len(x["joint_checks"]) for x in per_fusion),
            "per_fusion": per_fusion,
            "circuit": circuit, "checks": checks,
            "logicals": np.asarray(logicals, dtype=np.uint8),
            "fusions_list": fusions}
