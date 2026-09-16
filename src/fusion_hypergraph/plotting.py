from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np


LABELS = {
    "uniform_mwpm": "Uniform MWPM",
    "calibrated_mwpm": "Calibrated MWPM",
    "metadata_mwpm": "Metadata MWPM (graph projection)",
    "marginal_bp": "Hypergraph BP, syndrome only",
    "metadata_bp": "Hypergraph BP + optical metadata",
    "oracle_bp": "Oracle latent-state bound",
}


def make_plots(summary_path: Path, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    with summary_path.open(newline="", encoding="utf-8") as stream:
        rows = [_typed(row) for row in csv.DictReader(stream)]
    paths = [
        _logical_scaling(rows, output_dir),
        _information_gain(rows, output_dir),
        _runtime_scaling(rows, output_dir),
        _convergence(rows, output_dir),
    ]
    return paths


def _logical_scaling(rows: list[dict[str, Any]], output_dir: Path) -> Path:
    max_eff = max(row["detector_efficiency"] for row in rows)
    max_vis = max(row["visibility"] for row in rows)
    selected = [
        row for row in rows
        if row["detector_efficiency"] == max_eff and row["visibility"] == max_vis
    ]
    fig, ax = plt.subplots(figsize=(8.0, 5.2), constrained_layout=True)
    groups: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in selected:
        groups[(row["method"], row["distance"])].append(row)
    for (method, distance), values in sorted(groups.items()):
        values.sort(key=lambda row: row["physical_error_rate"])
        x = np.array([row["physical_error_rate"] for row in values])
        y = np.array([row["logical_error_rate"] for row in values])
        low = np.array([row["ci95_low"] for row in values])
        high = np.array([row["ci95_high"] for row in values])
        ax.errorbar(
            x,
            y,
            yerr=np.vstack((y - low, high - y)),
            marker="o",
            capsize=2,
            label=f"{LABELS.get(method, method)}, d={distance}",
        )
    ax.set(xlabel="Physical fault probability", ylabel="Logical error rate")
    ax.set_yscale("log")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=7, ncol=2)
    return _save(fig, output_dir / "logical_error_scaling")


def _information_gain(rows: list[dict[str, Any]], output_dir: Path) -> Path:
    metadata = [row for row in rows if row["method"] == "metadata_bp" and row["delta_info"] != ""]
    efficiencies = sorted({row["detector_efficiency"] for row in metadata})
    visibilities = sorted({row["visibility"] for row in metadata})
    grid = np.full((len(efficiencies), len(visibilities)), np.nan)
    for i, efficiency in enumerate(efficiencies):
        for j, visibility in enumerate(visibilities):
            values = [
                row["delta_info"] for row in metadata
                if row["detector_efficiency"] == efficiency and row["visibility"] == visibility
            ]
            if values:
                grid[i, j] = float(np.mean(values))
    fig, ax = plt.subplots(figsize=(7.0, 5.2), constrained_layout=True)
    image = ax.imshow(grid, origin="lower", aspect="auto", cmap="coolwarm")
    ax.set_xticks(range(len(visibilities)), [f"{x:.3g}" for x in visibilities])
    ax.set_yticks(range(len(efficiencies)), [f"{x:.3g}" for x in efficiencies])
    ax.set(xlabel="HOM visibility", ylabel="Detector efficiency", title="Mean information advantage Δinfo")
    fig.colorbar(image, ax=ax, label="Baseline logical error − metadata-BP logical error")
    return _save(fig, output_dir / "information_gain_heatmap")


def _runtime_scaling(rows: list[dict[str, Any]], output_dir: Path) -> Path:
    fig, ax = plt.subplots(figsize=(7.5, 5.0), constrained_layout=True)
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[row["method"]].append(row)
    for method, values in groups.items():
        by_size: dict[int, list[float]] = defaultdict(list)
        for row in values:
            by_size[row["num_sites"]].append(row["shots_per_second"])
        x = np.array(sorted(by_size))
        y = np.array([np.median(by_size[size]) for size in x])
        ax.plot(x, y, marker="o", label=LABELS.get(method, method))
    ax.set(xlabel="Fusion sites", ylabel="Median throughput (shots/s)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=8)
    return _save(fig, output_dir / "runtime_scaling")


def _convergence(rows: list[dict[str, Any]], output_dir: Path) -> Path:
    bp_rows = [row for row in rows if row["method"].endswith("_bp")]
    methods = sorted({row["method"] for row in bp_rows})
    values = [np.mean([row["converged_fraction"] for row in bp_rows if row["method"] == method]) for method in methods]
    fig, ax = plt.subplots(figsize=(7.0, 4.5), constrained_layout=True)
    ax.bar([LABELS.get(method, method) for method in methods], values)
    ax.set(ylabel="Converged fraction", ylim=(0, 1.02))
    ax.tick_params(axis="x", rotation=15)
    ax.grid(True, axis="y", alpha=0.25)
    return _save(fig, output_dir / "bp_convergence")


def _save(fig: plt.Figure, stem: Path) -> Path:
    png = stem.with_suffix(".png")
    fig.savefig(png, dpi=200)
    fig.savefig(stem.with_suffix(".pdf"))
    plt.close(fig)
    return png


def _typed(row: dict[str, str]) -> dict[str, Any]:
    integers = {"distance", "rounds", "num_sites", "shots", "logical_failures"}
    floats = {
        "physical_error_rate", "detector_efficiency", "visibility", "wall_seconds",
        "mean_iterations", "converged_fraction", "syndrome_consistent_fraction",
        "logical_error_rate", "ci95_low", "ci95_high", "shots_per_second",
        "delta_info", "delta_info_ci95_low", "delta_info_ci95_high",
    }
    typed: dict[str, Any] = {}
    for key, value in row.items():
        if value == "":
            typed[key] = ""
        elif key in integers:
            typed[key] = int(value)
        elif key in floats:
            typed[key] = float(value)
        else:
            typed[key] = value
    return typed

