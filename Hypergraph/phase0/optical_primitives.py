"""Balanced dual-rail analyzer primitives used by the six-ring local instrument."""
from __future__ import annotations

from collections import defaultdict
from math import comb, factorial, sqrt


def bs_amplitude(n: int, m: int, k: int) -> float:
    total = n + m
    polynomial = sum(comb(n, j) * comb(m, k - j) * (-1) ** (k - j)
                     for j in range(max(0, k - m), min(n, k) + 1))
    return (polynomial * sqrt(factorial(k) * factorial(total - k)
                              / (factorial(n) * factorial(m)))
            / (sqrt(2) ** total))


def apply_bs(state: dict[tuple[int, ...], complex], a: int, b: int,
             cutoff: int) -> dict[tuple[int, ...], complex]:
    output = defaultdict(complex)
    for occupation, input_amplitude in state.items():
        n, m = occupation[a], occupation[b]
        for k in range(n + m + 1):
            amplitude = bs_amplitude(n, m, k)
            if abs(amplitude) < 1e-14:
                continue
            candidate = list(occupation)
            candidate[a], candidate[b] = k, n + m - k
            if max(candidate) >= cutoff:
                raise ValueError("Fock cutoff truncates a nonzero amplitude")
            output[tuple(candidate)] += input_amplitude * amplitude
    return {key: value for key, value in output.items() if abs(value) > 1e-14}


def single_fusion_outcome(counts: tuple[int, int, int, int]) -> str:
    total = sum(counts)
    if total < 2:
        return "erasure"
    if total > 2:
        return "excess"
    a0, a1, b0, b1 = counts
    if a0 + b0 == 1 and a1 + b1 == 1:
        return "psi_plus" if (a0 and a1) or (b0 and b1) else "psi_minus"
    return "intrinsic_ambiguous"
