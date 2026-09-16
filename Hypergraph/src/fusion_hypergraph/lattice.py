from __future__ import annotations

from dataclasses import dataclass

import numpy as np


STATE_NAMES = ("none", "x_pair", "y_pair", "time_pair", "loss_triple", "multiphoton_quad")
NUM_STATES = len(STATE_NAMES)


@dataclass(frozen=True)
class FusionLattice:
    distance: int
    rounds: int
    supports: tuple[tuple[tuple[int, ...], ...], ...]
    logicals: np.ndarray
    detector_to_sites: tuple[tuple[int, ...], ...]
    site_to_detectors: tuple[tuple[int, ...], ...]

    @property
    def num_sites(self) -> int:
        return self.distance * self.distance * self.rounds

    @property
    def num_detectors(self) -> int:
        return self.num_sites

    def syndrome(self, states: np.ndarray) -> np.ndarray:
        result = np.zeros(self.num_detectors, dtype=np.uint8)
        for site, state in enumerate(states):
            for detector in self.supports[site][int(state)]:
                result[detector] ^= 1
        return result

    def logical(self, states: np.ndarray) -> int:
        return int(np.bitwise_xor.reduce(self.logicals[np.arange(self.num_sites), states], initial=0))


def build_lattice(distance: int, rounds: int) -> FusionLattice:
    if distance < 3 or rounds < 2:
        raise ValueError("distance must be >= 3 and rounds must be >= 2")

    def index(x: int, y: int, t: int) -> int:
        return ((t % rounds) * distance + (y % distance)) * distance + (x % distance)

    supports: list[tuple[tuple[int, ...], ...]] = []
    logicals = np.zeros((distance * distance * rounds, NUM_STATES), dtype=np.uint8)
    detector_to_sites: list[set[int]] = [set() for _ in range(distance * distance * rounds)]
    site_to_detectors: list[tuple[int, ...]] = []

    for t in range(rounds):
        for y in range(distance):
            for x in range(distance):
                site = index(x, y, t)
                here = index(x, y, t)
                xp = index(x + 1, y, t)
                yp = index(x, y + 1, t)
                tp = index(x, y, t + 1)
                site_supports = (
                    (),
                    (here, xp),
                    (here, yp),
                    (here, tp),
                    (here, xp, yp),
                    (here, xp, yp, tp),
                )
                supports.append(site_supports)
                # Crossing the periodic x seam is the modeled logical observable.
                if x == distance - 1:
                    logicals[site, (1, 4, 5)] = 1
                union = tuple(sorted({d for support in site_supports for d in support}))
                site_to_detectors.append(union)
                for detector in union:
                    detector_to_sites[detector].add(site)

    return FusionLattice(
        distance=distance,
        rounds=rounds,
        supports=tuple(supports),
        logicals=logicals,
        detector_to_sites=tuple(tuple(sorted(x)) for x in detector_to_sites),
        site_to_detectors=tuple(site_to_detectors),
    )

