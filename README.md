# Photonic Decoders

The repository contains the decoder landscape review and a reproducible test harness for its top-ranked **Fusion-Hypergraph Decoder** proposal.

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
