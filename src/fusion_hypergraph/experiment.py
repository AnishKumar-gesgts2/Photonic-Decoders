from __future__ import annotations

import csv
import json
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np

from .data import iter_shards, load_manifest
from .decoder import MinSumHypergraphDecoder
from .lattice import build_lattice
from .matching import ProjectedMatchingDecoder
from .physics import emission_table, local_costs, state_priors


RESULT_FIELDS = (
    "scenario_id",
    "method",
    "distance",
    "rounds",
    "num_sites",
    "physical_error_rate",
    "detector_efficiency",
    "visibility",
    "shots",
    "logical_failures",
    "wall_seconds",
    "mean_iterations",
    "converged_fraction",
    "syndrome_consistent_fraction",
)


def run_benchmark(
    config: dict[str, Any], data_dir: Path, output_dir: Path, workers: int = 1
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    prediction_dir = output_dir / "predictions"
    prediction_dir.mkdir(exist_ok=True)
    manifest = load_manifest(data_dir)
    _validate_manifest(config, manifest)
    raw_path = output_dir / "raw_results.csv"

    with raw_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=RESULT_FIELDS)
        writer.writeheader()
        scenario_list = manifest["scenarios"]
        if workers > 1:
            executor = ProcessPoolExecutor(max_workers=workers)
            result_iterator = executor.map(
                _run_scenario_job,
                [(config, str(data_dir), scenario) for scenario in scenario_list],
            )
        else:
            executor = None
            result_iterator = (_run_scenario(config, data_dir, scenario) for scenario in scenario_list)
        for scenario, scenario_results in zip(scenario_list, result_iterator):
            np.savez_compressed(
                prediction_dir / f"{scenario['id']}.npz",
                **{method: values["failures"] for method, values in scenario_results.items()},
            )
            for method, values in scenario_results.items():
                writer.writerow(
                    {
                        "scenario_id": scenario["id"],
                        "method": method,
                        "distance": scenario["distance"],
                        "rounds": scenario["rounds"],
                        "num_sites": scenario["distance"] ** 2 * scenario["rounds"],
                        "physical_error_rate": scenario["physical_error_rate"],
                        "detector_efficiency": scenario["detector_efficiency"],
                        "visibility": scenario["visibility"],
                        "shots": len(values["failures"]),
                        "logical_failures": int(values["failures"].sum()),
                        "wall_seconds": values["wall_seconds"],
                        "mean_iterations": _safe_mean(values["iterations"]),
                        "converged_fraction": _safe_mean(values["converged"]),
                        "syndrome_consistent_fraction": _safe_mean(values["consistent"]),
                    }
                )
            stream.flush()
        if executor is not None:
            executor.shutdown()
    (output_dir / "run_metadata.json").write_text(
        json.dumps({"config": config, "data_manifest": str(data_dir / "manifest.json")}, indent=2),
        encoding="utf-8",
    )
    return raw_path


def _run_scenario_job(
    job: tuple[dict[str, Any], str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    config, data_dir, scenario = job
    return _run_scenario(config, Path(data_dir), scenario)


def _run_scenario(
    config: dict[str, Any], data_dir: Path, scenario: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    lattice = build_lattice(int(scenario["distance"]), int(scenario["rounds"]))
    physics = config["physics"]
    priors = state_priors(
        float(scenario["physical_error_rate"]),
        float(physics["correlated_fraction"]),
        float(physics["multiphoton_fraction"]),
    )
    table = emission_table(float(scenario["detector_efficiency"]), float(scenario["visibility"]))
    bp = MinSumHypergraphDecoder(lattice, **{
        key: config["decoder"][key] for key in ("max_iterations", "damping", "tolerance")
    })
    mwpm = ProjectedMatchingDecoder(lattice, config["decoder"]["boundary_weight"])
    methods = list(config["methods"])
    collected: dict[str, dict[str, list[Any] | float]] = {
        method: {"failures": [], "iterations": [], "converged": [], "consistent": [], "wall_seconds": 0.0}
        for method in methods
    }

    for shard in iter_shards(data_dir, scenario):
        for shot in range(len(shard["logicals"])):
            syndrome = shard["syndromes"][shot]
            truth = int(shard["logicals"][shot])
            true_states = shard["states"][shot]
            outcome = shard["outcomes"][shot]
            pnr = shard["pnr"][shot]
            cost_cache = {
                mode: local_costs(priors, table, outcome, pnr, mode, true_states)
                for mode in ("marginal", "metadata", "oracle")
            }
            for method in methods:
                start = time.perf_counter()
                if method == "uniform_mwpm":
                    prediction = mwpm.decode(syndrome, cost_cache["marginal"], uniform=True)
                    result = None
                elif method == "calibrated_mwpm":
                    prediction = mwpm.decode(syndrome, cost_cache["marginal"])
                    result = None
                elif method == "metadata_mwpm":
                    prediction = mwpm.decode(syndrome, cost_cache["metadata"])
                    result = None
                elif method in {"marginal_bp", "metadata_bp", "oracle_bp"}:
                    mode = method.removesuffix("_bp")
                    result = bp.decode(syndrome, cost_cache[mode])
                    prediction = result.logical
                else:
                    raise ValueError(f"Unknown method: {method}")
                elapsed = time.perf_counter() - start
                target = collected[method]
                target["failures"].append(prediction != truth)
                target["wall_seconds"] = float(target["wall_seconds"]) + elapsed
                if result is not None:
                    target["iterations"].append(result.iterations)
                    target["converged"].append(result.converged)
                    target["consistent"].append(np.array_equal(lattice.syndrome(result.states), syndrome))

    finalized: dict[str, dict[str, Any]] = {}
    for method, values in collected.items():
        finalized[method] = {
            "failures": np.asarray(values["failures"], dtype=np.bool_),
            "iterations": np.asarray(values["iterations"], dtype=float),
            "converged": np.asarray(values["converged"], dtype=float),
            "consistent": np.asarray(values["consistent"], dtype=float),
            "wall_seconds": float(values["wall_seconds"]),
        }
    return finalized


def _safe_mean(values: np.ndarray) -> float:
    return float(values.mean()) if values.size else float("nan")


def _validate_manifest(config: dict[str, Any], manifest: dict[str, Any]) -> None:
    if manifest.get("schema_version") != 1:
        raise ValueError("Unsupported dataset schema")
    generated = manifest["config"]
    keys = ("seed", "shots", "shard_size", "physics")
    if any(generated[key] != config[key] for key in keys):
        raise ValueError("Runtime config does not match the dataset-generation config")
