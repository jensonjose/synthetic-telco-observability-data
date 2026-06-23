from __future__ import annotations

from copy import deepcopy

from app.validators import validate_dataset
from tests.conftest import small_dataset


def test_consistency_validator_catches_unknown_kpi_entity() -> None:
    dataset = deepcopy(small_dataset())
    dataset.ran_kpis[0].entity_id = "syn-missing"
    report = validate_dataset(dataset)
    assert not report.valid
    assert any("unknown entity" in error for error in report.errors)

