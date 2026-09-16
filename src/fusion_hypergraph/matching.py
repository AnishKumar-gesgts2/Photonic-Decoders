from __future__ import annotations

import math

import numpy as np
import pymatching

from .lattice import FusionLattice


class ProjectedMatchingDecoder:
    """MWPM baseline using the graphlike projection of local fault posteriors.

    Three two-detector states are represented exactly. Genuine 3/4-detector
    events are intentionally excluded: that structural mismatch is the baseline
    tested by the project, not silently decomposed into invented independent faults.
    """

    def __init__(self, lattice: FusionLattice, boundary_weight: float = 12.0) -> None:
        self.lattice = lattice
        self.boundary_weight = float(boundary_weight)

    def decode(self, syndrome: np.ndarray, costs: np.ndarray, uniform: bool = False) -> int:
        matching = pymatching.Matching()
        for detector in range(self.lattice.num_detectors):
            matching.add_boundary_edge(detector, weight=self.boundary_weight)

        for site in range(self.lattice.num_sites):
            probabilities = np.exp(-costs[site])
            probabilities /= probabilities.sum()
            if uniform:
                # Deliberately uncalibrated equal edge prior for the weakest baseline.
                probabilities[1:4] = 0.01 / 3.0
            for state in (1, 2, 3):
                a, b = self.lattice.supports[site][state]
                p = float(np.clip(probabilities[state], 1e-12, 1 - 1e-12))
                weight = math.log((1.0 - p) / p)
                fault_ids = {0} if self.lattice.logicals[site, state] else set()
                matching.add_edge(a, b, fault_ids=fault_ids, weight=weight, merge_strategy="independent")
        correction = matching.decode(syndrome)
        return int(correction[0]) if correction.size else 0
