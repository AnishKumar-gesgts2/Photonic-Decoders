import numpy as np
import pytest

from encoded_proxy import sample_shots


def test_ideal_two_photon_full_fraction_and_no_loss() -> None:
    shots = sample_shots(1000, 1.0, .5, 0.0, 0.0, 8712,
                         photons_per_bsm=2)
    records = shots["records"]
    assert np.all(records > 0)
    assert np.mean(records == 2) == pytest.approx(.5, abs=.03)


def test_two_photon_branch_average_cannot_be_arbitrarily_tuned() -> None:
    with pytest.raises(ValueError):
        sample_shots(1, 1.0, .7, 0.0, 0.0, 7, photons_per_bsm=2)
