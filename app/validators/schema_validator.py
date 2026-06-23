from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ValidationError

from app.schemas.alarm import AlarmRecord
from app.schemas.export import GeneratedDataset, ValidationReport
from app.schemas.incident import IncidentRecord
from app.schemas.kpi import KPIRecord
from app.schemas.service import ServiceImpactRecord
from app.schemas.topology import Topology
from app.validators.anomaly_validator import validate_scenario_behavior
from app.validators.consistency_validator import validate_consistency


def _counts(dataset: GeneratedDataset) -> dict[str, int]:
    return {
        "topology_entities": len(dataset.topology.entities),
        "topology_relationships": len(dataset.topology.relationships),
        "ran_kpis": len(dataset.ran_kpis),
        "core_kpis": len(dataset.core_kpis),
        "transport_kpis": len(dataset.transport_kpis),
        "cloud_kpis": len(dataset.cloud_kpis),
        "oss_kpis": len(dataset.oss_kpis),
        "alarms": len(dataset.alarms),
        "incidents": len(dataset.incidents),
        "service_impact": len(dataset.service_impact),
    }


def validate_dataset(dataset: GeneratedDataset, scenario: str | None = None) -> ValidationReport:
    errors: list[str] = []
    warnings: list[str] = []
    errors.extend(validate_consistency(dataset))
    errors.extend(validate_scenario_behavior(dataset, scenario or _infer_scenario(dataset)))
    if dataset.incidents and not dataset.service_impact:
        warnings.append("incidents exist without service impact records")
    return ValidationReport(
        valid=not errors,
        errors=errors,
        warnings=warnings,
        counts=_counts(dataset),
        scenario=scenario or _infer_scenario(dataset),
    )


def _infer_scenario(dataset: GeneratedDataset) -> str | None:
    all_kpis = dataset.ran_kpis + dataset.core_kpis + dataset.transport_kpis + dataset.cloud_kpis + dataset.oss_kpis
    return all_kpis[0].scenario.value if all_kpis else None


def _read_jsonl[T: BaseModel](path: Path, model: type[T]) -> tuple[list[T], list[str]]:
    records: list[T] = []
    errors: list[str] = []
    if not path.exists():
        return records, [f"missing required file: {path.name}"]
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                records.append(model.model_validate_json(line))
            except ValidationError as exc:
                errors.append(f"{path.name}:{line_number}: {exc.errors()[0]['msg']}")
    return records, errors


def _read_topology(path: Path) -> tuple[Topology | None, list[str]]:
    if not path.exists():
        return None, ["missing required file: topology.json"]
    try:
        return Topology.model_validate_json(path.read_text(encoding="utf-8")), []
    except ValidationError as exc:
        return None, [f"topology.json: {exc.errors()[0]['msg']}"]


def load_and_validate_directory(input_dir: Path) -> ValidationReport:
    topology, errors = _read_topology(input_dir / "topology.json")
    ran, ran_errors = _read_jsonl(input_dir / "ran_kpis.jsonl", KPIRecord)
    core, core_errors = _read_jsonl(input_dir / "core_kpis.jsonl", KPIRecord)
    transport, transport_errors = _read_jsonl(input_dir / "transport_kpis.jsonl", KPIRecord)
    cloud, cloud_errors = _read_jsonl(input_dir / "cloud_kpis.jsonl", KPIRecord)
    oss, oss_errors = _read_jsonl(input_dir / "oss_kpis.jsonl", KPIRecord)
    alarms, alarm_errors = _read_jsonl(input_dir / "alarms.jsonl", AlarmRecord)
    incidents, incident_errors = _read_jsonl(input_dir / "incidents.jsonl", IncidentRecord)
    impact, impact_errors = _read_jsonl(input_dir / "service_impact.jsonl", ServiceImpactRecord)
    errors.extend(ran_errors + core_errors + transport_errors + cloud_errors + oss_errors + alarm_errors + incident_errors + impact_errors)
    if topology is None:
        return ValidationReport(valid=False, errors=errors, counts={})
    dataset = GeneratedDataset(
        topology=topology,
        ran_kpis=ran,
        core_kpis=core,
        transport_kpis=transport,
        cloud_kpis=cloud,
        oss_kpis=oss,
        alarms=alarms,
        incidents=incidents,
        service_impact=impact,
    )
    report = validate_dataset(dataset)
    report.errors = errors + report.errors
    report.valid = not report.errors
    (input_dir / "validation_report.json").write_text(
        json.dumps(report.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report
