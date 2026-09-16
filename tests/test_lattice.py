import numpy as np

from fusion_hypergraph.lattice import build_lattice


def test_syndrome_is_xor_of_selected_hyperedges() -> None:
    lattice = build_lattice(3, 3)
    states = np.zeros(lattice.num_sites, dtype=np.uint8)
    states[0] = 4
    states[1] = 5
    expected = np.zeros(lattice.num_detectors, dtype=np.uint8)
    for site in (0, 1):
        for detector in lattice.supports[site][states[site]]:
            expected[detector] ^= 1
    np.testing.assert_array_equal(lattice.syndrome(states), expected)


def test_logical_seam_parity_cancels() -> None:
    lattice = build_lattice(3, 3)
    states = np.zeros(lattice.num_sites, dtype=np.uint8)
    states[2] = 1
    states[5] = 1
    assert lattice.logical(states) == 0

