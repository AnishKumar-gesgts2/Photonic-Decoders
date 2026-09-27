"""Check exact availability enumeration and its architecture assumptions."""
import pytest

from ancilla_free_information_gate import exact_availability


def test_lossless_unboosted_encoded_availability() -> None:
    result = exact_availability(0.5, 1.0, 2)
    assert result["both_encoded_parities_available"] == pytest.approx(0.75)
    assert result["encoded_xx_available"] == pytest.approx(1.0)
    assert result["encoded_zz_available"] == pytest.approx(0.75)
    assert result["photons_attempted_per_encoded_fusion"] == 8


def test_lossless_boosted_availability_and_photon_cost() -> None:
    result = exact_availability(0.693, 1.0, 4)
    assert result["both_encoded_parities_available"] == pytest.approx(1 - 0.307**2)
    assert result["photons_attempted_per_encoded_fusion"] == 16


def test_all_lost_provides_no_parity() -> None:
    for photons in (2, 4):
        result = exact_availability(0.5, 0.0, photons)
        assert result["both_encoded_parities_available"] == 0
        assert result["neither_encoded_parity_available"] == 1
