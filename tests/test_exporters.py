from __future__ import annotations

from app.exporters import export_csv, export_jsonl
from tests.conftest import small_dataset


def test_jsonl_and_csv_exports(tmp_path) -> None:  # type: ignore[no-untyped-def]
    dataset = small_dataset("upf_degradation")
    export_jsonl(dataset, tmp_path)
    export_csv(dataset, tmp_path)
    assert (tmp_path / "topology.json").exists()
    assert (tmp_path / "ran_kpis.jsonl").exists()
    assert (tmp_path / "ran_kpis.csv").exists()
    assert (tmp_path / "validation_report.json").exists()

