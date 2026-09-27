import numpy as np

from boosted_encoded import encoded_availability, sample_physical_records, theoretical_no_loss_full


def test_encoded_failure_rule_without_loss() -> None:
    rng = np.random.default_rng(10)
    records = sample_physical_records(100_000, 1, 1.0, .693, rng)
    available = encoded_availability(records)[:, 0]
    assert np.all(available[:, 0])
    assert abs(available[:, 1].mean() - theoretical_no_loss_full(.693)) < .003


def test_photon_loss_cannot_improve_availability() -> None:
    rng = np.random.default_rng(10)
    full = encoded_availability(sample_physical_records(100_000, 1, 1.0, .693, rng))
    rng = np.random.default_rng(10)
    lossy = encoded_availability(sample_physical_records(100_000, 1, .95, .693, rng))
    assert np.mean(lossy) < np.mean(full)
