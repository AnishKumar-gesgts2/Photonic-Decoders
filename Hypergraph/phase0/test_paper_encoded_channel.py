"""Validate the independent source-to-encoded fusion enumeration."""

import numpy as np

from run_paper_encoded_channel import (compose_two_photons, encoded_table,
                                       input_photon_channel)


def test_zero_fault_encoded_limit_and_probability_conservation() -> None:
    clean = encoded_table(np.array([1., 0., 0., 0.]), 1.0)
    assert np.isclose(clean["encoded_availability"]["both_known"], .75)
    assert np.allclose(clean["both_known_action_I_ZZ_only_XX_only_joint_per_attempt"],
                       [.75, 0, 0, 0])
    assert np.isclose(sum(row["probability_per_encoded_fusion"]
                          for row in clean["record_action_rows"]), 1)


def test_single_input_y_reproduces_earlier_exact_encoded_action() -> None:
    one_y = np.tile([1., 0., 0., 0.], (4, 1))
    one_y[0] = [0., 0., 0., 1.]
    result = encoded_table(np.array([1., 0., 0., 0.]), 1.0,
                           physical_bsm_channels=one_y)
    assert np.allclose(result["both_known_action_I_ZZ_only_XX_only_joint_per_attempt"],
                       [0, 0, .25, .5])
    assert np.isclose(result["encoded_availability"]["xx_only"], .25)


def test_paper_input_rates_and_two_input_pauli_composition() -> None:
    three = input_photon_channel("three_level", .01, .02)
    four = input_photon_channel("four_level", .01, .02)
    assert np.allclose(three, [.975, .005, .015, .005])
    assert np.allclose(four, [.9725, .0225, .0025, .0025])
    assert np.isclose(compose_two_photons(three).sum(), 1)
