"""Paper-style encoded-fusion availability from four boosted Bell measurements.

A,C failures retain XX; B,D failures retain ZZ. The four-qubit stabilizers
XXXX, ZZZZ, and Z_A Z_C give two reconstructions of each logical parity.
The reported 69.3% physical success is used as a scalar input; this is not a
reconstruction of the paper's experimental four-photon click-pattern table.
"""
from __future__ import annotations

import numpy as np


def sample_physical_records(shots: int, fusions: int, efficiency: float,
                            success: float, rng: np.random.Generator) -> np.ndarray:
    """0=lost, 1=one parity, 2=both; four measurements per encoded fusion."""
    if not 0 <= efficiency <= 1 or not 0 <= success <= 1:
        raise ValueError("Invalid physical parameter")
    survived = rng.random((shots, fusions, 4)) < efficiency**4
    full = rng.random((shots, fusions, 4)) < success
    return np.where(survived, np.where(full, 2, 1), 0).astype(np.uint8)


def encoded_availability(records: np.ndarray) -> np.ndarray:
    """Return known [logical XX, logical ZZ] for each encoded fusion."""
    if records.shape[-1] != 4:
        raise ValueError("Expected A,B,C,D physical fusion records")
    a, b, c, d = (records[..., i] for i in range(4))
    xx = ((a > 0) & (c > 0)) | ((b == 2) & (d == 2))
    zz = ((a == 2) | (c == 2)) & ((b > 0) | (d > 0))
    return np.stack((xx, zz), axis=-1)


def theoretical_no_loss_full(success: float) -> float:
    return 1 - (1 - success)**2
