import numpy as np

from six_ring_optical_instrument import (all_record_branch_table,
                                         bell_projection_table,
                                         optical_amplitudes)


def test_y_fault_preserves_raw_record_distribution_and_flips_both_full_bits() -> None:
    ideal = {tuple(row["record"]): row for row in all_record_branch_table("ideal", 1.0)}
    faulty = {tuple(row["record"]): row for row in all_record_branch_table("pauli_y_first", 1.0)}
    assert ideal.keys() == faulty.keys()
    for record in ideal:
        assert np.isclose(ideal[record]["probability"], faulty[record]["probability"])
    table = bell_projection_table("pauli_y_first", 1.0)
    assert np.isclose(table["conclusive_probability"], .5)
    joint = table["joint_report_and_branch"]
    assert np.isclose(joint["psi_plus|phi_minus"], .25)
    assert np.isclose(joint["psi_minus|phi_plus"], .25)
    assert np.isclose(sum(v for k, v in joint.items() if
                          k not in ("psi_plus|phi_minus", "psi_minus|phi_plus")), 0)


def test_y_fault_partial_record_flips_only_the_known_parity() -> None:
    a = optical_amplitudes("pauli_y_first", cutoff=4)
    b = optical_amplitudes("pauli_y_first", cutoff=5)
    assert a.keys() == b.keys()
    assert all(np.allclose(a[key], b[key]) for key in a)
    ideal = all_record_branch_table("ideal", 1.0)
    faulty = all_record_branch_table("pauli_y_first", 1.0)
    for rows, expected_prefix in ((ideal, "phi"), (faulty, "psi")):
        partial = [row for row in rows if row["class"] == "intrinsic_ambiguous"]
        assert partial
        for row in partial:
            assert sum(value for name, value in row["branches"].items()
                       if not name.startswith(expected_prefix)) < 1e-12
