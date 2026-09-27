"""Exact local Fock instrument for a dual-rail fusion of two six-ring ports.

Each fused graph-state qubit is maximally entangled with an orthonormal state
of the other five qubits of its ring. Those four reference states allow the
local fusion instrument to be computed in four modes without constructing the
full 24-mode two-ring state. The specified excess-photon faults are local
optical preparations, not calibrated six-ring source emission probabilities.
"""
from __future__ import annotations

from collections import defaultdict
from itertools import product
from math import comb, sqrt

import numpy as np

from optical_primitives import apply_bs, single_fusion_outcome


MECHANISMS = ("ideal", "extra_same_rail", "extra_opposite_rail", "extra_plus",
              "pauli_y_first")
BELL = {
    "phi_plus": np.array([1, 0, 0, 1]) / sqrt(2),
    "phi_minus": np.array([1, 0, 0, -1]) / sqrt(2),
    "psi_plus": np.array([0, 1, 1, 0]) / sqrt(2),
    "psi_minus": np.array([0, 1, -1, 0]) / sqrt(2),
}


def input_occupation(a: int, b: int, mechanism: str) -> tuple[int, ...]:
    if mechanism not in MECHANISMS:
        raise ValueError(mechanism)
    occupation = [0, 0, 0, 0]
    occupation[a] += 1
    occupation[2+b] += 1
    if mechanism == "extra_same_rail":
        occupation[a] += 1
    elif mechanism == "extra_opposite_rail":
        occupation[1-a] += 1
    return tuple(occupation)


def optical_amplitudes(mechanism: str, cutoff: int = 4,
                       twirl_x: bool = False, twirl_z: bool = False) -> dict[tuple[int, ...], np.ndarray]:
    """Output PNR amplitude, with four orthogonal graph-reference labels."""
    output = defaultdict(lambda: np.zeros(4, dtype=complex))
    for a, b in product((0, 1), repeat=2):
        if mechanism == "pauli_y_first":
            # Y|0> = i|1>, Y|1> = -i|0>. Keep the untouched graph-reference
            # label (a,b) while changing only the measured optical port.
            state = {input_occupation(1-a, b, "ideal"):
                     .5j*(1-2*a)}
        elif mechanism == "extra_plus":
            # A normalized application of a_+^dagger to the occupied port:
            # bosonic enhancement gives same-rail weight 2/3 and opposite
            # rail weight 1/3. This is a specified Kraus fault on the port.
            state = {input_occupation(a, b, "extra_same_rail"): 0.5*sqrt(2/3),
                     input_occupation(a, b, "extra_opposite_rail"): 0.5*sqrt(1/3)}
        else:
            state = {input_occupation(a, b, mechanism): 0.5}
        if twirl_x or twirl_z:
            randomized = defaultdict(complex)
            for occupation, amplitude in state.items():
                transformed = ((occupation[1], occupation[0],
                                occupation[3], occupation[2])
                               if twirl_x else occupation)
                phase = (-1) ** (transformed[1] + transformed[3]) if twirl_z else 1
                randomized[transformed] += phase * amplitude
            state = dict(randomized)
        for rail in (0, 1):
            state = apply_bs(state, rail, rail+2, cutoff=cutoff)
        for occupation, amplitude in state.items():
            output[occupation][2*a+b] += amplitude
    if abs(sum(float(np.vdot(v, v).real) for v in output.values()) - 1) > 1e-12:
        raise AssertionError("Optical instrument lost norm")
    return dict(output)


def conditional_reference_states(mechanism: str, efficiency: float,
                                 twirl_x: bool = False,
                                 twirl_z: bool = False) -> dict:
    if not 0 <= efficiency <= 1:
        raise ValueError(efficiency)
    vectors = defaultdict(lambda: np.zeros(4, dtype=complex))
    for actual, input_vector in optical_amplitudes(
            mechanism, twirl_x=twirl_x, twirl_z=twirl_z).items():
        for observed in product(*(range(n+1) for n in actual)):
            weight = 1.0
            for n, k in zip(actual, observed):
                weight *= sqrt(comb(n, k) * efficiency**k * (1-efficiency)**(n-k))
            if weight:
                lost = tuple(n-k for n, k in zip(actual, observed))
                vectors[(observed, lost)] += weight * input_vector
    if abs(sum(float(np.vdot(v, v).real) for v in vectors.values()) - 1) > 1e-12:
        raise AssertionError("Detector-loss instrument lost norm")
    return dict(vectors)


def bell_diagonality_audit(mechanism: str, efficiency: float,
                           tolerance: float = 1e-10,
                           pauli_twirl: bool = False) -> dict:
    """Test whether each accepted PNR effect admits a classical Bell-action table.

    Diagonal branch weights alone are insufficient: off-diagonal Bell terms
    retain coherent action on the untouched graph reference. Report the mass
    of records that cannot be passed to a categorical Pauli decoder.
    """
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")
    bell = np.column_stack(tuple(BELL.values()))
    effects = defaultdict(lambda: np.zeros((4, 4), dtype=complex))
    settings = ((False, False), (True, False), (False, True), (True, True)) if pauli_twirl else ((False, False),)
    for twirl_x, twirl_z in settings:
        for (record, _lost), vector in conditional_reference_states(
                mechanism, efficiency, twirl_x, twirl_z).items():
            effects[record] += np.outer(vector, vector.conj()) / len(settings)
    full = coherent = 0.0
    rows = []
    for record, effect in sorted(effects.items()):
        if not single_fusion_outcome(record).startswith("psi_"):
            continue
        in_bell_basis = bell.conj().T @ effect @ bell
        mass = float(np.trace(in_bell_basis).real)
        off_diagonal = in_bell_basis - np.diag(np.diag(in_bell_basis))
        relative = float(np.max(np.abs(off_diagonal)) / mass) if mass else 0.0
        unsupported = relative > tolerance
        full += mass
        if unsupported:
            coherent += mass
        rows.append({"record": list(record), "probability_per_fault_attempt": mass,
                     "max_bell_offdiagonal_relative_to_record_mass": relative,
                     "categorical_pauli_action_supported": not unsupported})
    return {"mechanism": mechanism, "efficiency": efficiency,
            "pauli_twirl": pauli_twirl,
            "full_record_probability": full,
            "coherent_full_record_probability": coherent,
            "categorical_full_record_probability": full - coherent,
            "full_record_action_supported": coherent <= tolerance,
            "records": rows}


def bell_projection_table(mechanism: str, efficiency: float) -> dict:
    """P(reported PNR, orthogonal ideal-fusion branch | optical cause)."""
    vectors = conditional_reference_states(mechanism, efficiency)
    by_record = defaultdict(lambda: np.zeros((4, 4), dtype=complex))
    for (record, _lost), vector in vectors.items():
        by_record[record] += np.outer(vector, vector.conj())
    branch_mass = defaultdict(float)
    record_rows = []
    conclusive = 0.0
    for record, rho in sorted(by_record.items()):
        report = single_fusion_outcome(record)
        if not report.startswith("psi_"):
            continue
        mass = float(np.trace(rho).real)
        conclusive += mass
        branches = {}
        for name, bell in BELL.items():
            probability = float(np.vdot(bell, rho @ bell).real)
            branches[name] = probability
            branch_mass[(report, name)] += probability
        if abs(sum(branches.values()) - mass) > 1e-12:
            raise AssertionError("Bell reference basis incomplete")
        record_rows.append({"record": list(record), "reported": report,
                            "probability": mass, "branches": branches})
    return {"mechanism": mechanism, "efficiency": efficiency,
            "conclusive_probability": conclusive,
            "joint_report_and_branch": {f"{report}|{branch}": p
                                        for (report, branch), p in sorted(branch_mass.items())},
            "record_rows": record_rows}


def all_record_branch_table(mechanism: str, efficiency: float) -> list[dict]:
    """Keep every observed PNR pattern, including partial and short records."""
    by_record = defaultdict(lambda: np.zeros((4, 4), dtype=complex))
    for (record, _lost), vector in conditional_reference_states(mechanism, efficiency).items():
        by_record[record] += np.outer(vector, vector.conj())
    result = []
    for record, rho in sorted(by_record.items()):
        probability = float(np.trace(rho).real)
        if probability < 1e-15:
            continue
        branches = {name: float(np.vdot(bell, rho @ bell).real)
                    for name, bell in BELL.items()}
        if abs(sum(branches.values()) - probability) > 1e-12:
            raise AssertionError("Branch probabilities do not conserve mass")
        result.append({"record": list(record),
                       "class": single_fusion_outcome(record),
                       "probability": probability,
                       "branches": branches})
    if abs(sum(row["probability"] for row in result) - 1) > 1e-12:
        raise AssertionError("Record table not normalized")
    return result
