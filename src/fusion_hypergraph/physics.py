from __future__ import annotations

import numpy as np

from .lattice import NUM_STATES


NUM_OUTCOMES = 3  # fusion success, failure, erasure
NUM_PNR_BINS = 3  # 0, 1, 2+


def state_priors(
    physical_error_rate: float,
    correlated_fraction: float,
    multiphoton_fraction: float,
) -> np.ndarray:
    if not 0.0 < physical_error_rate < 1.0:
        raise ValueError("physical_error_rate must be in (0, 1)")
    if not 0.0 <= correlated_fraction <= 1.0:
        raise ValueError("correlated_fraction must be in [0, 1]")
    if not 0.0 <= multiphoton_fraction <= correlated_fraction:
        raise ValueError("multiphoton_fraction must be <= correlated_fraction")
    pair_mass = physical_error_rate * (1.0 - correlated_fraction)
    loss_mass = physical_error_rate * (correlated_fraction - multiphoton_fraction)
    multi_mass = physical_error_rate * multiphoton_fraction
    return np.array(
        [1.0 - physical_error_rate, pair_mass / 3, pair_mass / 3, pair_mass / 3, loss_mass, multi_mass],
        dtype=float,
    )


def emission_table(detector_efficiency: float, visibility: float) -> np.ndarray:
    """Return P(fusion outcome, PNR bin | local latent fault state).

    The table is an explicit, replaceable surrogate for a Fock/experiment-derived
    local table. Lower efficiency/visibility smoothly removes information without
    changing the latent fault priors.
    """
    if not 0.0 <= detector_efficiency <= 1.0 or not 0.0 <= visibility <= 1.0:
        raise ValueError("efficiency and visibility must be in [0, 1]")
    outcome = np.array(
        [
            [0.965, 0.025, 0.010],
            [0.700, 0.250, 0.050],
            [0.700, 0.250, 0.050],
            [0.700, 0.250, 0.050],
            [0.100, 0.300, 0.600],
            [0.250, 0.650, 0.100],
        ],
        dtype=float,
    )
    pnr = np.array(
        [
            [0.01, 0.04, 0.95],
            [0.03, 0.22, 0.75],
            [0.03, 0.22, 0.75],
            [0.03, 0.22, 0.75],
            [0.58, 0.36, 0.06],
            [0.01, 0.08, 0.91],
        ],
        dtype=float,
    )
    informative = outcome[:, :, None] * pnr[:, None, :]
    quality = detector_efficiency * visibility
    uninformative = np.full_like(informative, 1.0 / (NUM_OUTCOMES * NUM_PNR_BINS))
    table = quality * informative + (1.0 - quality) * uninformative
    return table / table.sum(axis=(1, 2), keepdims=True)


def sample_observations(
    rng: np.random.Generator,
    states: np.ndarray,
    table: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    outcomes = np.empty(len(states), dtype=np.uint8)
    pnr = np.empty(len(states), dtype=np.uint8)
    for state in range(NUM_STATES):
        locations = np.flatnonzero(states == state)
        if locations.size == 0:
            continue
        draws = rng.choice(NUM_OUTCOMES * NUM_PNR_BINS, size=locations.size, p=table[state].ravel())
        outcomes[locations] = draws // NUM_PNR_BINS
        pnr[locations] = draws % NUM_PNR_BINS
    return outcomes, pnr


def local_costs(
    priors: np.ndarray,
    table: np.ndarray,
    outcomes: np.ndarray,
    pnr: np.ndarray,
    mode: str,
    true_states: np.ndarray | None = None,
) -> np.ndarray:
    eps = 1e-15
    if mode == "marginal":
        probabilities = np.broadcast_to(priors, (len(outcomes), NUM_STATES)).copy()
    elif mode == "metadata":
        likelihood = table[:, outcomes, pnr].T
        probabilities = likelihood * priors[None, :]
        probabilities /= probabilities.sum(axis=1, keepdims=True)
    elif mode == "oracle":
        if true_states is None:
            raise ValueError("oracle mode requires true_states")
        probabilities = np.full((len(outcomes), NUM_STATES), eps)
        probabilities[np.arange(len(outcomes)), true_states] = 1.0
        probabilities /= probabilities.sum(axis=1, keepdims=True)
    else:
        raise ValueError(f"Unknown local-cost mode: {mode}")
    costs = -np.log(np.clip(probabilities, eps, 1.0))
    return costs - costs.min(axis=1, keepdims=True)

