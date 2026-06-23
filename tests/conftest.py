from __future__ import annotations

from app.config import GenerationConfig
from app.generators import generate_dataset


def small_config(scenario: str = "normal", seed: int = 42) -> GenerationConfig:
    return GenerationConfig(
        scenario=scenario,  # type: ignore[arg-type]
        duration_hours=1,
        interval_minutes=15,
        regions=1,
        sites_per_region=2,
        cells_per_site=2,
        seed=seed,
        formats=["jsonl"],
    )


def small_dataset(scenario: str = "normal"):
    return generate_dataset(small_config(scenario))

