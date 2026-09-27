"""Checks for the published-map translation and exact logical scoring."""

import numpy as np

from bounded_optical_d3 import memory_signatures
from run_paper_source_sensitivity import exact_risks, paper_channel


def test_first_order_paper_map_keeps_all_axes_and_normalizes() -> None:
    three = paper_channel("three_level", .01)
    four = paper_channel("four_level", .01, .02)
    assert np.allclose(three, [.97, .01, .01, .01])
    assert np.allclose(four, [.975, .005, .015, .005])
    assert np.isclose(three.sum(), 1)
    assert np.isclose(four.sum(), 1)


def test_exact_logical_optimum_bounds_decoders_and_zero_fault_control() -> None:
    checks, logicals, _ = memory_signatures("z")
    clean = exact_risks(checks, logicals, np.array([1., 0., 0., 0.]))
    assert all(clean[name] == 0 for name in
               ("calibrated_mwpm", "joint_configuration_map",
                "optimal_logical_class_map"))
    biased = exact_risks(checks, logicals,
                         paper_channel("four_level", .01, .02))
    assert biased["optimal_logical_class_map"] <= biased["calibrated_mwpm"]
    assert biased["optimal_logical_class_map"] <= biased["joint_configuration_map"]
    # A configuration-MAP decision can be worse than matching on logical risk.
    assert biased["joint_configuration_map"] > biased["calibrated_mwpm"]
