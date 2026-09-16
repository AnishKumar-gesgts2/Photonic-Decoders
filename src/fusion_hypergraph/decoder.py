from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .lattice import FusionLattice, NUM_STATES


@dataclass(frozen=True)
class DecodeResult:
    logical: int
    states: np.ndarray
    iterations: int
    converged: bool
    final_delta: float


class MinSumHypergraphDecoder:
    """Normalized min-sum on categorical local faults and detector XOR factors."""

    def __init__(
        self,
        lattice: FusionLattice,
        max_iterations: int = 50,
        damping: float = 0.35,
        tolerance: float = 1e-6,
    ) -> None:
        if not 0.0 <= damping < 1.0:
            raise ValueError("damping must be in [0, 1)")
        self.lattice = lattice
        self.max_iterations = int(max_iterations)
        self.damping = float(damping)
        self.tolerance = float(tolerance)

    def decode(self, syndrome: np.ndarray, costs: np.ndarray) -> DecodeResult:
        if syndrome.shape != (self.lattice.num_detectors,):
            raise ValueError("syndrome has the wrong shape")
        if costs.shape != (self.lattice.num_sites, NUM_STATES):
            raise ValueError("costs have the wrong shape")

        contribution: dict[tuple[int, int], np.ndarray] = {}
        v_to_f: dict[tuple[int, int], np.ndarray] = {}
        f_to_v: dict[tuple[int, int], np.ndarray] = {}
        for site, detectors in enumerate(self.lattice.site_to_detectors):
            for detector in detectors:
                key = (site, detector)
                contribution[key] = np.array(
                    [detector in self.lattice.supports[site][state] for state in range(NUM_STATES)],
                    dtype=np.uint8,
                )
                v_to_f[key] = costs[site].copy()
                f_to_v[(detector, site)] = np.zeros(NUM_STATES, dtype=float)

        converged = False
        delta = float("inf")
        iteration = 0
        for iteration in range(1, self.max_iterations + 1):
            next_f_to_v: dict[tuple[int, int], np.ndarray] = {}
            for detector, sites in enumerate(self.lattice.detector_to_sites):
                for target in sites:
                    parity_cost = np.array([0.0, np.inf])
                    for site in sites:
                        if site == target:
                            continue
                        incoming = v_to_f[(site, detector)]
                        bits = contribution[(site, detector)]
                        best = np.array(
                            [incoming[bits == bit].min(initial=np.inf) for bit in (0, 1)]
                        )
                        parity_cost = np.array(
                            [
                                min(parity_cost[0] + best[0], parity_cost[1] + best[1]),
                                min(parity_cost[0] + best[1], parity_cost[1] + best[0]),
                            ]
                        )
                    bits = contribution[(target, detector)]
                    raw = parity_cost[np.bitwise_xor(int(syndrome[detector]), bits)]
                    raw -= raw.min()
                    previous = f_to_v[(detector, target)]
                    next_f_to_v[(detector, target)] = self.damping * previous + (1 - self.damping) * raw

            next_v_to_f: dict[tuple[int, int], np.ndarray] = {}
            for site, detectors in enumerate(self.lattice.site_to_detectors):
                total = costs[site].copy()
                for detector in detectors:
                    total += next_f_to_v[(detector, site)]
                for detector in detectors:
                    message = total - next_f_to_v[(detector, site)]
                    next_v_to_f[(site, detector)] = message - message.min()

            delta = max(
                (
                    float(np.max(np.abs(next_f_to_v[key] - f_to_v[key])))
                    for key in next_f_to_v
                ),
                default=0.0,
            )
            f_to_v, v_to_f = next_f_to_v, next_v_to_f
            if delta <= self.tolerance:
                converged = True
                break

        decoded = np.empty(self.lattice.num_sites, dtype=np.uint8)
        for site, detectors in enumerate(self.lattice.site_to_detectors):
            belief = costs[site].copy()
            for detector in detectors:
                belief += f_to_v[(detector, site)]
            decoded[site] = int(np.argmin(belief))
        return DecodeResult(
            logical=self.lattice.logical(decoded),
            states=decoded,
            iterations=iteration,
            converged=converged,
            final_delta=delta,
        )

