from __future__ import annotations

from tests.conftest import small_dataset


def test_upf_degradation_elevates_latency() -> None:
    dataset = small_dataset("upf_degradation")
    values = [record.metric_value for record in dataset.core_kpis if record.metric_name == "upf_latency_ms"]
    assert max(values) >= 80


def test_signaling_storm_elevates_control_plane_cpu() -> None:
    dataset = small_dataset("signaling_storm")
    values = [record.metric_value for record in dataset.core_kpis if record.metric_name == "control_plane_cpu_pct"]
    assert max(values) >= 80

