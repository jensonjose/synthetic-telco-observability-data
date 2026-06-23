from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from pydantic import BaseModel

from app.schemas.export import GeneratedDataset


def _write_jsonl(path: Path, records: Iterable[BaseModel]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(record.model_dump_json() + "\n")


def export_jsonl(dataset: GeneratedDataset, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "topology.json").write_text(
        json.dumps(dataset.topology.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_jsonl(output_dir / "ran_kpis.jsonl", dataset.ran_kpis)
    _write_jsonl(output_dir / "core_kpis.jsonl", dataset.core_kpis)
    _write_jsonl(output_dir / "transport_kpis.jsonl", dataset.transport_kpis)
    _write_jsonl(output_dir / "cloud_kpis.jsonl", dataset.cloud_kpis)
    _write_jsonl(output_dir / "oss_kpis.jsonl", dataset.oss_kpis)
    _write_jsonl(output_dir / "alarms.jsonl", dataset.alarms)
    _write_jsonl(output_dir / "incidents.jsonl", dataset.incidents)
    _write_jsonl(output_dir / "service_impact.jsonl", dataset.service_impact)
    if dataset.validation_report is not None:
        (output_dir / "validation_report.json").write_text(
            json.dumps(dataset.validation_report.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
