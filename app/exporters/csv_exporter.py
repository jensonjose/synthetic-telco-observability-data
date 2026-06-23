from __future__ import annotations

import csv
import json
from collections.abc import Iterable
from pathlib import Path

from pydantic import BaseModel

from app.schemas.export import GeneratedDataset


def _flatten(record: BaseModel) -> dict[str, str | int | float | bool | None]:
    data = record.model_dump(mode="json")
    flattened: dict[str, str | int | float | bool | None] = {}
    for key, value in data.items():
        if isinstance(value, list | dict):
            flattened[key] = json.dumps(value, sort_keys=True)
        else:
            flattened[key] = value
    return flattened


def _write_csv(path: Path, records: Iterable[BaseModel]) -> None:
    rows = [_flatten(record) for record in records]
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def export_csv(dataset: GeneratedDataset, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(output_dir / "topology_entities.csv", dataset.topology.entities)
    _write_csv(output_dir / "topology_relationships.csv", dataset.topology.relationships)
    _write_csv(output_dir / "ran_kpis.csv", dataset.ran_kpis)
    _write_csv(output_dir / "core_kpis.csv", dataset.core_kpis)
    _write_csv(output_dir / "transport_kpis.csv", dataset.transport_kpis)
    _write_csv(output_dir / "cloud_kpis.csv", dataset.cloud_kpis)
    _write_csv(output_dir / "oss_kpis.csv", dataset.oss_kpis)
    _write_csv(output_dir / "alarms.csv", dataset.alarms)
    _write_csv(output_dir / "incidents.csv", dataset.incidents)
    _write_csv(output_dir / "service_impact.csv", dataset.service_impact)
