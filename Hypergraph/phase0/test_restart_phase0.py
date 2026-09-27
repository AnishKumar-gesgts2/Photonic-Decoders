"""Regression checks for the restarted physical-information gate."""
from restart_phase0 import record_masses
from six_ring_optical_instrument import optical_amplitudes


def test_cutoff_and_ideal_record_limit() -> None:
    for cause in ("ideal", "extra_plus"):
        assert optical_amplitudes(cause, 4).keys() == optical_amplitudes(cause, 5).keys()
    ideal = record_masses(0, 0.95)["mixture"]
    assert abs(ideal["full"] - 0.5 * 0.95**2) < 1e-12
    assert abs(ideal["partial"] - 0.5 * 0.95**2) < 1e-12
    assert abs(ideal["short"] - (1 - 0.95**2)) < 1e-12


def test_fault_mixture_is_normalized_and_flags_excess() -> None:
    rows = record_masses(0.05, 0.95)["mixture"]
    assert abs(sum(rows.values()) - 1) < 1e-12
    assert rows["excess"] > 0
