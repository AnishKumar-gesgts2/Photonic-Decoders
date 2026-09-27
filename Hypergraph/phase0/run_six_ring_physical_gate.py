"""Audit whether optical records justify a categorical six-ring fault model."""
from __future__ import annotations

import json
from pathlib import Path

from native_gate_tests import structural_gate
from six_ring_optical_instrument import bell_diagonality_audit, bell_projection_table


def branch_error(reported: str, branch: str) -> str:
    reported_xx = int(reported.endswith("minus"))
    reported_zz = 1  # Both conclusive reports are Psi-family Bell outcomes.
    branch_xx = int(branch.endswith("minus"))
    branch_zz = int(branch.startswith("psi"))
    xx_flip = reported_xx ^ branch_xx
    zz_flip = reported_zz ^ branch_zz
    return {(0, 0): "none", (1, 0): "Z", (0, 1): "X", (1, 1): "Y"}[(xx_flip, zz_flip)]


def effective_channel(mechanism: str, efficiency: float = 0.95,
                      fault_prior: float = 0.01) -> dict:
    """Compile accepted events only when the optical action is Bell diagonal."""
    if not 0 <= fault_prior <= 1:
        raise ValueError(fault_prior)
    audit = bell_diagonality_audit(mechanism, efficiency)
    if fault_prior and not audit["full_record_action_supported"]:
        raise ValueError(f"{mechanism} has coherent accepted records; a categorical Pauli channel is unsupported")
    ideal = bell_projection_table("ideal", efficiency)
    faulty = bell_projection_table(mechanism, efficiency)
    priors = ((ideal, 1-fault_prior), (faulty, fault_prior))
    masses = {name: 0.0 for name in ("none", "X", "Z", "Y")}
    per_record = {}
    for table, prior in priors:
        for row in table["record_rows"]:
            key = tuple(row["record"])
            counts = per_record.setdefault(key, {name: 0.0 for name in masses})
            for branch, probability in row["branches"].items():
                name = branch_error(row["reported"], branch)
                masses[name] += prior*probability
                counts[name] += prior*probability
    accepted = sum(masses.values())
    conditional = {name: mass/accepted for name, mass in masses.items()}
    records = [{"counts": list(key), "probability_per_attempt": sum(row.values()),
                "conditional_fault_distribution": {name: mass/sum(row.values())
                                                  for name, mass in row.items()}}
               for key, row in sorted(per_record.items())]
    if abs(accepted - ((1-fault_prior)*ideal["conclusive_probability"] +
                       fault_prior*faulty["conclusive_probability"])) > 1e-12:
        raise AssertionError("Compiled optical mass disagrees with conclusive records")
    return {"optical_fault": mechanism, "detector_efficiency": efficiency,
            "fault_incidence_prior": fault_prior,
            "ideal_conclusive_probability": ideal["conclusive_probability"],
            "fault_conclusive_probability": faulty["conclusive_probability"],
            "mixed_conclusive_probability_per_attempt": accepted,
            "all_81_fusions_conclusive_probability_if_independent": accepted**81,
            "joint_y_probability_per_attempt": masses["Y"],
            "event_probabilities_conditioned_on_conclusive": conditional,
            "record_rows": records}


def run(output: Path) -> dict:
    structure = structural_gate()
    same = effective_channel("extra_same_rail")
    audits = {name: {str(eta): bell_diagonality_audit(name, eta)
                     for eta in (1.0, .995, .95)}
              for name in ("ideal", "extra_same_rail", "extra_opposite_rail",
                           "extra_plus", "pauli_y_first")}
    randomized = {name: {str(eta): bell_diagonality_audit(
                       name, eta, pauli_twirl=True)
                       for eta in (.995, .95)}
                  for name in ("ideal", "extra_opposite_rail", "extra_plus")}
    if same["joint_y_probability_per_attempt"] > 1e-12:
        raise AssertionError("Same-rail negative control unexpectedly made a joint fault")
    if not structure["all_joint_supports_weight_four"]:
        raise AssertionError("Six-ring structural gate failed")
    result = {"schema_version": "phase0-six-ring-optical-action-audit-v2",
              "structural_gate": {key: structure[key] for key in (
                  "resource_states", "resource_qubits", "fusions", "local_checks",
                  "nonlocal_membrane_observables", "stim_signatures_verified",
                  "all_joint_supports_weight_four")},
              "bell_action_audits": audits,
              "post_source_bilateral_pauli_randomization": randomized,
              "same_rail_negative_control": same,
              "decoder_gate": "not entered: extra-plus accepted records are Bell coherent and its source incidence is uncalibrated",
              "decision": "NO-GO for promoting extra-plus Bell-projected branch weights to Pauli Y probabilities",
              "claim_boundary": "The previous Bell-diagonal projection discarded coherent accepted-record terms and was a diagnostic approximation, not a physical joint-fault channel. Existing projected decoder numbers are superseded."}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(run(Path("outputs/phase0_six_ring_optical/results.json")), indent=2))
