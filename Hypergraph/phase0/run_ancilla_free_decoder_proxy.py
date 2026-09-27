"""Held-out ancilla-free encoded six-ring *periodic-sector proxy* comparison.

Joint four-state fault probabilities are explicit sensitivity assumptions.
No result from this file is a native bounded-memory or measured-source claim.
"""
from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter

import numpy as np

from encoded_proxy import (belief_priors, contracted_checks, deform_sectors,
                           fit_priors, matching_prediction, prior_for, sample_shots)
from joint_map import decode as joint_map_decode
from native_ring_bulk import validate_bulk
from run_encoded_phase0 import wilson


def evaluate(data: dict, fitted: dict, coarse: dict,
             level: str = "all") -> dict:
    bulk = validate_bulk(3)
    h, logicals = bulk["checks"], bulk["logicals"]
    shots = len(data["hard"])
    failures = {name: np.zeros(shots, dtype=bool)
                for name in ("mwpm", "belief_matching", "joint_map")}
    score = np.zeros(shots)
    erased = np.zeros(shots, dtype=bool)
    fallback = 0
    elapsed = {name: 0.0 for name in failures}
    for row in range(shots):
        known = data["known"][row]
        deformed = deform_sectors(h, logicals, known)
        if deformed is None:
            erased[row] = True
            for values in failures.values():
                values[row] = True
            continue
        checks = contracted_checks(h, known)
        syndrome = (checks @ data["hard"][row]) & 1
        truth = (deformed @ data["errors"][row]) & 1
        priors = np.asarray([prior_for(data, row, j, level, fitted, coarse)
                             for j in range(bulk["fusions"])])
        # This is calculated only from measured record classes/disagreement flags.
        score[row] = float(np.max(priors[:, 3]))
        start = perf_counter()
        mwpm = matching_prediction(checks, deformed, syndrome, priors)
        elapsed["mwpm"] += perf_counter() - start
        start = perf_counter()
        belief = matching_prediction(
            checks, deformed, syndrome, belief_priors(checks, syndrome, priors))
        elapsed["belief_matching"] += perf_counter() - start
        start = perf_counter()
        joint, solved = joint_map_decode(checks, deformed, syndrome, priors)
        elapsed["joint_map"] += perf_counter() - start
        if not solved:
            fallback += 1
            joint = mwpm
        for name, prediction in (("mwpm", mwpm),
                                 ("belief_matching", belief),
                                 ("joint_map", joint)):
            failures[name][row] = bool(np.any(prediction != truth))
    return {"failures": failures, "score": score, "erased": erased,
            "map_fallbacks": fallback, "elapsed_seconds": elapsed}


def paired(first: np.ndarray, second: np.ndarray, seed: int) -> dict:
    difference = first.astype(np.int8) - second.astype(np.int8)
    rng = np.random.default_rng(seed)
    estimates = np.empty(2000)
    for i in range(len(estimates)):
        estimates[i] = difference[rng.integers(0, len(difference), len(difference))].mean()
    return {"gain": float(difference.mean()),
            "gain_ci_95": np.quantile(estimates, [.025, .975]).tolist(),
            "mwpm_only_failures": int(np.count_nonzero(first & ~second)),
            "other_only_failures": int(np.count_nonzero(second & ~first))}


def metadata_interaction(core: dict, detailed: dict, seed: int) -> dict:
    """Paired change in metadata benefit: MAP minus MWPM."""
    a, b = core["failures"], detailed["failures"]
    mwpm_gain = a["mwpm"].astype(np.int8) - b["mwpm"].astype(np.int8)
    map_gain = a["joint_map"].astype(np.int8) - b["joint_map"].astype(np.int8)
    contrast = map_gain - mwpm_gain
    rng = np.random.default_rng(seed)
    draws = np.empty(2000)
    for i in range(len(draws)):
        draws[i] = contrast[rng.integers(0, len(contrast), len(contrast))].mean()
    return {"metadata_gain_mwpm": float(mwpm_gain.mean()),
            "metadata_gain_joint_map": float(map_gain.mean()),
            "extra_metadata_gain_for_joint_map": float(contrast.mean()),
            "extra_gain_ci_95": np.quantile(draws, [.025, .975]).tolist()}


def choose_threshold(tune: dict, latency_penalty: float = 0.0005) -> dict:
    """Lock a single global threshold on an independent tuning split."""
    score = tune["score"]
    candidates = sorted(set(float(x) for x in np.quantile(
        score[~tune["erased"]], np.linspace(0, 1, 21))))
    candidates.append(float("inf"))
    baseline = tune["failures"]["mwpm"]
    joint = tune["failures"]["joint_map"]
    rows = []
    for threshold in candidates:
        active = (~tune["erased"]) & (score >= threshold)
        selected = np.where(active, joint, baseline)
        gain = float(baseline.mean() - selected.mean())
        fraction = float(active.mean())
        rows.append({"threshold": threshold, "gain": gain,
                     "activation": fraction,
                     "objective": gain - latency_penalty*fraction})
    best = max(rows, key=lambda row: (row["objective"], -row["activation"]))
    return {"threshold": best["threshold"],
            "latency_penalty_per_activated_shot": latency_penalty,
            "tuning_gain": best["gain"],
            "tuning_activation": best["activation"],
            "candidate_count": len(rows)}


def summarize(evaluated: dict, threshold: float, seed: int) -> dict:
    failures = dict(evaluated["failures"])
    active = (~evaluated["erased"]) & (evaluated["score"] >= threshold)
    failures["locked_selector"] = np.where(active, failures["joint_map"], failures["mwpm"])
    shots = len(active)
    baseline = failures["mwpm"]
    arms = {}
    for name, values in failures.items():
        count = int(values.sum())
        arms[name] = {"failures": count, "rate": count/shots,
                      "wilson_95": wilson(count, shots)}
        if name != "mwpm":
            arms[name]["paired_vs_equally_informed_mwpm"] = paired(
                baseline, values, seed + len(arms))
    return {"shots": shots, "erased_sector_fraction": float(evaluated["erased"].mean()),
            "map_fallbacks": evaluated["map_fallbacks"],
            "selector_activation_fraction": float(active.mean()),
            "arms": arms,
            "mean_cpu_seconds_on_non_erased": {
                name: seconds/max(1, shots-int(evaluated["erased"].sum()))
                for name, seconds in evaluated["elapsed_seconds"].items()}}


def run(output: Path, train_shots: int = 12_000, tune_shots: int = 1_500,
        heldout_shots: int = 5_000) -> dict:
    settings = {"nominal": (.995, .005),
                "zero_joint": (.995, 0.0),
                "shifted": (.986, .007)}
    independent_flip = .002
    train = sample_shots(train_shots, .995, .5, independent_flip, .005,
                         260926, photons_per_bsm=2)
    coarse = fit_priors(train, "coarse")
    classes = fit_priors(train, "classes")
    fitted = fit_priors(train, "all")
    zero_train = sample_shots(train_shots, .995, .5, independent_flip, 0.0,
                              261926, photons_per_bsm=2)
    zero_coarse = fit_priors(zero_train, "coarse")
    zero_fitted = fit_priors(zero_train, "all")
    tune_data = sample_shots(tune_shots, .995, .5, independent_flip, .005,
                             270926, photons_per_bsm=2)
    locked = choose_threshold(evaluate(tune_data, fitted, coarse))
    results = {}
    for index, (name, (efficiency, joint_flip)) in enumerate(settings.items()):
        data = sample_shots(heldout_shots, efficiency, .5, independent_flip,
                            joint_flip, 280926 + 10000*index,
                            photons_per_bsm=2)
        cell_fitted, cell_coarse = ((zero_fitted, zero_coarse) if name == "zero_joint"
                                    else (fitted, coarse))
        detailed_evaluation = evaluate(data, cell_fitted, cell_coarse)
        results[name] = {"photon_efficiency": efficiency,
                         "assumed_joint_fault_rate": joint_flip,
                         "calibration": "zero-joint" if name == "zero_joint" else "nominal",
                         **summarize(detailed_evaluation,
                                     locked["threshold"], 290926 + index)}
        if name == "nominal":
            core_evaluation = evaluate(data, classes, coarse, level="classes")
            results[name]["core_record"] = summarize(
                core_evaluation,
                float("inf"), 390926)
            results[name]["metadata_interaction"] = metadata_interaction(
                core_evaluation, detailed_evaluation, 490926)
            results[name]["joint_map_vs_belief_matching"] = paired(
                detailed_evaluation["failures"]["belief_matching"],
                detailed_evaluation["failures"]["joint_map"], 590926)
    report = {"schema_version": "phase0-ancilla-free-periodic-proxy-v1",
              "architecture": "ancilla-free two-photon BSM; four physical BSMs per encoded fusion",
              "fault_model": "independent physical parity flips 0.2%; joint A-fusion XX/ZZ flip sensitivity axis, not optical calibration",
              "observable_features": "encoded parity availability, physical full/partial/lost classes, redundant parity disagreements; identical for all decoders",
              "decoder_scope": "global joint-configuration MAP integer program versus record-conditioned erasure-aware MWPM and joint BP followed by matching",
              "outcome_scope": "three nonlocal periodic sectors, not a bounded-memory logical failure rate",
              "split_seeds": {"training": 260926, "zero_joint_training": 261926,
                              "threshold_tuning": 270926,
                              "heldout": [280926, 290926, 300926]},
              "split_sizes": {"training": train_shots, "threshold_tuning": tune_shots,
                              "heldout_per_setting": heldout_shots},
              "locked_selector": locked, "settings": results}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    result = run(Path("outputs/phase0_ancilla_free_decoder_proxy/results.json"))
    for name, case in result["settings"].items():
        print(name, case["erased_sector_fraction"],
              {arm: item["rate"] for arm, item in case["arms"].items()})
