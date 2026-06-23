from __future__ import annotations

from tests.conftest import small_dataset


def test_fiber_cut_elevates_packet_loss() -> None:
    dataset = small_dataset("fiber_cut")
    values = [record.metric_value for record in dataset.transport_kpis if record.metric_name == "packet_loss_pct"]
    assert max(values) >= 20

