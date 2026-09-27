"""Optical and encoded-action gate for a Y fault on an unboosted fusion port."""
from __future__ import annotations

import json
from itertools import product
from pathlib import Path

import numpy as np

from boosted_encoded import encoded_availability
from native_ring_bulk import validate_bulk
from six_ring_optical_instrument import (all_record_branch_table,
                                         bell_projection_table)


def encoded_action_classes() -> dict[str, int]:
    """Exhaustively enumerate ideal Shor reconstruction after Y on physical A."""
    counts = {"joint_xx_zz": 0, "xx_only": 0, "zz_erased": 0}
    for x_a, x_b, z_a, logical_x, logical_z in product((0, 1), repeat=5):
        x = np.array([x_a, x_b, x_a ^ logical_x, x_b ^ logical_x], dtype=np.uint8)
        z = np.array([z_a, z_a ^ logical_z, z_a, z_a ^ logical_z], dtype=np.uint8)
        x[0] ^= 1
        z[0] ^= 1
        # Ideal two-photon BSM: A/C are basis-swapped and retain X on a
        # partial outcome; B/D retain Z. Full follows the measured branch.
        records = np.array([2 if x[0] else 1, 2 if z[1] else 1,
                            2 if x[2] else 1, 2 if z[3] else 1], dtype=np.uint8)
        known = encoded_availability(records)
        assert bool(known[0])
        decoded_x = int(x[0] ^ x[2])
        assert decoded_x ^ logical_x == 1
        if not known[1]:
            counts["zz_erased"] += 1
        else:
            left_z = int(z[0] if records[0] == 2 else z[2])
            right_z = int(z[1])
            if (left_z ^ right_z) ^ logical_z:
                counts["joint_xx_zz"] += 1
            else:
                counts["xx_only"] += 1
    if sum(counts.values()) != 32:
        raise AssertionError("Encoded action enumeration incomplete")
    return counts


def run(output: Path) -> dict:
    optical = {}
    for efficiency in (1.0, .995, .95):
        ideal = {tuple(row["record"]): row for row in
                 all_record_branch_table("ideal", efficiency)}
        faulty = {tuple(row["record"]): row for row in
                  all_record_branch_table("pauli_y_first", efficiency)}
        records = ideal.keys() | faulty.keys()
        tv = .5*sum(abs(ideal.get(record, {}).get("probability", 0) -
                         faulty.get(record, {}).get("probability", 0))
                     for record in records)
        optical[str(efficiency)] = {
            "raw_pnr_total_variation_ideal_vs_y_uniform_reference": tv,
            "conclusive_probability_y":
                bell_projection_table("pauli_y_first", efficiency)["conclusive_probability"]}
    conclusive = bell_projection_table("pauli_y_first", 1.0)["joint_report_and_branch"]
    if not (np.isclose(conclusive["psi_plus|phi_minus"], .25) and
            np.isclose(conclusive["psi_minus|phi_plus"], .25)):
        raise AssertionError("Y optical action did not flip both conclusive parities")
    classes = encoded_action_classes()
    bulk = validate_bulk(3)
    if not bulk["max_joint_outcome_detector_weight"] == 4:
        raise AssertionError("Periodic six-ring joint support changed")
    result = {"schema_version": "phase0-ancilla-free-pauli-y-gate-v1",
              "specified_fault": "single Pauli Y on first data photon before ideal two-photon dual-rail BSM",
              "source_incidence": None,
              "optical": optical,
              "ideal_encoded_action_counts_out_of_32_equal_input_assignments": classes,
              "periodic_six_ring_conclusive_joint_detector_weight": 4,
              "gate_status": {
                  "local_optical_action": "pass for specified Pauli Y fault",
                  "encoded_action": "pass but branches into joint, XX-only, and missing-Z outcomes",
                  "raw_pnr_fault_herald": "fail: distributions identical under uniform reference input",
                  "source_incidence": "missing",
                  "native_bounded_encoded_six_ring_logical": "missing",
                  "physical_decoder_claim": "no-go pending source incidence and native bounded-memory test"},
              "claim_boundary": "Ideal local Pauli mechanism and periodic support only; not a calibrated source, native bounded logical rate, or hardware result"}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(run(Path("outputs/phase0_ancilla_free_pauli_y_gate/results.json")), indent=2))
