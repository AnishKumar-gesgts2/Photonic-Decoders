# Optical action audit after the bounded MAP result — 2026-09-26

## Question

Can the current optical simulations supply a *complete, physically calibrated* joint-fault channel for a fair surface-code MAP versus MWPM comparison, without selecting a convenient $Y$ rate?

**Current answer: no.** The $3\%$ bounded-memory $Y$ result remains a valid decoder sensitivity result, but the present optical models do not justify its rate or its native-memory mapping. This audit uncovered an additional problem in the older extra-photon route: accepted extra-plus records are not Bell diagonal. Their diagonal branch weights cannot be promoted to a stochastic Pauli $Y$ channel.

## What was tested

The exact four-mode Fock instrument was evaluated for the ideal analyzer and every named local cause in the code: same-rail extra photon, opposite-rail extra photon, a specified coherent extra-plus photon, and input Pauli $Y$. For each accepted two-count PNR record, the full conditional effect on the untouched graph reference was transformed into the Bell basis. A categorical $I/X/Z/Y$ action is admitted only if its Bell off-diagonal entries vanish for **that individual record**. This checks the matrix, not just its diagonal probabilities. Detector efficiencies 100%, 99.5%, and 95% were audited. The machine-readable result is [results.json](../outputs/phase0_six_ring_optical/results.json).

| Specified input cause | Accepted-record action at 99.5% efficiency | Can it supply a calibrated useful joint channel now? |
|---|---|---|
| Ideal two-photon input | Bell diagonal; no wrong accepted parity | No joint error to exploit. Loss and partial outcomes still need their full encoded network treatment. |
| Extra photon in same rail | Bell diagonal; no projected joint $Y$ | No known useful joint error; source incidence remains uncalibrated. |
| Extra photon in opposite rail | All accepted records Bell coherent | No categorical Pauli channel without a justified coherent decoder or physical decoherence model. |
| Coherent extra-plus photon | All accepted records Bell coherent | No categorical Pauli channel; the earlier diagonal projection is invalid as a physical decoder input. |
| Specified input Pauli $Y$ | Bell diagonal on accepted records; flips both physical parity bits | Its occurrence probability is unknown, and encoded reconstruction makes its action branch dependent. |

At 99.5% detection, 0.6600% of **extra-plus fault attempts** produce an accepted full record; all of that accepted mass is Bell coherent. At 95% detection the corresponding fraction is 6.0167%. For illustration only, an assumed 5% extra-plus incidence at 95% detection would put 0.3008% of all attempted fusions into this unsupported accepted class. The previously reported 0.000871 projected joint fraction *among full records* came from dropping the coherence, so it is withdrawn as a physical probability. The code now refuses to compile extra-plus or opposite-rail accepted records into a categorical Pauli table.

The accepted $Y$ action does not determine its incidence. Under uniformly mixed Bell inputs, its raw PNR distribution is identical to the ideal distribution in the tested local model; one click record cannot estimate its rate. The ideal encoded four-BSM enumeration gives a joint encoded flip in 16/32 assignments, an $XX$-only flip in 8/32, and an unavailable $ZZ$ in 8/32. Thus even a calibrated input-$Y$ rate cannot simply be copied into the bounded surface-code $p_Y$ setting.

## Decision

**NO-GO for a physically grounded ancilla-free hypergraph logical advantage today.** This is a correction to a previous possible optical justification, not a negative result about all hypergraph decoders. The [bounded logical study](BOUNDED_JOINT_LOGICAL_RESULTS.md) proves advantage for a declared effective channel; the [ancilla-free periodic proxy](ANCILLA_FREE_DECODER_PROXY_RESULTS.md) is also conditional on assumed rates. Neither converts the coherent extra-photon action or unknown $Y$ incidence into a native encoded six-ring memory.

The [published-source sensitivity follow-up](PAPER_SOURCE_CHANNEL_RESULTS.md) evaluates full first-order Pauli mixtures without selecting a favorable $Y$ incidence. Its exact bounded-memory results are mixed: configuration MAP improves modestly for the three-level model but loses to calibrated MWPM for biased four-level Z memory. It also constructs an ancilla-free encoded local record/action table from independent input-photon Pauli marginals, while leaving source loss, correlations, and native boundaries unresolved. A tested bilateral Pauli randomization after extra-photon preparation leaves the accepted Bell coherence present. None of these additional checks closes the physical gate.

The next decisive inputs are (1) a source model or data that fixes the *joint* Pauli/action frequencies with uncertainty, including loss and partial records, and (2) a finite encoded six-ring memory with the paper's boundaries and a validated logical observable. A recent [source-characterization proposal](https://arxiv.org/abs/2608.03005) describes how optical coherence measurements could be used to infer photonic resource-state Pauli rates and post-fusion error maps; it does not provide measurements for this proposed source. Once the input channel and native circuit are fixed independently of decoder outcomes, run the whole frozen grid on identical shots with calibrated MWPM, belief matching, and MAP. A resolved held-out logical gain would be the physical go signal. If no such channel data become available, the result remains conditional; increasing a simulated $Y$ rate cannot close this gate.
