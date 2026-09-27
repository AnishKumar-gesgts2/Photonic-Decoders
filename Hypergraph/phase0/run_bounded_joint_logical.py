"""Bounded logical-memory comparison for an effective joint fusion-parity fault.

A physical fusion XX/ZZ joint flip is mapped to a Y data fault at one time
slice of a three-round rotated surface-code memory. That mapping is a declared
teleportation-frame adapter, not a native six-ring optical derivation.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from bounded_optical_d3 import memory_signatures
from encoded_proxy import belief_priors, matching_prediction
from exact_logical_map import lookup as exact_logical_lookup, syndrome_key
from joint_map import decode as joint_map_decode
from run_ancilla_free_decoder_proxy import paired
from run_encoded_phase0 import wilson


def local_channel(p_independent: float, p_joint: float) -> np.ndarray:
    if min(p_independent, p_joint) < 0 or 2*p_independent+p_joint >= 1:
        raise ValueError("Invalid categorical fault rates")
    return np.array([1-2*p_independent-p_joint,
                     p_independent, p_independent, p_joint])


def conditioned(channel: np.ndarray, flag: bool, sensitivity: float,
                false_positive: float) -> np.ndarray:
    likelihood = np.full(4, false_positive if flag else 1-false_positive)
    likelihood[3] = sensitivity if flag else 1-sensitivity
    posterior = channel*likelihood
    return posterior/posterior.sum()


def run_cell(basis: str, p_joint: float, shots: int, seed: int,
             use_flags: bool, sensitivity: float = .6,
             false_positive: float = .15,
             p_independent: float = .002) -> dict:
    checks, logicals, _ = memory_signatures(basis)
    n = checks.shape[1]//2
    channel = local_channel(p_independent, p_joint)
    rng = np.random.default_rng(seed)
    sampled = rng.choice(4, size=(shots, n), p=channel)
    flags = rng.random((shots, n)) < np.where(sampled == 3, sensitivity,
                                             false_positive)
    errors = np.zeros((shots, 2*n), dtype=np.uint8)
    errors[:, ::2] = sampled & 1
    errors[:, 1::2] = sampled >> 1
    syndromes = (errors @ checks.T) & 1
    logical_truth = (errors @ logicals.T) & 1
    failures = {name: np.zeros(shots, dtype=bool)
                for name in ("uniform_mwpm", "calibrated_mwpm",
                             "belief_matching", "joint_map")}
    logical_lookup = exact_logical_lookup(checks, logicals, channel) if not use_flags else None
    if logical_lookup is not None:
        failures["exact_logical_map"] = np.zeros(shots, dtype=bool)
    unsolved = 0
    priors_unflagged = (np.tile(channel, (n, 1)) if not use_flags else None)
    for row in range(shots):
        if use_flags:
            priors = np.asarray([conditioned(channel, bool(v), sensitivity,
                                              false_positive) for v in flags[row]])
        else:
            priors = priors_unflagged
        syndrome = syndromes[row]
        # Uniform graph weights deliberately ignore the declared joint rate.
        uniform = np.full((n, 4), [.994, .002, .002, .002])
        predictions = {
            "uniform_mwpm": matching_prediction(checks, logicals, syndrome, uniform),
            "calibrated_mwpm": matching_prediction(checks, logicals, syndrome, priors),
            "belief_matching": matching_prediction(
                checks, logicals, syndrome,
                belief_priors(checks, syndrome, priors)),
        }
        prediction, solved = joint_map_decode(checks, logicals, syndrome, priors)
        if not solved:
            unsolved += 1
            prediction = predictions["calibrated_mwpm"]
        predictions["joint_map"] = prediction
        if logical_lookup is not None:
            predictions["exact_logical_map"] = np.array(
                [logical_lookup[syndrome_key(syndrome)]], dtype=np.uint8)
        for name, value in predictions.items():
            failures[name][row] = bool(np.any(value != logical_truth[row]))
    arms = {}
    calibrated = failures["calibrated_mwpm"]
    for name, values in failures.items():
        count = int(values.sum())
        arms[name] = {"failures": count, "rate": count/shots,
                      "wilson_95": wilson(count, shots)}
        if name != "calibrated_mwpm":
            arms[name]["paired_calibrated_mwpm_gain"] = paired(
                calibrated, values, seed+10+len(arms))
    arms["joint_map"]["paired_belief_matching_gain"] = paired(
        failures["belief_matching"], failures["joint_map"], seed+70)
    return {"basis": basis, "p_joint": p_joint,
            "p_independent_each_axis": p_independent,
            "shots": shots, "seed": seed, "use_flags": use_flags,
            "flag_sensitivity_given_joint": sensitivity if use_flags else None,
            "flag_false_positive_otherwise": false_positive if use_flags else None,
            "joint_map_unsolved": unsolved,
            "detectors": int(checks.shape[0]),
            "logical_observables": int(logicals.shape[0]),
            "arms": arms}


def run(output: Path) -> dict:
    cases = [run_cell("z", 0.0, 5000, 31001, False),
             run_cell("z", .01, 5000, 31002, False),
             run_cell("z", .03, 20000, 31003, False),
             run_cell("z", 0.0, 20000, 31007, False,
                      p_independent=.032),
             run_cell("z", .03, 20000, 31004, True),
             run_cell("z", .05, 5000, 31005, True),
             run_cell("x", .03, 5000, 31006, True)]
    result = {"schema_version": "phase0-bounded-effective-joint-v1",
              "memory": "Stim three-round rotated d=3 memory with a declared logical observable",
              "adapter": "one fusion joint XX/ZZ report fault becomes one data-qubit Y at one time slice; effective-channel assumption, not native FBQC",
              "record_contract": "both decoders receive syndrome and the same optional noisy local joint-fault flag; latent fault states are audit-only",
              "flag_scope": "declared sensitivity analysis, not a characterized PNR or source herald",
              "decoder_claim": "joint categorical configuration MAP versus calibrated MWPM; belief matching is a correlation-aware control and no-flag exact logical-class MAP is the bounded optimum reference",
              "cases": cases}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = run(Path("outputs/phase0_bounded_effective_joint/results.json"))
    for case in result["cases"]:
        print(case["basis"], case["p_joint"], case["use_flags"],
              {name: arm["rate"] for name, arm in case["arms"].items()})
