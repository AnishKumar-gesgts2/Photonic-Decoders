"""Exact d=3 sensitivity to a published first-order photonic fusion map.

Gupta, Doherty and Mahmoodian (2026), Table 2, gives an *added* fusion Pauli
map for ideal Bell-pair inputs under a Pauli-reduction assumption. This is not
the full encoded six-ring resource/source channel; optical parameters here are
an explicitly declared grid, not measurements of the proposed device.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pymatching

from bounded_optical_d3 import memory_signatures
from joint_map import decode as configuration_map


def paper_channel(emitter: str, loss_times_leakage: float,
                  visibility_deficit: float = 0.0) -> np.ndarray:
    if emitter not in ("three_level", "four_level"):
        raise ValueError(emitter)
    if min(loss_times_leakage, visibility_deficit) < 0:
        raise ValueError("Optical parameter products must be nonnegative")
    if emitter == "three_level":
        px = py = pz = loss_times_leakage
    else:
        px = py = loss_times_leakage / 2
        pz = loss_times_leakage / 2 + visibility_deficit / 2
    if px + py + pz >= 1:
        raise ValueError("First-order channel does not normalize")
    # The local decoder convention is I, X, Z, Y.
    return np.array([1-px-py-pz, px, pz, py], dtype=float)


def exact_risks(checks: np.ndarray, logicals: np.ndarray,
                channel: np.ndarray) -> dict:
    if logicals.shape[0] != 1 or checks.shape[1] != 18:
        raise ValueError("This exact calculation is for the 9-site d=3 memory")
    count = 4**9
    configurations = np.arange(count, dtype=np.uint32)
    states = ((configurations[:, None] >>
               (2*np.arange(9, dtype=np.uint32))) & 3).astype(np.uint8)
    errors = np.zeros((count, 18), dtype=np.uint8)
    errors[:, ::2] = states & 1
    errors[:, 1::2] = states >> 1
    detectors = (errors @ checks.T) & 1
    logical = ((errors @ logicals.T) & 1)[:, 0]
    syndrome_keys = (detectors.astype(np.uint32) <<
                     np.arange(checks.shape[0], dtype=np.uint32)).sum(axis=1)
    weights = np.prod(channel[states], axis=1)
    if not np.isclose(weights.sum(), 1, atol=1e-12):
        raise AssertionError("Fault configurations do not conserve probability")
    keys, inverse = np.unique(syndrome_keys, return_inverse=True)
    mass = np.zeros((len(keys), 2), dtype=float)
    np.add.at(mass, (inverse, logical), weights)
    syndrome_bits = ((keys[:, None] >>
                      np.arange(checks.shape[0], dtype=np.uint32)) & 1).astype(np.uint8)

    marginals = np.tile([channel[1]+channel[3], channel[2]+channel[3]], 9)
    clipped = np.clip(marginals, 1e-12, 1-1e-12)
    matching = pymatching.Matching.from_check_matrix(
        checks, weights=np.log((1-clipped)/clipped), faults_matrix=logicals)
    mwpm = matching.decode_batch(syndrome_bits)[:, 0].astype(np.uint8)

    priors = np.tile(channel, (9, 1))
    map_choices = np.zeros(len(keys), dtype=np.uint8)
    for row, syndrome in enumerate(syndrome_bits):
        prediction, solved = configuration_map(checks, logicals, syndrome, priors)
        if not solved:
            raise RuntimeError("Configuration MAP solver did not finish")
        map_choices[row] = prediction[0]
    class_choices = np.argmax(mass, axis=1)
    def risk(prediction: np.ndarray) -> float:
        return float(mass[np.arange(len(keys)), 1-prediction].sum())
    return {"calibrated_mwpm": risk(mwpm),
            "joint_configuration_map": risk(map_choices),
            "optimal_logical_class_map": risk(class_choices),
            "syndrome_classes": len(keys),
            "configuration_map_disagrees_with_class_map":
                int(np.count_nonzero(map_choices != class_choices))}


def run(output: Path) -> dict:
    # Fixed broad first-order sensitivity grid. u=(1-eta)*|gamma|^2; v=1-V.
    # These are NOT inferred source settings or optimized on decoder outcomes.
    grid = [("sensitivity_grid", "three_level", u, 0.0)
            for u in (0.0001, 0.001, 0.01, 0.03)]
    grid += [("sensitivity_grid", "four_level", u, v)
             for u in (0.0001, 0.001, 0.01, 0.03)
             for v in (0.0, 0.02)]
    # Table 3's illustrative quality targets with |gamma|^2=0.01. They are
    # requirement boundaries, not observed source measurements.
    grid += [("paper_design_target", "three_level", (1-.967)*.01, 0.0),
             ("paper_design_target", "four_level", (1-.933)*.01, 1-.996)]
    cases = []
    signatures = {basis: memory_signatures(basis)[:2] for basis in ("x", "z")}
    for label, emitter, u, v in grid:
        channel = paper_channel(emitter, u, v)
        cases.append({"case_label": label, "emitter_model": emitter,
                      "loss_times_laser_leakage": u,
                      "visibility_deficit": v,
                      "first_order_added_fusion_channel_I_X_Z_Y": channel.tolist(),
                      "memory_results": {
                          basis: exact_risks(*signatures[basis], channel)
                          for basis in ("x", "z")}})
    result = {
        "schema_version": "phase0-paper-fusion-map-exact-d3-v1",
        "source": "Gupta, Doherty, Mahmoodian, arXiv:2608.03005v1, Table 2",
        "source_url": "https://arxiv.org/html/2608.03005",
        "meaning": "first-order added fusion Pauli map after successful Bell measurement, with the paper's Pauli-reduction assumption; no measured device parameters",
        "adapter": "one published added fusion Pauli per site of a rotated d=3 memory at one time slice; conventional surface-code sensitivity model, not native encoded FBQC",
        "excluded": "source-state preparation faults, partial/lost fusion actions, encoded four-BSM reconstruction, coherent residuals, native boundaries",
        "cases": cases}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    report = run(Path("outputs/phase0_paper_source_sensitivity/results.json"))
    for row in report["cases"]:
        print(row["emitter_model"], row["loss_times_laser_leakage"],
              row["visibility_deficit"], row["memory_results"])
