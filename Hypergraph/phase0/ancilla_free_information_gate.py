"""Exact encoded parity-availability gate for ancilla-free versus boosted BSMs.

This is an information and resource count, not a logical decoder experiment.
It uses the same four-physical-fusion encoded reconstruction for both arms.
"""
from __future__ import annotations

import json
from itertools import product
from pathlib import Path

import numpy as np

from boosted_encoded import encoded_availability


def exact_availability(success: float, photon_efficiency: float,
                       photons_per_bsm: int) -> dict:
    if not (0 <= success <= 1 and 0 <= photon_efficiency <= 1):
        raise ValueError("Probabilities must be in [0, 1]")
    if photons_per_bsm not in (2, 4):
        raise ValueError("Only the declared two- and four-photon BSMs are supported")
    survival = photon_efficiency ** photons_per_bsm
    probabilities = (1 - survival, survival * (1 - success), survival * success)
    total = xx = zz = both = neither = 0.0
    for outcome in product(range(3), repeat=4):
        probability = float(np.prod([probabilities[item] for item in outcome]))
        known = encoded_availability(np.asarray(outcome, dtype=np.uint8))
        x, z = bool(known[0]), bool(known[1])
        total += probability
        xx += probability * x
        zz += probability * z
        both += probability * (x and z)
        neither += probability * (not x and not z)
    if abs(total - 1) > 1e-12:
        raise AssertionError("Encoded outcome distribution not normalized")
    return {"physical_full_success_given_survival": success,
            "photon_efficiency": photon_efficiency,
            "photons_per_physical_bsm": photons_per_bsm,
            "photons_attempted_per_encoded_fusion": 4 * photons_per_bsm,
            "encoded_xx_available": xx, "encoded_zz_available": zz,
            "both_encoded_parities_available": both,
            "neither_encoded_parity_available": neither}


def run(output: Path) -> dict:
    settings = {}
    for efficiency in (1.0, 0.995, 0.986, 0.95):
        settings[str(efficiency)] = {
            "ancilla_free": exact_availability(0.5, efficiency, 2),
            "boosted_reference": exact_availability(0.693, efficiency, 4),
        }
    result = {
        "schema_version": "phase0-ancilla-free-information-v1",
        "architecture": "four physical BSMs per (2,2)-Shor encoded fusion",
        "assumptions": [
            "independent physical-BSM outcome classes and photon survival",
            "50% ideal unboosted full Bell discrimination",
            "69.3% measured average boosted full discrimination used as a scalar sensitivity input",
            "every surviving partial outcome retains the parity required by its A/C or B/D placement",
            "no source faults, optical back-action, conditional Pauli channel, or logical memory",
        ],
        "settings": settings,
        "decision": "information and photon-count comparison only; hypergraph-versus-MWPM go/no-go unresolved",
        "missing_for_decoder_decision": [
            "ancilla-free and boosted raw-record-conditioned fusion actions and source-calibrated incidence",
            "native bounded encoded six-ring memory with boundaries and logical observable",
            "held-out identical-shot hypergraph versus equally informed calibrated matching comparison",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(run(Path("outputs/phase0_ancilla_free_information/results.json")), indent=2))
