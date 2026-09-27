"""Checks for the local optical fusion channel and its six-ring compilation."""

import pytest

from run_six_ring_physical_gate import branch_error, effective_channel
from six_ring_optical_instrument import (bell_diagonality_audit,
                                         bell_projection_table, optical_amplitudes)


def test_local_fock_instrument_conserves_probability() -> None:
    for cause in ("ideal", "extra_same_rail", "extra_opposite_rail", "extra_plus"):
        amplitudes = optical_amplitudes(cause)
        assert abs(sum(float((v.conj() @ v).real) for v in amplitudes.values()) - 1) < 1e-12


def test_ideal_and_faulty_bell_branches() -> None:
    ideal = bell_projection_table("ideal", 0.95)
    same = bell_projection_table("extra_same_rail", 0.95)
    plus = bell_projection_table("extra_plus", 0.95)
    assert abs(ideal["conclusive_probability"] - 0.5 * 0.95**2) < 1e-12
    assert all(branch_error(row["reported"], branch) == "none" or probability < 1e-12
               for row in ideal["record_rows"]
               for branch, probability in row["branches"].items())
    assert all(probability < 1e-12
               for row in same["record_rows"]
               for branch, probability in row["branches"].items()
               if branch_error(row["reported"], branch) == "Y")
    joint = sum(probability
                for row in plus["record_rows"]
                for branch, probability in row["branches"].items()
                if branch_error(row["reported"], branch) == "Y")
    assert abs(joint / plus["conclusive_probability"] - 0.125) < 1e-12


def test_coherent_extra_photon_cannot_be_promoted_to_pauli_y_rate() -> None:
    for eta in (.995, .95):
        ideal = bell_diagonality_audit("ideal", eta)
        source_y = bell_diagonality_audit("pauli_y_first", eta)
        same = bell_diagonality_audit("extra_same_rail", eta)
        opposite = bell_diagonality_audit("extra_opposite_rail", eta)
        plus = bell_diagonality_audit("extra_plus", eta)
        assert ideal["coherent_full_record_probability"] == 0
        assert source_y["coherent_full_record_probability"] == 0
        assert same["coherent_full_record_probability"] == 0
        assert abs(opposite["coherent_full_record_probability"] -
                   opposite["full_record_probability"]) < 1e-12
        assert abs(plus["coherent_full_record_probability"] -
                   plus["full_record_probability"]) < 1e-12
        with pytest.raises(ValueError, match="coherent accepted records"):
            effective_channel("extra_plus", eta, fault_prior=.01)
    same_channel = effective_channel("extra_same_rail", .95, fault_prior=.01)
    assert same_channel["joint_y_probability_per_attempt"] < 1e-12


def test_post_source_local_pauli_randomization_does_not_remove_extra_photon_coherence() -> None:
    for eta in (.995, .95):
        ideal = bell_diagonality_audit("ideal", eta, pauli_twirl=True)
        extra = bell_diagonality_audit("extra_plus", eta, pauli_twirl=True)
        assert ideal["coherent_full_record_probability"] == 0
        assert abs(extra["coherent_full_record_probability"] -
                   extra["full_record_probability"]) < 1e-12
