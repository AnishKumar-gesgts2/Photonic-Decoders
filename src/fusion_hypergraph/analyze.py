from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any

import numpy as np


def wilson_interval(failures: int, shots: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if shots == 0:
        return float("nan"), float("nan")
    p = failures / shots
    denominator = 1 + z * z / shots
    center = (p + z * z / (2 * shots)) / denominator
    radius = z * math.sqrt(p * (1 - p) / shots + z * z / (4 * shots * shots)) / denominator
    return center - radius, center + radius


def process_results(result_dir: Path, seed: int = 99173, bootstrap_samples: int = 4000) -> Path:
    raw_path = result_dir / "raw_results.csv"
    with raw_path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    grouped = {row["scenario_id"]: [] for row in rows}
    for row in rows:
        grouped[row["scenario_id"]].append(row)

    output_rows: list[dict[str, Any]] = []
    rng = np.random.default_rng(seed)
    for sid, scenario_rows in grouped.items():
        with np.load(result_dir / "predictions" / f"{sid}.npz", allow_pickle=False) as loaded:
            predictions = {name: loaded[name].astype(float) for name in loaded.files}
        baseline_names = [name for name in ("calibrated_mwpm", "marginal_bp") if name in predictions]
        best_baseline = min(baseline_names, key=lambda name: predictions[name].mean()) if baseline_names else None
        for row in scenario_rows:
            shots = int(row["shots"])
            failures = int(row["logical_failures"])
            low, high = wilson_interval(failures, shots)
            processed = dict(row)
            processed.update(
                logical_error_rate=failures / shots,
                ci95_low=low,
                ci95_high=high,
                shots_per_second=shots / float(row["wall_seconds"]),
                best_syndrome_baseline=best_baseline or "",
                delta_info="",
                delta_info_ci95_low="",
                delta_info_ci95_high="",
            )
            if row["method"] == "metadata_bp" and best_baseline:
                paired = predictions[best_baseline] - predictions["metadata_bp"]
                # Chunking bounds memory even for publication-scale shot counts.
                chunks: list[np.ndarray] = []
                for start in range(0, bootstrap_samples, 200):
                    count = min(200, bootstrap_samples - start)
                    draws = rng.integers(0, shots, size=(count, shots))
                    chunks.append(paired[draws].mean(axis=1))
                samples = np.concatenate(chunks)
                processed["delta_info"] = float(paired.mean())
                processed["delta_info_ci95_low"] = float(np.quantile(samples, 0.025))
                processed["delta_info_ci95_high"] = float(np.quantile(samples, 0.975))
            output_rows.append(processed)

    summary_path = result_dir / "summary.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(output_rows[0]))
        writer.writeheader()
        writer.writerows(output_rows)
    return summary_path
