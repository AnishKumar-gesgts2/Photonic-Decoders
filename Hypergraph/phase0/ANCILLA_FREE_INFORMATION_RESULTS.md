# Ancilla-free encoded Phase 0 information gate — 2026-09-26

The exact enumeration is in [results.json](../outputs/phase0_ancilla_free_information/results.json). Run it from `Hypergraph` with `PYTHONPATH=phase0` and `python phase0/ancilla_free_information_gate.py`.

This calculation applies the existing four-physical-BSM $(2,2)$-Shor parity-reconstruction rule to both architectures. It assumes independent physical outcomes, ideal 50% complete Bell discrimination for the two-photon ancilla-free analyzer, and the reported 69.3% *average* complete discrimination as a scalar boosted-reference input. It also assumes every surviving partial outcome yields the parity required by its A/C or B/D placement. A physical fusion survives with probability $\eta^2$ or $\eta^4$, respectively. These are information and photon-attempt counts, not a resource-cost model or logical-failure rates.

| Per-photon efficiency | Ancilla-free: both encoded parities | Boosted: both encoded parities | Photons attempted per encoded fusion, U/B |
|---:|---:|---:|---:|
| 100% | 75.00% | 90.58% | 8 / 16 |
| 99.5% | 73.75% | 88.22% | 8 / 16 |
| 98.6% | 71.47% | 83.75% | 8 / 16 |
| 95% | 62.30% | 64.69% | 8 / 16 |

The existing native periodic-bulk code proves that a hypothetical joint $XX/ZZ$ flip has four local-check support, and its synthetic at-most-two-fault decoder control can outperform projected MWPM. That control uses a hand-specified fault channel, conditions away inconclusive fusions, and scores nonlocal periodic sectors. It does **not** establish that a physically characterized ancilla-free encoded fusion produces a retained useful hyperedge or that a hypergraph decoder beats equally informed MWPM on a bounded logical memory.

**Decision: no go to a physical hypergraph advantage claim or a $d=5$ run; the proposed ancilla-free versus MWPM hypothesis is unresolved.** The missing gates are (1) a calibrated raw-record-conditioned action and incidence for a common-cause fault in the ancilla-free encoded fusion, including partial and loss outcomes; (2) a native bounded encoded six-ring circuit with boundaries, checks, and a logical observable; and (3) an identical-shot held-out comparison of global/exact hypergraph inference with equally informed erasure-aware and correlation-aware matching. Ancilla savings alone do not pass any of these gates. Preserve the optical and synthetic controls as diagnostics rather than treating their favorable result as a go decision.
