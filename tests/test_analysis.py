from fusion_hypergraph.analyze import wilson_interval


def test_wilson_interval_contains_observed_rate() -> None:
    low, high = wilson_interval(10, 100)
    assert low < 0.1 < high
    assert 0.0 <= low <= high <= 1.0

