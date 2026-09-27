import numpy as np

from run_bounded_joint_logical import conditioned, local_channel


def test_flag_posterior_is_normalized_and_informative() -> None:
    channel = local_channel(.002, .03)
    flagged = conditioned(channel, True, .6, .15)
    unflagged = conditioned(channel, False, .6, .15)
    assert np.isclose(flagged.sum(), 1)
    assert np.isclose(unflagged.sum(), 1)
    assert flagged[3] > channel[3] > unflagged[3]


def test_zero_joint_channel_has_no_joint_support() -> None:
    assert local_channel(.002, 0)[3] == 0


def test_no_joint_control_matches_single_axis_marginals() -> None:
    correlated = local_channel(.002, .03)
    graphlike = local_channel(.032, 0)
    assert graphlike[3] == 0
    assert np.isclose(correlated[1] + correlated[3], graphlike[1])
    assert np.isclose(correlated[2] + correlated[3], graphlike[2])
