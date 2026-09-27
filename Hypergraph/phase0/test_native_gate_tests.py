"""Regression checks for native structural and synthetic decoder gates."""

from native_gate_tests import diagnostic_decoder_gate, structural_gate


def test_structural_hyperedge_is_a_stim_signature() -> None:
    result = structural_gate()
    assert result["fusions"] == 81
    assert result["stim_signatures_verified"] == 243
    assert result["all_xx_and_zz_supports_weight_two"]
    assert result["all_joint_supports_weight_four"]
    assert result["nonlocal_membrane_observables"] == 3


def test_synthetic_control_has_heldout_gain_without_optical_claim() -> None:
    result = diagnostic_decoder_gate()
    assert result["status"] == "synthetic diagnostic only"
    assert result["included_probability"] > 0.98
    assert result["full_channel_holdout_shots"] == 100_000
    assert result["full_channel_selected_failures"] < result["full_channel_mwpm_failures"]
    assert result["paired_mwpm_only_failures"] > result["paired_selector_only_failures"]
