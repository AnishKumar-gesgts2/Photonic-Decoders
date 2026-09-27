import numpy as np

from exact_logical_map import lookup, syndrome_key


def test_exact_logical_class_pools_configurations() -> None:
    checks = np.array([[1, 0, 1, 0]], dtype=np.uint8)
    logicals = np.array([[1, 0, 0, 1]], dtype=np.uint8)
    channel = np.array([.7, .1, .1, .1])
    table = lookup(checks, logicals, channel)
    assert set(table) == {0, 1}
    assert syndrome_key(np.array([1], dtype=np.uint8)) == 1
