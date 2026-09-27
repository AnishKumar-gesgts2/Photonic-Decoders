"""Paired encoded-fusion parity-sector benchmark with declared proxy noise."""
from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter

import numpy as np

from boosted_encoded import theoretical_no_loss_full
from encoded_proxy import (belief_priors, contracted_checks, deform_sectors,
                           fit_priors, matching_prediction,
                           prior_for, sample_shots)
from native_ring_bulk import validate_bulk


ARMS = (("coarse_mwpm", "coarse", False),
        ("flags_mwpm", "flags", False),
        ("classes_mwpm", "classes", False),
        ("all_classes_mwpm", "all", False),
        ("coarse_joint_bp_mwpm", "coarse", True),
        ("flags_joint_bp_mwpm", "flags", True),
        ("classes_joint_bp_mwpm", "classes", True),
        ("all_classes_joint_bp_mwpm", "all", True),
        ("selective_all_classes_bp_mwpm", "all", "selective"),
        ("shuffled_flags_joint_bp_mwpm", "shuffled_all", True))


def wilson(failures: int, shots: int) -> list[float]:
    if shots == 0:
        return [float("nan"), float("nan")]
    z = 1.959963984540054
    p = failures/shots
    denominator = 1 + z*z/shots
    center = (p + z*z/(2*shots))/denominator
    radius = z*np.sqrt(p*(1-p)/shots + z*z/(4*shots*shots))/denominator
    return [float(center-radius), float(center+radius)]


def compare(efficiency: float, train_shots: int, heldout_shots: int,
            independent_flip: float = .002, joint_flip: float = .005,
            success: float = .693, seed: int = 9026,
            test_efficiency: float | None = None,
            test_independent_flip: float | None = None,
            test_joint_flip: float | None = None,
            test_branch_conditioned: bool = False) -> dict:
    train = sample_shots(train_shots, efficiency, success,
                         independent_flip, joint_flip, seed)
    test_eta = efficiency if test_efficiency is None else test_efficiency
    test_ind = independent_flip if test_independent_flip is None else test_independent_flip
    test_joint = joint_flip if test_joint_flip is None else test_joint_flip
    test = sample_shots(heldout_shots, test_eta, success,
                        test_ind, test_joint, seed + 10_000,
                        branch_conditioned=test_branch_conditioned)
    fitted = {level: fit_priors(train, level)
              for level in ("coarse", "flags", "classes", "all")}
    shuffled = dict(test)
    shuffled["flags"] = test["flags"].copy()
    shuffle_rng = np.random.default_rng(seed + 30_000)
    flat_known = test["known"].reshape((-1, 2))
    flat_flags = shuffled["flags"].reshape((-1, 3))
    for x in (0, 1):
        for z in (0, 1):
            indices = np.flatnonzero((flat_known[:, 0] == x) & (flat_known[:, 1] == z))
            flat_flags[indices] = flat_flags[shuffle_rng.permutation(indices)]
    bulk = validate_bulk(3)
    h, logicals = bulk["checks"], bulk["logicals"]
    outcomes = {name: np.zeros(heldout_shots, dtype=bool) for name, _, _ in ARMS}
    elapsed = {name: 0.0 for name, _, _ in ARMS}
    activations = {name: 0 for name, _, _ in ARMS}
    no_checks = erased = 0
    for row in range(heldout_shots):
        known = test["known"][row]
        checks = contracted_checks(h, known)
        no_checks += len(checks) == 0
        deformed = deform_sectors(h, logicals, known)
        if deformed is None:
            erased += 1
            for name in outcomes:
                outcomes[name][row] = True
            continue
        syndrome = (checks @ test["hard"][row]) & 1
        truth = (deformed @ test["errors"][row]) & 1
        local_cache = {
            level: np.asarray([prior_for(test, row, j, level,
                                         fitted[level], fitted["coarse"])
                               for j in range(bulk["fusions"])])
            for level in ("coarse", "flags", "classes", "all")}
        local_cache["shuffled_all"] = np.asarray([
            prior_for(shuffled, row, j, "all", fitted["all"], fitted["coarse"])
            for j in range(bulk["fusions"])])
        for name, level, use_belief in ARMS:
            start = perf_counter()
            local = local_cache[level]
            activate = use_belief is True or (use_belief == "selective" and
                                               bool(np.any(test["flags"][row])))
            if activate:
                activations[name] += 1
                local = belief_priors(checks, syndrome, local)
            predicted = matching_prediction(checks, deformed, syndrome, local)
            elapsed[name] += perf_counter() - start
            outcomes[name][row] = np.any(predicted != truth)
    baseline = outcomes["coarse_mwpm"]
    rng = np.random.default_rng(seed + 20_000)
    def paired(a: np.ndarray, b: np.ndarray) -> dict:
        difference = a.astype(np.int8)-b.astype(np.int8)
        boot = rng.integers(0, heldout_shots, (2000, heldout_shots))
        return {"gain": float(difference.mean()),
                "gain_ci_95": np.quantile(difference[boot].mean(axis=1), [.025, .975]).tolist(),
                "first_only_failure": int(np.count_nonzero(a & ~b)),
                "second_only_failure": int(np.count_nonzero(b & ~a))}
    report = {}
    for name, values in outcomes.items():
        comparison = paired(baseline, values)
        report[name] = {"failures": int(values.sum()),
                        "proxy_rate": float(values.mean()),
                        "wilson_95": wilson(int(values.sum()), heldout_shots),
                        "paired_gain_over_coarse_mwpm": comparison,
                        "bp_activation_fraction_all_shots": activations[name]/heldout_shots,
                        "mean_cpu_decode_seconds": elapsed[name]/(heldout_shots-erased)
                        if heldout_shots > erased else None}
    matched_comparisons = {
        "all_classes_mwpm_to_joint_bp": paired(outcomes["all_classes_mwpm"],
                                               outcomes["all_classes_joint_bp_mwpm"]),
        "all_classes_mwpm_to_selective_bp": paired(outcomes["all_classes_mwpm"],
                                                   outcomes["selective_all_classes_bp_mwpm"]),
        "selective_to_global_bp": paired(outcomes["selective_all_classes_bp_mwpm"],
                                         outcomes["all_classes_joint_bp_mwpm"]),
        "classes_only_to_all_metadata_joint_bp": paired(outcomes["classes_joint_bp_mwpm"],
                                                         outcomes["all_classes_joint_bp_mwpm"]),
        "shuffled_to_real_flags_joint_bp": paired(outcomes["shuffled_flags_joint_bp_mwpm"],
                                                   outcomes["all_classes_joint_bp_mwpm"])}
    availability = test["known"].reshape(heldout_shots, bulk["fusions"], 2)
    return {"training_efficiency": efficiency,
            "heldout_efficiency": test_eta, "physical_bsm_success": success,
            "train_shots": train_shots, "heldout_shots": heldout_shots,
            "train_seed": seed, "heldout_seed": seed+10_000,
            "independent_physical_parity_flip_assumed": independent_flip,
            "joint_A_physical_parity_flip_assumed": joint_flip,
            "heldout_independent_flip_assumed": test_ind,
            "heldout_joint_flip_assumed": test_joint,
            "heldout_branch_conditioned_success": test_branch_conditioned,
            "no_loss_encoded_full_expected": theoretical_no_loss_full(success),
            "observed_logical_parity_availability": {
                "xx": float(availability[:, :, 0].mean()),
                "zz": float(availability[:, :, 1].mean()),
                "both": float(np.all(availability, axis=2).mean())},
            "no_measurable_local_check_fraction": no_checks/heldout_shots,
            "erased_nonlocal_sector_fraction": erased/heldout_shots,
            "latent_joint_events_audit_only": test["latent_joint_count"],
            "arms": report, "matched_comparisons": matched_comparisons}


def run(output: Path, train_shots: int = 12_000,
        heldout_shots: int = 3_000) -> dict:
    cases = [compare(.995, train_shots, heldout_shots, seed=9026),
             compare(.95, train_shots, heldout_shots, seed=19026),
             compare(.995, train_shots, heldout_shots, seed=29026,
                     test_efficiency=.992, test_independent_flip=.003,
                     test_joint_flip=.007),
             compare(.995, train_shots, heldout_shots, seed=39026,
                     test_branch_conditioned=True),
             compare(.995, train_shots, heldout_shots, seed=49026,
                     joint_flip=0.0)]
    result = {"schema_version": "phase0-boosted-encoded-proxy-v1",
              "paper_method": "four boosted physical Bell fusions per (2,2)-Shor encoded fusion; A/C failures retain XX and B/D failures retain ZZ",
              "metadata_levels": {
                  "coarse": "which encoded XX/ZZ bits are available",
                  "flags": "coarse plus disagreements among already measured redundant physical parities",
                  "classes": "coarse plus four physical full/partial/lost classes",
                  "all_classes": "classes plus physical parity-disagreement flags; not raw experimental PNR",
                  "shuffled_flags": "negative control: flags shuffled within identical encoded parity-availability classes"},
              "decoder_levels": {
                  "mwpm": "erasure-contracted matching with calibrated independent XX/ZZ marginals",
                  "joint_bp_mwpm": "four-state correlated belief propagation followed by erasure-contracted matching",
                  "selective_joint_bp_mwpm": "run joint BP only when an observed redundant physical-parity disagreement is present; otherwise matching"},
              "outcome": "periodic nonlocal parity-sector failure proxy; erased sectors counted as failures; not bounded-memory LER",
              "physical_scope": "boosted success rate taken from published experiment; physical parity-flip rates and loss independence are sensitivity assumptions, not measured boosted click-pattern/action calibration",
              "cases": cases}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = run(Path("outputs/phase0_encoded/results.json"))
    for case in result["cases"]:
        print(json.dumps({"train_efficiency": case["training_efficiency"],
                          "test_efficiency": case["heldout_efficiency"],
                          "availability": case["observed_logical_parity_availability"],
                          "erased": case["erased_nonlocal_sector_fraction"],
                          "rates": {k: v["proxy_rate"] for k, v in case["arms"].items()}}, indent=2))
