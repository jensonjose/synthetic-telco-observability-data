from __future__ import annotations

from tests.conftest import small_dataset


def test_non_normal_scenario_has_incident_and_service_impact() -> None:
    dataset = small_dataset("cell_outage")
    assert dataset.incidents
    assert dataset.service_impact
    assert dataset.incidents[0].correlation_id == "syn-corr-cell_outage-001"


def test_normal_has_no_major_incident() -> None:
    dataset = small_dataset("normal")
    assert dataset.incidents == []

