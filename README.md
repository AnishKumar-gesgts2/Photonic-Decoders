# Quantum Research

This Obsidian vault contains quantum photonics and quantum information research. The existing decoder work and the new Gaussian boson sampling (GBS) classical-simulation project live in separate folders.

- [Quantum Research index](Quantum%20Research.md)
- [GBS classical-simulation project description](GBS%20Classical%20Simulation/GBS%20Classical%20Simulation%20Project%20Description.md)
- [GBS research plan and preliminary evidence](GBS%20Classical%20Simulation/Correlation-Based%20Classical%20Simulation%20of%20GBS.md)

## Photonic decoder work

The decoder landscape review and reproducible test harness for the **Fusion-Hypergraph Decoder** remain in this repository.

- [Photonic Decoder Evaluations](Photonic%20Decoder%20Evaluations.md)
- [Hypergraph decoder project](Hypergraph/Fusion%20Hypergraph%20Decoder%20Test%20Plan.md)

Quick start:

```powershell
Set-Location Hypergraph
python -m venv .venv
.venv\Scripts\pip install -e ".[dev]"
fusion-hypergraph all --config configs/smoke.toml --workdir runs/smoke
pytest
```

The smoke configuration checks the pipeline. `configs/full_scale.toml` is the research sweep and should be run on appropriately provisioned compute.
