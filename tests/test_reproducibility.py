from __future__ import annotations

from app.generators import generate_dataset
from tests.conftest import small_config


def test_same_seed_produces_identical_records() -> None:
    first = generate_dataset(small_config("ran_congestion", seed=99))
    second = generate_dataset(small_config("ran_congestion", seed=99))
    assert first.model_dump(mode="json") == second.model_dump(mode="json")
