# Fusion-Hypergraph Decoder: Full-Scale Test Plan

## Project decision

This project implements the highest-ranked direction in *Photonic Decoder Evaluations*: an outcome-conditioned fusion hypergraph/factor decoder with latent photonic fault states. The scientific claim being tested is deliberately narrow:

> Observable fusion outcome and photon-number metadata can identify common-cause photonic faults well enough that hypergraph inference lowers logical error rate relative to decoders restricted to syndrome information or a pairwise graph projection.

The novelty is the physical factorization and its observable metadata, not belief propagation, hypergraphs, or FPGA implementation by themselves.

## What the code models

The synthetic model is a periodic $d \times d \times r$ detector lattice, where $d$ is the linear spatial size and $r$ is the number of time layers. In the current code, these parameters control the size of a **surrogate detector complex**; $d$ has not yet been shown to be the distance of a named FBQC code. There are

$$
N=d^2r
$$

local fusion sites and the same number of detector nodes. A site $i$ represents one local physical process. Its categorical latent state is

$$
z_i\in\{0,1,2,3,4,5\},
$$

with the following meanings:

1. no fault;
2. an x-directed pair fault;
3. a y-directed pair fault;
4. a time-directed pair fault;
5. a three-detector loss burst; or
6. a four-detector multiphoton burst.

The geometry is constructed in [`src/fusion_hypergraph/lattice.py`](src/fusion_hypergraph/lattice.py). If site $i$ has coordinates $(x,y,t)$, define the local detector as $D_{x,y,t}$, with all coordinates interpreted periodically. The six supports are

$$
\begin{aligned}
z_i=0 &: \varnothing,\\
z_i=1 &: \{D_{x,y,t},D_{x+1,y,t}\},\\
z_i=2 &: \{D_{x,y,t},D_{x,y+1,t}\},\\
z_i=3 &: \{D_{x,y,t},D_{x,y,t+1}\},\\
z_i=4 &: \{D_{x,y,t},D_{x+1,y,t},D_{x,y+1,t}\},\\
z_i=5 &: \{D_{x,y,t},D_{x+1,y,t},D_{x,y+1,t},D_{x,y,t+1}\}.
\end{aligned}
$$

States 4 and 5 are genuine hyperedges because one local cause touches three or four detectors at once. The code therefore does not model them as several independent pair faults.

Each site also emits two observable fields: a fusion class (`success`, `failure`, or `erasure`) and a photon-number-resolving (PNR) bin (`0`, `1`, or `2+`). Detector efficiency and HOM visibility control how informative these observations are. The latent state is used to generate the synthetic shot, but only the syndrome and these observable fields are available to the proposed decoder. The true latent state is exposed only to `oracle_bp` as an information-ceiling diagnostic.

The local table in `src/fusion_hypergraph/physics.py` is a **surrogate table used to exercise the complete test system**. It is normalized, parameter-sensitive, and auditable, but it is not a substitute for an optical derivation. Before using results in a scientific claim, replace `emission_table` with a table derived from a selected fusion primitive, Fock simulation, or experimental calibration:

$$
P(F,L,O\mid\theta),
$$

where $F$ is the local QEC fault, $L$ is the latent photon/source state, $O$ is observable metadata, and $\theta$ contains efficiency, visibility, loss, and source parameters.

### The mathematical objects and where they live

The implementation uses sparse lists where a paper would normally display matrices. The following objects are the complete bridge between the physics model and the decoder.

| Mathematical object | Shape | Meaning | Code location |
|---|---:|---|---|
| $A_{d i s}$ | $N\times N\times6$, binary | Whether state $s$ at site $i$ flips detector $d$ | `FusionLattice.supports` in [`lattice.py`](src/fusion_hypergraph/lattice.py); materialized per factor-graph connection as `contribution` in [`decoder.py`](src/fusion_hypergraph/decoder.py) |
| $L_{is}$ | $N\times6$, binary | Whether state $s$ at site $i$ crosses the modeled logical seam | `FusionLattice.logicals` in [`lattice.py`](src/fusion_hypergraph/lattice.py) |
| $\pi_s$ | $6$ | Prior probability of each local state | `state_priors` in [`physics.py`](src/fusion_hypergraph/physics.py) |
| $T_{son}$ | $6\times3\times3$ | $P(O=o,\mathrm{PNR}=n\mid z=s)$ | `emission_table` in [`physics.py`](src/fusion_hypergraph/physics.py) |
| $C_{is}$ | $N\times6$ per shot | Negative log posterior cost for assigning state $s$ to site $i$ | `local_costs` in [`physics.py`](src/fusion_hypergraph/physics.py) |
| $m_{i\rightarrow d}(s),m_{d\rightarrow i}(s)$ | length 6 per factor-graph connection | Variable-to-detector and detector-to-variable min-sum messages | `v_to_f` and `f_to_v` in [`decoder.py`](src/fusion_hypergraph/decoder.py) |

The incidence object $A$ is conceptually a three-index binary tensor because a site has six possible supports. It is not stored as a dense tensor. `supports[i][s]` stores only the detector indices for which $A_{dis}=1$. `site_to_detectors` and `detector_to_sites` are the two adjacency-list views of the same factor graph. This sparse design avoids storing mostly zero entries and directly tells the message-passing decoder which variables meet at each parity constraint.

For a sampled latent-state vector $\mathbf z=(z_1,\ldots,z_N)$, the detector syndrome is

$$
y_d=\bigoplus_{i=1}^{N}A_{d i z_i},
$$

and the modeled logical bit is

$$
\ell=\bigoplus_{i=1}^{N}L_{i z_i}.
$$

Both equations are implemented as XOR operations in `FusionLattice.syndrome` and `FusionLattice.logical`. The logical matrix marks states 1, 4, and 5 only when their site lies at $x=d-1$, because those supports cross the periodic x seam. This is a controlled topological parity label for the surrogate lattice, not yet a logical membrane derived from a named six-ring, RHG, or other FBQC architecture.

### How the synthetic photonic noise is created

[`physics.py`](src/fusion_hypergraph/physics.py) first divides the total local physical-fault probability $p$ among pair and correlated states. With correlated fraction $c$ and multiphoton fraction $m$,

$$
\begin{aligned}
\pi_0 &= 1-p,\\
\pi_1=\pi_2=\pi_3 &= \frac{p(1-c)}{3},\\
\pi_4 &= p(c-m),\\
\pi_5 &= pm.
\end{aligned}
$$

For example, the checked-in configurations use $c=0.30$ and $m=0.10$. Therefore 70% of the fault mass is divided among pair faults, 20% is assigned to the loss triple, and 10% is assigned to the multiphoton quadruple. Sites are currently sampled independently from this six-state prior. The correlations being tested are therefore **within one fault's multi-detector support**, not correlations between different sites or across a source history.

The emission tensor starts from two hand-authored conditional tables: one for fusion class and one for PNR bin. Their outer product assumes those two observables are conditionally independent once $z_i$ is known:

$$
T^{\mathrm{informative}}_{son}
=P(o\mid z_i=s)P(n\mid z_i=s).
$$

The exact checked-in rows are shown below. Rows follow the state order in `STATE_NAMES`; these numbers are defined literally inside `emission_table`.

| Latent state | $P(\text{success})$ | $P(\text{failure})$ | $P(\text{erasure})$ | $P(0)$ | $P(1)$ | $P(2+)$ |
|---|---:|---:|---:|---:|---:|---:|
| none | 0.965 | 0.025 | 0.010 | 0.01 | 0.04 | 0.95 |
| x pair | 0.700 | 0.250 | 0.050 | 0.03 | 0.22 | 0.75 |
| y pair | 0.700 | 0.250 | 0.050 | 0.03 | 0.22 | 0.75 |
| time pair | 0.700 | 0.250 | 0.050 | 0.03 | 0.22 | 0.75 |
| loss triple | 0.100 | 0.300 | 0.600 | 0.58 | 0.36 | 0.06 |
| multiphoton quadruple | 0.250 | 0.650 | 0.100 | 0.01 | 0.08 | 0.91 |

The table encodes the intended qualitative reasoning: ordinary events are usually successful and contain the expected multi-click signature; pair faults make failure more likely; loss bursts favor erasure and low photon count; and multiphoton bursts favor failure while retaining a `2+` count. These values were selected to create distinguishable but overlapping observation distributions. They were not derived from beamsplitter amplitudes, detector POVMs, or measured hardware, which is why results from this table can validate the pipeline but cannot establish a photonic-decoder advantage.

The current surrogate then defines a quality parameter

$$
q=\eta_{\mathrm{det}}V,
$$

where $\eta_{\mathrm{det}}$ is detector efficiency and $V$ is HOM visibility, and interpolates toward a completely uninformative nine-outcome distribution:

$$
T_{son}=qT^{\mathrm{informative}}_{son}+(1-q)\frac{1}{9}.
$$

The final tensor is normalized over $(o,n)$ for each state. Thus lower efficiency or visibility does not change which latent faults occur; it makes the recorded metadata less able to distinguish them. This is a deliberate information-quality experiment, not yet a physical law connecting efficiency and visibility to a real fusion circuit.

For each site, `sample_observations` draws one of the nine `(outcome, PNR)` combinations from the row belonging to the sampled state. [`data.py`](src/fusion_hypergraph/data.py) then writes five arrays per shard:

| Array | Shape for a shard of $B$ shots | Role |
|---|---:|---|
| `states` | $B\times N$ | Simulator-only local truth; used by `oracle_bp` |
| `syndromes` | $B\times N$ | Measured detector bits supplied to every decoder |
| `outcomes` | $B\times N$ | Observable fusion class supplied to metadata-aware methods |
| `pnr` | $B\times N$ | Observable PNR bin supplied to metadata-aware methods |
| `logicals` | $B$ | Simulator truth used only to score decoder failure |

This division is important: the proposed method never receives the hidden labels that created the data. `data.py` stores them so the oracle control and audit tests are possible, while `experiment.py` passes them only into `local_costs(..., mode="oracle")`.

## Decoder and controlled comparisons

`MinSumHypergraphDecoder` performs normalized, damped min-sum over categorical local fault variables and detector XOR factors. The experiment runs the following methods on exactly the same shots:

| Method | Information available | Purpose |
|---|---|---|
| `uniform_mwpm` | Syndrome and one fixed edge weight | Weak sanity baseline |
| `calibrated_mwpm` | Syndrome and calibrated marginal pair probabilities | Fair pairwise graph baseline |
| `metadata_mwpm` | Syndrome and metadata-conditioned pair weights | Tests whether metadata alone is enough after graph projection |
| `marginal_bp` | Syndrome and the complete marginalized hypergraph | Controls for inference/model capacity |
| `metadata_bp` | Syndrome, full hypergraph, fusion outcome, and PNR bin | Proposed decoder |
| `oracle_bp` | Syndrome and true local latent states | Information-ceiling diagnostic and simulator check |

The matching implementation represents the three two-detector states exactly and intentionally omits the three- and four-detector events. Boundary edges let it return a correction when a hyperedge creates a syndrome outside the projected model. This is an honest graph-projection baseline, **not a claim to reproduce a particular correlated-MWPM implementation**. A paper-quality comparison must additionally plug in the project’s selected calibrated correlated PyMatching/Stim pipeline and preserve the same generated shots and metadata ablations.

### What the hypergraph decoder is actually solving

The decoder is given the measured syndrome $\mathbf y$ and a local cost matrix $C$. It approximately solves the constrained maximum-a-posteriori problem

$$
\hat{\mathbf z}
=\underset{\mathbf z}{\operatorname{argmin}}
\sum_{i=1}^{N}C_{i,z_i}
\quad\text{subject to}\quad
\bigoplus_i A_{d i z_i}=y_d
\quad\text{for every detector }d.
$$

The cost matrix determines what information a method is allowed to use.

For `marginal_bp`, every site receives the same state prior:

$$
C_{is}=-\log \pi_s+\text{row constant}.
$$

For `metadata_bp`, Bayes' rule converts the observed fusion class $o_i$ and PNR bin $n_i$ into a site-specific posterior:

$$
P(z_i=s\mid o_i,n_i)
=\frac{T_{s o_i n_i}\pi_s}
{\sum_{s'}T_{s'o_i n_i}\pi_{s'}},
$$

followed by

$$
C_{is}=-\log P(z_i=s\mid o_i,n_i)+\text{row constant}.
$$

Subtracting the minimum cost in each row does not alter the preferred configuration; it only keeps the numerical scale manageable. `oracle_bp` uses a nearly one-hot posterior at the true state and exists only to test the implementation and show what perfect latent-state information would permit. Because it still uses loopy min-sum, it is an information-ceiling diagnostic rather than a mathematically guaranteed performance bound.

[`decoder.py`](src/fusion_hypergraph/decoder.py) represents the constrained problem as a factor graph:

- one categorical variable node for each fusion site $z_i$;
- one XOR factor for each measured detector bit $y_d$; and
- one connection whenever some state at site $i$ can flip detector $d$.

Each message is a six-entry vector, one entry per possible local state. The variable-to-factor update is

$$
m_{i\rightarrow d}(s)
=C_{is}
+\sum_{d'\in N(i)\setminus d}m_{d'\rightarrow i}(s),
$$

up to subtraction of its smallest entry. The detector-to-variable update asks what the other neighboring sites must cost in order to satisfy detector $d$:

$$
m_{d\rightarrow i}(s)
=\min_{\{z_j:j\in N(d)\setminus i\}}
\left[
\sum_{j\ne i}m_{j\rightarrow d}(z_j)
\right]
$$

subject to

$$
\bigoplus_{j\ne i}A_{d j z_j}
=y_d\oplus A_{d i s}.
$$

The implementation does not enumerate all neighboring assignments. It reduces every incoming six-state message to two numbers—the cheapest state that contributes detector parity 0 and the cheapest state that contributes parity 1—then combines those numbers with a two-entry even/odd dynamic program. That is the role of `parity_cost` in `MinSumHypergraphDecoder.decode`.

After every detector update, damping mixes the new message with the previous message:

$$
m^{(k)}\leftarrow
\lambda m^{(k-1)}+(1-\lambda)m^{(k)}_{\mathrm{raw}},
$$

where the checked-in value is $\lambda=0.35$. Damping reduces oscillation caused by short loops. Iteration stops when the largest detector-message change falls below the configured tolerance or when `max_iterations` is reached. The final belief is

$$
b_i(s)=C_{is}+\sum_{d\in N(i)}m_{d\rightarrow i}(s),
$$

and the decoder selects $\hat z_i=\operatorname{argmin}_s b_i(s)$. It converts that local-state estimate into a logical prediction using the same $L_{is}$ matrix used to label the sampled shot.

This is normalized, damped **min-sum**, an approximation to max-product belief propagation. Because the factor graph has loops, convergence and exact syndrome satisfaction are not guaranteed. `experiment.py` therefore records both `converged_fraction` and `syndrome_consistent_fraction`; a logically correct prediction from an inconsistent state assignment must not be mistaken for proof that the physical error was reconstructed exactly.

### How the MWPM projection is constructed

[`matching.py`](src/fusion_hypergraph/matching.py) builds a new PyMatching graph from the same per-shot cost matrix. For states 1, 2, and 3, the two detectors in `supports[i][s]` become an ordinary matching edge. Converting the normalized costs back to probabilities gives $p_{is}$, and the edge weight is the usual log-likelihood ratio

$$
w_{is}=\log\frac{1-p_{is}}{p_{is}}.
$$

If a pair state crosses the x seam, the edge receives logical fault ID 0 so PyMatching can return the predicted logical parity. `uniform_mwpm` replaces all pair-state probabilities by $0.01/3$; `calibrated_mwpm` uses the marginalized prior; and `metadata_mwpm` changes the pair-edge weights shot by shot using the observed metadata posterior.

The projection has no matching edge for the loss triple or multiphoton quadruple. Adding three pair edges for one four-detector cause would falsely allow those pieces to occur independently, changing both the probability and the set of allowed explanations. Instead, every detector receives a fixed-weight boundary edge so matching can still produce an answer when a sampled hyperedge creates a syndrome outside the pair model. The boundary weight is a configuration parameter, currently 12.0; it is an engineering fallback, not a calibrated physical likelihood.

### Why it could be better than MWPM—and when it should not be

MWPM is very strong when the detector error model is graphlike: one elementary fault creates at most two detection events, and accurate edge weights capture the relevant statistics. Under that model, replacing matching with generic message passing should not be assumed to help.

The proposed decoder has a plausible advantage only because this experiment gives it two kinds of structure that the projected graph cannot represent simultaneously:

1. **Common-cause support.** One categorical choice can flip three or four detectors. The decoder pays for that cause once and preserves the fact that its detector changes occur together.
2. **Outcome-conditioned evidence.** Fusion class and PNR data change the posterior over all six local causes before syndrome inference. A `2+` PNR result can make a multiphoton explanation cheaper without revealing the hidden state directly.

For example, if four observed defects match one state-5 support, the hypergraph model can explain them with cost $C_{i5}$. A pairwise projection must either combine several edge events, use boundary edges, or omit that explanation. Those alternatives can have the wrong total likelihood and may predict the wrong seam parity. However, this mechanism produces a real improvement only if states 4 and 5 occur often enough, the metadata is informative and calibrated, and min-sum finds a good solution.

The comparisons separate these effects:

| Contrast | Main question answered |
|---|---|
| `marginal_bp` vs `calibrated_mwpm` | Does retaining higher-order supports help even without metadata? |
| `metadata_bp` vs `marginal_bp` | Does observable photonic metadata add useful information with the inference engine held fixed? |
| `metadata_bp` vs `metadata_mwpm` | Does retaining the full higher-order model help after both methods receive the same metadata? |
| `oracle_bp` vs `metadata_bp` | How much performance is lost because the observables do not perfectly identify the latent cause? |

The current `calibrated_mwpm` and `metadata_mwpm` remain deliberately projected baselines. They are not the final strong control because they omit the genuine hyperedges rather than using a published correlated-matching construction. A positive result against them is evidence that the projection loses information, not yet proof of superiority over the best available MWPM-family decoder.

## Primary hypotheses and metrics

The primary endpoint is the surrogate logical-parity failure rate with a 95% Wilson interval. It should be called a physical code's logical error rate only after the detector complex and seam operator are derived from that code. The primary contrast is paired on the same shots:

$$
\Delta_{\mathrm{info}} = p_L(\text{best syndrome-only baseline}) - p_L(\text{metadata BP}).
$$

The processor reports a paired bootstrap interval for $\Delta_{\mathrm{info}}$. A positive interval excluding zero supports an information advantage. It does not, by itself, establish that the optical model is realistic.

Secondary metrics are:

- logical-error scaling with physical fault rate and lattice size; call this code-distance scaling only after the lattice is mapped to a named code whose distance is verified;
- convergence rate and mean min-sum iterations;
- decoded-syndrome consistency;
- wall-clock throughput versus the number of fusion sites;
- the gap between metadata BP and the perfect-latent-information diagnostic; and
- information advantage across detector-efficiency and visibility shifts.

## Full experimental matrix

`configs/full_scale.toml` sweeps:

- distances and round counts: 3, 5, 7, 9, and 11;
- physical fault probabilities from 0.0025 through 0.08;
- detector efficiencies: 0.85, 0.92, 0.97, and 0.995;
- HOM visibilities: 0.85, 0.92, 0.97, and 0.995; and
- 10,000 paired shots per scenario.

Because equal-length distance and round lists are zipped in `config.scenarios`, this is 5 geometries $\times$ 7 fault rates $\times$ 4 efficiencies $\times$ 4 visibilities = 560 scenarios, or 5.6 million sampled shots before applying six decoders to every shot.

This is intentionally expensive. First run `configs/smoke.toml`. For the full sweep, distribute scenarios across independent jobs or reduce the broad scan, identify the threshold region, and then allocate more shots there. Keep at least enough shots that the confidence interval, rather than zero observed failures, determines the claimed error rate.

## Reproducible workflow

Install Python 3.11 or later and the project dependencies:

```powershell
Set-Location Hypergraph
python -m venv .venv
.venv\Scripts\pip install -e ".[dev]"
```

Run the small end-to-end check:

```powershell
fusion-hypergraph all --config configs/smoke.toml --workdir runs/smoke
```

Or run the stages separately:

```powershell
fusion-hypergraph generate --config configs/full_scale.toml --output runs/full/data
fusion-hypergraph run --config configs/full_scale.toml --data runs/full/data --output runs/full/results --workers 8
fusion-hypergraph analyze --results runs/full/results --bootstrap-samples 4000
fusion-hypergraph plot --summary runs/full/results/summary.csv --output runs/full/figures
```

Generation writes deterministic compressed NumPy shards and a JSON manifest. Every shot has a stable seed derived from the master seed, scenario, and shot number, so changing shard size does not change the sample. The run stage streams one shard at a time, stores aggregate measurements in `raw_results.csv`, and retains paired logical-failure vectors in compressed form. The analysis stage adds confidence intervals and paired $\Delta_{\mathrm{info}}$. The plotting stage produces both PNG and PDF figures:

- `logical_error_scaling`;
- `information_gain_heatmap`;
- `runtime_scaling`; and
- `bp_convergence`.

No benchmark results are checked into the repository because this delivery writes, but does not execute, the full experiment.

## How the implementation works

The complete path for one shot is:

```text
configuration
    |
    v
state prior pi_s + emission tensor T_son       lattice supports A_dis + logicals L_is
    |                                                        |
    +------------------------+-------------------------------+
                             v
                 sample hidden state z_i at every site
                             |
              +--------------+---------------+
              |                              |
              v                              v
    sample observable (outcome, PNR)    XOR supports A_d,i,z_i
              |                              |
              v                              v
       per-site metadata O_i             syndrome y_d
              |                              |
              +---------------+--------------+
                              v
               build per-shot local costs C_is
                              |
          +-------------------+-------------------+
          |                                       |
          v                                       v
 sparse hypergraph/factor graph              projected MWPM graph
          |                                       |
          v                                       v
 min-sum state estimate z_hat                 logical correction bit
          |
          v
 predicted logical parity ell_hat
          |
          +-------------------+-------------------+
                              v
                 compare with hidden label ell
```

The stages correspond to specific files:

1. **Read the experiment definition.** [`config.py`](src/fusion_hypergraph/config.py) loads the TOML configuration and expands it into scenarios. If `distances` and `rounds` have equal lengths, they are paired, so the full configuration uses geometries `(3,3)`, `(5,5)`, ..., `(11,11)` rather than all 25 distance-round combinations. A scenario ID is a hash of its geometry and physical parameters.
2. **Create the sparse detector geometry.** [`lattice.py`](src/fusion_hypergraph/lattice.py) constructs `supports`, `logicals`, `site_to_detectors`, and `detector_to_sites`. This is where the hypergraph and its modeled logical seam are designed.
3. **Create the local noise and observation model.** [`physics.py`](src/fusion_hypergraph/physics.py) computes $\pi$ and $T$. This is the only current connection to photonic parameters, and it is explicitly a surrogate pending a real fusion-circuit derivation.
4. **Generate immutable paired data.** [`data.py`](src/fusion_hypergraph/data.py) uses a seed derived from the master seed, scenario ID, and shot number. It samples $\mathbf z$, $\mathbf y$, metadata, and $\ell$, then writes compressed `.npz` shards plus `manifest.json`. Because the seed is shot-specific, changing shard size does not change the generated shots.
5. **Interpret the observable evidence.** `local_costs` in [`physics.py`](src/fusion_hypergraph/physics.py) converts the allowed inputs into $C_{is}$. This is the boundary between observation and inference: marginalized mode ignores metadata, metadata mode uses Bayes' rule, and oracle mode uses simulator truth.
6. **Construct the decoding representation.** [`decoder.py`](src/fusion_hypergraph/decoder.py) builds sparse factor-graph messages from `site_to_detectors`, `detector_to_sites`, and the state-dependent support bits. [`matching.py`](src/fusion_hypergraph/matching.py) instead constructs pair edges and boundaries in a PyMatching graph. These graphs are not the physical lattice itself; they are two different inference representations derived from the same physical-event support table.
7. **Decode identical shots.** [`experiment.py`](src/fusion_hypergraph/experiment.py) sends the same syndrome and permitted metadata through every configured method. It records `prediction != truth` as the logical-failure vector and separately records runtime, min-sum iterations, convergence, and syndrome consistency. Timing surrounds decoder work, not data generation.
8. **Interpret the benchmark.** [`analyze.py`](src/fusion_hypergraph/analyze.py) uses Wilson intervals for each binomial logical-error rate and a paired bootstrap for $\Delta_{\mathrm{info}}$. Pairing matters because every method sees the same shots. [`plotting.py`](src/fusion_hypergraph/plotting.py) reads the processed summary only, so plotting cannot change the experiment.

The code therefore separates five concepts that are easy to blur together:

- **creating noise:** sample local latent causes from $\pi$ and observables from $T$;
- **interpreting noise:** turn observable metadata into a posterior cost matrix $C$;
- **creating a syndrome:** XOR each selected state's detector support using $A$;
- **creating a decoding graph:** retain $A$ as a factor graph or project only pair states into a matching graph; and
- **decoding and scoring:** infer a logical parity and compare it with $\ell$.

Stim is not currently part of this executable path. The present harness generates its own synthetic detector lattice and syndrome arrays. A future physically grounded version should obtain detector supports and logical-observable actions from a named FBQC circuit or detector error model, then retain exactly the same separation between simulator truth, experimentally observable metadata, and decoder inputs.

## Required validation before a research claim

1. Replace the surrogate emission table with one derived from a named fusion circuit and document every optical parameter.
2. Verify sampled local frequencies against the table and small exact calculations.
3. Add calibrated correlated MWPM from the same detector error model; do not compare only with uniform matching.
4. Repeat the same min-sum implementation with and without each metadata field: outcome class, PNR, source/history, visibility/timing, and uncertain-loss posterior.
5. Hold out lattice sizes initially—and verified code distances once a real code is integrated—along with source pairs, loss, visibility, efficiency, and routing histories.
6. Repeat with deliberately miscalibrated parameters and report degradation.
7. Quantize messages and likelihood tables only after the floating-point physics advantage is established.
8. Predefine the primary operating region and shot budget before inspecting final results.

## Decision rule

Continue toward a physical/FPGA implementation only if metadata BP beats both the best syndrome-only hypergraph decoder and the strongest calibrated correlated-matching baseline across multiple lattice sizes—and later across verified code distances—with a paired confidence interval for $\Delta_{\mathrm{info}}$ above zero, while remaining robust to held-out hardware parameters. If the gain disappears when the baseline is calibrated or when the optical table is made realistic, the correct result is to stop or change the information source.
