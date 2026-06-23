from __future__ import annotations

from tests.conftest import small_dataset


def test_slice_degradation_lowers_sla_compliance() -> None:
    dataset = small_dataset("slice_degradation")
    values = [record.metric_value for record in dataset.oss_kpis if record.metric_name == "sla_compliance_pct"]
    assert min(values) <= 90

