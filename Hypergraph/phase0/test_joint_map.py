import numpy as np
from itertools import product

from joint_map import decode


def test_joint_event_is_kept_as_one_categorical_fault() -> None:
    # One common-cause state flips both detectors. Independent graph states
    # could reproduce the syndrome only through two separate variables.
    checks = np.array([[1, 0], [0, 1]], dtype=np.uint8)
    logicals = np.array([[1, 1]], dtype=np.uint8)
    priors = np.array([[.70, .05, .05, .20]])
    prediction, success = decode(checks, logicals,
                                 np.array([1, 1], dtype=np.uint8), priors)
    assert success
    assert prediction.tolist() == [0]


def test_joint_map_rejects_unnormalized_priors() -> None:
    checks = np.array([[1, 0]], dtype=np.uint8)
    logicals = np.array([[1, 0]], dtype=np.uint8)
    try:
        decode(checks, logicals, np.array([1], dtype=np.uint8),
               np.array([[1., 1., 1., 1.]]))
    except ValueError:
        pass
    else:
        raise AssertionError("Unnormalized priors accepted")


def test_joint_map_matches_exhaustive_configuration_map() -> None:
    checks = np.array([[1, 0, 1, 0, 0, 1],
                       [0, 1, 1, 0, 1, 0]], dtype=np.uint8)
    logicals = np.array([[1, 1, 0, 0, 1, 0]], dtype=np.uint8)
    priors = np.array([[.70, .10, .08, .12],
                       [.65, .08, .12, .15],
                       [.75, .05, .10, .10]])
    syndrome = np.array([1, 1], dtype=np.uint8)
    best = None
    for states in product(range(4), repeat=3):
        error = np.zeros(6, dtype=np.uint8)
        error[::2] = np.asarray(states) & 1
        error[1::2] = np.asarray(states) >> 1
        if np.array_equal((checks @ error) & 1, syndrome):
            probability = float(np.prod(priors[np.arange(3), states]))
            if best is None or probability > best[0]:
                best = (probability, (logicals @ error) & 1)
    assert best is not None
    prediction, success = decode(checks, logicals, syndrome, priors)
    assert success
    assert np.array_equal(prediction, best[1])
