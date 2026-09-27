"""Exact four-photon click instrument of Hauser et al.'s 4x4 boosted BSM.

Spatial modes 1,2 carry the Bell input; 3,4 carry an ancillary Bell pair.
Each has H,V rails. The published 4x4 unitary acts identically on H and V.
This module models number-resolving detection and specified ancilla Pauli faults;
it does not use measured click frequencies or invent an experimental fault rate.
"""
from __future__ import annotations

from collections import defaultdict
from itertools import product
from math import sqrt

import numpy as np


U = np.array([[1, 1, 1, 1], [1, -1, -1j, 1j],
              [1, -1, 1j, -1j], [1, 1, -1, -1]], complex) / 2
BELL = ("phi+", "phi-", "psi+", "psi-")


def bell_terms(label: str, first: int, second: int) -> list[tuple[complex, tuple[int, int]]]:
    """Bell-state creation terms in H=0,V=1 polarization."""
    if label not in BELL:
        raise ValueError(label)
    sign = 1 if label.endswith("+") else -1
    pairs = ((0, 0), (1, 1)) if label.startswith("phi") else ((0, 1), (1, 0))
    return [(1/sqrt(2), (2*first+pairs[0][0], 2*second+pairs[0][1])),
            (sign/sqrt(2), (2*first+pairs[1][0], 2*second+pairs[1][1]))]


def output_state(data_bell: str, ancilla_bell: str = "phi+",
                 extra_input_mode: int | None = None) -> dict[tuple[int, ...], complex]:
    """Coherent Fock amplitudes, optionally with a fifth input photon.

    The extra-mode preparation is a† on data mode 0H, normalized by sqrt(3/2)
    for every Bell input. This is a specified source fault, not its incidence.
    """
    if not np.allclose(U.conj().T @ U, np.eye(4)):
        raise AssertionError("Multiport is not unitary")
    amplitudes: dict[tuple[int, ...], complex] = defaultdict(complex)
    if extra_input_mode is not None and not 0 <= extra_input_mode < 4:
        raise ValueError("Extra photon must enter one of the two data spatial modes")
    for ca, pair_a in bell_terms(data_bell, 0, 1):
        for cb, pair_b in bell_terms(ancilla_bell, 2, 3):
            partial = {tuple([0]*8): ca*cb/(sqrt(1.5) if extra_input_mode is not None else 1)}
            inputs = pair_a + pair_b + (() if extra_input_mode is None else (extra_input_mode,))
            for input_mode in inputs:
                next_state: dict[tuple[int, ...], complex] = defaultdict(complex)
                for occupation, amplitude in partial.items():
                    for out_spatial in range(4):
                        out_mode = 2*out_spatial + input_mode % 2
                        updated = list(occupation)
                        updated[out_mode] += 1
                        next_state[tuple(updated)] += amplitude * U[out_spatial, input_mode//2] * sqrt(updated[out_mode])
                partial = next_state
            for occupation, amplitude in partial.items():
                amplitudes[occupation] += amplitude
    result = {k: v for k, v in amplitudes.items() if abs(v) > 1e-12}
    if not np.isclose(sum(abs(v)**2 for v in result.values()), 1, atol=1e-12):
        raise AssertionError("Optical Fock state not normalized")
    return result


def instrument(ancilla_bell: str) -> dict:
    """Click probabilities and Bell-basis POVM, including coherence diagnostic."""
    states = [output_state(label, ancilla_bell) for label in BELL]
    records = sorted(set().union(*(set(s) for s in states)))
    effects = {}
    probabilities = np.zeros((4, len(records)))
    for j, record in enumerate(records):
        v = np.array([state.get(record, 0) for state in states])
        effects[record] = np.outer(v.conj(), v)
        probabilities[:, j] = np.abs(v)**2
    if not np.allclose(probabilities.sum(axis=1), 1, atol=1e-12):
        raise AssertionError("Conditional PNR probabilities not normalized")
    return {"records": records, "probabilities": probabilities, "effects": effects}


def ideal_report(record: tuple[int, ...], ideal: dict, tol: float = 1e-12) -> tuple[int | None, int | None]:
    """Return reported XX,ZZ bits if fixed across ideal compatible Bell inputs."""
    j = ideal["records"].index(record) if record in ideal["records"] else None
    possible = [] if j is None else np.flatnonzero(ideal["probabilities"][:, j] > tol)
    if not len(possible):
        return None, None
    xx = {int(i % 2) for i in possible}
    zz = {int(i >= 2) for i in possible}
    return (next(iter(xx)) if len(xx) == 1 else None,
            next(iter(zz)) if len(zz) == 1 else None)


def report_table(ancilla_bell: str) -> list[dict]:
    """P(click, reported parity, true Bell input) for a specified ancilla state."""
    ideal = instrument("phi+")
    actual = instrument(ancilla_bell)
    rows = []
    for j, record in enumerate(actual["records"]):
        report = ideal_report(record, ideal)
        for bell, label in enumerate(BELL):
            probability = float(actual["probabilities"][bell, j])
            if probability > 1e-14:
                rows.append({"record": record, "input": label, "probability": probability,
                             "reported_xx": report[0], "reported_zz": report[1]})
    return rows


def excess_photon_loss_effects(efficiency: float, extra_input_mode: int = 0) -> dict:
    """Bell-basis Gram matrices for a specified five-photon source fault.

    Returned effects include the physical probability eta**4*(1-eta). The
    lost photon's mode is traced out, so amplitudes from different loss modes
    are never added coherently. The normalized a† preparation is a conditional
    source-fault map, not a complete trace-preserving channel on arbitrary
    two-qubit input states.
    """
    if not 0 <= efficiency <= 1:
        raise ValueError(efficiency)
    states = [output_state(label, extra_input_mode=extra_input_mode) for label in BELL]
    vectors: dict[tuple[tuple[int, ...], int], np.ndarray] = defaultdict(lambda: np.zeros(4, complex))
    factor = efficiency**2 * sqrt(1-efficiency)
    for bell, state in enumerate(states):
        for occupation, amplitude in state.items():
            for lost_mode, count in enumerate(occupation):
                if count:
                    observed = list(occupation)
                    observed[lost_mode] -= 1
                    vectors[(tuple(observed), lost_mode)][bell] += amplitude*sqrt(count)*factor
    effects: dict[tuple[int, ...], np.ndarray] = defaultdict(lambda: np.zeros((4, 4), complex))
    for (record, _lost_mode), vector in vectors.items():
        effects[record] += np.outer(vector.conj(), vector)
    target_mass = 5*efficiency**4*(1-efficiency)
    if not np.allclose([sum(float(e[i, i].real) for e in effects.values()) for i in range(4)],
                       target_mass, atol=1e-10):
        raise AssertionError("One-loss excess-photon probability does not normalize")
    return dict(effects)
