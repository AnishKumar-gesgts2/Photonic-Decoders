# Optical-derived boosted fusion into bounded d=3 memory — 2026-09-26

## Question and method

Can an explicitly derived boosted Bell-measurement fault produce decoder-visible
correlation and improve a genuine bounded logical-memory comparison? The local
optical calculation uses the 4×4 unitary in [Hauser et al., Eq. 4](https://arxiv.org/html/2410.16380),
four indistinguishable photons, an ancillary $|\Phi^+\rangle$ pair, and ideal
number-resolving detectors. A Pauli $Z$ on one ancilla photon changes it to
$|\Phi^-\rangle$; its probability is varied as an **assumption**, not read from
the experiment. The four physical Bell measurements are combined using the
paper's $(2,2)$-Shor encoded parity rules. The code converts a wrong encoded
Bell-frame bit to a Pauli error on one data qubit of a three-round Stim rotated
$d=3$ memory, with unknown frame bits randomized and their availability flagged.
This last conversion is a declared teleportation **proxy**; it is not the
native bounded encoded six-ring fusion network.

The exact optical model reproduces the ideal boosted discrimination probabilities:
$50\%$ for each $\Phi$ input and $100\%$ for each $\Psi$ input, averaging $75\%$.
It does not reproduce the experiment's measured $69.3\%$ or its imperfect
click-pattern and source statistics. The $|\Phi^-\rangle$ ancilla fault swaps
the reported $XX$ bit on conclusive $\Phi$ outcomes and leaves the reported
$ZZ$ bit unchanged. Conclusive outcomes have zero Bell-basis off-diagonal
POVM element in this model. For a uniformly distributed Bell input, the ideal
and phase-fault raw PNR record distributions are identical (total-variation
distance zero): one physical click pattern alone cannot herald the fault.
The *encoded* redundant parity measurements can still reveal disagreements.

## Original extra-photon fault audit

I also applied a normalized creation operator to one data input mode before
the same boosted multiport. With perfect PNR, the five-photon record is
identified as excess and is not a Bell result. Independent detector loss can
make it appear as a four-count record. At assumed 99.5% per-photon detection,
exactly one photon is missed in **2.450%** of these fault events; **1.593%**
of all such events have an apparent *conclusive* four-count Bell pattern.
Among exactly-one-loss events, 65% mimic a conclusive pattern. At 80%
detection, the corresponding false-conclusive fraction of extra-photon
events is 26.624%.

The conditional Bell-basis Gram matrices of those apparent conclusive
records have nonzero off-diagonal terms. Thus the five-photon fault plus
one lost count does **not** justify the stochastic wrong-Bell-bit action
that a Stim Pauli-fault table would require. The Gram calculation is for a
specified conditional source-fault preparation; it does not supply a
trace-preserving source channel, its incidence, or the complete state left
by the encoded six-ring architecture. These percentages are conditional
on the extra-photon event, **not** physical logical error rates. Full values
are in the [excess-photon audit](../outputs/phase0_bounded_optical_d3/excess_audit.json).

## Results

Each case uses separately seeded 12,000-shot training and 3,000-shot holdout
datasets. The main 2% ancilla-phase sensitivity setting was repeated with
25,000 training and 20,000 held-out shots. Decoder inputs are the syndrome,
available parity bits, four full/partial outcome classes, and redundant parity
disagreements. Latent fault labels are used only for simulation scoring and
offline calibration. The comparison gives both decoders identical metadata.

| Assumed ancilla phase fault rate | Memory basis | Availability-only MWPM | Metadata-aware MWPM | Metadata-aware joint BP + MWPM |
|---:|:---:|---:|---:|---:|
| 0% | Z | 0.033% | 0.033% | 0.033% |
| 0.5% | Z | 0.267% | 0.167% | 0.133% |
| 2% | Z | 0.967% | 0.433% | 0.467% |
| 2%, 20,000-shot holdout | Z | 0.810% | **0.350% (70/20,000)** | 0.325% (65/20,000) |

All X-memory comparisons were 0/3,000, or 0/20,000 in the larger holdout,
because this fault model produces only the complementary Pauli axis. In the
20,000-shot Z-memory holdout, the paired joint-decoder gain over equally
informed MWPM was **0.025 percentage points**, with a 95% bootstrap interval
of **−0.005 to +0.055 percentage points**. The small 0.5% setting has too few
failures for a reliable difference. At 2%, encoded $XX$ error was zero and
encoded $ZZ$ error was 3.709% per location, including unknown-frame
randomization on missing parity outcomes. Both parities were available at
93.79% of encoded fusions; at least one redundancy disagreement occurred on
10.07% of held-out shots.

## Interpretation and decision

**No-go for this specific ancilla phase fault as a source of a useful
hyperedge.** Its justified conclusive action changes one encoded parity;
the Stim data-error signatures are graphlike (at most two detectors per
single-axis fault). The encoded metadata materially improves MWPM, but the
joint decoder has no statistically resolved advantage when it receives the
same metadata. The result supports using metadata-aware MWPM for this
effective channel.

This is **not a no-go for every fusion fault or for the overall hypergraph
hypothesis**. The earlier assumed joint-$XX/ZZ$ proxy demonstrated a
conditional gain; this optical test shows that the specified ancilla-phase
mechanism does not supply that joint action. The original extra-photon
mechanism *can* hide behind a conclusive-looking record when one count is
lost, but its calculated conditional state is not Bell diagonal. Assigning
that event a Pauli hyperedge from its PNR count alone would be unjustified.
The partial-outcome instrument also has coherent back-action beyond the
simple unknown-frame adapter used here. A device-level decision requires
a calibrated boosted source-fault incidence and complete conditional
postfusion instrument, followed by a native bounded encoded six-ring memory.

Run `python phase0/run_bounded_optical_d3.py` with `PYTHONPATH=phase0` from the
repository root. Code: [optical model](boosted_optical.py),
[bounded adapter and decoders](bounded_optical_d3.py),
[runner](run_bounded_optical_d3.py). Data:
[primary cases](../outputs/phase0_bounded_optical_d3/results.json),
[larger holdout](../outputs/phase0_bounded_optical_d3/high_statistics.json),
[extra-photon audit](../outputs/phase0_bounded_optical_d3/excess_audit.json).
