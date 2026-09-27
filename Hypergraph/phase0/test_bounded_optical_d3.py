import numpy as np

from boosted_optical import BELL, excess_photon_loss_effects, ideal_report, instrument
from bounded_optical_d3 import memory_signatures, sample_encoded


def test_exact_optical_probabilities_and_published_ideal_success():
    ideal = instrument("phi+")
    assert np.allclose(ideal["probabilities"].sum(axis=1), 1)
    full = [sum(ideal["probabilities"][i, j]
                for j, record in enumerate(ideal["records"])
                if None not in ideal_report(record, ideal)) for i in range(4)]
    assert np.allclose(full, [.5, .5, 1, 1])


def test_phase_fault_changes_only_one_conclusive_parity():
    ideal = instrument("phi+")
    faulty = instrument("phi-")
    for i, label in enumerate(BELL):
        for j, record in enumerate(faulty["records"]):
            if faulty["probabilities"][i, j] < 1e-12:
                continue
            xx, zz = ideal_report(record, ideal)
            if xx is not None and zz is not None:
                assert zz == int(i >= 2)
    ideal_marginal = {record: np.mean(ideal["probabilities"][:, j])
                      for j, record in enumerate(ideal["records"])}
    fault_marginal = {record: np.mean(faulty["probabilities"][:, j])
                      for j, record in enumerate(faulty["records"])}
    assert all(np.isclose(ideal_marginal.get(r, 0), fault_marginal.get(r, 0))
               for r in ideal_marginal.keys() | fault_marginal.keys())


def test_stim_bounded_signatures_and_encoded_observables():
    for basis in ("x", "z"):
        h, logical, data = memory_signatures(basis)
        assert h.shape == (24, 18)
        assert logical.shape == (1, 18)
        assert len(data) == 9
        assert np.any(h)
        assert np.any(logical)
    shots = sample_encoded(100, .02, 42)
    assert shots["known"].shape == (100, 9, 2)
    assert np.all(shots["known"][:, :, 0])
    assert 0.8 < shots["known"][:, :, 1].mean() < 1


def test_extra_photon_loss_alias_is_not_bell_diagonal():
    ideal = instrument("phi+")
    effects = excess_photon_loss_effects(.8)
    assert np.isclose(sum(np.trace(e).real for e in effects.values())/4,
                      5*.8**4*.2)
    assert any(np.max(np.abs(e-np.diag(np.diag(e)))) > 1e-6
               for record, e in effects.items()
               if None not in ideal_report(record, ideal))
