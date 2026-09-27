import numpy as np

from encoded_proxy import (belief_priors, contracted_checks, deform_sectors,
                           sample_shots)
from native_ring_bulk import validate_bulk


def test_clean_encoded_records_reconstruct_every_available_parity() -> None:
    data = sample_shots(32, 1.0, .693, 0.0, 0.0, 17)
    assert not np.any(data["flags"])
    assert not np.any(data["errors"][data["known"]])


def test_branch_conditioned_success_is_a_distinct_sensitivity_case() -> None:
    scalar = sample_shots(500, 1.0, .693, 0, 0, 19)
    conditional = sample_shots(500, 1.0, .693, 0, 0, 19, branch_conditioned=True)
    assert scalar["known"].shape == conditional["known"].shape
    assert not np.array_equal(scalar["records"], conditional["records"])
    assert not np.any(conditional["errors"][conditional["known"]])


def test_superchecks_and_deformed_sectors_avoid_missing_bits() -> None:
    bulk = validate_bulk(3)
    known = np.ones(2*bulk["fusions"], dtype=bool)
    known[0] = False
    checks = contracted_checks(bulk["checks"], known)
    sectors = deform_sectors(bulk["checks"], bulk["logicals"], known)
    assert not np.any(checks[:, ~known])
    assert np.max(checks.sum(axis=0)) <= 2
    assert sectors is not None
    assert not np.any(sectors[:, ~known])


def test_joint_belief_updates_are_normalized() -> None:
    checks = np.array([[1, 0, 1, 0]], dtype=np.uint8)
    syndrome = np.array([1], dtype=np.uint8)
    prior = np.array([[.9, .02, .02, .06], [.9, .02, .02, .06]])
    posterior = belief_priors(checks, syndrome, prior)
    assert np.allclose(posterior.sum(axis=1), 1)
    assert np.all(np.isfinite(posterior))
