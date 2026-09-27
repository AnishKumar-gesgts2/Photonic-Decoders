"""Minimal physical-information gate for the six-ring fusion hypothesis.

This run deliberately stops before logical decoder benchmarking when optical
records lack a justified fusion action or the unencoded network loses most
checks. No hidden optical mechanism is passed to a decoder.
"""
from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path

from native_gate_tests import structural_gate
from nonconclusive_decode import information_audit, raw_record_information
from six_ring_optical_instrument import (all_record_branch_table,
                                         bell_diagonality_audit, optical_amplitudes)


def record_masses(fault_prior: float, efficiency: float) -> dict:
    by_class = defaultdict(float)
    by_cause = {}
    for cause, prior in (("ideal", 1 - fault_prior), ("extra_plus", fault_prior)):
        rows = all_record_branch_table(cause, efficiency)
        total = sum(row["probability"] for row in rows)
        if abs(total - 1) > 1e-12:
            raise AssertionError("Optical record mass is not normalized")
        by_cause[cause] = {}
        for row in rows:
            cls = row["class"]
            key = ("full" if cls.startswith("psi_") else
                   "partial" if cls == "intrinsic_ambiguous" else
                   "short" if cls == "erasure" else "excess")
            by_class[key] += prior * row["probability"]
            by_cause[cause][key] = by_cause[cause].get(key, 0.0) + row["probability"]
    if abs(sum(by_class.values()) - 1) > 1e-12:
        raise AssertionError("Prior mixture does not conserve probability")
    return {"mixture": dict(by_class), "by_cause": by_cause}


def run(output: Path, shots: int = 10_000, efficiency: float = 0.95,
        fault_prior: float = 0.05) -> dict:
    if not 0 <= fault_prior <= 1:
        raise ValueError("Invalid fault prior")
    for cause in ("ideal", "extra_plus"):
        a = optical_amplitudes(cause, cutoff=4)
        b = optical_amplitudes(cause, cutoff=5)
        if set(a) != set(b) or any(max(abs(a[k] - b[k])) > 1e-12 for k in a):
            raise AssertionError("Fock-cutoff check failed")
    structure = structural_gate()
    if not structure["all_joint_supports_weight_four"]:
        raise AssertionError("Stim did not verify four-check joint support")
    records = record_masses(fault_prior, efficiency)
    ideal = records["by_cause"]["ideal"]
    if abs(ideal.get("full", 0) - efficiency**2 / 2) > 1e-12:
        raise AssertionError("Ideal Bell success limit failed")
    if abs(ideal.get("partial", 0) - efficiency**2 / 2) > 1e-12:
        raise AssertionError("Ideal partial-parity limit failed")
    audit = information_audit(shots=shots, efficiency=efficiency)
    accepted_action = bell_diagonality_audit("extra_plus", efficiency)
    information = raw_record_information(fault_prior, efficiency)
    if records["mixture"]["full"] >= 0.75:
        raise AssertionError("Architecture gate assumption needs reassessment")
    result = {
        "schema_version": "phase0-restart-action-audit-v2",
        "assumptions": {"efficiency": efficiency, "extra_plus_incidence": fault_prior,
                        "network": "periodic unencoded six-ring bulk, not bounded memory"},
        "validation": {"optical_normalization": "passed",
                       "fock_cutoff_4_vs_5": "passed",
                       "ideal_bell_limit": "passed",
                       "stim_injected_fault_signatures": structure["stim_signatures_verified"],
                       "joint_xx_zz_support_weight_four": True},
        "optical_record_fractions": records,
        "accepted_extra_plus_action": accepted_action,
        "categorical_joint_fault_probability_per_attempt": None,
        "raw_pnr_information": {
            "class_bits": information["bell_branch_information_bits_with_outcome_class"],
            "raw_bits": information["bell_branch_information_bits_with_full_pnr_record"],
            "increment_bits": information["additional_information_from_existing_raw_pnr_bits"]},
        "periodic_bulk_observability": audit,
        "decoder_gate": "not entered: extra-plus accepted records are Bell coherent, nonconclusive records have no validated action-conditioned channel, and unencoded fusion success is below the published failure tolerance",
        "decision": "NO-GO for current unboosted, unencoded Phase 0 hypothesis; conditional four-check mechanism retained",
        "unresolved": [
            "extra-plus incidence is assumed rather than measured",
            "accepted extra-plus records are Bell coherent and cannot be assigned a categorical Pauli Y rate from branch weights",
            "partial, short and excess optical operations have not been propagated through a bounded six-ring memory",
            "periodic nonlocal sectors are not a memory logical error rate",
            "boosted or encoded fusion would change the architecture and requires a new instrument"],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(run(Path("outputs/phase0_restart/results.json")), indent=2))
