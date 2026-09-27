# Fusion-Hypergraph Decoder and Ancilla-Cost Study: Physics-to-QEC Project Plan

## Decision and research question

The project now separates an **accuracy-first, bounded logical decoder test** from the later physical FBQC claim. The first test may use a declared fusion-correlated effective channel to establish whether joint decoding actually lowers logical failure. Such an assumption is labeled as a sensitivity model, never as optical calibration. The physical stage must then connect an identifiable source/fusion mechanism to observable records, postfusion actions, and native detector/logical effects.

The present project has two linked questions. First, on the **same physical fusion circuit and the same observable records**, can a decoder that retains validated multi-detector fault mechanisms reduce logical failure relative to the strongest calibrated matching baseline? Second, can an **ancilla-free encoded fusion circuit plus that decoder** reach a useful logical reliability at lower physical resource cost than a boosted circuit plus metadata-aware MWPM? The second comparison is an architecture-and-decoder result; the first isolates the decoder's contribution.

The eventual selective implementation may be hybrid:

1. calibrated MWPM handles the ordinary case: no fault, located erasure, or approximately pairwise error;
2. a cheap, local posterior trigger uses the syndrome to identify regions where one validated physical fusion mechanism plausibly explains several detector events; observable fusion metadata is an optional additional likelihood input; and
3. bounded hypergraph refinement compares that common-cause explanation with the MWPM explanation only in activated regions.

The primary near-term question is:

> Can global joint-fault inference beat equally informed calibrated MWPM and belief matching on a bounded logical memory under a declared fusion-error channel, and does that advantage survive a physically derived ancilla-free encoded fusion model? Compare ancilla cost only after the decoder claim is established.

First test **global or bounded exact hypergraph inference** to establish whether the correlation helps at all. Only after an accuracy gain exists should a posterior trigger be tested for retaining it at lower classical cost. A sparse trigger is therefore a later engineering gate, not a prerequisite for judging the ancilla-free hardware hypothesis. Metadata is tested as a separate improvement, not a condition for syndrome-only hypergraph decoding.

### Accuracy-first objective — 2026-09-26

**Immediate goal:** demonstrate a lower *bounded-memory logical failure rate* from a decoder that keeps a common-cause fusion $XX/ZZ$ fault intact than from equally informed, calibrated MWPM. Compare correlation-aware belief matching too; uncalibrated MWPM is a secondary reference and cannot establish the result. Do not optimize a selective trigger or runtime until the global accuracy contrast is established. Ancilla cost and boosted-versus-ancilla-free system comparisons remain later questions.

The [FBQC framework](https://www.nature.com/articles/s41467-023-36493-1) supplies the six-ring fusion measurement/check setting and motivates retaining correlations between a fusion's $XX$ and $ZZ$ outcomes. [Belief-matching](https://journals.aps.org/prx/abstract/10.1103/PhysRevX.13.031007) is a published correlation-aware benchmark; beating ordinary MWPM alone is weaker. Neither paper gives this project's fault incidence or record-conditioned optical action. A decoder advantage therefore has **two** levels of evidence, never one blended claim:

1. **Effective-channel logical proof:** use a finite Stim memory with a declared logical observable and inject a single categorical $I/X/Z/Y$ event at a specified location. A joint fusion-parity flip maps to $Y$ through an explicitly declared teleportation-frame adapter. Freeze a sensitivity grid including zero correlation, identical held-out shots, and record access before comparison. Give calibrated MWPM, belief matching, and global joint-configuration MAP the same syndrome and any observable flags. On a tractable no-flag case, enumerate logical classes exactly as an optimum reference. Count logical failures with paired uncertainty. This proves only that a decoder can exploit the hypothesized fusion-type correlation in a bounded code.
2. **Physical FBQC proof:** derive or measure $P(R,A\mid\theta)$ for a named ancilla-free fusion and source fault, including conclusive, partial, loss, and ambiguous outcomes. Inject representable actions into a **native bounded encoded six-ring memory** with explicit boundaries and logical observable. Preserve unsupported coherent/leakage outcomes and coverage. Repeat the same fair decoder matrix across the frozen physical grid. Only this level can support a photonic fusion logical-advantage claim.

The first success gate is a resolved held-out logical gain of global joint decoding over both calibrated MWPM and the correlation-aware matching control at a **predeclared** primary effective-channel point, with zero-correlation and low-rate controls reported even if inconclusive. A numerical gain under assumed $Y$ incidence does not set the physical operating range. The second gate requires calibrated action incidence and native-memory validation; it cannot be passed by tuning that incidence or by counting a periodic-sector proxy as a logical memory. For metadata, compare core and detailed records *within the same circuit and shot set*, and test whether the extra benefit to the joint decoder over MWPM is itself resolved. A sparse selector and comparable runtime are subsequent engineering gates.

The [completed bounded effective-channel result](phase0/BOUNDED_JOINT_LOGICAL_RESULTS.md) passes that first gate at the predeclared $3\%$ joint-fault sensitivity point: on 20,000 held-out Z-memory shots, calibrated MWPM fails 319 times, belief matching 134 times, and global joint configuration MAP 67 times; exhaustive logical-class MAP also fails 67 times. The paired MAP gain over calibrated MWPM is 1.260 percentage points (95% interval 1.090–1.425), and over belief matching 0.335 points (0.245–0.425). When the joint fault is removed but the marginal $X/Z$ rates are matched, MWPM has 307 failures and MAP 308 on 20,000 shots. The $1\%$ joint arm is unresolved at 5,000 shots. These are **logical-memory results under a declared effective fusion-to-$Y$ adapter**, not optical or native FBQC validation. The physical second gate remains open.

The subsequent [improved-idea Phase 0 audit](phase0/IMPROVED_IDEA_GO_NO_GO.md) tests a named Pauli $Y$ fault entering the ideal ancilla-free two-photon analyzer. The exact optical instrument verifies the conclusive joint parity flip and shows zero raw-PNR discrimination under a uniform Bell input. After the four-BSM encoded reconstruction, the same fault is a joint encoded $XX/ZZ$ event for half of ideal input assignments, an $XX$-only event for one quarter, and a missing-$ZZ$ event for one quarter. Thus the higher-order mechanism is real **for this specified local fault**, but the rate of that fault is not calibrated and no native bounded encoded six-ring memory has been validated. The present decision is **go for mechanism study, no-go for a physical decoder-advantage claim**. Resume the physical gate only with a sourced incidence/channel and paper-consistent bounded logical circuit; do not promote the 3% effective-memory sensitivity point to a device prediction.

The later [optical action audit](phase0/PHYSICAL_CHANNEL_AUDIT.md) checks the **full Bell-basis effect matrix per accepted PNR record** for all named local causes. The older extra-plus-photon calculation retained only Bell-diagonal branch weights; every accepted extra-plus record at 99.5% and 95% detection has nonzero Bell coherence. Its previously quoted projected joint-$Y$ rate is therefore withdrawn as a physical Pauli-channel rate. Same-rail extra photons have a diagonal accepted action but no joint-$Y$ component; the specified input $Y$ has the right accepted action but unknown incidence. No currently modeled, calibrated source supplies a complete useful joint channel. Do not run the physical decoder gate by projecting away coherent terms, conditioning only on conclusive records, or selecting a favorable $Y$ incidence. A [recent source-characterization method](https://arxiv.org/abs/2608.03005) suggests optical measurements that could yield resource-state Pauli rates and post-fusion maps; this project still needs source-specific measurements or independently justified parameters.

The [paper-source follow-up](phase0/PAPER_SOURCE_CHANNEL_RESULTS.md) tests whole published first-order Pauli mixtures instead of choosing a favorable $Y$ incidence. It exactly scores all $4^9$ fault configurations on the existing $d=3$ surface-code sensitivity model, with identical channel knowledge for calibrated MWPM, global configuration MAP, and optimal logical-class MAP. The three-level model gives a modest configuration-MAP gain. In the biased four-level model, configuration MAP **loses** to calibrated MWPM on Z memory, although logical-class MAP improves slightly. Thus finding the most likely fault configuration is not the right final objective for logical reliability. A separate exact four-BSM calculation propagates the paper's input-photon marginals into a local ancilla-free encoded record/action table, retaining partial and lost records. That table assumes independent photon Pauli errors and detector survival; it is not a measured source channel or a native logical-memory test. A tested post-source bilateral Pauli randomization did not remove the extra-photon Bell coherence. The physical gate remains **NO-GO**. Next, validate a source-specific joint record/action channel and a finite six-ring circuit with the paper's primal and dual boundaries, then score a locked logical-class decoder and calibrated matching controls on identical native shots. Keep the Table 1 input-source and Table 2 added-fusion channels separate until a complete physical model justifies combining them.

## Claim boundary

This is a staged computational study. A small Fock-space simulation can validate probabilities and observability for one chosen fusion primitive and short fusion network. An event-level decoder benchmark can test logical performance under the resulting effective noise model. Neither alone validates a full native FBQC architecture, a surface-code hardware implementation, or experimental performance.

Hidden Fock occupations, simulated loss locations, and simulator truth are allowed only for generating data, validating the compiler, and scoring synthetic labels. The online decoder receives only the observable detector record, approved calibration context, and QEC syndrome.

## Architecture choice

### Initial encoding: dual-rail path encoding

The initial circuit uses dual-rail path encoding:

$$
\lvert 0\rangle=\lvert 1,0\rangle,\qquad
\lvert 1\rangle=\lvert 0,1\rangle.
$$

Each qubit is one photon distributed across two spatial modes. This is the correct first benchmark because a linear-optical fusion can be expressed directly with beamsplitters, phase shifts, loss channels, and PNR detectors. Each output mode has a clear physical interpretation, and the full detector pattern can be retained as metadata.

The circuit uses synchronized photon pulses. Time is initially a measurement coordinate, not the logical encoding: detector timestamps are compared with the expected fusion window. Time-bin encoding and explicit spectral/temporal-mode encodings are deferred. They are valuable extensions for modeling distinguishability, but would otherwise make it unclear whether a result comes from the fusion mechanism or the choice of qubit encoding.

### Local 3–4-layer benchmark

Construct a small six-ring resource-state network with a named fusion layout and at least two connected fusions; add further layers only when the local optical operation is characterized:

```text
small resource states
    |
two independent fusions
    |
one joining fusion
    |
optional final fusion / readout
```

The circuit must include at least one shared resource state and one downstream fusion. This lets a single source, loss, or interference mechanism alter more than one later measurement. The result is a bounded, inspectable map from one physical cause to its possible detector-event support.

This circuit is a physics benchmark, not a claimed surface-code patch. Its purpose is to answer: which raw records are observable, which mechanisms can be confused, and when one local mechanism produces a genuinely correlated effective QEC event.

## Two simulation tiers

### Tier 1: local optical physics compiler

Use Strawberry Fields with its Fock backend for the selected primitive and short network. The Fock backend can represent Fock inputs, linear interferometers, loss, and photon-number measurements. Run low photon cutoffs first, then demonstrate cutoff convergence for every reported probability.

Strawberry Fields is appropriate here because the circuit is small and the outputs are explicitly non-Gaussian PNR records. It is not the engine for a full surface code or large fusion network: a multimode Fock state has a cutoff-sized axis per optical mode, so the state space grows rapidly with mode count. The optical tier therefore produces a table; it does not generate every large-code shot.

Validate Tier 1 in this order:

1. ideal two-photon interference and expected fusion/Bell-measurement patterns;
2. pure loss, with analytic or independent Monte Carlo agreement;
3. source multiphoton contamination and PNR outcomes;
4. a reduced partial-distinguishability model using photon-mode overlap;
5. two-fusion propagation; and
6. the complete 3–4-layer benchmark.

For distinguishability, start with an explicit overlap parameter $\mu\in[0,1]$. A later high-fidelity treatment may represent temporal or spectral wave packets as additional modes, but that expansion must remain local because it increases Fock-space cost. A successful-looking fusion outcome is not automatically error-free when photons are partially distinguishable.

### Tier 2: scalable effective-noise and QEC benchmark

Compile Tier-1 probabilities into fusion-level effective actions and observable records:

$$
P(A,R\mid \theta),
$$

Here $A$ specifies a justified fusion-outcome bit flip, located erasure, Pauli-frame effect, or explicit ambiguous/unmodeled outcome; $R$ is the observable raw record or compressed metadata. The table may retain several possible actions for the same record. A named stabilizer circuit in Stim then maps each representable action at a specified fusion location to detector and logical-observable effects $E=(D,L)$. A Fock output pattern alone is not a surface-code detector event. The scalable benchmark must never pass hidden Fock labels or simulated physical causes to a decoder.

This separation is the central scalability decision:

$$
\text{optical parameters}
\rightarrow
P(A,R\mid\theta)
\rightarrow
\text{Stim-derived detector/logical supports and observable heralds}
\rightarrow
\text{calibrated MWPM / global hypergraph / optional selective-refinement benchmark}.
$$

### Stim bridge: from fusion outcomes to code detectors

Stim is the stabilizer-circuit and detector-error-model tool, not the optical simulator. First specify the resource state, fusion measurements, measurement order, Pauli-frame rules, check parities, and logical observable for the chosen fusion network. Encode its ideal Clifford/stabilizer behavior in Stim. `DETECTOR` annotations identify combinations of measurement results that are deterministic without faults; `OBSERVABLE_INCLUDE` identifies the logical parity. A conventional rotated surface-code circuit is acceptable only as a clearly labeled effective-channel proxy. It does not by itself establish a native fusion-based surface-code mapping.

Next derive the interface from each optical record to its possible *fusion-level* actions. A conclusive record might imply a reported $XX$ or $ZZ$ outcome, a wrong outcome bit, or a Pauli-frame change. A missing outcome is a located erasure, not automatically a bit flip. An excess-photon or leakage case that has no defensible stabilizer action remains ambiguous/unmodeled. This interface requires a physical fusion-instrument derivation or independent validation; Stim cannot infer it from PNR counts.

For each representable action at each fusion location, inject the corresponding Pauli fault or outcome-bit perturbation into the annotated circuit and determine which detectors and logical observables change relative to the ideal circuit. Equivalently, when the action is a vector of measurement-result flips $\delta m$ and the declared detector/logical parities are $H$ and $g$, the effect is

$$
\delta D=H\delta m\pmod 2,\qquad
\delta L=g\delta m\pmod 2.
$$

Derive $H$ and $g$ from the specified circuit's measurement definitions; do not assign $\delta D$ or $\delta L$ by intuition. For Pauli mechanisms, use Stim fault propagation and inspect an **undecomposed** detector error model so a genuine multi-detector support remains visible. Graphlike decomposition is allowed later for an MWPM control, but cannot be the source of the claimed hyperedge. Keep erasure flags and record-dependent unavailable checks explicit; validate their conditional detector treatment rather than representing every erasure as an ordinary Pauli error. The resulting versioned map is $(\text{fusion location},A)\mapsto(D,L,\text{erasure/check mask})$ and is joined with $P(A,R\mid\theta)$ for shot generation.

## Physical noise model

For every fusion attempt, model a discrete physical mechanism:

$$
c\in\{
\text{ideal},
\text{intrinsic fusion failure},
\text{photon loss},
\text{multiphoton emission},
\text{partial distinguishability},
\text{detector artifact}
\}.
$$

The initial parameter vector is:

$$
\theta=(\eta_{\mathrm{src}},p_2,\eta_{\mathrm{path}},
\mu,\eta_{\mathrm{det}},p_{\mathrm{dark}},\sigma_t).
$$

| Parameter | Physical role |
|---|---|
| $\eta_{\mathrm{src}}$ | Probability a source supplies its intended photon. |
| $p_2$ | Probability of multiphoton emission or two-photon contamination. |
| $\eta_{\mathrm{path}}$ | Transmission through routing, switches, and fusion optics. |
| $\mu$ | Photon mode overlap; $\mu=1$ is ideal indistinguishability. |
| $\eta_{\mathrm{det}}$ | Detector efficiency. |
| $p_{\mathrm{dark}}$ | Dark-count probability in one detection window. |
| $\sigma_t$ | Timing jitter or relative-arrival-time spread. |

The compiler applies a mechanism to the incoming optical state, propagates it through the benchmark circuit, and evaluates the detector POVM:

$$
P(r\mid c,\theta)
=\operatorname{Tr}\left[E_r\,\mathcal N_c(\rho_{\mathrm{in}})\right].
$$

Here $r$ is the raw record, $\mathcal N_c$ is the physical noise process, and $E_r$ is the optical detector measurement associated with that record. A separate fusion-instrument analysis assigns possible fusion-level actions to the record; the Stim circuit then determines their QEC detector and logical effects. Keep ambiguous or non-stabilizer outcomes explicit. Do not classify an optical record as a QEC hyperedge before that propagation.

Do not automatically convert every loss or multiphoton event into a hyperedge. It becomes a hyperedge only when the compiled circuit demonstrates that one cause creates a support of three or more QEC detector events. A mechanism whose effective support is pairwise remains an MWPM edge or a located erasure.

## Observable metadata contract

The trigger receives a compact record for each fusion:

$$
r_i=(\text{output-mode click pattern},
\text{ PNR counts},
\Delta t,
\text{ declared fusion outcome},
\text{ source herald},
\text{ route ID},
\text{ detector-health flags}).
$$

| Metadata | Mechanism it helps separate | Important limitation |
|---|---|---|
| Full output-mode click pattern | Conclusive fusion, ordinary failure, anomalous events | Must retain more information than a success/failure label. |
| PNR count per output | Loss versus excess-photon contamination | Inefficiency can make multiphoton events appear ordinary. |
| Relative arrival time $\Delta t$ | Timing mismatch and partial distinguishability | Evidence only; not a direct measurement of a wrong logical outcome. |
| Source-generation herald | Source failure versus downstream loss | Available only in compatible source architectures. |
| Route/switch identity | Location-specific loss prior | Usually control metadata, not proof per shot. |
| Detector dead-time, afterpulse, and dark-count flags | Detector artifacts | Requires actual hardware characterization. |
| Local QEC syndrome neighborhood | Whether the physical hypothesis explains several observed defects | Must be available without hidden physical truth. |

Separate per-event evidence from slow calibration context. A measured HOM visibility should set an error prior for a device/run unless a concrete per-event proxy, such as timing residual, is measured. The trigger must never claim per-shot knowledge that the hardware does not expose.

## Posterior trigger and decoder action

At candidate region $R$, compare:

$$
H_0=\text{no relevant fault},\qquad
H_G=\text{ordinary graphlike fault},\qquad
H_F=\text{correlated fusion fault}.
$$

With local syndrome $Y_R$, compute the syndrome-only posterior:

$$
P(H\mid Y_R)=
\frac{P(Y_R\mid H)P(H)}{\sum_{H'}P(Y_R\mid H')P(H')}.
$$

When an independently measured local record $M_R$ has a validated likelihood model, also compute:

$$
P(H\mid M_R,Y_R)
=
\frac{P(M_R,Y_R\mid H)P(H)}
{\sum_{H'}P(M_R,Y_R\mid H')P(H')}.
$$

For each arm, activate refinement only when its own posterior odds exceed its development-locked threshold. Set $Z_R=Y_R$ for the syndrome-only arm or $Z_R=(M_R,Y_R)$ for the metadata arm:

$$
\log\frac{P(H_F\mid Z_R)}
{P(H_0\mid Z_R)+P(H_G\mid Z_R)}
>\tau_{\mathrm{arm}}.
$$

After activation, use the posterior distribution over allowed correlated supports to choose a bounded local factor-graph or exact-MAP refinement. A useful trigger should prioritize regions where refinement can change the logical decision or reduce expected logical risk relative to the baseline; a high fault posterior alone is insufficient. If no correlated hypothesis clears the threshold, preserve the region for calibrated MWPM. Multiple simultaneous faults can cancel detector bits, so a visual count of fired checks is not itself a hyperedge label.

The required trigger output is a posterior over no relevant fault, graphlike explanations, each *validated* higher-order mechanism, and an ambiguous class. Do not reserve positive probability for a loss or multiphoton hyperedge unless its physical action and detector support have been derived. Store the selected action, score, threshold version, and controlled fallback state with that posterior.

## Why the posterior does not defeat selective decoding

Posterior inference is cheap if the expensive physics is moved offline. For a fixed small mechanism set, precompute:

$$
\ell_{c,r,y}=\log P(r,y\mid c).
$$

Online scoring then requires only table lookups, additions, and a small normalization. The syndrome-only table marginalizes over records, $P(y\mid c)=\sum_r P(r,y\mid c)$; the metadata table retains only measured $r$. Candidate generation is a local support-overlap test. Both operations are $O(N)$ over fusion sites with a small constant factor.

The expensive work is reserved for activated fraction $q$ of sites. Cap each merged refinement region at $k$ variables and record fallbacks:

```text
all sites:          local candidate test + small posterior lookup
activated regions:  bounded exact/hypergraph refinement
remaining lattice:  calibrated MWPM
```

Measure $q$, region-size distribution, mean latency, p95/p99 latency, and fallback frequency for each arm. If either arm requires $q$ near one or regions routinely exceed the cap, it has failed the selective-compute premise even if logical error improves.

## Controls and benchmarks

Run all methods on identical immutable event-level shots:

| Method | Purpose |
|---|---|
| Calibrated MWPM | Primary baseline for no-fault, pairwise, and calibrated erasure information. |
| Metadata-conditioned MWPM | Determines whether metadata helps without hypergraph structure. |
| Selective hybrid with syndrome-only trigger | Tests the primary syndrome-driven hypothesis without fusion metadata. |
| Selective hybrid with physical metadata trigger | Tests the incremental value of measured fusion metadata. |
| Global/full hypergraph reference | Measures retained benefit versus full higher-order inference. |
| Oracle trigger and oracle local inference | Simulator-only correctness ceiling; never deployable. |

Before a paper-level claim, add the strongest available calibrated correlated-MWPM-family control using the same observable information. A win over a pairwise projection alone shows that the projection loses information; it does not establish superiority over all matching-based decoders.

## Validation stages and gates

### Stage 0 — specify before coding

Select one fusion primitive, resource state, detector model, and source model. Define the raw measurement record and online-observable fields. Separately specify the stabilizer fusion network, its check parities, logical observable, and the proposed optical-record-to-fusion-action interface. Freeze the outcome taxonomy before fitting trigger thresholds; Stim-derived detector supports are not inputs to the optical model.

### Stage 1 — optical primitive validation

Verify ideal limits, loss limits, probability normalization, PNR behavior, and Fock-cutoff convergence. Cross-check simple cases analytically or with independent Monte Carlo. No QEC claim is allowed at this stage.

### Stage 2 — short-network compiler validation

Run the 3–4-layer benchmark and enumerate fusion-level actions. Propagate each representable action through the annotated Stim circuit and enumerate its detector/logical supports. Verify that every claimed hyperedge has both a demonstrated common physical cause and a Stim-derived support of at least three detectors; each record must be mapped, flagged ambiguous, or explicitly excluded.

### Stage 3 — global higher-order decoder validation; trigger development afterward

First fit physically justified higher-order likelihoods on development data and validate the global/bounded exact decoder against explicit small-region enumeration. Compare its held-out accuracy with equally informed calibrated MWPM and correlation-aware matching. If the higher-order explanation helps, use a separate development/tuning split to choose locked thresholds for syndrome-only and metadata-assisted *selective* arms, plus a candidate radius and region cap. Optimize a predeclared selector objective:

$$
\mathcal L(\tau)=
c_{\mathrm{miss}}P(\text{missed correlated fault})+
c_{\mathrm{false}}P(\text{false activation})+
c_{\mathrm{latency}}E[\text{refined regions}].
$$

Lock all choices before the final architecture-sweep logical evaluation. The physical sweep grid itself is not selected by this objective.

### Stage 4 — complete held-out physical and decoder sweep

For U and B, execute every predeclared physical grid cell and every applicable decoder/record arm. The core grid crosses per-photon loss with correlated-fault incidence; separately declared stress panels cover source multiphoton parameter $p_2$, overlap $\mu$, detector efficiency, timing uncertainty, and metadata degradation. Report Wilson intervals for logical failure, paired intervals for decoder differences on identical within-architecture shots, and cost–reliability curves. Do not select a favorable physical subrange after seeing results.

### Stage 5 — robustness

Test likelihood miscalibration, missing PNR data, imperfect heralds, shifted supports, higher overlap density, and out-of-distribution parameters. Ablate each metadata field. A gain that requires perfect synthetic PNR, timing, or truth-derived labels does not survive this gate.

## Success, pause, and stop criteria

For the new architecture comparison, proceed to a larger-code study if a physically justified multi-detector event exists, the bounded memory and optical-action maps validate, and a locked hypergraph decoder shows either a resolved logical benefit over equally informed matching **within an architecture** or a clearly measured near miss with a plausible resource-cost advantage. Report a near miss as an exploratory research result, not as proven decoder or hardware superiority. If no validated hyperedge exists, change the mechanism or resource preparation before scaling; if the ancilla-free circuit loses too many indispensable parity outcomes, identify that information limit rather than tuning an error rate to hide it.

For the later **selective** decoder, continue to a physically derived larger-code deployment study only if the locked selective decoder:

1. improves on the strongest calibrated MWPM baseline in the predeclared operating region with paired uncertainty excluding zero;
2. retains a material fraction of the global-hypergraph reference benefit;
3. has calibrated trigger probabilities, acceptable miss rate, and bounded false activation;
4. activates a meaningfully small fraction of bounded regions; and
5. remains beneficial under held-out physical parameters and metadata degradation.

Pause or stop if calibrated MWPM removes the gain, the trigger cannot distinguish mechanisms beyond chance, useful metadata is not physically available online, or activation becomes dense enough that global higher-order inference would be comparably appropriate.

## Phase 0 — Small-scale go/no-go feasibility test

### Purpose and boundary

Phase 0 is a deliberately small falsification test. Before committing to the $d=5$ effective-channel study, it asks:

> Do characterized ancilla-free and boosted encoded fusions admit a common-cause multi-detector action, and does **global or exact bounded hypergraph inference** improve logical recovery over equally informed matching on a bounded memory? A separate comparison asks how close the ancilla-free system comes to the boosted system at lower resource cost.

An optical primitive or periodic check proxy alone does not test native FBQC, hardware, an asymptotic threshold, or a publication-level decoder advantage. The new architecture study requires a bounded memory with a declared logical observable. A validated hyperedge and an accuracy gain authorize studying a selective trigger; the $d=5$ transition additionally requires the full optical-action and bounded-memory gates described below. A negative result is reported for the tested mechanism and operating range, not silently redefined as a favorable parameter search.

### Minimal scope

First run a local **information and architecture gate** on one specified dual-rail fusion primitive: conserve optical probability, check the obtainable parity bits, and establish that a proposed network has enough measurable checks to justify the full decoder experiment. If it passes, use a **connected** two-fusion resource-state chain with an intermediate outcome and a downstream fusion, then a bounded six-ring memory. Begin with ideal operation, photon loss, and multiphoton emission. Add partial distinguishability after this three-class model passes validation. Two disconnected beamsplitter/PNR gates that share only a source-state label are an optical observability control, not this required chain.

The observable record contains the full output-mode click pattern, PNR count bins, an available source herald, and local detector syndrome. Include timing only if the model produces an actual measurable timing proxy. First compile the optical table

$$
P(A,R\mid c,\theta),
$$

where $c$ is a simulator-only mechanism, $R$ is the observable record, and $A$ is a justified fusion-level action. The same $R$ may remain compatible with several actions. Use an explicit ambiguous class whenever the optical model does not justify a stabilizer action. Compose this table with the Stim-derived action map to obtain $P(E,R\mid\theta)$, where $E$ includes detector support, logical effect, and any located erasure/check mask. A physical mechanism becomes a hyperedge only if the connected circuit demonstrates one common cause and the code circuit shows that its one action flips at least three detectors.

### Phase 0 Stim procedure and gate

1. Define the ideal two-fusion stabilizer circuit: resource-state preparation, the measured fusion parities (for example $XX$ and $ZZ$ when appropriate to the selected primitive), intermediate feedforward/Pauli-frame rule, downstream fusion, and final readout. Annotate its deterministic check parities as Stim `DETECTOR`s and its tracked logical parity as `OBSERVABLE_INCLUDE`. Test that the noiseless circuit has no detection events and that the declared checks are deterministic rather than gauge outcomes.
2. For each optical action $A$, state the exact perturbation of that circuit: which reported fusion-result bit changes, which Pauli/frame action occurs, or which outcome is erased. Do not treat a missing photon as an automatic Pauli error. Keep physically ambiguous and non-stabilizer leakage outcomes outside the claimed support table until their behavior is justified.
3. Insert one representable action at a time at its actual fusion location. Use Stim to calculate the changed detector set $D$ and logical bit $L$, or calculate measurement-bit effects from the circuit-derived parity matrix and cross-check by Stim sampling. Inspect the undecomposed detector error model. Repeat at the source/shared-resource location to test whether one cause affects both fusion measurements and produces at least three detector events.
4. Preserve a traceable row $(c,R,A,\text{location},D,L,\text{erasure/check mask})$ and compare the generated support with direct fault-injected shots. A multi-detector row is valid only if its optical cause, fusion action, and code response are all documented. If the small chain has no defined deterministic detectors, extend or change the named stabilizer circuit before claiming a surface-code hyperedge; do not add abstract detector nodes to force the test.

Only after this gate passes, decode the resulting small detector circuit with pairwise and any validated three- or four-detector supports. The Phase 0 circuit is a controlled representation test, not a $d=5$ or hardware claim. If all justified effects are pairwise or located erasures, the higher-order hypothesis is no-go **for this primitive** and the project must not proceed to the $d=5$ selector benchmark on invented hyperedges.

### Required controls

These controls apply to the architecture comparison. Trigger-specific controls become decision gates only after global higher-order decoding shows a held-out accuracy gain.

All decoders use identical immutable shots. Physical mechanism labels are stored only in an audit dataset and never passed to the proposed trigger.

| Control | Required result |
|---|---|
| Ideal-source, no-correlated-event limit | No systematic correlated-fault activation. |
| Pure-loss limit | Missing-photon records map to the declared erasure/loss event. |
| Elevated multiphoton limit | Measure excess-photon records and test whether any justified fusion action produces a Stim-derived correlated support; do not assume one exists. |
| Metadata-shuffled control | Tests whether metadata adds value beyond priors and syndrome geometry; applies to the metadata arm. |
| Syndrome-only trigger | Tests whether syndrome structure alone selects useful refinement regions. |
| Metadata-conditioned MWPM | Ensures the comparison gives both relevant methods the same observables. |
| Global hypergraph or exact local-MAP reference | Establishes available higher-order benefit and validates refinement. |
| Oracle trigger | Audit-only implementation ceiling, never deployable evidence. |

### Data separation and measurements

Generate deterministic development, threshold-tuning, and held-out datasets from the frozen table. They use non-overlapping seeds; the held-out set also contains at least one unseen physical parameter setting. Use stratified audit data for mechanism recall/precision, but use realistic-prior mixtures for logical-error evaluation. Never present an enriched classifier sample as a logical-error benchmark.

Validate probability conservation, Fock-cutoff convergence, and analytic ideal/pure-loss limits. For each arm, measure trigger recall, precision, activation fraction $q$, posterior calibration, and Brier score; mark recall/precision undefined when the evaluated physical table has no positive hyperedge cases. Measure logical failure, 95% Wilson intervals, paired bootstrap intervals against an equally informed calibrated MWPM-family baseline for each arm, parity consistency, fallbacks, and CPU-only timing for candidate scoring, refinement, and MWPM.

Choose the selector threshold on tuning data only by a frozen objective:

$$
\mathcal L(\tau)=
c_{\mathrm{miss}}P(\text{missed correlated fault})+
c_{\mathrm{false}}P(\text{false activation})+
c_{\mathrm{latency}}E[\text{refined regions}].
$$

Copy the selected threshold unchanged into the held-out run.

### Predeclared decision

Before executing the held-out test, freeze the bounded-memory circuit, source-calibrated physical channel, declared parameter grid, baseline implementations, decoder settings, shot budget or uniform precision rule, and interpretation of unsupported events. For the later selective study, additionally freeze numerical definitions for maximum activation fraction, acceptable fallback rate, and required fraction of global-hypergraph gain. These are engineering targets, not universal physical constants.

**Go to a native $d=5$ architecture comparison** only if the physical tables are normalized and validated for both circuits; the bounded six-ring check, boundary, and logical maps agree with fault-injected Stim shots; at least one physically justified common-cause action has a retained support of three or more detectors; and the held-out bounded-memory study resolves a hypergraph accuracy gain over an equally informed matching baseline or produces a sufficiently informative, quantified cost–accuracy near miss to justify the larger test. If the bounded result is a near miss, label the $d=5$ continuation exploratory and retain the unchanged full-grid reporting rule. The selective-compute claim has its own later gate: after global hypergraph accuracy gain, a separately locked selector must retain useful benefit with acceptably sparse activation. A metadata-assisted claim additionally requires observed metadata to add value over a shuffled-record control; syndrome-only success needs no informative optional metadata.

**Pause and repair** if the physical table is not converged, the fusion action or Stim check map is undefined, an action needs an ambiguity channel, local exact-MAP disagrees with refinement, or uncertainty is too wide for a decision. State the repair target precisely: circuit model, detector POVM, fusion instrument, check/logical definition, calibration, or shot budget. An optical classifier result alone cannot pass this gate.

**No-go for a metadata field** if its arm performs no better than shuffled metadata or the syndrome-only arm. **No-go for hypergraph advantage on the tested event model** if there is no validated higher-order support or a strong calibrated matching decoder removes its logical advantage throughout the predeclared grid. **No-go for selective compute on that model** if useful accuracy requires activating almost every candidate region. These are distinct conclusions. Preserve the compiler, bounded-memory circuit, and all negative grid results; change the physical mechanism or architecture before retesting an absent support.

### Literature-informed restart — 2026-09-26

The founding [FBQC paper](https://www.nature.com/articles/s41467-023-36493-1) derives the six-ring outcome-to-check map and explicitly identifies correlated errors between a fusion's $XX$ and $ZZ$ outcomes as information unused by its separately decoded graphs. [Experimental boosted Bell measurements](https://www.nature.com/articles/s41534-025-00986-2) show how to retain raw click patterns and connect them to an encoded six-ring simulation. [Temporal fusion measurements](https://www.nature.com/articles/s41467-025-62130-0) show why the conditional state left by each outcome must be characterized, not inferred from count labels alone. [Syndrome-based hypergraph estimation](https://arxiv.org/abs/2504.20212) can calibrate candidate event probabilities across repeated runs, but cannot recover an unmeasured parity on one shot. [Belief-matching](https://arxiv.org/abs/2203.04948) demonstrates a downstream gain from a sufficiently informative correlated circuit model, without supplying the missing optical model for this architecture.

The restarted Phase 0 uses the existing four-mode six-ring port instrument, its raw PNR records, and the Stim-derived six-ring checks. It discards the unrelated resource-code proxy. The optical output must be an *operation-conditioned* table $P(R,A\mid c,\theta)$, not merely a posterior over ideal Bell branches. For each full, partial, short, and excess record, characterize the surviving-reference density operator or equivalent quantum instrument, verify whether its action is representable as a known parity, noisy parity, erasure, or leakage, and retain unresolved actions explicitly. Measure or justify the incidence of each physical cause. A Bell-basis diagonal extracted from a density operator is a useful diagnostic, but is not by itself proof that an arbitrary nonconclusive fusion acted as a sampled Pauli error.

Propagate each justified action through a **bounded six-ring memory with boundaries and a declared logical observable**. Stim supplies detector and logical signatures for representable faults; erased outcomes require the corresponding check-mask/supercheck construction. Cross-check the resulting candidate hyperedge probabilities against repeated syndrome correlations. Only after optical action, check availability, and architecture success gates pass should locked held-out logical comparisons run: equally informed erasure-aware MWPM, correlated matching/belief-matching, and local or exact hypergraph inference. Report paired uncertainty and an ablation of raw PNR detail. The unencoded 50%-success Bell primitive must not be treated as viable merely because a conclusive event has a four-check signature; boosting or encoding changes the instrument and requires its own calibration.

The runnable restart entry point is `phase0/restart_phase0.py`. Its **first gate** exhaustively checks the small optical instrument, verifies Stim's single-fault signatures, and measures how many local checks remain under actual ideal fusion outcome classes. If that gate fails, the decoder benchmark is deliberately not entered and the decision is no-go for the current unboosted architecture. A later boosted/encoded Phase 0 is a new architecture experiment rather than a retune of the same decoder.

The [restarted Phase 0 result](phase0/RESULTS.md) records the optical, Stim, and information gates. The periodic six-ring bulk has a four-check signature for a hypothetical joint $XX/ZZ$ flip, but the specified extra-plus-photon accepted records are Bell coherent and do not justify assigning that signature a stochastic source rate. The present unboosted architecture also has too little usable check information for the required bounded-memory decoder comparison. Preserve the optical instrument and rerun only with a characterized boosted or encoded source and its complete action map.

### Encoded, boosted architecture trial — 2026-09-26

Use the [experimentally demonstrated boosted Bell measurement](https://www.nature.com/articles/s41534-025-00986-2) with an ancillary Bell pair and its reported 69.3% complete physical-Bell discrimination, then the paper's four-physical-fusion $(2,2)$-Shor encoded six-ring arrangement. A/C fusion failures retain $XX$; B/D failures retain $ZZ$. From the encoded stabilizers, logical $XX$ has two physical reconstructions and logical $ZZ$ is recovered unless both A and C fail in the no-loss limit, so the encoded fusion-failure probability is $p_{\mathrm{fail,physical}}^2$. Include independent survival of all four photons entering each boosted physical measurement; evaluate both 95% and 99.5% per-photon efficiency. The paper reports a 1.4% photon-loss threshold for its measured boosted encoded architecture, so 95% detection is a deliberate adverse sensitivity case, not a plausible operating point under its assumptions.

The [encoded trial code](phase0/run_encoded_phase0.py) uses the published encoded parity-availability rule and the existing Stim six-ring checks. It retains three deployable metadata levels: encoded parity availability; disagreement between redundant physical parity reconstructions; and the four physical full/partial/lost outcome classes. These are classical functions of already measured physical-fusion outcomes and do not touch surviving qubits. Compare erasure-contracted MWPM with independent calibrated $XX/ZZ$ marginals against joint four-state belief propagation followed by the same matching step, for every metadata level, on identical held-out shots. Train local likelihood tables separately from held-out evaluation. Count a nonlocal parity sector that cannot be deformed around erased outcomes as a block failure; report that fraction separately. The periodic sectors are a **proxy**, not a bounded-memory logical error rate.

The boosted paper supplies a measured *average success rate and architecture*, not a calibrated action-conditioned channel for our mode-matched extra-photon fault. Its reported correct-identification rates also differ substantially across the four Bell branches, and the measurement-discrimination fidelity is not an equivalent per-parity Pauli error rate. Therefore independent physical-parity flips and a joint A-fusion flip in this trial are explicit sensitivity assumptions. Test a held-out lower-efficiency/higher-fault setting and a separate branch-conditioned-success setting using the paper's four published correct-identification probabilities; the latter is a sensitivity translation, not a reconstruction of raw click patterns. The trial can determine whether the encoded record and redundancy flags make correlated decoding useful in this declared model. It cannot pass the physical Phase 0 go gate until raw four-photon click-pattern likelihoods and conditional postfusion actions are measured or derived, a bounded logical memory is implemented, and the same comparison survives realistic source calibration. Keep any positive proxy outcome separate from a physical go decision.

The completed [encoded Phase 0 result](phase0/ENCODED_RESULTS.md) uses 12,000 training shots and 3,000 independent held-out shots per setting. At 99.5% photon efficiency, both logical parities are available for 88.19% of encoded fusions, and the equally informed metadata-aware MWPM and joint-BP-plus-MWPM sector-failure proxies are 14.43% and 13.27%, respectively; the paired gain is 1.17 percentage points (95% bootstrap interval 0.57–1.73). The gain survives a shifted lower-efficiency/higher-fault holdout and a Bell-branch-conditioned success sensitivity arm. It disappears when the joint fault is set to zero. At 95% photon efficiency, 98.93% of diagnostic-sector shots are erased, so no decoder is useful. The principal benefit is the redundant physical parity metadata, which cuts the 99.5% MWPM proxy from 31.50% using encoded availability alone to 14.43% with all measured classes and disagreement flags. An additional fresh holdout with a fixed disagreement-triggered selector keeps most of the joint-decoder gain but activates on 60.87% of shots and remains about seven times slower than metadata-aware MWPM in this implementation. **Decision: go to boosted/encoded optical calibration; no-go for the current sparse selective-compute claim, a physical $d=5$ hypergraph claim, or decoder deployment on this proxy.**

### Optical-derived bounded $d=3$ follow-up — 2026-09-26

The [bounded follow-up](phase0/BOUNDED_OPTICAL_D3_RESULTS.md) derives ideal boosted four-photon PNR probabilities directly from the published 4×4 unitary and tests a specified ancilla $Z$ fault, which changes $|\Phi^+\rangle$ to $|\Phi^-\rangle$. Unlike the earlier sensitivity flips, the conditional conclusive outcome action is derived from the optical model: it flips one Bell parity on the affected $\Phi$ branch, not both. Four such physical outcomes are reconstructed into one encoded fusion. A declared teleportation-frame adapter then injects the encoded error into a three-round bounded Stim rotated $d=3$ memory; this is a conventional surface-code proxy, **not** a native bounded six-ring memory. The assumed fault incidence is swept; ideal PNR and perfect indistinguishability differ from the measured experiment. Unknown partial-outcome back-action is conservatively represented by a randomized missing frame bit, so its full quantum instrument remains an open validation item.

The derived raw PNR distribution is identical with and without this fault under a uniform Bell input, so a lone click record cannot herald it; encoded redundancy can supply disagreement flags. In a 20,000-shot held-out 2% fault-incidence setting, availability-only MWPM, equally informed metadata-aware MWPM, and metadata-aware joint BP plus MWPM have Z-memory failure rates 0.810%, 0.350%, and 0.325%, respectively. The paired gain for the joint decoder over metadata-aware MWPM is 0.025 percentage points (95% bootstrap interval −0.005 to +0.055); it is unresolved. Every derived encoded error is single-axis and graphlike. **Decision: no-go for this ancilla-phase mechanism as the proposed useful hyperedge; retain metadata-aware MWPM as the baseline.** The overall hypergraph question remains open for a *different* physically characterized fault. The current extra-photon candidates require a coherent-action treatment or a justified physical reduction before any Pauli hyperedge benchmark. Resume only by deriving or measuring their raw-record-conditioned postfusion action and incidence, and by evaluating them in a native bounded encoded six-ring memory. Do not translate an out-of-qubit-sector count anomaly to a Pauli action without that instrument.

An additional [five-photon optical audit](outputs/phase0_bounded_optical_d3/excess_audit.json) injects a specified extra mode-matched photon before the boosted multiport. Ideal PNR flags all five-count records. With assumed 99.5% independent detection efficiency, one lost count produces an apparent conclusive four-count record in 1.593% of *extra-photon events*. Its conditional Bell-basis Gram matrix has nonzero off-diagonal terms, so that record cannot be compiled as a sampled Pauli fault or hyperedge by count classification alone. This is a conditional fault diagnostic, not a measured source-incidence rate or a complete trace-preserving instrument. The remaining repair target is explicit: characterize the source fault and surviving-reference state through the bounded encoded resource, including non-Pauli actions or a justified reduction to stabilizer faults. Until that exists, no valid extra-photon logical decoder comparison can be claimed.

## Next study: ancilla-free hypergraph decoding versus boosted matching

### Objective, evidence, and separate claims

The [ancilla-free joint-MAP proxy](phase0/ANCILLA_FREE_DECODER_PROXY_RESULTS.md) is an intermediate sensitivity result: on an assumed 0.5% encoded joint-fault channel with branch-dependent ideal two-photon BSM classes, global configuration MAP has a held-out 1.18-percentage-point periodic-sector gain over equally informed MWPM, but 73.82% of shots have an undeformable sector. The optional disagreement flags have no resolved greater benefit for MAP than for MWPM, and the locked selector activates on about 67.8% of measurable nominal shots. This does not pass the optical-action or native bounded-memory gates below; retain those gates before any physical or logical advantage claim.

The stretch objective is an **ancilla-free encoded fusion network decoded by a real hypergraph method** that both improves logical recovery on its own circuit and reaches competitive logical reliability at lower physical cost than a boosted, metadata-aware MWPM system. A result that is close to the boosted reference at substantially lower cost is scientifically useful even when it is not a logical-error win. Report the gap directly; do not relabel a near miss as an advantage.

There are three different claims, and the experiment must not conflate them:

1. **Decoder claim:** on the same ancilla-free circuit and identical held-out shots, a hypergraph decoder improves logical failure over equally informed, fully calibrated MWPM and a strong correlation-aware matching control. This isolates the use of retained multi-detector fault mechanisms.
2. **System claim:** at the same physical operating conditions and a predeclared target logical reliability, ancilla-free hypergraph decoding uses fewer expected physical resources than the best boosted reference. This comparison includes any larger code distance, retries, resource-state generation overhead, and decoder cost needed by either architecture.
3. **Stretch claim:** at equal code distance and physical conditions, ancilla-free hypergraph decoding also beats boosted metadata-aware MWPM in logical failure. This would be unusually strong; its absence does not erase a valid within-architecture decoder gain or a measured cost–reliability tradeoff.

The [boosted BSM experiment](https://arxiv.org/html/2410.16380) reports 69.3% average full Bell discrimination with an ancillary pair and 49.05% for its unboosted comparison. Its **encoded six-ring, fixed-success, erasure-based simulations** report photon-loss thresholds of 1.4% and 0.45%, respectively. These are context for a broad sweep, not thresholds already established for this project's full correlated-noise model or decoder. The [FBQC framework](https://arxiv.org/html/2101.09310) identifies correlations between a fusion's $XX$ and $ZZ$ results as information that separately decoded syndrome graphs leave unused. Neither source proves that a hypergraph decoder can replace the missing Bell information or ancillary photons.

### Architecture and record matrix

Keep the same $(2,2)$-Shor encoded six-ring resource, fusion placement, finite boundaries, memory duration, logical observable, and physical input-loss conditions in the primary comparison. Change the BSM implementation and its validated optical instrument. The *ancilla-free* label means no separate Bell-pair photons supplied to **each physical BSM**; the encoded resource photons, source preparation, and detection hardware still count. If the two optical encodings differ (path dual-rail versus polarization rails), specify the mode mapping and price the actual chosen hardware rather than declaring them cost-equivalent by notation.

| Architecture | Physical BSM | Optical inputs per physical BSM | Encoded fusion and primary risk |
|---|---|---:|---|
| U: ancilla-free | Standard two-photon Bell analyzer | Two data photons, zero BSM-ancilla photons | Four physical BSMs per encoded fusion; more partial outcomes may leave insufficient checks. |
| B: boosted | Four-photon Bell analyzer | Two data photons plus one ancillary Bell pair | Same encoded fusion; more complete outcomes, but ancilla generation, loss, detectors, and optical complexity have costs. |

The ideal, independent, zero-loss formula $1-(1-p_c)^2$ gives both encoded parities at $75\%$ for $p_c=0.5$ and $93.75\%$ for $p_c=0.75$. These are **availability calculations only**. Branch-specific successes, source faults, loss, encoded stabilizer reconstruction, and finite-memory decoding must be simulated or measured; the ideal percentages are not logical error rates or cost estimates.

Both architectures retain their standard observable record: syndrome, which fusion parity bits are known, which are absent, and the associated heralded check/erasure mask. A decoder cannot be made artificially weak by hiding a known erasure. Define two *optional-detail* record levels for each architecture:

| Record level | Decoder-visible fields | Hardware interpretation |
|---|---|---|
| Core | Syndrome, encoded $XX/ZZ$ values when known, conclusive/partial/lost status, locations and check masks | Required information from the selected fusion measurement; supplied to every decoder. |
| Detailed | Core plus raw PNR pattern, source heralds if physically present, and disagreement among already measured redundant physical parities | Supply exactly the fields that the selected hardware can produce online. If obtaining detail needs more PNR channels or electronics, add those costs. |

Run the same decoder families at both record levels on each architecture. There is no dedicated “ancilla-only metadata”: raw click patterns and encoded redundancy may also exist without a BSM ancilla. Do not give boosted MWPM detailed records while depriving the ancilla-free hypergraph of its own available details, or vice versa, in a **within-architecture** decoder claim. The cross-architecture system comparison may legitimately use each design's best physically available record level, with its extra detector/electronics cost included.

### Fault channel and hyperedge admission gate

For U and B independently, derive or calibrate $P(R,A\mid\theta,\text{architecture})$ from a named source and optical circuit. Include ideal fusion success/failure, photon loss, detector inefficiency, resource-preparation errors, and at least one physically motivated *single common cause* that may affect both $XX$ and $ZZ$ or several neighboring fusion outcomes. A stochastic Pauli $Y$ on a physical resource photon is an algebraic candidate because it anticommutes with both ideal fusion parities; in an **encoded** fusion, redundancy may absorb that physical fault, so its logical action and rate must be derived rather than copied from an unencoded check map. A source fault involving several photons is another candidate only after its source mechanism and incidence are specified. The previous five-photon count-alias audit remains an ambiguous/non-Pauli channel until its conditional surviving-state action is justified.

For each representable action and location, inject it into a **native bounded encoded six-ring memory** with a declared boundary and logical observable. Stim supplies $(D,L)$ for stabilizer-representable faults; optical modeling supplies the record/action likelihood. Preserve an undecomposed common-cause event when $|D|\geq3$. Missing parity outcomes require actual unavailable-check masks or superchecks. A record with unresolved coherent or leakage back-action remains explicitly unsupported and contributes to a coverage report; do not silently map it to $X$, $Y$, $Z$, or an erasure. Compare inferred higher-order event probabilities with direct fault-injected samples and repeated-syndrome correlations before claiming the hyperedge is physically grounded. A four-check pattern in the earlier periodic bulk is an existence check, not this bounded encoded-memory gate.

### Decoder matrix and what constitutes a fair win

The core matrix is $\{U,B\}\times\{\text{core},\text{detailed}\}\times\{\text{MWPM},\text{hypergraph}\}$. Add the strongest available **correlation-aware matching/belief-matching** control at the same record level, plus a small-region exact-MAP reference and an audit-only oracle. MWPM gets calibrated, record-conditional graph weights and erasure-aware check treatment; it is not intentionally restricted to uniform weights. The hypergraph arm keeps each justified common-cause multi-detector event as one factor with a likelihood fitted on training data. On bounded regions, compare its decisions with exact enumeration; do not call ordinary BP followed by graph matching an exact hypergraph decoder.

First run **global or bounded exact** higher-order inference. Establish whether full use of the joint fault model improves held-out logical decisions at all. Only then tune a local selector on a separate development/tuning split and measure whether it retains the accuracy gain at lower classical latency. If the global hypergraph fails to beat equally informed strong matching, changing a trigger threshold cannot rescue the physical hypothesis. If global inference helps but selection is dense, report the accuracy gain and the classical-cost limitation separately.

Within an architecture, every decoder processes the same immutable generated shots and the same versioned optical table. Across architectures, use matched physical parameter values and, where possible, coupled random source/loss draws for variance reduction, but preserve the different numbers of photons and outcome distributions. Do not equate two differently generated shot indices with the same physical event. Mechanism truth, hidden photon number before loss, and simulated Pauli labels remain audit-only.

### Predeclared full sweep, with no favorable-rate selection

The **physical** parameters are experimental axes, not knobs to optimize against logical-error outcomes. After validating the two optical instruments but **before viewing held-out logical results**, save a versioned sweep manifest containing the complete grid, source of each parameter, circuit/table revisions, decoder revision, seeds, shot-count/precision rule, cost assumptions, and primary target reliabilities. The initial planned per-photon loss axis is $0,0.1,0.2,\ldots,2.0,3.0,5.0\%$ for **both** architectures. It spans low loss, both published threshold neighborhoods, and adverse high loss. This axis can be revised for physical relevance only before the held-out benchmark and with the revision recorded; it cannot be shortened after observing an unfavorable curve.

Cross that loss axis with a predeclared correlated-fault axis. If an independent calibration provides a nominal incidence $p_0$, use $\{0,0.5p_0,p_0,2p_0\}$ as the primary stress levels and record any physically allowed cap. If no incidence has been validated, use an explicitly **sensitivity-only** absolute grid such as $\{0,0.1,0.25,0.5,1,2\}\%$; none of those points alone licenses a device claim. Complete the Cartesian product for the core optical model and both architectures, including zero-correlation and pure-loss controls. Predeclare separate detector-efficiency, source-herald quality, distinguishability, and calibration-shift stress panels; report every point in each declared panel. This is a finite, complete study grid, not a claim to sample every value in a continuum.

Tune only *decoder* weights, inference settings, and selector thresholds on development/tuning data; freeze them or freeze a training-only calibration rule **before** the held-out grid. A decoder may read the physical calibration corresponding to the operating point if that calibration would be available in deployment, and both competing decoders receive the same calibration context. It may not choose, remove, or relabel physical test points according to which one gives its best logical error. Any additional exploratory point is appended with an exploratory tag; it cannot replace a predefined cell. Retain a separate held-out parameter-shift panel to test whether the fitted channel transfers beyond the nominal training condition.

Use a common predeclared minimum shot count and a uniform precision-extension rule applied to **all** cells that meet the same uncertainty criterion, with a recorded maximum budget. This avoids spending extra shots only where the hypergraph appears promising. Store failures and denominators even when no failures are observed; report Wilson intervals rather than interpreting zero observed failures as zero error. Mark a cell inconclusive when the precision cap is reached. Preserve failed or unsupported circuit points as explicit outcomes with reasons, never as missing rows removed from the plot.

### Logical, statistical, and resource outputs

For every grid point, architecture, record level, decoder, and code size, publish the logical failure count/rate and interval; available-$XX$, available-$ZZ$, and both-available fractions; erasure/check-mask and ambiguous-event fractions; hyperedge incidence and overlap; decoder runtime/activation/fallback if applicable; and the parameter/table/circuit versions. On identical shots within each architecture, publish paired hypergraph-minus-MWPM differences with 95% intervals and discordant-shot counts. Show full loss and correlation-rate curves, not only the best point. If a standout point is claimed after scanning many cells, use a predeclared primary contrast or multiple-comparison-aware uncertainty; ordinary pointwise 95% intervals do not validate the most favorable point selected post hoc.

Keep two related system views: (a) logical failure at **equal physical conditions and code size**, and (b) resources required to meet each predeclared target logical failure when each architecture may choose its code size. At minimum account for expected data/resource photons attempted, ancillary photons and Bell-pair preparation attempts, preparation and multiplexing yield, detector channels and efficiency, optical depth/components, retry or discarded-block rate, memory duration, and online classical latency. Report a cost **vector** and Pareto frontier instead of inventing a single price for unlike resources. If a scalar cost is useful, publish its weights and uncertainty as a sensitivity analysis. Count the extra encoded photons and larger distances that U may require; “zero BSM ancillas” does not mean “free architecture.” If the tested sizes never meet a target reliability, mark the cost to that target *not established* rather than extrapolating a favorable number.

For a near miss, report $\Delta P_L=P_L(U,\mathrm{hypergraph})-P_L(B,\mathrm{metadata\ MWPM})$ with its interval at matched conditions, the ratio and absolute gap, and the resource-cost difference at matched target reliability. A confidence interval crossing zero is **not** proof of equivalence. If “comparable” is to be used as a formal result, freeze an application-relevant equivalence margin before evaluation and show the whole interval lies within it. Otherwise use descriptive language: the measured gap and its uncertainty. Negative, uncorrectable, unsupported, and near-equal regions remain in the final report and machine-readable output.

### Ordered gates and claim boundaries for the comparison

1. **Local-physics gate:** both optical tables conserve probability and reproduce ideal/pure-loss limits; record-conditioned actions and non-Pauli/ambiguous cases are separated; source-fault incidences have provenance or are sensitivity-only.
2. **Native-memory gate:** a finite encoded six-ring circuit has deterministic checks, explicit boundaries/logical observable, validated erasure handling, and direct Stim agreement for each admitted single-fault $(D,L)$ map.
3. **Hyperedge gate:** at least one single physical cause remains a nontrivial $|D|\geq3$ event after encoding; its likelihood is observable-calibrated or explicitly syndrome-only, and is distinguishable from independent graphlike alternatives at a meaningful incidence. A detector count without an action and rate does not pass.
4. **Decoder gate:** the real higher-order decoder is checked against bounded exact MAP and compared on held-out identical shots with fully calibrated MWPM and correlation-aware matching. This gate may pass for U, B, both, or neither; publish all four outcomes.
5. **Architecture/cost gate:** evaluate the complete predeclared grid and Pareto curves. The ancilla-free system may win outright, offer a quantified near miss at lower cost, lose due to unavailable parity information, or be inconclusive. None of these outcomes authorizes hiding the other regions.
6. **Selective and larger-code gate:** pursue a sparse selector only if global higher-order decoding has a real accuracy gain. Proceed to $d=5$ and beyond with versioned physical tables and new Stim maps, retaining the entire physical sweep and claim boundaries. No bounded proxy or literature threshold is a hardware demonstration.

## Ordered implementation action list

The architecture comparison above supplies the **new bounded-memory prerequisite** for the existing $d=5$ implementation sequence. Complete its local-physics, native-memory, hyperedge, and global-decoder gates for U and B before Step 3 below. A predeclared sweep over *physical loss and fault conditions* is the experiment itself; a sweep over a *selector threshold* is decoder tuning and must use development data only. No large-code performance claim begins until the preceding gate passes. The programs below are deliberately separate: normal decoder deployment must never retune its threshold, regenerate its physical likelihood table, or inspect hidden simulation labels.

### 1. Freeze the shared data contract

- Select the ancilla-free and boosted physical Bell instruments on the **same encoded six-ring resource**, plus a connected small optical benchmark and a native bounded memory. Declare the optical qubit/mode mapping for both instruments. A conventional rotated-code circuit may remain an auxiliary proxy, but cannot replace the native architecture for the cost claim.
- Specify the finite encoded network, fusion schedule, stabilizer checks, boundary, memory duration, logical observable, and location correspondence. Record resource preparation and physical BSM requirements so hardware cost is traceable to the circuit. Extend these definitions to $d=5$ only after the bounded gate.
- Version a shared schema containing architecture ID, physical parameters, source model, raw fusion record, core/detailed observable fields, fusion-level action or ambiguous class, Stim circuit version, fusion-location ID, detector support, logical effect, erasure/check mask, seed, and likelihood-table version. Add a sweep-manifest version and audit-only mechanism label.
- State which metadata are per-event and which are only calibration context. Hidden photon occupations, latent mechanism labels, and simulator truth are prohibited decoder inputs.
- Define an explicit ambiguous/unmodeled event class. Write analytic-limit and unit-test requirements before implementation: ideal source, pure loss, perfect herald, perfect overlap, and normalization.

**Gate:** both physical instruments, the shared schema, native bounded stabilizer circuit, check/logical definitions, and action interfaces are fixed enough that every later program can read and write one event-table format. No detector support is assigned before Stim propagation.

### 2. Implement the small-scale physical compiler first

- Build the local Strawberry Fields Fock model for one fusion primitive, then a two-fusion chain, then the 3–4-layer benchmark.
- For **each** BSM architecture, model source vacuum/single/multiphoton statistics, path loss, detector efficiency, dark counts, timing jitter, and a reduced distinguishability/overlap parameter. Document which imperfections are shared and which arise only from ancilla preparation.
- Retain PNR output patterns and timing-related observable bins. Demonstrate Fock-cutoff convergence and compare simple ideal and loss cases with analytic or independent Monte Carlo calculations.
- Compile the validated optical simulations into a versioned likelihood table:

$$
P(A,R\mid \theta),
$$

where $A$ is a fusion-level action and $R$ is an observable fusion record. Keep multiple possible actions for an ambiguous record instead of inferring a physical mechanism from its appearance alone.
- Build the annotated small Stim circuit and inject each representable action at its actual location. Store the derived detector set, logical effect, and erasure/check mask with circuit and fault provenance. Include zero-, two-, three-, and four-detector supports only when this propagation produces them. Do not invent hyperedges to exercise the decoder.

**Programs:** **build_small_physical_table** creates a separate versioned table for each optical architecture; **derive_small_stim_map** creates the annotated native bounded circuit and architecture-specific fault-to-detector map. Add **audit_bounded_hyperedges** to record physical cause, retained support, logical effect, and unsupported outcomes. Rerun the relevant program when its assumptions, instrument, or stabilizer circuit change.

**Gate:** every optical row is normalized, cutoff-converged, classified, and traceable to the stated model; every claimed detector support is reproduced by one fault in the annotated Stim circuit. Unmapped actions remain explicit. This is local physics and stabilizer-map validation, not a large-code or hardware result.

### 3. Implement deterministic $d=5$ dataset generation after the bounded comparison

- Build and version a fixed $d=5$ stabilizer circuit in Stim, with explicitly declared checks, logical observable, fusion schedule, and boundary behavior. If it is a conventional rotated surface code receiving an effective photonic channel, label it a proxy and document the assumed adapter from fusion actions to code operations. If a native fusion-based claim is intended, use a named fusion network instead.
- Inject each allowed fusion-level action at each modeled location; derive $(D,L,\text{erasure/check mask})$ from the $d=5$ circuit, preserve undecomposed multi-detector mechanisms, and verify sampled fault signatures against that map. No detector or logical support may be copied from the existing periodic surrogate lattice.
- Generate immutable seeded shot shards for **every declared grid cell and both architectures**. Each shot samples an action and raw record from its frozen optical table, applies its Stim-derived effect to the $d=5$ circuit or validated detector model, and stores the resulting syndrome and logical label for scoring. Retain the physical mechanism only in an audit view. Record every generated cell, including unsupported ones, in the sweep manifest.
- Store only observable syndrome and metadata in the deployable dataset view. A separate audit-only view may retain latent labels solely for trigger-calibration diagnostics.
- Generate non-overlapping development, threshold-tuning, and final held-out datasets. Hold out some physical parameter combinations as well as random seeds.

**Programs:** **derive_d5_stim_map** versions the circuit and location/action-to-detector map; **generate_d5_dataset** reads that frozen map and writes immutable datasets and a manifest. Neither tunes a decoder.

**Gate:** the noiseless circuit has the expected deterministic detectors and logical observable; single-fault Stim samples reproduce each declared $(D,L)$; regeneration from the same manifest is identical; ideal, pure-loss, and zero-correlated-event controls behave as expected; erasure masks are handled consistently; no decoder can read audit-only truth.

### 4. Implement the modular decoder; add a selector only after global benefit

- Implement calibrated core- and detailed-record MWPM, the strongest feasible correlation-aware matching control, and a **real global higher-order decoder** on the same event interface for both architectures. Retain one factor for every validated multi-detector common cause; verify bounded cases against exact enumeration.
- Run a locked held-out global-hypergraph versus equally informed matching comparison before investing in trigger design. If there is no accuracy gain, report it and stop selector tuning for that event model.
- Implement local support-overlap candidate generation and separate syndrome-only and metadata-assisted posterior scorers using precomputed likelihood tables:

$$
P(H\mid Y_R),\qquad P(H\mid M_R,Y_R).
$$

- **Only after the global-benefit gate**, lock an independent threshold for each selective arm; implement selectors that merge overlaps, cap region size, and record controlled fallbacks. Keep mechanism truth out of online features.
- Implement bounded local exact-MAP or hypergraph refinement; verify against exhaustive enumeration on small regions before full $d=5$ integration.
- Time decoding only: candidate generation, posterior lookup, refinement, and MWPM. Exclude data generation, file I/O, physical-table construction, and plotting.

**Program:** **decode_d5_dataset** runs one locked decoder configuration on an existing dataset. It reads a supplied threshold/table version and cannot change either.

**Gate:** tests show parity consistency, correct fallback, no truth leakage, agreement with exact local enumeration, and deterministic decoding on fixed shots.

### 5. Implement postprocessing before threshold tuning

- Use NumPy to aggregate per-shot decoder outputs and calculate:

$$
\hat p_L=\frac{\text{logical failures}}{\text{decoded shots}}.
$$

- Compute 95% Wilson intervals for each logical error rate and paired bootstrap intervals for the difference from MWPM on identical shots.
- Use Matplotlib to plot **all** logical-error grid points and intervals, paired decoder differences, cost–reliability Pareto fronts, available-parity and unsupported fractions, and, if selective decoding is attempted, activation fraction, posterior reliability, trigger precision/recall, region sizes, fallback rate, and decode-time distribution.
- Record mean, median, p95, and p99 local-computer decode latency. Label these as small-scale CPU timing, not GPU or real-time hardware results.
- Persist architecture/circuit revision, event-table and sweep-manifest versions, decoder and threshold versions when applicable, seeds, shot counts, full configuration, resource-cost assumptions, and CPU details.

**Program:** **analyze_d5_results** reads completed decoder outputs only. It cannot generate data, tune thresholds, or rerun decoders.

**Gate:** analysis tests reproduce known Wilson intervals and paired contrasts on fixed toy data; figures regenerate only from stored outputs.

### 6. Tune the selector only after a held-out global hypergraph gain

- Use the architecture-specific physical table and dedicated development/tuning dataset to sweep threshold $\tau$, candidate radius, and region cap. Do this **after** the bounded global hypergraph decoder has shown useful accuracy, while keeping final $d=5$ held-out data untouched.
- Lock an objective before reading held-out logical results:

$$
\mathcal L(\tau)=
c_{\mathrm{miss}}P(\text{missed correlated fault})+
c_{\mathrm{false}}P(\text{false activation})+
c_{\mathrm{latency}}E[\text{refined regions}].
$$

- Run a coarse threshold grid, inspect calibration and activation/latency curves, then choose a narrow refinement range.
- Write one versioned threshold artifact tied to the table and development split. Do not select it based on held-out logical error.

**Program:** **tune_selector_threshold** is manually invoked on development data and writes the threshold artifact. It is never called by normal data generation, deployment, or analysis.

**Gate:** a locked threshold artifact exists before any held-out benchmark; deployment can only read it.

### 7. Execute the full-grid held-out benchmark

- Decode identical held-out datasets **within each architecture** with core/detailed calibrated MWPM, correlation-aware matching, and global hypergraph. Add locked syndrome-only and detailed-record selectors only if their earlier gate passed.
- Execute the entire frozen loss-by-correlated-fault grid for U and B. Store one row for every architecture, code size, physical cell, record level, and decoder, including unsupported and above-threshold outcomes. Report logical error with uncertainty, paired within-architecture gains, the U-versus-B gap, resource-cost vector, and any trigger quality, activation, timing, or fallback results.
- Perform metadata ablations and physical-model robustness tests without changing a locked decoder or omitting unfavorable cells. Report each panel in full.

**Program:** **benchmark_locked_d5_decoders** is a deployment benchmark, not a tuner. It writes raw outputs for **analyze_d5_results**.

**Gate:** distinguish a conditional decoder benefit from a weak baseline, threshold overfit, unavailable metadata, a changed physical architecture, or a post-selected favorable error rate. A hardware-cost conclusion requires a declared target logical reliability and complete resource accounting.

### 8. Implement the large-scale physical compiler only after the small stack works

- Preserve the small physical model as a regression baseline. Build a separate larger optical/fusion-network model with greater depth, resource complexity, and parameter resolution.
- Use large computational resources only for offline likelihood/event-table construction and convergence studies. Do not use accelerated physics simulation to disguise online decoder cost.
- Generate a new optical-table version rather than overwriting the small-model table. For every new fusion action or location, rerun the matching Stim fault-propagation map against the frozen $d=5$ circuit, or version and revalidate a changed circuit. Do not carry small-model detector supports forward by assumed geometry.
- Demonstrate probability conservation, numerical convergence, agreement with the small optical model in their shared regime, and consistency between the large model's allowed actions and the versioned $d=5$ Stim map. New leakage or ambiguous outcomes stay outside the stabilizer decoder claim until a justified action is derived.

**Program:** **build_large_physical_table** is deferred until the small physics compiler, dataset generator, decoder, and analysis stack are complete.

### 9. Fine-tune and benchmark the large model separately

- Generate new development and held-out datasets from the large optical-table version and its compatible Stim map. Record both version identifiers with every result.
- Run a fine $\tau$ sweep only on the new development split and lock a table-specific threshold artifact.
- Decode the large held-out dataset and use enough shots to characterize mean and tail CPU latency accurately.
- Report accelerated physical-simulation time separately from decoder time. GPU hours do not establish GPU decoder performance unless the decoder itself is separately implemented and benchmarked on that hardware.

**Programs:** **tune_large_model_threshold** and **benchmark_large_model_decoders** are distinct from each other and from their small-model counterparts.

**Gate:** report whether the small-model conclusion transfers, changes, or fails. A change is evidence, not a reason to retune using held-out results.

## Why dataset generation is necessary

The physical circuit simulation supplies a probability distribution, not the many statistically independent $d=5$ syndrome samples needed for a fair decoder comparison. A dataset generator is therefore required: it draws random observable fusion records and fusion-level actions from the frozen optical table, applies the compatible Stim-derived detector/logical effect at each $d=5$ fusion location, writes immutable seeded shots, and separates development/tuning data from final held-out data. This makes the benchmark reproducible and guarantees every decoder processes the same random errors. A stored DEM may accelerate sampling, but its error supports must be traceable to the annotated code circuit and validated fusion actions.

## Deliverables

1. Documented U and B optical circuits, encoded-resource preparation, detector configurations, and a shared finite six-ring memory with a declared logical observable.
2. Independently validated local optical simulations or calculations for both BSMs, including ideal/pure-loss limits, cutoff convergence where applicable, and conditional actions or explicit non-Pauli ambiguity.
3. Versioned architecture-specific tables $P(A,R\mid\theta,U/B)$ and a common core/detailed record contract.
4. Annotated bounded and, after its gate, $d=5$ native Stim circuits; versioned action/location-to-detector/logical maps, erasure masks, and single-fault validation evidence.
5. A real higher-order decoder checked against bounded exact MAP, plus equally informed calibrated MWPM and correlation-aware matching baselines; a selective module only after global gain.
6. A frozen full-sweep manifest, immutable shot shards, all-cell logical and paired results, precision/unsupported accounting, and reproducible full curves.
7. Physical resource accounting and cost–reliability Pareto fronts for both architectures, including near misses and regions where neither design is viable.
8. A final report separating local optical validation, native-memory validation, bounded or larger-code computational evidence, and any later device/hardware claim.

## References for the plan

### Surface codes and logical-error evaluation

- [Dennis, Kitaev, Landahl, and Preskill, Topological quantum memory](https://arxiv.org/abs/quant-ph/0110143) — foundational surface-code recovery, logical failure, and threshold framework.
- [Fowler, Mariantoni, Martinis, and Cleland, Surface codes: Towards practical large-scale quantum computation](https://arxiv.org/abs/1208.0928) — surface-code stabilizer circuits and practical fault-tolerant context.
- [Fowler, Proof of finite surface code threshold for matching](https://arxiv.org/abs/1206.0800) — matching-based surface-code threshold under local circuit noise.
- [Stim circuit and detector-error-model documentation](https://github.com/quantumlib/Stim/blob/main/doc/file_format_stim_circuit.md) — `DETECTOR`/`OBSERVABLE_INCLUDE` definitions and circuit-to-detector analysis; keep the original multi-detector support visible before any graphlike matching decomposition.

### MWPM and calibrated graph decoding

- [Higgott, PyMatching: A Python Package for Decoding Quantum Codes with Minimum-Weight Perfect Matching](https://doi.org/10.1145/3505637) — MWPM decoding implementation and graph-model assumptions.
- [Google Quantum AI, Suppressing quantum errors by scaling a surface code logical qubit](https://doi.org/10.1038/s41586-022-05434-1) — detector-error hypergraphs, belief matching, and comparison with stronger decoding references.
- [Higgott et al., Improved decoding of circuit noise and fragile boundaries of tailored surface codes](https://arxiv.org/abs/2203.04948) — belief matching, which updates matching information from a decoding hypergraph.

### Hyperedges, posterior inference, and hypergraph-aware decoding

- [Poulin and Chung, On the iterative decoding of sparse quantum codes](https://arxiv.org/abs/0801.1241) — syndrome-based belief propagation, posterior inference, and the loop/degeneracy limitations that must be reported.
- [Kuo and Lai, Exploiting degeneracy in belief propagation decoding of quantum codes](https://doi.org/10.1038/s41534-022-00623-2) — belief-propagation behavior on degenerate quantum codes, including surface/toric settings.
- [Higgott and Breuckmann, Improved single-shot decoding of higher-dimensional hypergraph-product codes](https://doi.org/10.1103/PRXQuantum.4.020332) — decoding directly from a probability distribution over errors and syndrome; useful background for higher-order inference, not a surface-code implementation prescription.

### Linear-optical fusion and photonic error mechanisms

- [Browne and Rudolph, Resource-efficient linear optical quantum computation](https://arxiv.org/abs/quant-ph/0405157) — foundational Type-I/Type-II fusion operations in linear optics.
- [Bartolucci et al., Fusion-based quantum computation](https://arxiv.org/abs/2101.09310) — FBQC formalism, fusion non-determinism, loss, and fault-tolerant architecture.
- [Shaw et al., Errors in heralded circuits for linear optical entanglement generation](https://arxiv.org/abs/2305.08452) — partial distinguishability and leakage/error-model limitations in photonic entangling circuits.
- [van den Hoven, Lamers, and Renema, Photonic fusion operations transform partial distinguishability](https://arxiv.org/abs/2609.01019) — how fusion outcomes and error models affect distinguishability.

### Local photonic simulation

- [Strawberry Fields Fock-backend and boson-sampling documentation](https://strawberryfields.ai/photonics/demos/run_boson_sampling.html) — Fock inputs, interferometers, PNR measurements, and the mode/cutoff scaling limitation motivating the local-compiler design.
