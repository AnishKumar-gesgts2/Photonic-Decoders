"""Exact four-BSM encoded record/action table from published source Pauli rates.

Table 1 of Gupta et al. (2026) gives first-order *input resource photon*
Pauli rates. We explicitly assume errors on eight photons are independent,
compose the two input Pauli errors at each BSM, and use the ancilla-free
(2,2)-Shor parity reconstruction. This is a model-derived local table, not a
measured source or a native bounded six-ring logical experiment.
"""
from __future__ import annotations

from itertools import product
import json
from pathlib import Path

import numpy as np


def input_photon_channel(emitter: str, loss_times_leakage: float,
                         bias_deficit: float = 0.0) -> np.ndarray:
    if emitter not in ("three_level", "four_level"):
        raise ValueError(emitter)
    if min(loss_times_leakage, bias_deficit) < 0:
        raise ValueError("Optical parameters must be nonnegative")
    if emitter == "three_level":
        px = py = loss_times_leakage / 2
        pz = loss_times_leakage / 2 + bias_deficit / 2
    else:
        px = loss_times_leakage / 4 + bias_deficit
        py = pz = loss_times_leakage / 4
    if px + py + pz >= 1:
        raise ValueError("First-order channel does not normalize")
    return np.array([1-px-py-pz, px, pz, py])  # I, X, Z, Y


def compose_two_photons(channel: np.ndarray) -> np.ndarray:
    """Paulis on either BSM input XOR their XX/ZZ outcome flips."""
    result = np.zeros(4)
    for left, right in product(range(4), repeat=2):
        # Index bits encode (ZZ-flip, XX-flip): X=1, Z=2, Y=3.
        result[left ^ right] += channel[left] * channel[right]
    return result


def encoded_table(photon_channel: np.ndarray,
                  detection_efficiency: float,
                  physical_bsm_channels: np.ndarray | None = None) -> dict:
    if not 0 <= detection_efficiency <= 1:
        raise ValueError("Invalid detection efficiency")
    physical_channel = compose_two_photons(photon_channel)
    per_bsm = (np.tile(physical_channel, (4, 1)) if physical_bsm_channels is None
               else np.asarray(physical_bsm_channels, dtype=float))
    if per_bsm.shape != (4, 4) or np.any(per_bsm < 0) or not np.allclose(per_bsm.sum(axis=1), 1):
        raise ValueError("Each physical BSM must have a four-state channel")
    assignments = np.array(list(product((0, 1), repeat=5)), dtype=np.uint8)
    xa, xb, za, lx, lz = assignments.T
    clean_x = np.stack((xa, xb, xa ^ lx, xb ^ lx), axis=1)
    clean_z = np.stack((za, za ^ lz, za, za ^ lz), axis=1)
    indices = np.arange(256, dtype=np.uint16)
    states = ((indices[:, None] >> (2*np.arange(4))) & 3).astype(np.uint8)
    source_weights = np.prod(per_bsm[np.arange(4)[None, :], states], axis=1)
    x = (clean_x[:, None, :] ^ ((states[None, :, :] >> 1) & 1)).reshape(-1, 4)
    z = (clean_z[:, None, :] ^ (states[None, :, :] & 1)).reshape(-1, 4)
    truth_x = np.repeat(lx, 256)
    truth_z = np.repeat(lz, 256)
    base_weights = np.tile(source_weights, 32) / 32
    # Each physical Bell measurement sees two photons.
    survival = detection_efficiency**2
    classes: dict[tuple[int, ...], float] = {}
    joint = np.zeros(4)
    class_mass = np.zeros(4)  # both, X only, Z only, neither
    for mask in range(16):
        survived = np.array([(mask >> j) & 1 for j in range(4)], dtype=bool)
        survival_weight = survival**int(survived.sum()) * (1-survival)**int((~survived).sum())
        if survival_weight == 0:
            continue
        full = np.zeros_like(x, dtype=bool)
        full[:, (0, 2)] = x[:, (0, 2)] == 1
        full[:, (1, 3)] = z[:, (1, 3)] == 1
        record = np.where(survived[None, :], np.where(full, 2, 1), 0)
        known_x = np.broadcast_to(survived, x.shape).copy()
        known_z = known_x.copy()
        known_x[:, (1, 3)] &= full[:, (1, 3)]
        known_z[:, (0, 2)] &= full[:, (0, 2)]
        xa_known = known_x[:, 0] & known_x[:, 2]
        xb_known = known_x[:, 1] & known_x[:, 3]
        left_known = known_z[:, 0] | known_z[:, 2]
        right_known = known_z[:, 1] | known_z[:, 3]
        encoded_x_known = xa_known | xb_known
        encoded_z_known = left_known & right_known
        reported_x = np.where(xa_known, x[:, 0] ^ x[:, 2], x[:, 1] ^ x[:, 3])
        left = np.where(known_z[:, 0], z[:, 0], z[:, 2])
        right = np.where(known_z[:, 1], z[:, 1], z[:, 3])
        error_x = reported_x ^ truth_x
        error_z = (left ^ right) ^ truth_z
        weights = base_weights * survival_weight
        class_mass[0] += float(weights[encoded_x_known & encoded_z_known].sum())
        class_mass[1] += float(weights[encoded_x_known & ~encoded_z_known].sum())
        class_mass[2] += float(weights[~encoded_x_known & encoded_z_known].sum())
        class_mass[3] += float(weights[~encoded_x_known & ~encoded_z_known].sum())
        for j, (rec, xk, zk, ex, ez) in enumerate(zip(
                record, encoded_x_known, encoded_z_known, error_x, error_z)):
            key = (int(rec[0]), int(rec[1]), int(rec[2]), int(rec[3]),
                   int(ex) if xk else -1, int(ez) if zk else -1)
            classes[key] = classes.get(key, 0.0) + float(weights[j])
            if xk and zk:
                joint[2*int(ex)+int(ez)] += weights[j]
    if not np.isclose(sum(classes.values()), 1, atol=1e-12):
        raise AssertionError("Encoded record/action table lost probability")
    # joint indices are I, ZZ-only, XX-only, both in physical parity notation.
    rows = [{"physical_record_A_B_C_D": list(key[:4]),
             "encoded_xx_flip": key[4] if key[4] >= 0 else None,
             "encoded_zz_flip": key[5] if key[5] >= 0 else None,
             "probability_per_encoded_fusion": value}
            for key, value in sorted(classes.items()) if value > 0]
    return {"detection_efficiency_per_photon": detection_efficiency,
            "input_photon_channel_I_X_Z_Y": photon_channel.tolist(),
            "physical_bsm_channels_A_B_C_D_I_X_Z_Y": per_bsm.tolist(),
            "encoded_availability": {
                "both_known": float(class_mass[0]),
                "xx_only": float(class_mass[1]),
                "zz_only": float(class_mass[2]),
                "neither": float(class_mass[3])},
            "both_known_action_I_ZZ_only_XX_only_joint_per_attempt": joint.tolist(),
            "joint_flip_probability_conditioned_on_both_known":
                float(joint[3]/class_mass[0]) if class_mass[0] else None,
            "record_action_rows": rows}


def run(output: Path) -> dict:
    grid = [(emitter, u, bias, eta)
            for emitter in ("three_level", "four_level")
            for u in (.001, .01)
            for bias in (0.0, .02)
            for eta in (1.0, .995)]
    cases = []
    for emitter, u, bias, eta in grid:
        table = encoded_table(input_photon_channel(emitter, u, bias), eta)
        cases.append({"emitter_model": emitter, "loss_times_laser_leakage": u,
                      "visibility_or_birefringence_deficit": bias, **table})
    result = {"schema_version": "phase0-paper-input-encoded-action-v1",
              "source": "Gupta, Doherty, Mahmoodian, arXiv:2608.03005v1, Table 1",
              "source_url": "https://arxiv.org/html/2608.03005",
              "model_assumptions": "independent first-order Pauli errors on all eight input photons; each two-photon BSM composes the errors; ideal ancilla-free branch-dependent full/partial analyzer; independent detector survival",
              "excluded": "measured source parameters, inter-photon source correlations, coherent residuals, native finite six-ring memory",
              "cases": cases}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    report = run(Path("outputs/phase0_paper_encoded_channel/results.json"))
    for row in report["cases"]:
        print(row["emitter_model"], row["loss_times_laser_leakage"],
              row["visibility_or_birefringence_deficit"],
              row["detection_efficiency_per_photon"],
              row["encoded_availability"],
              row["joint_flip_probability_conditioned_on_both_known"])
