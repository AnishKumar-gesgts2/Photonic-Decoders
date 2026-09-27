"""Reproducible optical-derived bounded d=3 memory comparison."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from boosted_optical import BELL, excess_photon_loss_effects, ideal_report, instrument
from bounded_optical_d3 import decode, sample_encoded


def bootstrap(values: list[int], seed: int) -> list[float]:
    data = np.asarray(values, dtype=np.int8)
    rng = np.random.default_rng(seed)
    counts = np.array([(data == -1).sum(), (data == 0).sum(), (data == 1).sum()])
    draws = rng.multinomial(len(data), counts/len(data), size=5000)
    return np.quantile((draws[:, 2]-draws[:, 0])/len(data), [.025, .975]).tolist()


def optical_audit() -> dict:
    ideal = instrument("phi+")
    fault = instrument("phi-")
    report_mass = {}
    for name, channel in (("ideal", ideal), ("ancilla_phase", fault)):
        branch = {}
        for i, label in enumerate(BELL):
            mass = {}
            for j, record in enumerate(channel["records"]):
                report = ideal_report(record, ideal)
                key = f"{report[0]},{report[1]}"
                mass[key] = mass.get(key, 0) + float(channel["probabilities"][i, j])
            branch[label] = {key: value for key, value in mass.items() if value > 1e-12}
        report_mass[name] = branch
    offdiag_conclusive = max(float(np.max(np.abs(effect-np.diag(np.diag(effect)))))
                             for record, effect in fault["effects"].items()
                             if None not in ideal_report(record, ideal))
    ideal_marginal = {record: float(np.mean(ideal["probabilities"][:, j]))
                      for j, record in enumerate(ideal["records"])}
    fault_marginal = {record: float(np.mean(fault["probabilities"][:, j]))
                      for j, record in enumerate(fault["records"])}
    raw_record_tv = .5*sum(abs(ideal_marginal.get(record, 0)-fault_marginal.get(record, 0))
                         for record in ideal_marginal.keys() | fault_marginal.keys())
    return {"unitary": "Hauser 2025 Eq. 4, ideal four-photon indistinguishable PNR",
            "ancilla_fault": "Z on one photon of Phi+ gives Phi-",
            "ideal_record_count": len(ideal["records"]),
            "fault_record_count": len(fault["records"]),
            "conclusive_fault_povm_max_offdiagonal": offdiag_conclusive,
            "ideal_vs_phase_fault_raw_record_tv_uniform_bell_input": raw_record_tv,
            "per_input_report_probabilities": report_mass}


def excess_photon_audit(path: Path) -> dict:
    """Check whether detector loss aliases a fifth photon as a valid BSM."""
    ideal = instrument("phi+")
    cases = []
    for eta in (.995, .95, .8):
        effects = excess_photon_loss_effects(eta, extra_input_mode=0)
        all_mass = sum(float(np.trace(effect).real)/4
                       for effect in effects.values())
        conclusive = {record: effect for record, effect in effects.items()
                      if None not in ideal_report(record, ideal)}
        conclusive_mass = sum(float(np.trace(effect).real)/4
                              for effect in conclusive.values())
        offdiagonal_sum = sum(float(np.sum(np.abs(effect-np.diag(np.diag(effect)))))
                              for effect in conclusive.values())
        diagonal_sum = sum(float(np.trace(effect).real)
                           for effect in conclusive.values())
        cases.append({"detector_efficiency_assumed": eta,
                      "all_five_photons_seen_probability": eta**5,
                      "exactly_one_photon_lost_probability": all_mass,
                      "four_count_false_conclusive_probability": conclusive_mass,
                      "fraction_of_one_loss_records_false_conclusive":
                          conclusive_mass/all_mass,
                      "conclusive_gram_offdiagonal_to_diagonal_l1_ratio":
                          offdiagonal_sum/diagonal_sum,
                      "conclusive_gram_max_offdiagonal":
                          max(float(np.max(np.abs(effect-np.diag(np.diag(effect)))))
                              for effect in conclusive.values())})
    result = {"schema": "phase0-five-photon-loss-alias-v1",
              "fault": "normalized creation of one mode-matched extra photon in data mode 0H before published 4x4 multiport",
              "meaning": "conditional source-fault Gram matrix diagnostic; nonzero Bell offdiagonal means a clicked record cannot be assigned a stochastic Bell/Pauli action from PNR alone",
              "cases": cases}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def run(path: Path, train_shots: int = 12000, heldout_shots: int = 3000,
        phase_faults: tuple[float, ...] = (0.0, .005, .02)) -> dict:
    cases = []
    for i, phase_fault in enumerate(phase_faults):
        train = sample_encoded(train_shots, phase_fault, 11200+100*i)
        test = sample_encoded(heldout_shots, phase_fault, 21200+100*i)
        decoded = [decode(train, test, basis) for basis in ("x", "z")]
        for j, arm in enumerate(decoded):
            arm["paired_ci_95"] = bootstrap(arm.pop("paired_metadata_mwpm_minus_joint"), 31200+100*i+j)
        cases.append({"assumed_ancilla_phase_fault_probability": phase_fault,
                      "train_shots": train_shots, "heldout_shots": heldout_shots,
                      "heldout_known_xx": float(test["known"][:, :, 0].mean()),
                      "heldout_known_zz": float(test["known"][:, :, 1].mean()),
                      "heldout_encoded_xx_error_rate": float(test["error"][:, :, 0].mean()),
                      "heldout_encoded_zz_error_rate": float(test["error"][:, :, 1].mean()),
                      "heldout_joint_xx_zz_error_rate": float(np.all(test["error"], axis=2).mean()),
                      "heldout_any_redundancy_disagreement": float(np.any(test["flags"], axis=(1,2)).mean()),
                      "observed_training_faults_audit_only": train["fault_count"],
                      "observed_heldout_faults_audit_only": test["fault_count"],
                      "memory_basis_results": decoded})
    result = {"schema": "phase0-ideal-optical-bounded-d3-v1",
              "optical_audit": optical_audit(),
              "scope": "exact ideal boosted-BSM click likelihood for specified ancilla phase fault; (2,2)-Shor parity reconstruction; bounded three-round Stim rotated d=3 memory with one encoded fusion proxy per data qubit; independent fault incidence and unknown-frame randomization are assumptions",
              "decoder_input": "syndrome plus encoded parity availability, four full/partial records, and redundancy disagreements; no latent fault labels",
              "arms": "availability MWPM, equally informed metadata MWPM, metadata joint-BP plus MWPM",
              "cases": cases}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    if sys.argv[1:] == ["--excess-audit"]:
        result = excess_photon_audit(
            Path("outputs/phase0_bounded_optical_d3/excess_audit.json"))
        print(json.dumps(result, indent=2))
    elif not sys.argv[1:]:
        result = run(Path("outputs/phase0_bounded_optical_d3/results.json"))
        for case in result["cases"]:
            print(case["assumed_ancilla_phase_fault_probability"],
                  case["heldout_known_xx"], case["heldout_known_zz"])
            for basis in case["memory_basis_results"]:
                print(basis["basis"], basis["rates"], basis["paired_ci_95"])
    else:
        raise SystemExit("Usage: run_bounded_optical_d3.py [--excess-audit]")
