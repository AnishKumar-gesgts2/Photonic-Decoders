"""Bounded d=3 memory proxy driven by an exact boosted-BSM optical channel.

The optical model is exact for ideal indistinguishable four photons, PNR and a
specified ancilla Z fault. The adapter from encoded Bell-frame uncertainty to
a data-qubit Pauli at one time slice is an explicit teleportation proxy, not a
native six-ring memory or a measured source-fault model.
"""
from __future__ import annotations

from collections import defaultdict

import numpy as np
import pymatching
import stim

from boosted_optical import BELL, ideal_report, instrument
from encoded_proxy import belief_priors


def optical_channels() -> dict:
    ideal = instrument("phi+")
    result = {}
    for ancilla in ("phi+", "phi-"):
        table = instrument(ancilla)
        result[ancilla] = {}
        for bell in range(4):
            p = table["probabilities"][bell]
            active = np.flatnonzero(p > 1e-14)
            reports = [ideal_report(table["records"][int(j)], ideal) for j in active]
            result[ancilla][bell] = (p[active]/p[active].sum(), reports)
    return result


def sample_encoded(shots: int, phase_fault: float, seed: int) -> dict:
    if not 0 <= phase_fault <= 1:
        raise ValueError("phase_fault must be a probability")
    rng = np.random.default_rng(seed)
    optical = optical_channels()
    logical = rng.integers(0, 2, (shots, 9, 2), dtype=np.uint8)
    x = np.empty((shots, 9, 4), dtype=np.uint8)
    z = np.empty_like(x)
    x[:, :, 0] = rng.integers(0, 2, (shots, 9), dtype=np.uint8)
    x[:, :, 2] = x[:, :, 0] ^ logical[:, :, 0]
    x[:, :, 1] = rng.integers(0, 2, (shots, 9), dtype=np.uint8)
    x[:, :, 3] = x[:, :, 1] ^ logical[:, :, 0]
    z[:, :, 0] = rng.integers(0, 2, (shots, 9), dtype=np.uint8)
    z[:, :, 2] = z[:, :, 0]
    z[:, :, 1] = z[:, :, 0] ^ logical[:, :, 1]
    z[:, :, 3] = z[:, :, 1]
    reported = np.zeros((shots, 9, 4, 2), dtype=np.uint8)
    known = np.zeros_like(reported, dtype=bool)
    full = np.zeros((shots, 9, 4), dtype=np.uint8)
    fault_count = 0
    for row in range(shots):
        for site in range(9):
            for physical in range(4):
                swapped = physical in (0, 2)  # A,C failure retains logical XX.
                bell_x = int(z[row, site, physical] if swapped else x[row, site, physical])
                bell_z = int(x[row, site, physical] if swapped else z[row, site, physical])
                bell = 2*bell_z + bell_x
                fault = rng.random() < phase_fault
                fault_count += fault
                p, reports = optical["phi-" if fault else "phi+"][bell]
                out_x, out_z = reports[int(rng.choice(len(p), p=p))]
                result = (out_z, out_x) if swapped else (out_x, out_z)
                for parity in range(2):
                    if result[parity] is not None:
                        known[row, site, physical, parity] = True
                        reported[row, site, physical, parity] = result[parity]
                full[row, site, physical] = all(v is not None for v in result)
    xa_known = known[:, :, 0, 0] & known[:, :, 2, 0]
    xb_known = known[:, :, 1, 0] & known[:, :, 3, 0]
    xa = reported[:, :, 0, 0] ^ reported[:, :, 2, 0]
    xb = reported[:, :, 1, 0] ^ reported[:, :, 3, 0]
    left_known = known[:, :, 0, 1] | known[:, :, 2, 1]
    right_known = known[:, :, 1, 1] | known[:, :, 3, 1]
    left = np.where(known[:, :, 0, 1], reported[:, :, 0, 1], reported[:, :, 2, 1])
    right = np.where(known[:, :, 1, 1], reported[:, :, 1, 1], reported[:, :, 3, 1])
    logical_known = np.stack((xa_known | xb_known, left_known & right_known), axis=-1)
    hard = np.stack((np.where(xa_known, xa, xb), left ^ right), axis=-1)
    flags = np.stack((xa_known & xb_known & (xa != xb),
                      known[:, :, 0, 1] & known[:, :, 2, 1] &
                      (reported[:, :, 0, 1] != reported[:, :, 2, 1]),
                      known[:, :, 1, 1] & known[:, :, 3, 1] &
                      (reported[:, :, 1, 1] != reported[:, :, 3, 1])), axis=-1)
    # Unknown teleportation frame bit is uniformly random; explicit adapter.
    random_frame = rng.integers(0, 2, hard.shape, dtype=np.uint8)
    error = np.where(logical_known, hard ^ logical, random_frame).astype(np.uint8)
    return {"error": error, "known": logical_known, "flags": flags,
            "full": full, "fault_count": int(fault_count)}


def memory_signatures(basis: str) -> tuple[np.ndarray, np.ndarray, list[int]]:
    if basis not in ("x", "z"):
        raise ValueError(basis)
    original = stim.Circuit.generated(f"surface_code:rotated_memory_{basis}", distance=3, rounds=3)
    flat = original.flattened()
    data = [1, 3, 5, 8, 10, 12, 15, 17, 19]
    def inserted(pauli: str | None, qubit: int | None) -> stim.Circuit:
        circuit = stim.Circuit()
        first_round_measurements = 0
        placed = False
        for instruction in flat:
            if not placed and instruction.name == "TICK" and first_round_measurements:
                if pauli is not None:
                    circuit.append(pauli + "_ERROR", [qubit], 1)
                placed = True
            circuit.append(instruction)
            if instruction.name == "MR":
                first_round_measurements += 1
        if not placed:
            raise AssertionError("Could not locate first syndrome round")
        return circuit
    baseline = inserted(None, None)
    base_d, base_l = baseline.compile_detector_sampler(seed=1).sample(1, separate_observables=True)
    if np.any(base_d) or np.any(base_l):
        raise AssertionError("Ideal bounded memory has nonzero detector or logical values")
    checks = np.zeros((baseline.num_detectors, 18), dtype=np.uint8)
    logicals = np.zeros((1, 18), dtype=np.uint8)
    for site, qubit in enumerate(data):
        for bit, pauli in enumerate(("Z", "X")):
            d, l = inserted(pauli, qubit).compile_detector_sampler(seed=1).sample(1, separate_observables=True)
            checks[:, 2*site+bit] = d[0]
            logicals[:, 2*site+bit] = l[0]
    if np.max(checks.sum(axis=0)) > 2:
        raise AssertionError("Single-axis data fault is not graphlike")
    if not np.any(checks) or not np.any(logicals):
        raise AssertionError("Stim fault signatures vanished into the reference sample")
    return checks, logicals, data


def fit_priors(train: dict, detail: bool) -> tuple[dict, np.ndarray]:
    counts = defaultdict(lambda: np.zeros(4, dtype=float))
    global_counts = np.zeros(4, dtype=float)
    for error, known, flags, full in zip(train["error"].reshape(-1, 2),
                                         train["known"].reshape(-1, 2),
                                         train["flags"].reshape(-1, 3),
                                         train["full"].reshape(-1, 4)):
        key = tuple(known.tolist())
        if detail:
            key += tuple(flags.tolist()) + tuple(full.tolist())
        state = int(error[0] + 2*error[1])
        counts[key][state] += 1
        global_counts[state] += 1
    global_prior = (global_counts + 2)/(global_counts.sum()+8)
    return {key: (value + 8*global_prior)/(value.sum()+8) for key, value in counts.items()}, global_prior


def priors_for(test: dict, row: int, fitted: dict, global_prior: np.ndarray, detail: bool) -> np.ndarray:
    result = []
    for site in range(9):
        key = tuple(test["known"][row, site].tolist())
        if detail:
            key += tuple(test["flags"][row, site].tolist()) + tuple(test["full"][row, site].tolist())
        result.append(fitted.get(key, global_prior))
    return np.asarray(result)


def matching_decode(checks: np.ndarray, logicals: np.ndarray, syndrome: np.ndarray, prior: np.ndarray) -> int:
    marginals = np.stack((prior[:, 1]+prior[:, 3], prior[:, 2]+prior[:, 3]), axis=1).reshape(-1)
    marginals = np.clip(marginals, 1e-6, .499999)
    weights = np.log((1-marginals)/marginals)
    matching = pymatching.Matching.from_check_matrix(checks, weights=weights, faults_matrix=logicals)
    return int(matching.decode(syndrome)[0])


def decode(train: dict, test: dict, basis: str) -> dict:
    checks, logicals, data = memory_signatures(basis)
    fitted_coarse, global_coarse = fit_priors(train, False)
    fitted_detail, global_detail = fit_priors(train, True)
    arms = {name: np.zeros(len(test["error"]), dtype=bool) for name in
            ("coarse_mwpm", "metadata_mwpm", "metadata_joint_bp_mwpm")}
    for row in range(len(test["error"])):
        error = test["error"][row].reshape(-1)
        syndrome = (checks @ error) & 1
        truth = int((logicals @ error)[0] & 1)
        coarse = priors_for(test, row, fitted_coarse, global_coarse, False)
        detail = priors_for(test, row, fitted_detail, global_detail, True)
        predictions = (matching_decode(checks, logicals, syndrome, coarse),
                       matching_decode(checks, logicals, syndrome, detail),
                       matching_decode(checks, logicals, syndrome,
                                       belief_priors(checks, syndrome, detail)))
        for key, prediction in zip(arms, predictions):
            arms[key][row] = prediction != truth
    return {"basis": basis, "data_qubits": data, "num_detectors": int(checks.shape[0]),
            "max_single_axis_detector_support": int(checks.sum(axis=0).max()),
            "rates": {key: float(v.mean()) for key, v in arms.items()},
            "failures": {key: int(v.sum()) for key, v in arms.items()},
            "paired_metadata_mwpm_minus_joint":
                (arms["metadata_mwpm"].astype(int)-arms["metadata_joint_bp_mwpm"].astype(int)).tolist()}
