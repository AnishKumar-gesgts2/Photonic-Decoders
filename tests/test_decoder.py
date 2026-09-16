import numpy as np

from fusion_hypergraph.decoder import MinSumHypergraphDecoder
from fusion_hypergraph.lattice import NUM_STATES, build_lattice


def test_oracle_decodes_known_hyperedge() -> None:
    lattice = build_lattice(3, 3)
    truth = np.zeros(lattice.num_sites, dtype=np.uint8)
    truth[2] = 5
    costs = np.full((lattice.num_sites, NUM_STATES), 100.0)
    costs[np.arange(lattice.num_sites), truth] = 0.0
    result = MinSumHypergraphDecoder(lattice, max_iterations=10).decode(
        lattice.syndrome(truth), costs
    )
    assert result.logical == lattice.logical(truth)
    np.testing.assert_array_equal(result.states, truth)

