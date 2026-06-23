from __future__ import annotations

from tests.conftest import small_dataset


def test_ran_congestion_elevates_prb() -> None:
    dataset = small_dataset("ran_congestion")
    values = [record.metric_value for record in dataset.ran_kpis if record.metric_name == "prb_utilization_pct"]
    assert max(values) >= 80

