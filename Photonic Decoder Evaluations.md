# STORM-Style Multi-Perspective Evaluation of 30 Photonic-Aware Decoder Ideas

**Date:** 13 September 2026  
**Question:** Which photonic-aware QEC decoder directions are sufficiently novel, physically justified, capable of outperforming a properly calibrated/correlated MWPM baseline, general enough to matter, and realistic enough to simulate now and eventually implement on an FPGA?

> **Important:** The “experts” below are simulated role-based perspectives used to structure the review. They are not real people who were contacted. The method follows Stanford STORM’s central idea: generate multiple perspectives, ask source-grounded questions from each perspective, then synthesize them into one research judgment. [R1]

## Simulated expert panel

1. **Fusion-based photonic architecture researcher** — asks whether the decoder uses information actually exposed by FBQC hardware.
2. **Integrated quantum photonics/device physicist** — checks loss, MZI/switch, source, spectral and timing realism.
3. **Single-photon source physicist** — evaluates multiphoton emission, purity, indistinguishability and heralding.
4. **Single-photon/PNR detector physicist** — evaluates efficiency, jitter, dark counts, dead time, saturation and count semantics.
5. **CV/GKP theorist** — checks whether a CV idea is already standard analog-GKP decoding.
6. **Surface-code decoder theorist** — compares against calibrated and correlated MWPM rather than straw-man matching.
7. **QLDPC/BP decoding researcher** — evaluates factor graphs, degeneracy, min-sum/BP and higher-order correlations.
8. **Bayesian/statistical-inference researcher** — asks whether a proposed latent-variable model is identifiable from observable data.
9. **Machine-learning decoder researcher** — checks whether ML adds anything beyond existing GNN/transformer decoders.
10. **Generalization/robustness researcher** — evaluates held-out hardware regimes, uncertainty and model mismatch.
11. **Real-time control/calibration researcher** — evaluates drift, calibration timescales and decoder-control feedback.
12. **FPGA/digital hardware architect** — checks locality, memory, fixed-point arithmetic, bounded iterations and streaming.
13. **Quantum information theorist** — asks what information is discarded by the baseline and whether that can fundamentally change the posterior.
14. **Experimental photonic-systems engineer** — checks whether the required metadata is measurable without an oracle.
15. **Skeptical journal reviewer** — asks whether the core algorithm is truly new relative to 2023–2026 literature.
16. **Science-fair/research-project advisor** — asks whether the project can produce a decisive result before outside experimental collaboration.

## Scoring rubric

Each score is 0–10.

- **N — Novelty (20%)**: standalone novelty after current literature.
- **P — Performance upside (20%)**: credible chance to beat a **strong calibrated correlated-MWPM** baseline.
- **A — Architecture/photonic specificity (15%)**: uses genuinely photonic physical information.
- **F — Feasibility now (15%)**: can be simulated with local optical models + Stim/PyMatching without full hardware.
- **G — Generality (10%)**: useful beyond one microscopic circuit.
- **H — FPGA path (10%)**: can eventually become bounded-latency/local/fixed-point logic.
- **U — Publication potential (10%)**: likely to support a defensible paper if results are positive.

The overall score is a decision aid, not an objective probability of publication.

## Executive conclusion

The panel does **not** recommend trying to build a decoder that simply “understands photonics” in one huge model. The strongest scientific thesis is more precise:

> **Infer QEC faults from experimentally observable, outcome-conditioned photonic latent variables and higher-order correlations before reducing the problem to ordinary syndrome decoding.**

The best first architecture is **fusion-based dual-rail photonics**, because it provides a sharp contrast between standard matching inputs and richer optical information: fusion outcome class, photon-number pattern, source history, loss ambiguity, timing, and interference quality.

The strongest single project family is therefore:

### Outcome-Conditioned Latent-Factor Decoder for Fusion-Based Photonic QEC

A local optical model produces
\[
P(F, L \mid O, \theta),
\]
where \(F\) is the QEC-relevant fault set, \(L\) contains latent physical states such as photon presence/source multiplicity/mode overlap, \(O\) is observable optical metadata, and \(	heta\) contains calibrated hardware parameters. These factors are connected to a large Stim-generated detector graph and decoded by min-sum/BP or a reliability-guided local algorithm.

The most defensible novelty comes from the **physical factor model**, not from claiming BP, GNNs, hypergraphs, FPGA, or soft decoding as new.

## Ranked scorecard

| Rank | # | Idea | Total | N | P | A | F | G | H | U | Novelty grade | Recommended role |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|:---:|---|
| 1 | 1 | Fusion-Hypergraph Decoder | **8.60** | 8.5 | 9 | 10 | 8 | 8 | 7 | 9 | A | Standalone/core |
| 2 | 2 | Latent Photon-Presence Decoder | **8.53** | 9 | 8.5 | 10 | 7.5 | 8.5 | 6.5 | 9 | A | Standalone/core |
| 3 | 4 | Multiphoton-Contamination Decoder | **8.43** | 8.5 | 8.5 | 10 | 7.5 | 8 | 7 | 9 | A | Standalone/core |
| 4 | 5 | Partial-Distinguishability Decoder | **8.15** | 8 | 8 | 10 | 7 | 8 | 7.5 | 8.5 | A- | Standalone/core |
| 5 | 3 | Full Photon-Number-Pattern Decoder | **8.10** | 8 | 7.5 | 10 | 8 | 7 | 8 | 8 | A- | Standalone/module |
| 6 | 20 | Confidence-to-Erasure GKP Decoder | **8.05** | 7.5 | 8 | 10 | 7 | 8 | 8 | 8 | A- | Standalone |
| 7 | 15 | Timing-Jitter Decoder | **7.97** | 8.5 | 7.5 | 9.5 | 7 | 7 | 7.5 | 8.5 | A | Standalone |
| 8 | 6 | Outcome-Semantic Fusion Decoder | **7.90** | 6.5 | 7 | 10 | 9 | 7.5 | 9 | 7 | B+ | Module/first paper |
| 9 | 22 | Photonic Belief-Propagation Decoder | **7.88** | 6 | 8 | 9.5 | 8 | 9 | 8 | 7.5 | B+ | Algorithmic backbone |
| 10 | 21 | Hybrid DV-CV Factor-Graph Decoder | **7.80** | 8.5 | 8 | 10 | 5 | 9 | 5 | 8.5 | A- | Ambitious standalone |
| 11 | 29 | Decoder-Control Co-Design | **7.78** | 7 | 9 | 10 | 5.5 | 9 | 6 | 7.5 | B+ | Second-stage paper |
| 12 | 10 | Multiplexing-State Decoder | **7.70** | 7.5 | 7 | 9.5 | 7.5 | 7 | 8 | 7.5 | B+ | Standalone/module |
| 13 | 18 | Loss-Aware GKP Decoder | **7.62** | 6.5 | 8 | 10 | 6.5 | 8 | 7 | 7.5 | B+ | Standalone if sharpened |
| 14 | 14 | Detector-Memory Decoder | **7.60** | 8 | 7 | 9 | 7 | 7 | 7 | 8 | A- | Standalone |
| 15 | 24 | Reliability-Guided Local Statistics Decoder | **7.58** | 5.5 | 8.5 | 8.5 | 7 | 8.5 | 9 | 7 | B | FPGA backbone |
| 16 | 28 | Uncertainty-Aware Robust Decoder | **7.53** | 6.5 | 8 | 8.5 | 7 | 9 | 7 | 7 | B+ | Extension |
| 17 | 16 | Spectral/Frequency-Mode Decoder | **7.50** | 7.5 | 7 | 9 | 7 | 7 | 7.5 | 7.5 | B+ | Standalone/module |
| 18 | 19 | Non-Gaussian GKP Likelihood Decoder | **7.50** | 7.5 | 7.5 | 9 | 6 | 7.5 | 7 | 8 | A- | Standalone |
| 19 | 27 | Online Self-Calibrating Decoder | **7.45** | 5 | 8.5 | 9 | 7 | 9 | 8 | 6.5 | B | Infrastructure/extension |
| 20 | 8 | Generated-Topology Decoder | **7.40** | 6.5 | 7 | 9 | 8 | 7 | 7.5 | 7 | B | Module |
| 21 | 9 | Route-Dependent Loss Decoder | **7.28** | 6.5 | 5.5 | 8.5 | 9 | 7.5 | 9 | 6 | B- | Module |
| 22 | 13 | Detector-Efficiency Bayesian Decoder | **7.25** | 5.5 | 6 | 9 | 9 | 7.5 | 9 | 6 | B- | Module |
| 23 | 11 | MZI/Beamsplitter-Drift Decoder | **7.15** | 5.5 | 6.5 | 9 | 8 | 8 | 8 | 6 | B- | Infrastructure |
| 24 | 12 | Coherent Optical-Fault Decoder | **7.15** | 7.5 | 7.5 | 8.5 | 5.5 | 8 | 4.5 | 8 | B+ | High-risk standalone |
| 25 | 23 | Photonic Graph-Neural-Network Decoder | **7.00** | 4.5 | 8 | 9 | 7 | 9 | 5.5 | 6.5 | B- | Secondary baseline |
| 26 | 7 | Boosted-Fusion-Aware Decoder | **6.80** | 5.5 | 6 | 9 | 8 | 5.5 | 8 | 6 | B- | Module |
| 27 | 26 | Mixture-of-Experts Photonic Decoder | **6.67** | 4.5 | 7.5 | 9 | 6.5 | 9 | 5 | 5.5 | C+ | Avoid as core |
| 28 | 17 | Analog GKP Soft-Information Decoder | **6.65** | 2.5 | 8 | 10 | 7 | 8 | 8 | 4 | C | Established component |
| 29 | 25 | Photonic Ensemble Decoder | **6.38** | 3.5 | 7 | 7.5 | 8 | 8 | 7 | 4.5 | C | Baseline/helper |
| 30 | 30 | Streaming FPGA Photonic Decoder | **6.05** | 3 | 6 | 6 | 7 | 9 | 10 | 4 | C | Validation layer |

## Idea-by-idea STORM synthesis

### 1. Fusion-Hypergraph Decoder — **8.60/10** — Novelty A

**Panel verdict:** One of the strongest ideas. FBQC already has higher-order outcome structure, while graph matching prefers pairwise detector edges. Generic hypergraph and correlation-aware decoding now exist, so the novelty must be specifically *fusion-derived, outcome-conditioned hyperedges*, not “use a hypergraph.” [R2,R6,R31]  
**Why MWPM can lose:** a single fusion/source fault can create several detector events whose joint probability is not equal to a product of pairwise edge probabilities. Correlated MWPM partially repairs this, so benchmark against it directly.  
**Key experiment:** characterize 2–4 realistic fusion primitives, compile exact local fault factors, and compare factor/hypergraph inference against calibrated correlated PyMatching over several code distances.  
**Risk:** if the effective detector error model becomes nearly graphlike after marginalization, the advantage disappears.  
**Panel:** QEC theorist ++; FBQC architect ++; inference expert ++; FPGA expert +; novelty reviewer ++.

**Scores:** Novelty 8.5/10 · MWPM-beating upside 9.0/10 · Photonic specificity 10.0/10 · Feasibility 8.0/10 · Generality 8.0/10 · FPGA 7.0/10 · Publication 9.0/10. **Role:** Standalone/core.

### 2. Latent Photon-Presence Decoder — **8.53/10** — Novelty A

**Panel verdict:** Arguably the most original standalone direction. The decoder tracks a latent `photon-present / photon-lost / ambiguous` state through time instead of assuming every loss is immediately and perfectly heralded. Nearby work exists on heralded leakage/erasure and Bayesian error tracking, but a photonic hidden-state decoder built around delayed/imperfect loss information is not a crowded area. [R8,R27,R30]  
**Why MWPM can lose:** MWPM can exploit a known erasure location, but it is much less natural when the erasure location itself is uncertain and must be inferred from a sequence of optical observations.  
**Key experiment:** HMM/factor graph over photon survival, imperfect detector efficiency, fusion outcomes, and later clicks; compare to (i) no loss side information, (ii) oracle erasure locations, (iii) best calibrated MWPM.  
**Risk:** dual-rail schemes often make loss strongly heralded; choose a realistic regime where ambiguity genuinely exists.  
**Panel:** photonic architect ++; Bayesian expert ++; QEC theorist ++; reviewer ++; FPGA expert 0/+.

**Scores:** Novelty 9.0/10 · MWPM-beating upside 8.5/10 · Photonic specificity 10.0/10 · Feasibility 7.5/10 · Generality 8.5/10 · FPGA 6.5/10 · Publication 9.0/10. **Role:** Standalone/core.

### 3. Full Photon-Number-Pattern Decoder — **8.10/10** — Novelty A-

**Panel verdict:** Strong if the architecture genuinely exposes more PNR structure than the baseline decoder uses. PNR is central to modern photonic systems, but “use more detector information” is not enough by itself. [R3,R4,R24]  
**Why MWPM can lose:** reducing a count vector to a binary success/erasure symbol throws away likelihood information about multiphoton contamination, detector loss, and source state.  
**Key experiment:** derive \(P(F|n_1,\ldots,n_k)\) from small Fock simulations, then pass LLRs/factors into the outer decoder.  
**Risk:** in some dual-rail fusion circuits the full count pattern may already deterministically collapse to the standard fusion outcome, leaving little extra information.  
**Panel:** detector physicist ++; optical theorist ++; QEC expert +; FPGA expert ++ because LUT implementation is plausible; reviewer +.

**Scores:** Novelty 8.0/10 · MWPM-beating upside 7.5/10 · Photonic specificity 10.0/10 · Feasibility 8.0/10 · Generality 7.0/10 · FPGA 8.0/10 · Publication 8.0/10. **Role:** Standalone/module.

### 4. Multiphoton-Contamination Decoder — **8.43/10** — Novelty A

**Panel verdict:** Top-tier. Multiphoton contamination is intrinsically photonic, experimentally relevant, and not captured by the standard loss+Pauli abstraction. Recent source work shows multiphoton error remains a serious hardware metric, but decoder-side exploitation is much less saturated. [R24,R3]  
**Why MWPM can lose:** one excess-photon event can create correlated downstream observations; after loss, an apparently valid detector pattern may hide the original source fault. Pairwise matching sees only the final syndrome.  
**Key experiment:** source model \(P(n)\) -> optical primitive -> observed pattern -> conditional fault distribution -> large Stim study. Ablate whether the decoder receives source/herald/PNR metadata.  
**Risk:** exact Fock simulation scales badly; characterize local primitives only.  
**Panel:** source physicist ++; photonic QEC ++; inference ++; publication reviewer ++; FPGA +.

**Scores:** Novelty 8.5/10 · MWPM-beating upside 8.5/10 · Photonic specificity 10.0/10 · Feasibility 7.5/10 · Generality 8.0/10 · FPGA 7.0/10 · Publication 9.0/10. **Role:** Standalone/core.

### 5. Partial-Distinguishability Decoder — **8.15/10** — Novelty A-

**Panel verdict:** Very strong. Partial distinguishability is a known fault-tolerance bottleneck and has architecture-level threshold studies, which actually helps: the physical relevance is established while the decoder-specific opportunity remains. [R5,R17]  
**Why MWPM can lose:** visibility/mode-overlap changes the conditional distribution of fusion faults; a global Pauli probability cannot express per-source-pair or time-dependent overlap quality.  
**Key experiment:** simulate/synthesize \(P(F|O,V)\), vary HOM visibility by source pair, and test whether visibility-conditioned decoding beats a decoder calibrated only to the average visibility.  
**Risk:** if visibility only rescales independent edge probabilities, calibrated MWPM may absorb nearly all benefit. The winning regime must generate distinguishability-dependent correlations or soft outcome information.  
**Panel:** quantum optics ++; FBQC ++; decoder theorist +; reviewer ++.

**Scores:** Novelty 8.0/10 · MWPM-beating upside 8.0/10 · Photonic specificity 10.0/10 · Feasibility 7.0/10 · Generality 8.0/10 · FPGA 7.5/10 · Publication 8.5/10. **Role:** Standalone/core.

### 6. Outcome-Semantic Fusion Decoder — **7.90/10** — Novelty B+

**Panel verdict:** Excellent first implementation, weaker as the final grand claim. FBQC literature already distinguishes success, failure and erasure semantics. [R2,R32]  
**Why MWPM can lose:** only if the baseline collapses physically distinct outcomes that imply different conditional fault distributions.  
**Key experiment:** treat raw fusion classes as separate local factors and demonstrate an ablation from binary erasure -> semantic outcome classes -> full physical likelihood.  
**Risk:** a carefully built matching graph may encode most of these cases via topology/weights, reducing novelty.  
**Use:** ideal Phase 1 for building the software stack and validating the core thesis before adding latent variables.  
**Panel:** systems ++; FPGA ++; novelty reviewer 0/+; QEC +.

**Scores:** Novelty 6.5/10 · MWPM-beating upside 7.0/10 · Photonic specificity 10.0/10 · Feasibility 9.0/10 · Generality 7.5/10 · FPGA 9.0/10 · Publication 7.0/10. **Role:** Module/first paper.

### 7. Boosted-Fusion-Aware Decoder — **6.80/10** — Novelty B-

**Panel verdict:** Do not make this the central paper. Boosted Bell-state measurements and the fusion-failure/loss tradeoff are already heavily studied, including logical-error consequences. [R2,R16]  
**Potential contribution:** condition decoding on which boosting realization/ancilla pattern occurred, rather than optimizing boosting only at architecture level.  
**Why MWPM can lose:** only if partial boosted-fusion outcomes expose soft/correlated information omitted by standard erasure models.  
**Risk:** otherwise this is parameter-aware edge reweighting and likely incremental.  
**Panel:** FBQC +; novelty reviewer --; FPGA +; architecture expert +.

**Scores:** Novelty 5.5/10 · MWPM-beating upside 6.0/10 · Photonic specificity 9.0/10 · Feasibility 8.0/10 · Generality 5.5/10 · FPGA 8.0/10 · Publication 6.0/10. **Role:** Module.

### 8. Generated-Topology Decoder — **7.40/10** — Novelty B

**Panel verdict:** Useful but probably a module. Fusion failures alter graph-state topology, and photonic graph-state/fusion literature already treats successful and failed construction paths explicitly. [R2,R17,R33]  
**Potential contribution:** dynamically decode the *realized* graph with local factor reuse rather than reconstructing a large static decoder.  
**Why MWPM can lose:** mostly implementation/topology mismatch, not a fundamental limitation; MWPM itself can run on a dynamically generated graph.  
**Risk:** the improvement may be engineering rather than algorithmic novelty.  
**Panel:** MBQC architect ++; QEC theorist 0/+; FPGA +; reviewer 0.

**Scores:** Novelty 6.5/10 · MWPM-beating upside 7.0/10 · Photonic specificity 9.0/10 · Feasibility 8.0/10 · Generality 7.0/10 · FPGA 7.5/10 · Publication 7.0/10. **Role:** Module.

### 9. Route-Dependent Loss Decoder — **7.28/10** — Novelty B-

**Panel verdict:** Important engineering feature, weak standalone novelty. Optical switch networks, path-dependent losses, and nonuniform weighting are already natural architectural concerns. [R4,R23]  
**Why MWPM can lose:** only an *uncalibrated or averaged* MWPM baseline loses badly; a properly calibrated matching graph can directly use nonuniform edge weights.  
**Best use:** feed route-conditioned priors into Ideas 1, 2, 4, 10 or 22.  
**Risk:** unfair baseline.  
**Panel:** photonic systems ++; QEC theorist -- as standalone; FPGA ++; reviewer --.

**Scores:** Novelty 6.5/10 · MWPM-beating upside 5.5/10 · Photonic specificity 8.5/10 · Feasibility 9.0/10 · Generality 7.5/10 · FPGA 9.0/10 · Publication 6.0/10. **Role:** Module.

### 10. Multiplexing-State Decoder — **7.70/10** — Novelty B+

**Panel verdict:** Better than route-dependent loss because the entire multiplexing history can be a latent cause, not just one scalar transmission value. Aurora-class architectures make real-time multiplexing central. [R4,R23]  
**Why MWPM can lose:** different source/switch/buffer histories can induce distinct mixtures of loss, preparation impurity, and timing/spectral mismatch even when their final nominal qubits occupy equivalent code locations.  
**Key experiment:** condition factors on a compact path-history token and test held-out routing patterns.  
**Risk:** may collapse into ordinary calibration conditioning if the history only changes independent probabilities.  
**Panel:** architecture ++; ML/generalization +; QEC +; FPGA ++; reviewer +.

**Scores:** Novelty 7.5/10 · MWPM-beating upside 7.0/10 · Photonic specificity 9.5/10 · Feasibility 7.5/10 · Generality 7.0/10 · FPGA 8.0/10 · Publication 7.5/10. **Role:** Standalone/module.

### 11. MZI/Beamsplitter-Drift Decoder — **7.15/10** — Novelty B-

**Panel verdict:** Useful extension, no longer novel enough alone. Self-calibrating photonics, decoder reweighting under drift, calibration-conditioned neural decoders, and online QEC control all exist. [R13,R14,R15,R25]  
**Best use:** demonstrate that the *core photonic-aware decoder* remains performant during MZI/phase drift by updating a few physical parameters online.  
**Why MWPM can lose:** static MWPM loses under mismatch, but adaptive MWPM is already a strong competitor.  
**Panel:** controls ++; photonics ++; novelty reviewer --; FPGA +.

**Scores:** Novelty 5.5/10 · MWPM-beating upside 6.5/10 · Photonic specificity 9.0/10 · Feasibility 8.0/10 · Generality 8.0/10 · FPGA 8.0/10 · Publication 6.0/10. **Role:** Infrastructure.

### 12. Coherent Optical-Fault Decoder — **7.15/10** — Novelty B+

**Panel verdict:** Scientifically interesting and potentially publishable, but much harder. Coherent errors are known to differ from stochastic Pauli channels and have dedicated surface-code theory. [R26]  
**Why MWPM can lose:** matching consumes a classical probability model after coherence has effectively been discarded. A photonic decoder could preserve a compact phase-dependent likelihood through a local primitive before discretization.  
**Key experiment:** compare exact small coherent optical block -> Pauli-twirled approximation -> decoder performance.  
**Risk:** syndrome measurement often rapidly converts coherent physical noise into effectively stochastic logical behavior at larger distances, reducing gains; FPGA realization is difficult.  
**Panel:** QEC theory ++; optics +; implementation --; reviewer +.

**Scores:** Novelty 7.5/10 · MWPM-beating upside 7.5/10 · Photonic specificity 8.5/10 · Feasibility 5.5/10 · Generality 8.0/10 · FPGA 4.5/10 · Publication 8.0/10. **Role:** High-risk standalone.

### 13. Detector-Efficiency Bayesian Decoder — **7.25/10** — Novelty B-

**Panel verdict:** Very sensible feature, weak standalone novelty. Bayesian inference between “no photon” and “missed photon” is straightforward once detector efficiency is known.  
**Why MWPM can lose:** uncertain erasure state is richer than a hard erasure flag, but this is essentially a special case of Idea 2.  
**Best use:** make detector efficiency/dark counts one observation channel inside the latent photon-presence model.  
**Risk:** if PNR/fusion patterns already herald loss with very high confidence, little gain remains.  
**Panel:** detector expert ++; Bayesian ++; reviewer -- alone.

**Scores:** Novelty 5.5/10 · MWPM-beating upside 6.0/10 · Photonic specificity 9.0/10 · Feasibility 9.0/10 · Generality 7.5/10 · FPGA 9.0/10 · Publication 6.0/10. **Role:** Module.

### 14. Detector-Memory Decoder — **7.60/10** — Novelty A-

**Panel verdict:** Underexplored and potentially strong. Detector dead time, recovery, saturation and afterpulsing create *temporal memory*, violating the independent measurement-error assumption. Detector physics literature models these effects, but photonic-QEC decoders rarely center them. [R34]  
**Why MWPM can lose:** the probability of the current readout error depends on the detector’s previous hidden state/click history, creating temporal correlations and state-dependent missing events.  
**Key experiment:** finite-state detector model + repeated syndrome stream; compare history-aware decoder to averaged detector-error MWPM.  
**Risk:** state-of-the-art SNSPD behavior in the target operating regime may make memory effects too small to matter.  
**Panel:** detector physicist ++; inference ++; QEC +; reviewer +.

**Scores:** Novelty 8.0/10 · MWPM-beating upside 7.0/10 · Photonic specificity 9.0/10 · Feasibility 7.0/10 · Generality 7.0/10 · FPGA 7.0/10 · Publication 8.0/10. **Role:** Standalone.

### 15. Timing-Jitter Decoder — **7.97/10** — Novelty A

**Panel verdict:** One of the best “narrow but impactful” ideas. Arrival-time postselection already changes fusion fidelity experimentally, proving that timestamps contain physically meaningful reliability information. [R17]  
**Why MWPM can lose:** hard assignment of a click to a time bin discards uncertainty; jitter can also couple neighboring temporal modes.  
**Key experiment:** use continuous timestamp likelihoods to jointly infer time-bin assignment/fusion reliability, then decode. Compare hard-window postselection, ordinary MWPM, and soft-timing decoding.  
**Risk:** requires a realistic timing model and architecture where temporal bins are close enough for ambiguity.  
**Panel:** experimental photonics ++; Bayesian ++; decoder +; FPGA +; reviewer ++.

**Scores:** Novelty 8.5/10 · MWPM-beating upside 7.5/10 · Photonic specificity 9.5/10 · Feasibility 7.0/10 · Generality 7.0/10 · FPGA 7.5/10 · Publication 8.5/10. **Role:** Standalone.

### 16. Spectral/Frequency-Mode Decoder — **7.50/10** — Novelty B+

**Panel verdict:** Promising if tied to a concrete architecture. Spectral distinguishability is experimentally relevant, but the strongest version is not “frequency-dependent edge weights”; it is a decoder conditioned on measured/estimated mode-overlap structure. [R5,R17]  
**Why MWPM can lose:** source-pair spectral overlap can create structured interference errors and correlations.  
**Key experiment:** frequency-bin/source-ID dependent visibility model with held-out source pairs.  
**Risk:** overlaps heavily with Idea 5. Prefer merging them into a general *mode-distinguishability-aware decoder*.  
**Panel:** optics ++; novelty +; systems +.

**Scores:** Novelty 7.5/10 · MWPM-beating upside 7.0/10 · Photonic specificity 9.0/10 · Feasibility 7.0/10 · Generality 7.0/10 · FPGA 7.5/10 · Publication 7.5/10. **Role:** Standalone/module.

### 17. Analog GKP Soft-Information Decoder — **6.65/10** — Novelty C

**Panel verdict:** Reject as a standalone novelty claim. Analog GKP decoding has existed since at least 2017, and surface-GKP decoders already dynamically weight matching graphs using analog measurement history. [R9,R10,R11]  
**Use:** mandatory baseline/component for any CV project.  
**Why it still matters:** it proves the general principle that physical analog side information can materially improve QEC—the conceptual precedent for your broader thesis.  
**Panel:** CV theorist -- novelty; QEC ++ as baseline; FPGA +.

**Scores:** Novelty 2.5/10 · MWPM-beating upside 8.0/10 · Photonic specificity 10.0/10 · Feasibility 7.0/10 · Generality 8.0/10 · FPGA 8.0/10 · Publication 4.0/10. **Role:** Established component.

### 18. Loss-Aware GKP Decoder — **7.62/10** — Novelty B+

**Panel verdict:** Potentially publishable only if sharply beyond existing GKP loss models. Photon loss is already central to photonic GKP architecture studies. [R4,R29]  
**Strong version:** infer a *joint posterior* from homodyne residual + path-specific loss + state-factory record rather than simply changing the displacement variance as a function of transmissivity.  
**Why MWPM can lose:** outer MWPM usually sees marginalized qubit error probabilities, not the full latent physical state.  
**Risk:** Aurora-like inner decoders already account for correlations from state generation and hand marginalized probabilities outward, shrinking novelty. [R4]  
**Panel:** CV +; architecture +; novelty 0/+.

**Scores:** Novelty 6.5/10 · MWPM-beating upside 8.0/10 · Photonic specificity 10.0/10 · Feasibility 6.5/10 · Generality 8.0/10 · FPGA 7.0/10 · Publication 7.5/10. **Role:** Standalone if sharpened.

### 19. Non-Gaussian GKP Likelihood Decoder — **7.50/10** — Novelty A-

**Panel verdict:** Stronger CV idea. Most practical GKP decoding starts from Gaussian/approximately Gaussian displacement models; a physically derived non-Gaussian likelihood could matter for realistic resource-state preparation.  
**Why MWPM can lose:** even analog-weighted MWPM is only as good as the likelihood supplied to it. Heavy tails or multimodality change relative logical hypotheses.  
**Key experiment:** derive non-Gaussian residuals from a specific optical state-preparation/loss mechanism and compare Gaussian LLR, mixture/LUT likelihood, and near-ML decoding.  
**Risk:** do not invent arbitrary heavy-tailed noise; novelty requires a real photonic mechanism.  
**Panel:** CV theorist ++; inference ++; reviewer +; FPGA + via LUTs.

**Scores:** Novelty 7.5/10 · MWPM-beating upside 7.5/10 · Photonic specificity 9.0/10 · Feasibility 6.0/10 · Generality 7.5/10 · FPGA 7.0/10 · Publication 8.0/10. **Role:** Standalone.

### 20. Confidence-to-Erasure GKP Decoder — **8.05/10** — Novelty A-

**Panel verdict:** Very good if formulated as *logical-error-optimal erasure conversion*, not merely postselection. Confidence/postselection and decoder confidence already exist, while photonics naturally benefits from converting hidden errors into heralded erasures. [R30,R35]  
**Why MWPM can lose:** the decoder/controller can choose when uncertain analog information should become an explicit erasure, changing the channel seen by the outer code.  
**Key experiment:** optimize the threshold \(t\) or policy \(a(q_{
m mod})\) for total logical error, including the cost of erasures.  
**Risk:** threshold-decision methods already appear in GKP work; the contribution must be joint optimization under realistic loss + finite squeezing + outer-code decoding.  
**Panel:** CV ++; QEC ++; FPGA ++; reviewer +.

**Scores:** Novelty 7.5/10 · MWPM-beating upside 8.0/10 · Photonic specificity 10.0/10 · Feasibility 7.0/10 · Generality 8.0/10 · FPGA 8.0/10 · Publication 8.0/10. **Role:** Standalone.

### 21. Hybrid DV-CV Factor-Graph Decoder — **7.80/10** — Novelty A-

**Panel verdict:** High-upside, high-risk. A unified DV/CV decoder interface is timely, and recent work has begun exploring hardware-to-decoder hybrid stacks, so the claim must be stronger than “one API handles both.” [R4,R36]  
**Strong version:** one heterogeneous factor graph performs *joint inference* over discrete fusion/PNR events and continuous homodyne variables that are statistically coupled.  
**Why MWPM can lose:** pairwise binary matching is structurally mismatched to mixed continuous/discrete factors.  
**Risk:** difficult to find a physically compelling architecture where DV and CV information are jointly coupled rather than simply concatenated.  
**Panel:** information theorist ++; CV/DV architect ++; FPGA --; reviewer ++ if physics is real.

**Scores:** Novelty 8.5/10 · MWPM-beating upside 8.0/10 · Photonic specificity 10.0/10 · Feasibility 5.0/10 · Generality 9.0/10 · FPGA 5.0/10 · Publication 8.5/10. **Role:** Ambitious standalone.

### 22. Photonic Belief-Propagation Decoder — **7.88/10** — Novelty B+

**Panel verdict:** Best algorithmic backbone, not sufficient novelty alone. BP/min-sum and learned message passing are now highly active, including correlated-error decoders with FPGA results. [R6,R19]  
**Strong version:** the *factorization* is photonic and novel; BP is merely the efficient inference engine.  
**Why it can beat MWPM:** BP can naturally consume local higher-order factors and soft priors instead of reducing everything to pairwise matching.  
**Risk:** short cycles/degeneracy can make vanilla BP fail; use normalized min-sum, graph transforms, or local postprocessing.  
**Panel:** coding theorist ++; FPGA ++; novelty reviewer 0 alone.

**Scores:** Novelty 6.0/10 · MWPM-beating upside 8.0/10 · Photonic specificity 9.5/10 · Feasibility 8.0/10 · Generality 9.0/10 · FPGA 8.0/10 · Publication 7.5/10. **Role:** Algorithmic backbone.

### 23. Photonic Graph-Neural-Network Decoder — **7.00/10** — Novelty B-

**Panel verdict:** Too crowded as the primary novelty. Neural decoders already exploit soft inputs, leakage information, device-specific data and graph message passing. [R12,R19]  
**When useful:** as a comparator proving whether hand-designed photonic factors capture the right physics, or as a learned local factor potential.  
**Publication trap:** “GNN beats MWPM on synthetic data” is no longer compelling without generalization, ablations, interpretability and very strong baselines.  
**Panel:** ML expert +; QEC reviewer -- as core; generalization expert demands held-out architectures.

**Scores:** Novelty 4.5/10 · MWPM-beating upside 8.0/10 · Photonic specificity 9.0/10 · Feasibility 7.0/10 · Generality 9.0/10 · FPGA 5.5/10 · Publication 6.5/10. **Role:** Secondary baseline.

### 24. Reliability-Guided Local Statistics Decoder — **7.58/10** — Novelty B

**Panel verdict:** Excellent hardware path after the physics novelty is established. LSD is already published as a reliability-guided, parallelizable decoder, so “photonic LSD” alone is incremental. [R7]  
**Strong version:** derive unusually informative photonic reliability measures and show LSD turns them into an FPGA-friendly advantage.  
**Why MWPM can lose:** local statistics can exploit reliability in ambiguous regions without global matching overhead.  
**Panel:** FPGA ++; QLDPC decoder ++; novelty reviewer 0/+.

**Scores:** Novelty 5.5/10 · MWPM-beating upside 8.5/10 · Photonic specificity 8.5/10 · Feasibility 7.0/10 · Generality 8.5/10 · FPGA 9.0/10 · Publication 7.0/10. **Role:** FPGA backbone.

### 25. Photonic Ensemble Decoder — **6.38/10** — Novelty C

**Panel verdict:** Reject as core novelty. Ensemble decoders are already used at high performance, including correlated min-sum ensembles and matching ensembles. [R6,R37]  
**Use:** strong benchmark or accuracy booster late in the project.  
**Risk:** expensive FPGA resource duplication and unclear scientific insight.  
**Panel:** reviewer --; systems 0/+.

**Scores:** Novelty 3.5/10 · MWPM-beating upside 7.0/10 · Photonic specificity 7.5/10 · Feasibility 8.0/10 · Generality 8.0/10 · FPGA 7.0/10 · Publication 4.5/10. **Role:** Baseline/helper.

### 26. Mixture-of-Experts Photonic Decoder — **6.67/10** — Novelty C+

**Panel verdict:** Weak core novelty in 2026. Mixture-of-experts QEC decoders already exist in preprint form, and generic regime-specialization is an obvious ML construction. [R38]  
**Use:** only if a physically interpretable gate routes between genuinely different photonic channel models and demonstrates transfer to unseen architectures.  
**Risk:** data hungry, hardware heavy, easy to criticize as architecture search.  
**Panel:** ML +; FPGA --; reviewer --.

**Scores:** Novelty 4.5/10 · MWPM-beating upside 7.5/10 · Photonic specificity 9.0/10 · Feasibility 6.5/10 · Generality 9.0/10 · FPGA 5.0/10 · Publication 5.5/10. **Role:** Avoid as core.

### 27. Online Self-Calibrating Decoder — **7.45/10** — Novelty B

**Panel verdict:** High practical value but crowded. Decoder graph reweighting under drift, calibration-conditioned decoding, and RL-based calibration/decoder steering now have strong precedents. [R13,R14,R15]  
**Use:** a later experiment showing your photonic latent-factor decoder can self-update its physical parameters without retraining.  
**Strong metric:** recovery time after abrupt source/phase/detector drift.  
**Panel:** controls ++; architecture ++; novelty reviewer -- alone.

**Scores:** Novelty 5.0/10 · MWPM-beating upside 8.5/10 · Photonic specificity 9.0/10 · Feasibility 7.0/10 · Generality 9.0/10 · FPGA 8.0/10 · Publication 6.5/10. **Role:** Infrastructure/extension.

### 28. Uncertainty-Aware Robust Decoder — **7.53/10** — Novelty B+

**Panel verdict:** Good extension and important for credible generalization. Uncertainty-aware neural decoding is emerging, and real hardware inevitably has parameter uncertainty. [R39]  
**Strong photonic version:** propagate uncertainty over visibility, loss, efficiency, squeezing, etc. into the local factor likelihoods instead of pretending calibration parameters are exact.  
**Why MWPM can lose:** point-estimate weights can be badly miscalibrated under distribution shift.  
**Risk:** robust/adaptive MWPM is also possible; compare against it.  
**Panel:** statistics ++; reviewer +; FPGA + if uncertainty is discretized/LUT-based.

**Scores:** Novelty 6.5/10 · MWPM-beating upside 8.0/10 · Photonic specificity 8.5/10 · Feasibility 7.0/10 · Generality 9.0/10 · FPGA 7.0/10 · Publication 7.0/10. **Role:** Extension.

### 29. Decoder-Control Co-Design — **7.78/10** — Novelty B+

**Panel verdict:** Potentially major *second paper*, but no longer greenfield. Aurora already uses decoder confidence to trigger keep/cut feedforward, and 2026 Nature work unifies QEC control with online reinforcement learning. [R4,R14]  
**Strong photonic version:** decoder confidence determines fusion boosting, rerouting, resource discard, or additional checks under a quantitatively optimized latency/loss budget.  
**Why important:** the decoder changes the future physical channel instead of passively interpreting it.  
**Risk:** scope explosion; attribution becomes difficult.  
**Panel:** systems ++; controls ++; novelty reviewer +/0; science-fair feasibility --.

**Scores:** Novelty 7.0/10 · MWPM-beating upside 9.0/10 · Photonic specificity 10.0/10 · Feasibility 5.5/10 · Generality 9.0/10 · FPGA 6.0/10 · Publication 7.5/10. **Role:** Second-stage paper.

### 30. Streaming FPGA Photonic Decoder — **6.05/10** — Novelty C

**Panel verdict:** Essential validation, not scientific novelty by itself. Multiple groups have already demonstrated FPGA/local real-time QEC decoding, including photonic real-time feedforward. [R4,R6,R8,R40]  
**Use:** implement the winning decoder’s local likelihood/BP/LSD kernel in fixed point and show the performance-latency Pareto frontier. That materially strengthens the project even though FPGA itself is not the new idea.  
**Panel:** FPGA ++; reviewer -- as core; experimentalist ++ as validation.

**Scores:** Novelty 3.0/10 · MWPM-beating upside 6.0/10 · Photonic specificity 6.0/10 · Feasibility 7.0/10 · Generality 9.0/10 · FPGA 10.0/10 · Publication 4.0/10. **Role:** Validation layer.

# Panel synthesis: what should actually be built?

## Tier 1 — Best standalone scientific cores

### 1) Fusion hypergraph/factor decoder + latent photon state
Combine **Ideas 1 + 2**.

This has the cleanest theoretical story:
- fusion/source processes generate common-cause faults;
- imperfect heralding makes some physical state latent;
- optical outcomes constrain the posterior;
- pairwise matching is an approximation to that posterior;
- a local factor graph keeps the relevant information.

This is the panel's **best overall recommendation**.

### 2) Multiphoton + distinguishability-aware fusion decoder
Combine **Ideas 4 + 5**, optionally with **3**.

This has the cleanest quantum-optics story:
- source emission number and mode overlap are concrete device parameters;
- both change fusion statistics;
- their downstream faults can be correlated;
- PNR/timing/source metadata may reveal partial information about the cause.

This is especially attractive if you want Strawberry Fields / Fock simulation to play a substantial role.

### 3) Soft timing / mode assignment decoder
Build **Idea 15**, possibly merging spectral information from **16**.

This is narrower but experimentally legible: use a continuous timestamp or mode-overlap likelihood instead of hard temporal-window acceptance. It may be easier to validate decisively than a huge all-physics decoder.

### 4) GKP logical-error-optimal erasure converter
Build **Idea 20**, optionally adding **19**.

This is the strongest CV branch. Do **not** pitch analog GKP soft decoding itself as novel. Pitch the project as deciding when uncertain continuous information should be transformed into a located erasure under a physically realistic non-Gaussian/lossy channel.

## Tier 2 — Strong supporting modules

Use these to improve the chosen Tier-1 project:
- **6 Outcome semantics** — first implementation and ablation.
- **10 Multiplexing-state conditioning** — adds real architecture history.
- **14 Detector memory** — adds a second latent-state mechanism.
- **16 Spectral/mode conditioning** — merge with distinguishability.
- **22 Photonic BP/min-sum** — preferred efficient inference engine.
- **24 Reliability-guided LSD** — preferred later FPGA-oriented postprocessor.
- **28 Uncertainty-aware decoding** — robustness under calibration uncertainty.

## Tier 3 — Important but not core novelty

- 7 Boosted-fusion awareness
- 8 Generated topology
- 9 Route-dependent loss
- 11 MZI drift
- 13 Detector efficiency
- 17 Analog GKP soft decoding
- 18 Generic loss-aware GKP
- 23 Photonic GNN
- 25 Ensemble
- 26 Mixture of experts
- 27 Self-calibration
- 30 FPGA implementation

These are useful, but current literature makes them weak standalone paper claims.

## Tier 4 — High-risk later work

- **12 Coherent optical-fault decoder** — scientifically deep but difficult to scale and hard to map to an FPGA.
- **21 Hybrid DV-CV joint factor graph** — potentially broad, but the physically coupled use case must be real.
- **29 Decoder-control co-design** — potentially high impact, but should follow a successful passive decoder.

# Recommended research program

## Phase 1 — Prove the information advantage

Choose one FBQC primitive and generate an exact local table

\[
P(F,L,O \mid \theta).
\]

Start with:
- photon loss,
- fusion success/failure/erasure,
- imperfect detector efficiency,
- one of {multiphoton emission, partial distinguishability}.

Then compare:
1. uniform MWPM,
2. calibrated MWPM,
3. correlated MWPM,
4. BP/min-sum given only the same marginalized detector model,
5. **your decoder given observable photonic metadata**,
6. oracle decoder given true latent states only as an upper bound.

The critical scientific quantity is

\[
\Delta_{\rm info}
=
p_L(\text{best baseline using syndrome})
-
p_L(\text{decoder using syndrome + observable photonic metadata}).
\]

If \(\Delta_{\rm info}\) is not significant, the project should stop or change the physical information source.

## Phase 2 — Show the gain comes from physics, not model capacity

Ablate the metadata:
- remove fusion outcome semantics,
- remove PNR pattern,
- remove source ID/history,
- remove visibility/timing,
- remove uncertain-loss posterior.

Also compare the **same inference algorithm** with and without these features. This prevents a reviewer from saying the gain merely comes from replacing MWPM with a stronger generic decoder.

## Phase 3 — Generalization

Hold out:
- code distances,
- physical error rates,
- source pairs,
- visibility values,
- detector efficiencies,
- loss values,
- routing histories.

A photonic-aware decoder should generalize by changing calibrated physical parameters, not by retraining from scratch for every device.

## Phase 4 — Hardware shape before FPGA

Convert the winning algorithm to:
- log-likelihood or fixed-point messages,
- LUT-based optical likelihoods,
- bounded BP/min-sum iterations,
- local graph neighborhoods,
- streaming syndrome input,
- fixed maximum memory.

Only then move to an FPGA. The FPGA is the **validation of practicality**, not the original novelty.

# What would count as a publishable result?

A strong positive result would look like:

> Under a realistic fusion-based optical model, observable photon-count/timing/source information changes the posterior over correlated QEC faults in a way that cannot be captured exactly by a graphlike matching model. A local photonic factor decoder reduces logical error rate versus calibrated correlated MWPM across several code distances and physical regimes, preserves most of the gain under calibration mismatch, and can be quantized into a bounded-latency message-passing implementation.

A weak result would look like:

> A neural network trained on extra simulator labels beats uncalibrated MWPM at one code distance.

The first is publishable science. The second is not a convincing architecture-aware decoder result.

# Final ranking by research decision

**Pursue now:** 1, 2, 4, 5, 15, 20.  
**Build into the main system:** 3, 6, 10, 14, 16, 22, 24, 28.  
**Use as baselines/infrastructure:** 7, 8, 9, 11, 13, 17, 18, 23, 25, 26, 27, 30.  
**Save for a second paper:** 12, 21, 29.


## Research anchors

**[R1]** Shao et al., *Assisting in Writing Wikipedia-like Articles From Scratch with Large Language Models* / Stanford STORM, NAACL 2024; STORM uses perspective-guided question asking and source-grounded simulated conversations.

**[R2]** Bartolucci et al., *Fusion-based quantum computation*, Nature Communications 14, 912 (2023).

**[R3]** PsiQuantum team, *A manufacturable platform for photonic quantum computing*, Nature 641, 876–883 (2025).

**[R4]** *Scaling and networking a modular photonic quantum computer*, Nature (2025). Demonstrates real-time photonic decoding/feedforward and a GKP inner/outer decoding architecture.

**[R5]** Chan et al., *Tailoring Fusion-Based Photonic Quantum Computing Schemes to Quantum Emitters*, PRX Quantum 6, 020304 (2025).

**[R6]** Maan et al., *Decoding correlated errors in quantum LDPC codes*, Nature Communications 17, 3965 (2026).

**[R7]** Hillmann et al., *Localized statistics decoding for quantum low-density parity-check codes*, Nature Communications 16, 8214 (2025).

**[R8]** *Local clustering decoder as a fast and adaptive hardware decoder for the surface code*, Nature Communications 16, 11048 (2025).

**[R9]** Fukui, Tomita & Okamoto, *Analog Quantum Error Correction with Encoding a Qubit into an Oscillator*, Physical Review Letters 119, 180507 (2017).

**[R10]** Noh, Chamberland & Brandão, *Low-Overhead Fault-Tolerant Quantum Error Correction with the Surface-GKP Code*, PRX Quantum 3, 010315 (2022).

**[R11]** *Closest Lattice Point Decoding for Multimode Gottesman-Kitaev-Preskill Codes*, PRX Quantum 4, 040334 (2023).

**[R12]** Bausch et al., *Learning high-accuracy error decoding for quantum processors* (AlphaQubit), Nature 635, 834–840 (2024).

**[R13]** Wang et al., *DGR: Tackling Drifted and Correlated Noise in Quantum Error Correction via Decoding Graph Re-weighting* (2023 preprint).

**[R14]** *Reinforcement learning control of quantum error correction*, Nature 655, 879–884 (2026).

**[R15]** Stein et al., *Calibration-Conditioned FiLM Decoders for Low-Latency Decoding of Quantum Error Correction* (2026 preprint).

**[R16]** Hauser et al., *Boosted Bell-state measurements for photonic quantum computation*, npj Quantum Information 11, 41 (2025).

**[R17]** Thomas et al., *Fusion of deterministically generated photonic graph states*, Nature 629, 567–572 (2024).

**[R18]** Kuo & Ouyang, *Degenerate quantum erasure decoding*, npj Quantum Information (2026).

**[R19]** Maan & Paler, *Machine learning message-passing for the scalable decoding of QLDPC codes*, npj Quantum Information 11, 78 (2025).

**[R20]** Nguyen et al., *A Mixture of Experts Vision Transformer for High-Fidelity Surface Code Decoding* (2026 preprint).

**[R21]** Bravyi, Englbrecht, König & Peard, *Correcting coherent errors with surface codes*, npj Quantum Information 4, 55 (2018).

**[R22]** *Demonstrating real-time and low-latency quantum error correction with superconducting qubits*, Nature Communications (2026).

**[R23]** Bartolucci et al., *Switch networks for photonic fusion-based quantum computing* (2021 preprint).

**[R24]** *Selective filtering of multi-photon events from a single-photon emitter*, Nature Communications 17, 8412 (2026), plus recent high-efficiency single-photon-source work emphasizing multiphoton purity.

**[R25]** Xu et al., *Self-calibrating programmable photonic integrated circuits*, Nature Photonics 16, 595–602 (2022).

**[R26]** Bravyi et al., coherent-error surface-code literature; see [R21].

**[R27]** *Parity-encoding-based quantum computing with Bayesian error tracking*, npj Quantum Information (2023).

**[R28]** Recent 2026 work on hybrid CV/DV hardware-to-decoder interfaces (LiDMaS+ preprint); relevant as novelty pressure on “unified interface” claims.

**[R29]** Bourassa et al., *Fault-Tolerant Quantum Computation with Static Linear Optics*, PRX Quantum 2, 040353 (2021).

**[R30]** Wu et al., *Erasure conversion for fault-tolerant quantum computing in alkaline earth Rydberg atom arrays*, Nature Communications 13, 4657 (2022). Platform differs, but establishes the general QEC value of converting hidden errors into located erasures.

**[R31]** Bhave et al., *HyperNQ: A Hypergraph Neural Network Decoder for Quantum LDPC Codes* (2025 preprint), showing novelty pressure on generic “hypergraph decoder” claims.

**[R32]** Recent experimental temporal-fusion work reports different retained/erased observables and different error rates conditioned on fusion success/failure outcomes, supporting outcome-semantic likelihoods.

**[R33]** Gold et al., *Heralded photonic graph states with inefficient quantum emitters*, npj Quantum Information 12, 35 (2026).

**[R34]** Recent superconducting-nanowire detector modeling explicitly includes dark counts and notes afterpulsing/dead-time effects as relevant detector-memory mechanisms.

**[R35]** Recent work on decoder confidence / efficient postselection in QEC and Aurora’s keep/cut decision logic provide precedent; novelty requires optimizing erasure conversion at the logical level.

**[R36]** Wayo et al., *A Unified Hardware-to-Decoder Architecture for Hybrid Continuous-Variable and Discrete-Variable Quantum Error Correction in LiDMaS+* (2026 preprint).

**[R37]** Google Quantum AI, *Quantum error correction below the surface code threshold*, Nature 638, 920–926 (2025), uses high-accuracy correlated/ensemble matching approaches.

**[R38]** See [R20].

**[R39]** Mi & Mueller, *Toward Uncertainty-Aware and Generalizable Neural Decoding for Quantum LDPC Codes* (2025 preprint).

**[R40]** Barber et al., *A real-time, scalable, fast and resource-efficient decoder for a quantum computer*, Nature Electronics (2025), plus [R8], [R22], and the photonic real-time FPGA chain in [R4].
