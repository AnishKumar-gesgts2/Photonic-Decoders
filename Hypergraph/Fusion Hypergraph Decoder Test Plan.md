# Fusion-Hypergraph Decoder: Full-Scale Test Plan

## Project decision

This project implements the highest-ranked direction in *Photonic Decoder Evaluations*: an outcome-conditioned fusion hypergraph/factor decoder with latent photonic fault states. The scientific claim being tested is deliberately narrow:

> Observable fusion outcome and photon-number metadata can identify common-cause photonic faults well enough that hypergraph inference lowers logical error rate relative to decoders restricted to syndrome information or a pairwise graph projection.

The novelty is the physical factorization and its observable metadata, not belief propagation, hypergraphs, or FPGA implementation by themselves.

## What the code models

The synthetic model is a periodic (d \times d \times r) detector lattice. Every local fusion site has one categorical latent state:

1. no fault;
2. an x-directed pair fault;
3. a y-directed pair fault;
4. a time-directed pair fault;
5. a three-detector loss burst; or
6. a four-detector multiphoton burst.

The last two states are genuine hyperedges. A shot samples all local states, XORs their detector supports to form the measured syndrome, and records the parity of seam-crossing events as the logical observable. Each site also emits two observable fields: fusion class (`success`, `failure`, or `erasure`) and a PNR bin (`0`, `1`, or `2+`). Detector efficiency and HOM visibility control how informative these observations are.

The local table in `src/fusion_hypergraph/physics.py` is a **surrogate table used to exercise the complete test system**. It is normalized, parameter-sensitive, and auditable, but it is not a substitute for an optical derivation. Before using results in a scientific claim, replace `emission_table` with a table derived from a selected fusion primitive, Fock simulation, or experimental calibration:

\[
P(F,L,O\mid\theta),
\]

where (F) is the local QEC fault, (L) is the latent photon/source state, (O) is observable metadata, and \(\theta\) contains efficiency, visibility, loss, and source parameters.

## Decoder and controlled comparisons

`MinSumHypergraphDecoder` performs normalized, damped min-sum over categorical local fault variables and detector XOR factors. The experiment runs the following methods on exactly the same shots:

| Method | Information available | Purpose |
|---|---|---|
| `uniform_mwpm` | Syndrome and one fixed edge weight | Weak sanity baseline |
| `calibrated_mwpm` | Syndrome and calibrated marginal pair probabilities | Fair pairwise graph baseline |
| `metadata_mwpm` | Syndrome and metadata-conditioned pair weights | Tests whether metadata alone is enough after graph projection |
| `marginal_bp` | Syndrome and the complete marginalized hypergraph | Controls for inference/model capacity |
| `metadata_bp` | Syndrome, full hypergraph, fusion outcome, and PNR bin | Proposed decoder |
| `oracle_bp` | Syndrome and true local latent states | Upper bound and simulator check |

The matching implementation represents the three two-detector states exactly and intentionally omits the three- and four-detector events. Boundary edges let it return a correction when a hyperedge creates a syndrome outside the projected model. This is an honest graph-projection baseline, **not a claim to reproduce a particular correlated-MWPM implementation**. A paper-quality comparison must additionally plug in the project’s selected calibrated correlated PyMatching/Stim pipeline and preserve the same generated shots and metadata ablations.

## Primary hypotheses and metrics

The primary endpoint is logical error rate with a 95% Wilson interval. The primary contrast is paired on the same shots:

\[
\Delta_{\mathrm{info}} = p_L(\text{best syndrome-only baseline}) - p_L(\text{metadata BP}).
\]

The processor reports a paired bootstrap interval for \(\Delta_{\mathrm{info}}\). A positive interval excluding zero supports an information advantage. It does not, by itself, establish that the optical model is realistic.

Secondary metrics are:

- logical-error scaling with physical fault rate and code distance;
- convergence rate and mean min-sum iterations;
- decoded-syndrome consistency;
- wall-clock throughput versus the number of fusion sites;
- the gap between metadata BP and the oracle bound; and
- information advantage across detector-efficiency and visibility shifts.

## Full experimental matrix

`configs/full_scale.toml` sweeps:

- distances and round counts: 3, 5, 7, 9, and 11;
- physical fault probabilities from 0.0025 through 0.08;
- detector efficiencies: 0.85, 0.92, 0.97, and 0.995;
- HOM visibilities: 0.85, 0.92, 0.97, and 0.995; and
- 10,000 paired shots per scenario.

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

Generation writes deterministic compressed NumPy shards and a JSON manifest. Every shot has a stable seed derived from the master seed, scenario, and shot number, so changing shard size does not change the sample. The run stage streams one shard at a time, stores aggregate measurements in `raw_results.csv`, and retains paired logical-failure vectors in compressed form. The analysis stage adds confidence intervals and paired \(\Delta_{\mathrm{info}}\). The plotting stage produces both PNG and PDF figures:

- `logical_error_scaling`;
- `information_gain_heatmap`;
- `runtime_scaling`; and
- `bp_convergence`.

No benchmark results are checked into the repository because this delivery writes, but does not execute, the full experiment.

## How the implementation works

`lattice.py` defines each local state’s detector support and logical-seam action. `physics.py` produces latent-state priors and optical observation likelihoods. `data.py` samples latent states, observations, syndromes, and logical labels into immutable data shards. This separation prevents a decoder from accidentally receiving a simulator-only field.

For each detector factor, `decoder.py` reduces all incoming messages to the minimum cost for even and odd parity. It then sends each neighboring fusion site the cost required to satisfy the measured detector bit. Site updates combine those messages with either marginalized, metadata-conditioned, or oracle local costs. Damping controls short-cycle oscillation; normalized messages avoid numerical growth. The final categorical decisions determine a predicted logical parity.

`matching.py` maps only graphlike two-detector states to weighted matching edges. `experiment.py` sends identical syndromes through every configured method and times decoder work only. `analyze.py` uses Wilson intervals for binomial logical-error rates and a memory-bounded paired bootstrap for the main information contrast. `plotting.py` reads only the processed summary, so figure generation cannot change the underlying statistics.

## Required validation before a research claim

1. Replace the surrogate emission table with one derived from a named fusion circuit and document every optical parameter.
2. Verify sampled local frequencies against the table and small exact calculations.
3. Add calibrated correlated MWPM from the same detector error model; do not compare only with uniform matching.
4. Repeat the same min-sum implementation with and without each metadata field: outcome class, PNR, source/history, visibility/timing, and uncertain-loss posterior.
5. Hold out code distances, source pairs, loss, visibility, efficiency, and routing histories.
6. Repeat with deliberately miscalibrated parameters and report degradation.
7. Quantize messages and likelihood tables only after the floating-point physics advantage is established.
8. Predefine the primary operating region and shot budget before inspecting final results.

## Decision rule

Continue toward a physical/FPGA implementation only if metadata BP beats both the best syndrome-only hypergraph decoder and the strongest calibrated correlated-matching baseline across multiple distances, with a paired confidence interval for \(\Delta_{\mathrm{info}}\) above zero, while remaining robust to held-out hardware parameters. If the gain disappears when the baseline is calibrated or when the optical table is made realistic, the correct result is to stop or change the information source.
