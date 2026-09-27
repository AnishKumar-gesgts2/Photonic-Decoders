# Accuracy-first bounded logical-memory test — 2026-09-26

Run `PYTHONPATH=phase0 python phase0/run_bounded_joint_logical.py` from `Hypergraph`; the full reproducible output is [results.json](../outputs/phase0_bounded_effective_joint/results.json). This test follows the project's new accuracy-first gate. The [FBQC framework](https://www.nature.com/articles/s41467-023-36493-1) motivates preserving a joint fusion $XX/ZZ$ fault; [belief-matching](https://journals.aps.org/prx/abstract/10.1103/PhysRevX.13.031007) motivates a stronger correlation-aware control than ordinary matching.

## What this experiment actually models

Stim generates a three-round rotated $d=3$ surface-code memory, its detectors, and a declared logical observable. A single fusion-report $XX/ZZ$ flip is represented by one categorical $Y$ fault on a data qubit at one time slice through a **declared teleportation-frame adapter**. This is an effective-channel bridge, **not** an optical derivation or native bounded six-ring fusion network. Each location has four mutually exclusive states: no fault, $X$, $Z$, or joint $Y$. The physical rate of this fusion mechanism is unknown; all rates below are sensitivity settings. No optical or source record is claimed.

Every decoder receives the same syndrome and the same declared channel calibration. In flagged arms, every decoder also gets the same imperfect local flag; its 60% sensitivity and 15% false-positive rate are assumed. Latent fault states never enter a test-time decoder. Calibrated MWPM gets the exact $X$ and $Z$ marginals of each local posterior. Belief matching uses a four-state posterior before matching. Global joint **configuration** MAP keeps $Y$ as one event and enforces all detector constraints. A separate exhaustive **logical-class** MAP reference sums all $4^9$ fault configurations for homogeneous no-flag channels. Uniform MWPM is a secondary weak reference; it is not the success benchmark.

## Held-out results

| Memory, channel | Shots | Calibrated MWPM logical failures | Belief matching | Joint configuration MAP | MAP gain over calibrated MWPM, 95% paired interval |
|---|---:|---:|---:|---:|---:|
| Z, $p_Y=0$, $p_X=p_Z=0.2\%$, no flag | 5,000 | 0 | 0 | 0 | Uninformative low-rate control |
| Z, $p_Y=1\%$, $p_X=p_Z=0.2\%$, no flag | 5,000 | 6 | 5 | 4 | 0.04 points, −0.06 to 0.14 |
| **Z, $p_Y=3\%$, $p_X=p_Z=0.2\%$, no flag** | **20,000** | **319 (1.595%)** | **134 (0.670%)** | **67 (0.335%)** | **1.260 points, 1.090 to 1.425** |
| Z, $p_Y=0$, $p_X=p_Z=3.2\%$, no flag: **same marginal $X/Z$ rates as preceding row** | 20,000 | 307 (1.535%) | 307 (1.535%) | 308 (1.540%) | −0.005 points, −0.025 to 0.010 |
| Z, $p_Y=3\%$, $p_X=p_Z=0.2\%$, noisy flag | 20,000 | 324 (1.620%) | 96 (0.480%) | 52 (0.260%) | 1.360 points, 1.200 to 1.535 |
| Z, $p_Y=5\%$, $p_X=p_Z=0.2\%$, noisy flag | 5,000 | 189 (3.780%) | 51 (1.020%) | 23 (0.460%) | 3.320 points, 2.840 to 3.860 |
| X, $p_Y=3\%$, $p_X=p_Z=0.2\%$, noisy flag | 5,000 | 86 (1.720%) | 22 (0.440%) | 15 (0.300%) | 1.420 points, 1.100 to 1.780 |

The predeclared primary no-flag $3\%$ joint channel passes the **effective-channel logical accuracy gate**. MAP's paired gain over belief matching is 0.335 percentage points (95% interval 0.245 to 0.425). The exhaustive logical-class reference also has **67/20,000** failures in that arm; configuration MAP reaches its observed rate, though equal counts alone do not prove identical shot-level predictions. No MAP optimization timed out or needed a matching fallback.

The matched-marginal control is the key mechanism check: it gives MWPM the **same 3.2% $X$ and $Z$ marginals** as the $p_Y=3\%$ channel but removes the joint event. Its MAP–MWPM difference is unresolved and essentially zero. This supports the interpretation that the primary gain comes from modeling the cross-parity common cause, not from an increased marginal error rate. The 1% arm is also unresolved at its shot count. The 0% low-rate arm has no failures and cannot establish decoder equivalence.

## Decision and next gate

**Go for the narrow algorithmic claim:** a global four-state hypergraph decoder lowers **bounded logical-memory failure** versus equally informed calibrated MWPM and belief matching when the declared fusion-type $XX/ZZ$ correlation occurs at the tested effective-channel rate. This is stronger than the earlier periodic-sector proxy because it scores a genuine finite-memory logical observable. It is not yet a photonic device or native FBQC result. The injected $Y$ adapter, fault incidence, and noisy flag are assumptions; the flag arms use different random shots from the no-flag arm, so their rate difference is not a paired metadata-effect estimate.

**No-go for a physical fusion advantage claim yet.** Derive or measure the ancilla-free encoded fusion's $P(R,A\mid\theta)$ and incidence for a named common-cause mechanism, including nonconclusive records and unsupported coherent actions. Propagate its admitted actions through a native bounded encoded six-ring memory with boundaries and a declared logical observable. Then repeat the identical-shot calibrated MWPM, belief-matching, and joint-MAP matrix across the frozen physical grid. Only after that accuracy gate passes should the project tune a selective threshold or benchmark online runtime.
