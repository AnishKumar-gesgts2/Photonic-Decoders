from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator

import numpy as np

from .config import scenario_id, scenarios, stable_seed
from .lattice import build_lattice
from .physics import emission_table, sample_observations, state_priors


def generate_data(config: dict[str, Any], output_dir: Path) -> Path:
    """Generate deterministic, compressed shards and an auditable manifest."""
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {"schema_version": 1, "config": config, "scenarios": []}
    physics = config["physics"]

    for scenario in scenarios(config):
        sid = scenario_id(scenario)
        lattice = build_lattice(scenario["distance"], scenario["rounds"])
        priors = state_priors(
            scenario["physical_error_rate"],
            physics["correlated_fraction"],
            physics["multiphoton_fraction"],
        )
        table = emission_table(scenario["detector_efficiency"], scenario["visibility"])
        files: list[str] = []
        for start in range(0, int(config["shots"]), int(config["shard_size"])):
            count = min(int(config["shard_size"]), int(config["shots"]) - start)
            states = np.empty((count, lattice.num_sites), dtype=np.uint8)
            syndromes = np.empty((count, lattice.num_detectors), dtype=np.uint8)
            outcomes = np.empty_like(states)
            pnr = np.empty_like(states)
            logicals = np.empty(count, dtype=np.uint8)
            for offset in range(count):
                shot = start + offset
                rng = np.random.default_rng(stable_seed(config["seed"], sid, shot))
                state = rng.choice(len(priors), size=lattice.num_sites, p=priors).astype(np.uint8)
                outcome, photon_count = sample_observations(rng, state, table)
                states[offset] = state
                syndromes[offset] = lattice.syndrome(state)
                outcomes[offset] = outcome
                pnr[offset] = photon_count
                logicals[offset] = lattice.logical(state)

            file_name = f"{sid}_shots{start:07d}-{start + count - 1:07d}.npz"
            np.savez_compressed(
                output_dir / file_name,
                states=states,
                syndromes=syndromes,
                outcomes=outcomes,
                pnr=pnr,
                logicals=logicals,
            )
            files.append(file_name)
        manifest["scenarios"].append({"id": sid, **scenario, "files": files})

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest_path


def load_manifest(data_dir: Path) -> dict[str, Any]:
    return json.loads((data_dir / "manifest.json").read_text(encoding="utf-8"))


def iter_shards(data_dir: Path, scenario: dict[str, Any]) -> Iterator[dict[str, np.ndarray]]:
    for file_name in scenario["files"]:
        with np.load(data_dir / file_name, allow_pickle=False) as values:
            yield {name: values[name] for name in values.files}

