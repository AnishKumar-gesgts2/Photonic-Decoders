import numpy as np

from fusion_hypergraph.physics import emission_table, local_costs, state_priors


def test_probability_tables_are_normalized() -> None:
    priors = state_priors(0.05, 0.3, 0.1)
    table = emission_table(0.92, 0.95)
    assert np.isclose(priors.sum(), 1.0)
    np.testing.assert_allclose(table.sum(axis=(1, 2)), 1.0)


def test_oracle_cost_selects_true_state() -> None:
    priors = state_priors(0.05, 0.3, 0.1)
    table = emission_table(0.92, 0.95)
    truth = np.array([0, 4, 5], dtype=np.uint8)
    costs = local_costs(
        priors,
        table,
        np.zeros(3, dtype=np.uint8),
        np.zeros(3, dtype=np.uint8),
        "oracle",
        truth,
    )
    np.testing.assert_array_equal(np.argmin(costs, axis=1), truth)

