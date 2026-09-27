# Paper-parameter and encoded-fusion follow-up — 2026-09-26

## Why this run exists

The previous large bounded-memory gain used $p_Y=3\%$ and $p_X=p_Z=0.2\%$ at each effective site. This is a useful algorithm test but makes the joint event fifteen times more frequent than either single-axis event. To avoid selecting the correlation that favors MAP, this follow-up uses **all** $I/X/Y/Z$ probabilities given by a published first-order photonic-source model. It reports every cell in a fixed parameter grid and exact logical risks instead of Monte Carlo estimates.

The source is [Gupta, Doherty, and Mahmoodian, arXiv:2608.03005v1](https://arxiv.org/html/2608.03005). Its Table 1 gives input-photon Pauli probabilities for three- and four-level emitters; Table 2 gives *additional*, success-averaged fusion Pauli probabilities for a Bell-pair example. Let $u=(1-\eta)|\gamma|^2$ denote source loss times mean leaked-laser photon number. For Table 2, the three-level model has $p_X=p_Y=p_Z=u$. The four-level model has $p_X=p_Y=u/2$ and $p_Z=u/2+(1-\mathcal V)/2$. The paper assumes a Pauli reduction such as twirling and does not supply measured parameters for this proposed encoded six-ring source. Table 1 and Table 2 are **separate** calculations here; their fault probabilities are not added together or treated as a complete device channel.

## Exact bounded surface-code sensitivity

The [full output](../outputs/phase0_paper_source_sensitivity/results.json) enumerates all $4^9$ Pauli configurations of the existing three-round rotated $d=3$ memory, sums the exact probability of each syndrome/logical class, and scores calibrated MWPM, global *configuration* MAP, and optimal *logical-class* MAP. Both decoders receive the same known channel. This still uses a declared fusion-to-data adapter and has no native six-ring boundary.

| Table 2 channel, Z memory | Calibrated MWPM logical failure | Configuration MAP | Logical-class MAP |
|---|---:|---:|---:|
| Three-level, $u=0.001$ | 0.007144% | 0.006558% | 0.005970% |
| Three-level, $u=0.01$ | 0.665581% | 0.625761% | 0.568946% |
| Four-level, $u=0.001$, $1-\mathcal V=0.02$ | 0.208628% | **0.210345%** | 0.206509% |
| Four-level, $u=0.01$, $1-\mathcal V=0.02$ | 0.665581% | **0.680162%** | 0.623935% |

The bold configuration-MAP rates are **worse** than calibrated MWPM. The fixed grid also includes $u=0.0001$ and $0.03$, both memory bases, and four-level visibility deficits 0 and 0.02. The three-level configuration decoder improves in all tested cells but far less than the 1.26-point result from the Y-heavy channel. In four-level, Z-memory configuration MAP worsens for every tested nonzero-visibility-deficit cell. Optimal logical-class MAP never does worse in this exact calculation because it directly minimizes logical error probability under the supplied model. It can differ from the most likely **fault configuration**, so configuration MAP should not be presented as the optimum logical decoder.

Table 3 of the source paper gives **illustrative design targets**, not measurements: for $|\gamma|^2=0.01$, approximately $\eta=0.967$ for a three-level emitter and $\eta=0.933$, $\mathcal V=0.996$ for a four-level emitter. At those boundary values, the three-level Z-memory risks are $7.821\times10^{-6}$ (MWPM) and $7.280\times10^{-6}$ (configuration MAP). The four-level Z-memory risks are $1.270\times10^{-4}$ (MWPM) and $1.299\times10^{-4}$ (configuration MAP). These are model-exact sensitivity numbers, **not** measured logical error rates. The source paper's first-order formulas and assumed Bell-pair input limit their physical interpretation.

## Ancilla-free encoded record/action table

The [second output](../outputs/phase0_paper_encoded_channel/results.json) uses **Table 1 input-photon rates**, composes independent errors on both photons of each physical Bell measurement, and exactly enumerates the four ancilla-free measurements, their branch-dependent full/partial outcomes, and independent photon detection. It retains every record, including lost and partly known parity cases. This gives a local $P(R,A)$ for the **stated independent Pauli-source model**. It is not the full experimental source channel: multi-photon correlations, unmodeled coherent terms, and source-loss/herald probabilities are not supplied by Table 1 marginals.

In the ideal no-fault, no-loss limit, both encoded parities are available on 75% of attempts, matching the previous information gate. Injecting a deterministic $Y$ at physical fusion A reproduces the prior exhaustive 32-assignment result: 16 joint flips, 8 $XX$-only flips, and 8 with $ZZ$ unavailable. Under the full three-level Table 1 input channel with $u=0.001$, zero bias deficit, and 99.5% detector efficiency, both encoded parities are known on 73.986% of attempts. The joint encoded flip has probability **0.07373% per attempted encoded fusion**, or **0.09965% conditioned on both parities being known**. This is a parameter illustration, not a claimed operating point; the source's loss and leakage values have not been measured together with this detector efficiency.

## Other paths checked

The [optical action audit](../outputs/phase0_six_ring_optical/results.json) now also tests a practical-looking randomization: apply random paired rail swaps and phase flips to the two analyzer inputs **after** the specified extra-photon preparation. Ideal accepted records remain Bell diagonal, but every accepted extra-plus and opposite-rail record remains Bell coherent at 99.5% and 95% detection. This particular post-source randomization cannot justify a categorical Pauli projection. It does not rule out a properly designed source-level twirl or a coherent decoder.

For the native-memory route, the [FBQC boundary figure](https://arxiv.org/pdf/2101.09310) specifies distinct primal/dual boundaries using both single-qubit $Z$ substitutions and omitted resource states. The available [FusionLattices reference code](https://github.com/StefanoPaesani/FusionLattices) explicitly builds periodic six-ring boundaries only. The present periodic code therefore cannot be relabeled as a finite logical memory. A paper-consistent finite construction, encoded resource stabilizers, and injected-fault agreement remain necessary.

## Decision

**No physical go yet.** A full published source mixture can make MAP helpful in the declared $d=3$ effective channel, but the gain is much smaller at the paper's illustrative quality targets, and configuration MAP can lose under bias. The ancilla-free encoded local table is now available, but it lacks measured source parameters, correlated source errors, and a native finite logical circuit. The next defensible physical benchmark must validate those ingredients and test the complete record/action table on identical native-memory shots. Increasing $u$, reducing the visibility, dropping partial records, or choosing only favorable basis cells after viewing these results would not establish a physical advantage.
