from __future__ import annotations

import hashlib
import itertools
import json
import tomllib
from pathlib import Path
from typing import Any, Iterator


def load_config(path: Path) -> dict[str, Any]:
    with path.open("rb") as stream:
        config = tomllib.load(stream)
    required = {
        "seed",
        "distances",
        "rounds",
        "physical_error_rates",
        "detector_efficiencies",
        "visibilities",
        "shots",
        "shard_size",
        "methods",
        "physics",
        "decoder",
    }
    missing = required - config.keys()
    if missing:
        raise ValueError(f"Missing configuration fields: {sorted(missing)}")
    if config["shots"] <= 0 or config["shard_size"] <= 0:
        raise ValueError("shots and shard_size must be positive")
    return config


def scenarios(config: dict[str, Any]) -> Iterator[dict[str, Any]]:
    # A round count is paired with the same distance when both lists have equal
    # length; otherwise the Cartesian product is deliberate.
    ds = list(map(int, config["distances"]))
    rs = list(map(int, config["rounds"]))
    geometries = list(zip(ds, rs)) if len(ds) == len(rs) else list(itertools.product(ds, rs))
    for (distance, rounds), p, efficiency, visibility in itertools.product(
        geometries,
        config["physical_error_rates"],
        config["detector_efficiencies"],
        config["visibilities"],
    ):
        yield {
            "distance": distance,
            "rounds": rounds,
            "physical_error_rate": float(p),
            "detector_efficiency": float(efficiency),
            "visibility": float(visibility),
        }


def scenario_id(scenario: dict[str, Any]) -> str:
    encoded = json.dumps(scenario, sort_keys=True, separators=(",", ":")).encode()
    suffix = hashlib.sha256(encoded).hexdigest()[:10]
    return f"d{scenario['distance']}_r{scenario['rounds']}_{suffix}"


def stable_seed(master_seed: int, *parts: object) -> int:
    encoded = "|".join(map(str, (master_seed, *parts))).encode()
    return int.from_bytes(hashlib.sha256(encoded).digest()[:8], "little")

