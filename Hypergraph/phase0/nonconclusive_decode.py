"""Measurable-check and raw-PNR information audits for the six-ring bulk."""
from __future__ import annotations

from collections import defaultdict
from math import log2

import numpy as np

from native_ring_bulk import gf2_nullspace, gf2_rank, validate_bulk
from six_ring_optical_instrument import all_record_branch_table


def observable_check_basis(h: np.ndarray, known: np.ndarray) -> np.ndarray:
    """All independent combinations of local checks avoiding missing bits."""
    combinations = gf2_nullspace(h[:, ~known].T)
    basis = np.zeros((0, h.shape[1]), dtype=np.uint8)
    for coefficients in combinations:
        row = (coefficients @ h) & 1
        if np.any(row) and gf2_rank(np.vstack((basis, row))) > len(basis):
            basis = np.vstack((basis, row))
    if np.any(basis[:, ~known]):
        raise AssertionError("Observable check still uses a missing outcome")
    return basis


def make_masks(measurements: np.ndarray, efficiency: float,
               rng: np.random.Generator, excess_probability: float = 0.0
               ) -> tuple[np.ndarray, np.ndarray]:
    """Coarse PNR mask; excess is an explicit nonqubit/unknown category."""
    shots, bits = measurements.shape
    fusions = bits // 2
    both_detected = rng.random((shots, fusions)) < efficiency**2
    zz = measurements[:, 1::2]
    known = np.zeros_like(measurements, dtype=bool)
    known[:, ::2] = both_detected & (zz == 1)
    known[:, 1::2] = both_detected
    categories = np.full((shots, fusions), 2, dtype=np.uint8)  # short
    categories[both_detected & (zz == 0)] = 1  # partial
    categories[both_detected & (zz == 1)] = 0  # full
    if excess_probability:
        excess = rng.random((shots, fusions)) < excess_probability
        known[:, ::2] &= ~excess
        known[:, 1::2] &= ~excess
        categories[excess] = 3
    return known, categories


def information_audit(shots: int = 10_000, efficiency: float = 0.95,
                      seed: int = 5187) -> dict:
    bulk = validate_bulk(3)
    h = bulk["checks"]
    a = np.vstack((h, bulk["logicals"]))
    outcomes = bulk["circuit"].compile_sampler(seed=seed).sample(shots)[:, :2*bulk["fusions"]]
    known, categories = make_masks(outcomes, efficiency, np.random.default_rng(seed+1))
    directly_measurable = np.all(known[:, None, :] | (h[None, :, :] == 0), axis=2).sum(axis=1)
    unknown_count = (~known).sum(axis=1)
    measurable_local = np.empty(shots, dtype=int)
    measurable_all = np.empty(shots, dtype=int)
    free_bits = np.empty(shots, dtype=int)
    for shot in range(shots):
        missing = ~known[shot]
        local_rank_on_missing = gf2_rank(h[:, missing])
        full_rank_on_missing = gf2_rank(a[:, missing])
        measurable_local[shot] = gf2_rank(h) - local_rank_on_missing
        measurable_all[shot] = gf2_rank(a) - full_rank_on_missing
        free_bits[shot] = int(unknown_count[shot]) - full_rank_on_missing
    return {"shots": shots, "seed": seed, "detector_efficiency": efficiency,
            "fusion_outcome_category_fractions": {
                name: float(np.mean(categories == j))
                for j, name in enumerate(("full_both_parities", "partial_zz_only", "short_count_neither"))},
            "mean_missing_outcome_bits_per_shot": float(unknown_count.mean()),
            "mean_directly_measurable_checks": float(directly_measurable.mean()),
            "fraction_with_no_directly_measurable_check": float(np.mean(directly_measurable == 0)),
            "mean_independent_measurable_check_combinations": float(measurable_local.mean()),
            "fraction_with_no_independent_measurable_check_combination": float(np.mean(measurable_local == 0)),
            "mean_measurable_check_or_sector_combinations": float(measurable_all.mean()),
            "fraction_with_no_measurable_check_or_sector_combination": float(np.mean(measurable_all == 0)),
            "mean_free_missing_bits_even_if_all_29_ideal_constraints_were_known": float(free_bits.mean()),
            "minimum_free_missing_bits": int(free_bits.min())}


def raw_record_information(fault_prior: float = 0.05,
                           efficiency: float = 0.95) -> dict:
    """How much Bell-branch information survives beyond the coarse class?"""
    rows = []
    for cause, prior in (("ideal", 1-fault_prior), ("extra_plus", fault_prior)):
        for row in all_record_branch_table(cause, efficiency):
            rows.append({"record": tuple(row["record"]), "class": row["class"],
                         "branches": {name: prior*p for name, p in row["branches"].items()}})
    def mutual_information(label) -> float:
        joint = defaultdict(float)
        labels = defaultdict(float)
        branches = defaultdict(float)
        for row in rows:
            key = label(row)
            for branch, mass in row["branches"].items():
                joint[(key, branch)] += mass
                labels[key] += mass
                branches[branch] += mass
        return sum(p*log2(p/(labels[key]*branches[branch]))
                   for (key, branch), p in joint.items() if p > 0)
    coarse = mutual_information(lambda row: row["class"])
    raw = mutual_information(lambda row: row["record"])
    by_record = defaultdict(lambda: {"branches": defaultdict(float),
                                 "fault_mass": 0.0, "class": None})
    for cause, prior in (("ideal", 1-fault_prior), ("extra_plus", fault_prior)):
        for row in all_record_branch_table(cause, efficiency):
            entry = by_record[tuple(row["record"])]
            entry["class"] = row["class"]
            for branch, probability in row["branches"].items():
                entry["branches"][branch] += prior*probability
            if cause == "extra_plus":
                entry["fault_mass"] += prior*row["probability"]
    record_rows = []
    for record, entry in sorted(by_record.items()):
        mass = sum(entry["branches"].values())
        record_rows.append({"counts": list(record), "class": entry["class"],
                            "probability": mass,
                            "fault_posterior": entry["fault_mass"]/mass,
                            "bell_branch_posterior": {
                                branch: probability/mass
                                for branch, probability in entry["branches"].items()}})
    return {"fault_incidence_assumption": fault_prior,
            "distinct_raw_pnr_records": len({row["record"] for row in rows}),
            "bell_branch_information_bits_with_outcome_class": coarse,
            "bell_branch_information_bits_with_full_pnr_record": raw,
            "additional_information_from_existing_raw_pnr_bits": raw-coarse,
            "scope": "Shannon information in local optical instrument; not a measured logical decoding gain",
            "record_rows": record_rows}
