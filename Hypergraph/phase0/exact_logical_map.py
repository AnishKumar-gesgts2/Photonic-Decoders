"""Exhaustive logical-class MAP reference for a small homogeneous channel."""
from __future__ import annotations

import numpy as np


def lookup(checks: np.ndarray, logicals: np.ndarray,
           channel: np.ndarray) -> dict[int, int]:
    if logicals.shape[0] != 1 or len(channel) != 4 or checks.shape[1] % 2:
        raise ValueError("Expected one logical and four states per location")
    n = checks.shape[1]//2
    if n > 10 or checks.shape[0] > 30:
        raise ValueError("Exact enumeration is limited to small circuits")
    configurations = np.arange(4**n, dtype=np.uint32)
    states = ((configurations[:, None] >>
               (2*np.arange(n, dtype=np.uint32))) & 3).astype(np.uint8)
    errors = np.zeros((len(configurations), 2*n), dtype=np.uint8)
    errors[:, ::2] = states & 1
    errors[:, 1::2] = states >> 1
    syndromes = (errors @ checks.T) & 1
    logical = ((errors @ logicals.T) & 1)[:, 0]
    masks = (syndromes.astype(np.uint32) <<
             np.arange(checks.shape[0], dtype=np.uint32)).sum(axis=1)
    weights = np.prod(channel[states], axis=1)
    keys, inverse = np.unique(masks*2+logical, return_inverse=True)
    masses = np.bincount(inverse, weights=weights)
    if abs(masses.sum()-1) > 1e-10:
        raise AssertionError("Exact posterior mass is not normalized")
    by_syndrome: dict[int, np.ndarray] = {}
    for key, mass in zip(keys, masses):
        syndrome, label = divmod(int(key), 2)
        by_syndrome.setdefault(syndrome, np.zeros(2))[label] = mass
    return {key: int(np.argmax(mass)) for key, mass in by_syndrome.items()}


def syndrome_key(syndrome: np.ndarray) -> int:
    return int((syndrome.astype(np.uint32) <<
                np.arange(len(syndrome), dtype=np.uint32)).sum())
