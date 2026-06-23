from __future__ import annotations

from tests.conftest import small_dataset


def test_cloud_kpis_are_generated() -> None:
    dataset = small_dataset()
    metrics = {record.metric_name for record in dataset.cloud_kpis}
    assert "pod_cpu_pct" in metrics
    assert "deployment_replicas_available_pct" in metrics

