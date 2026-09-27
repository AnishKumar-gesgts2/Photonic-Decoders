# Boosted, encoded Phase 0 trial — 2026-09-26

## Architecture and claim boundary

The code implements the four-physical-fusion $(2,2)$-Shor parity reconstruction used with the boosted Bell measurement in [Hauser et al.](https://www.nature.com/articles/s41534-025-00986-2). Physical BSM success is 69.3% in the main arm; A/C failures retain $XX$, B/D failures retain $ZZ$. Each boosted BSM uses four photons, so a 95% or 99.5% per-photon survival probability is applied before success/failure classification. A separate sensitivity arm uses the paper's Bell-branch-specific correct-identification rates (46.1%, 46.2%, 92.4%, 92.7%). These rates do not supply the full raw click-pattern or postfusion quantum instrument.

The four-qubit stabilizer algebra supplies two reconstructions of each encoded parity. The simulated physical parity-flip rates are **assumptions**: 0.2% independent flip per physical $XX$ and $ZZ$ result, plus a 0.5% joint $XX/ZZ$ flip at physical fusion A. The latter is a structured-fault sensitivity model, not a measured probability for an extra photon in the boosted analyzer. The seeded 12,000-shot training set learns local likelihoods; each arm uses the same separate 3,000 held-out shots. The deployed decoder sees only reported parity bits, full/partial/lost outcome classes, and disagreements between redundant measurements. It never sees the fault label or ideal state.

The score is failure on **three periodic nonlocal parity sectors**, not a bounded surface-code memory logical-error rate. Each sector is first deformed by local checks to avoid missing outcomes; shots where that cannot be done count as failures for every decoder. Missing graph edges are contracted into measurable superchecks. MWPM receives calibrated independent $XX/ZZ$ marginals for its chosen metadata level. The correlation-aware arm runs four-state joint belief propagation, then matching on those same superchecks. The full output, Wilson intervals, paired bootstrap intervals, and timing are in [results.json](../outputs/phase0_encoded/results.json).

## Paired results

| Held-out setting | Both encoded parities available per fusion | Unrecoverable sector shots | MWPM, availability only | MWPM, all metadata | Joint BP + MWPM, all metadata | Joint gain over equally informed MWPM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 99.5% photon efficiency, average 69.3% BSM success | 88.19% | 6.53% | 31.50% | 14.43% | **13.27%** | **1.17 points**, paired 95% CI 0.57–1.73 |
| 95% photon efficiency | 64.57% | 98.93% | 99.27% | 99.23% | 99.20% | No useful distinction |
| Train at 99.5%, test at 99.2%; test flip rates 0.3% independent, 0.7% joint | 86.78% | 8.67% | 47.13% | 24.00% | **22.17%** | **1.83 points**, paired 95% CI 1.13–2.57 |
| 99.5%, branch-conditioned success sensitivity | 83.22% | 23.93% | 49.40% | 33.00% | **32.20%** | **0.80 points**, paired 95% CI 0.33–1.30 |
| 99.5%, zero joint physical faults | 88.18% | 6.67% | 19.70% | **10.97%** | 11.10% | −0.13 points, paired 95% CI −0.40–0.13 |

At 99.5%, using redundancy disagreements and physical outcome classes gives a much larger benefit than switching decoders: metadata-aware MWPM falls from 31.50% to 14.43%. Joint decoding then yields a smaller but paired-significant additional gain. Shuffling the redundancy flags while retaining encoded parity availability raises the joint arm from 13.27% to 30.97%. In the zero-joint-fault control, the joint decoder has no demonstrated advantage over equally informed MWPM. This supports the mechanism interpretation *within the stipulated model*.

At the **same 95% efficiency**, the encoded model reduces shots with no measurable local-check combination from the unboosted ideal audit's 88.17% to 26.43%. Its three nonlocal sectors are still erased on 98.93% of shots, so this local improvement is insufficient at that efficiency. At 99.5%, every sampled shot has at least one measurable local-check combination.

## Selective-compute check

A fixed selector runs joint BP only when at least one pair of redundant physical parity measurements disagrees; otherwise it uses metadata-aware MWPM. This uses only observed data. On an **additional independent 3,000-shot holdout** ([selective_holdout.json](../outputs/phase0_encoded/selective_holdout.json)), metadata-aware MWPM has 14.40% sector failure, global joint BP + MWPM has 13.27%, and the selective arm has 13.40%. The selective gain over equally informed MWPM is 1.00 percentage point (paired 95% CI 0.47–1.50); its difference from global joint BP is unresolved (paired CI for the global improvement −0.13–0.40 points). However, BP activates on **60.87% of all shots**, and measured mean decode time is 1.24 ms versus 0.184 ms for MWPM on this Python implementation. This does not satisfy the original sparse-activation or lower-compute premise. Timing is implementation-specific and excludes offline calibration.

## Decision and unresolved work

**Go for the boosted/encoded architecture as the next physics-calibration target. No-go for the current selective-hypergraph compute claim, a physically validated hypergraph logical advantage, or starting the $d=5$ decoder benchmark now.** The encoded measurement provides considerably more usable parity information than the unboosted primitive at high efficiency, and observable redundancy metadata helps both decoders. The joint decoder has a smaller conditional accuracy gain, but this selector activates too often. At 95% photon efficiency, missing outcomes dominate even the encoded proxy. The branch-conditioned sensitivity arm also has substantially more sector erasure than the average-rate model; this dependence needs direct optical calibration.

The published boosted BSM average success and per-branch correct-identification rates are not a record-conditioned error channel for our fault. Its measured discrimination fidelity cannot simply be entered as an independent Pauli-flip rate. Required next evidence is a raw four-photon PNR-to-postfusion-action table under the selected fault mechanisms, source incidence and loss correlations, and a bounded six-ring memory with boundaries and a genuine logical observable. Until then, the numerical rates above are a transparent architecture/decoder **proxy**, not device LER or a hardware threshold.
