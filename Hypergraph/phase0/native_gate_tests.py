"""Stim structural gates and a diagnostic periodic-sector decoder control."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pymatching
import stim

from native_ring_bulk import validate_bulk


def insert_pauli_before_fusion(circuit: stim.Circuit, fusion_index: int,
                               qubit: int, pauli: str) -> stim.Circuit:
    if pauli not in ("X", "Y", "Z"):
        raise ValueError(pauli)
    result = stim.Circuit()
    seen = 0
    for instruction in circuit:
        if instruction.name == "MXX":
            if seen == fusion_index:
                # A stochastic error keeps Stim's noiseless detector reference.
                result.append(f"{pauli}_ERROR", [qubit], 1.0)
            seen += 1
        result.append(instruction)
    if fusion_index >= seen:
        raise IndexError(fusion_index)
    return result


def structural_gate() -> dict:
    bulk = validate_bulk(3)
    checks, logicals = bulk["checks"], bulk["logicals"]
    examples = {}
    verified = 0
    for fusion_index, (qubit, _) in enumerate(bulk["fusions_list"]):
        for pauli, bit in (("X", 1), ("Z", 0), ("Y", None)):
            altered = insert_pauli_before_fusion(bulk["circuit"], fusion_index,
                                                  qubit, pauli)
            detections, observables = altered.compile_detector_sampler(seed=27).sample(
                shots=8, separate_observables=True)
            changed = ([2*fusion_index+bit] if bit is not None
                       else [2*fusion_index, 2*fusion_index+1])
            expected_d = np.bitwise_xor.reduce(checks[:, changed], axis=1)
            expected_l = np.bitwise_xor.reduce(logicals[:, changed], axis=1)
            if not (np.all(detections == expected_d) and
                    np.all(observables == expected_l)):
                raise AssertionError(f"Stim signature mismatch at fusion {fusion_index}, {pauli}")
            verified += 1
            if fusion_index == 0:
                examples[pauli] = {"detectors": np.flatnonzero(expected_d).tolist(),
                                   "membrane_observables": np.flatnonzero(expected_l).tolist()}
    result = {key: bulk[key] for key in (
        "side", "resource_states", "resource_qubits", "fusions", "local_checks",
        "independent_check_rank", "nonlocal_membrane_observables",
        "local_check_weights", "min_joint_outcome_detector_weight",
        "max_joint_outcome_detector_weight")}
    result.update({"stim_signatures_verified": verified,
                   "all_xx_and_zz_supports_weight_two": all(
                       len(row["xx_checks"]) == len(row["zz_checks"]) == 2
                       for row in bulk["per_fusion"]),
                   "all_joint_supports_weight_four": all(
                       len(row["joint_checks"]) == 4 for row in bulk["per_fusion"]),
                   "first_fusion_diagnostic_signatures": examples})
    return result


def diagnostic_decoder_gate(p_each: float = 0.002, threshold: float = 0.5,
                            shots: int = 100_000,
                            channel_label: str = "synthetic diagnostic only") -> dict:
    """Exact 0/1/2-fault synthetic channel; Y is a hypothetical joint event.

    This control establishes whether the native check geometry plus event prior
    can help predict nonlocal parity sectors. It has no calibrated optical
    interpretation and is not a bounded memory logical-error-rate study.
    """
    from collections import defaultdict
    from itertools import combinations
    from math import log

    bulk = validate_bulk(3)
    h, logicals = bulk["checks"], bulk["logicals"]
    n = bulk["fusions"]
    p0 = 1 - 3*p_each
    if p0 <= 0:
        raise ValueError("Invalid synthetic channel")
    odds = p_each / p0
    signatures = []
    for j in range(n):
        for name, indices in (("X", (2*j+1,)), ("Z", (2*j,)),
                              ("Y", (2*j, 2*j+1))):
            det = np.bitwise_xor.reduce(h[:, indices], axis=1)
            obs = np.bitwise_xor.reduce(logicals[:, indices], axis=1)
            d_key = sum(int(bit) << k for k, bit in enumerate(det))
            o_key = sum(int(bit) << k for k, bit in enumerate(obs))
            signatures.append((j, name, d_key, o_key))
    groups = defaultdict(lambda: {"logical": np.zeros(8), "y": 0.0, "total": 0.0})
    def add(d: int, l: int, weight: float, y: bool) -> None:
        group = groups[d]
        group["logical"][l] += weight
        group["total"] += weight
        if y:
            group["y"] += weight
    add(0, 0, 1.0, False)
    for _j, name, d, l in signatures:
        add(d, l, odds, name == "Y")
    pair_count = 0
    for a, b in combinations(signatures, 2):
        if a[0] == b[0]:
            continue
        add(a[2] ^ b[2], a[3] ^ b[3], odds**2,
            a[1] == "Y" or b[1] == "Y")
        pair_count += 1
    # Strong graphlike baseline uses the true X and Z marginal rates.
    marginal = 2*p_each
    matching = pymatching.Matching.from_check_matrix(
        h, weights=np.full(2*n, log((1-marginal)/marginal)),
        faults_matrix=logicals)
    keys = list(groups)
    syndrome_matrix = np.asarray(
        [[(key >> k) & 1 for k in range(h.shape[0])] for key in keys],
        dtype=np.uint8)
    predictions = matching.decode_batch(syndrome_matrix)
    total_mass = baseline_wrong = map_wrong = selected_wrong = active_mass = y_mass = captured_y = 0.0
    active_groups = 0
    for key, prediction in zip(keys, predictions):
        group = groups[key]
        mass = group["total"]
        baseline_label = sum(int(bit) << k for k, bit in enumerate(prediction))
        map_label = int(np.argmax(group["logical"]))
        active = group["y"] > 0 and group["y"] / mass > threshold
        selected_label = map_label if active else baseline_label
        total_mass += mass
        baseline_wrong += mass - group["logical"][baseline_label]
        map_wrong += mass - group["logical"][map_label]
        selected_wrong += mass - group["logical"][selected_label]
        y_mass += group["y"]
        if active:
            active_groups += 1
            active_mass += mass
            captured_y += group["y"]
    # Independent full-channel holdout, including three-or-more-fault shots.
    rng = np.random.default_rng(14091)
    sampled = rng.choice(4, size=(shots, n), p=(p0, p_each, p_each, p_each))
    x = np.isin(sampled, (1, 3)).astype(np.uint8)
    z = np.isin(sampled, (2, 3)).astype(np.uint8)
    sx = h[:, 1::2].T
    sz = h[:, 0::2].T
    lx = logicals[:, 1::2].T
    lz = logicals[:, 0::2].T
    sampled_syndrome = ((x @ sx) ^ (z @ sz)) & 1
    sampled_logical = ((x @ lx) ^ (z @ lz)) & 1
    baseline = matching.decode_batch(sampled_syndrome)
    selected = baseline.copy()
    activated = np.zeros(shots, dtype=bool)
    for row in range(shots):
        key = sum(int(bit) << k for k, bit in enumerate(sampled_syndrome[row]))
        group = groups.get(key)
        if group is not None and group["y"] > 0 and group["y"] / group["total"] > threshold:
            best = int(np.argmax(group["logical"]))
            selected[row] = [(best >> k) & 1 for k in range(3)]
            activated[row] = True
    baseline_failure = np.any(baseline != sampled_logical, axis=1)
    selected_failure = np.any(selected != sampled_logical, axis=1)
    paired_gain = int(np.count_nonzero(baseline_failure & ~selected_failure))
    paired_harm = int(np.count_nonzero(selected_failure & ~baseline_failure))
    # Account for the tail discarded by the exact at-most-two-fault analysis.
    included_mass = p0**n * total_mass
    return {"status": channel_label, "p_x_per_fusion": p_each,
            "p_z_per_fusion": p_each, "p_y_per_fusion": p_each,
            "max_faults_enumerated": 2, "enumerated_distinct_pairs": pair_count,
            "distinct_syndromes": len(groups), "included_probability": included_mass,
            "baseline_mwpm_sector_failure_conditional": baseline_wrong/total_mass,
            "oracle_exact_map_sector_failure_conditional": map_wrong/total_mass,
            "syndrome_selected_map_sector_failure_conditional": selected_wrong/total_mass,
            "selector_threshold": threshold,
            "selector_activation_probability_conditional": active_mass/total_mass,
            "selector_active_syndrome_groups": active_groups,
            "y_event_probability_conditional": y_mass/total_mass,
            "selector_y_recall": captured_y/y_mass if y_mass else None,
            "full_channel_holdout_shots": shots,
            "full_channel_holdout_seed": 14091,
            "full_channel_mwpm_failures": int(baseline_failure.sum()),
            "full_channel_selected_failures": int(selected_failure.sum()),
            "full_channel_mwpm_sector_failure": float(baseline_failure.mean()),
            "full_channel_selected_sector_failure": float(selected_failure.mean()),
            "full_channel_selector_activation": float(activated.mean()),
            "paired_mwpm_only_failures": paired_gain,
            "paired_selector_only_failures": paired_harm}


def run(output: Path) -> dict:
    structural = structural_gate()
    diagnostic = diagnostic_decoder_gate()
    report = {"schema_version": "phase0-native-gates-v2",
              "structural_hyperedge": structural,
              "hypothetical_decoder_control": diagnostic}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(run(Path("outputs/phase0_native_gates/results.json")), indent=2))
