"""Checks for erased-parity information accounting and decoder likelihoods."""

import numpy as np

from nonconclusive_decode import (
    information_audit, observable_check_basis,
    raw_record_information,
)


def test_observable_checks_do_not_touch_unknown_outcomes() -> None:
    h = np.array([[1, 0, 1, 0], [0, 1, 0, 1]], dtype=np.uint8)
    known = np.array([1, 0, 1, 0], dtype=bool)
    basis = observable_check_basis(h, known)
    assert basis.shape == (1, 4)
    assert np.array_equal(basis[0], h[0])


def test_information_audit_and_existing_raw_record_gain() -> None:
    audit = information_audit(shots=500)
    assert audit["fraction_with_no_independent_measurable_check_combination"] > 0.75
    assert audit["mean_free_missing_bits_even_if_all_29_ideal_constraints_were_known"] > 15
    raw = raw_record_information()
    assert 0 < raw["additional_information_from_existing_raw_pnr_bits"] < 0.1
