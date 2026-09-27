# Phase 0: six-ring fusion information gate

The current decision is **no-go for a physically grounded ancilla-free logical advantage**. The [paper-source follow-up](PAPER_SOURCE_CHANNEL_RESULTS.md) explains the latest complete-mixture tests; the [project plan](../Fusion%20Hypergraph%20Decoder%20Test%20Plan.md) defines the remaining gate.

Run from the `Hypergraph` directory. The first command runs the tests. The two paper-source commands reproduce the latest sensitivity results. Earlier experiment commands are retained below for their linked evidence.

```powershell
$env:PYTHONPATH='phase0'
.\.venv\Scripts\python.exe -m pytest phase0 tests -q
.\.venv\Scripts\python.exe phase0\run_paper_source_sensitivity.py
.\.venv\Scripts\python.exe phase0\run_paper_encoded_channel.py
```

Earlier experiments:

```powershell
.\.venv\Scripts\python.exe phase0\restart_phase0.py
.\.venv\Scripts\python.exe phase0\run_encoded_phase0.py
.\.venv\Scripts\python.exe phase0\run_bounded_optical_d3.py
.\.venv\Scripts\python.exe phase0\run_bounded_optical_d3.py --excess-audit
.\.venv\Scripts\python.exe phase0\ancilla_free_information_gate.py
.\.venv\Scripts\python.exe phase0\run_ancilla_free_decoder_proxy.py
.\.venv\Scripts\python.exe phase0\run_bounded_joint_logical.py
.\.venv\Scripts\python.exe phase0\run_ancilla_free_pauli_gate.py
.\.venv\Scripts\python.exe phase0\run_six_ring_physical_gate.py
```

The [result](RESULTS.md) and `outputs/phase0_restart/results.json` contain the current evidence. The small exact optical model uses one dual-rail Bell analyzer on two maximally mixed six-ring ports, detector efficiency 0.95, and an explicitly assumed 5% incidence of an extra mode-matched photon. Stim derives the local check signatures of a periodic 3×3×3 six-ring bulk. The run audits measurable checks before attempting decoder comparison.

The current architecture fails the information and fusion-success gates. A bounded-memory logical comparison requires a characterized nonconclusive quantum instrument and a boosted or encoded architecture; the code refuses to infer either from a PNR class.

The boosted/encoded [follow-on](ENCODED_RESULTS.md) reuses the Stim six-ring checks and implements the paper's four-physical-fusion parity availability. It compares metadata and decoder combinations on held-out diagnostic sectors, including an efficiency shift, Bell-branch sensitivity, and zero-joint-fault control. It uses assumed parity-flip rates because the published boosted experiment does not provide our fault's record-conditioned optical action.

The [bounded optical follow-up](BOUNDED_OPTICAL_D3_RESULTS.md) computes exact ideal four-photon PNR likelihoods for a specified ancilla phase fault, reconstructs encoded parity observations, and benchmarks a three-round Stim d=3 surface-code memory proxy. It shows a metadata gain for MWPM but no resolved additional joint-decoder gain for this single-axis fault. Its ideal optics and teleportation-frame adapter are explicit model assumptions, not experimental or native six-ring validation.

The same follow-up audits a specified five-photon input with detector loss. Some one-loss records mimic a conclusive four-photon BSM, but their conditional Bell-basis state has coherent terms, so the present Stim Pauli adapter cannot score them as logical faults without a justified further reduction.

The ancilla-free encoded [information gate](ANCILLA_FREE_INFORMATION_RESULTS.md) exactly enumerates the four physical BSM record classes and parity availability under declared independent-outcome assumptions. It compares the two-photon, no-BSM-ancilla case with the ancillary-pair boosted reference and counts photons attempted. It does not contain a native bounded logical decoder comparison.

The [ancilla-free joint-MAP proxy result](ANCILLA_FREE_DECODER_PROXY_RESULTS.md) compares global categorical hypergraph configuration MAP, equally informed metadata-aware MWPM, and belief matching on held-out six-ring periodic sectors. It uses a separately tuned selector and a core-versus-detailed metadata ablation. Its joint fault rate and action are sensitivity assumptions; the optical-to-native-memory gates remain open.

The [accuracy-first bounded logical result](BOUNDED_JOINT_LOGICAL_RESULTS.md) maps a declared joint fusion parity fault to one data-qubit $Y$ event in a three-round Stim surface-code memory. It compares calibrated MWPM, belief matching, global joint configuration MAP, and a no-flag exact logical-class reference on a finite logical observable, including a matched-marginal no-correlation control. This establishes an effective-channel decoder result; native six-ring and optical-action validation remain open.

The [improved-idea go/no-go audit](IMPROVED_IDEA_GO_NO_GO.md) tests a specific Pauli $Y$ input fault in the ideal ancilla-free Fock instrument, then enumerates its encoded actions and checks the current decoder and native-memory gates. It passes the local optical-action gate but cannot pass the physical logical-advantage gate without a source incidence and native bounded encoded six-ring memory.

The [physical-channel action audit](PHYSICAL_CHANNEL_AUDIT.md) then checks Bell-basis coherence in every accepted optical record. It finds that the older extra-plus-photon diagonal projection discarded coherent terms, so its quoted joint-$Y$ rate is withdrawn as a physical Pauli-channel probability. The optical compiler now rejects that conversion. This leaves the physical decoder go gate unpassed even though the effective-channel MAP sensitivity test remains valid.

The [paper-source follow-up](PAPER_SOURCE_CHANNEL_RESULTS.md) tests complete published first-order Pauli mixtures over a fixed grid. Exact $d=3$ logical scoring finds modest configuration-MAP gains in the three-level model and losses to calibrated MWPM for biased four-level Z memory; optimal logical-class MAP does slightly better. A separate exact ancilla-free four-BSM enumeration produces a local record/action table under independent source-photon errors and detector survival. These are source-model sensitivity calculations, with no measured device parameters or native finite six-ring logical memory. The physical decoder-advantage decision remains **NO-GO**.
