from __future__ import annotations

from collections.abc import Sequence

from app.schemas.alarm import AlarmRecord
from app.schemas.export import GeneratedDataset
from app.schemas.kpi import KPIRecord


def validate_consistency(dataset: GeneratedDataset) -> list[str]:
    errors: list[str] = []
    entity_ids = dataset.topology.entity_ids()
    for rel in dataset.topology.relationships:
        if rel.source_id not in entity_ids or rel.target_id not in entity_ids:
            errors.append(f"relationship references unknown entity: {rel.source_id}->{rel.target_id}")
    entity_records: list[tuple[str, Sequence[KPIRecord | AlarmRecord]]] = [
        ("ran_kpis", dataset.ran_kpis),
        ("core_kpis", dataset.core_kpis),
        ("transport_kpis", dataset.transport_kpis),
        ("cloud_kpis", dataset.cloud_kpis),
        ("oss_kpis", dataset.oss_kpis),
        ("alarms", dataset.alarms),
    ]
    for file_name, records in entity_records:
        for record in records:
            if record.entity_id not in entity_ids:
                errors.append(f"{file_name} references unknown entity: {record.entity_id}")
            if not record.synthetic:
                errors.append(f"{file_name} record missing synthetic flag: {record}")
    for incident in dataset.incidents:
        for entity_id in incident.affected_entities:
            if entity_id not in entity_ids:
                errors.append(f"incident references unknown entity: {entity_id}")
    service_slices = {entity.id for entity in dataset.topology.entities if entity.type.value == "service_slice"}
    for impact in dataset.service_impact:
        if impact.service_slice not in service_slices:
            errors.append(f"service impact references unknown slice: {impact.service_slice}")
        if impact.related_incident_id and impact.related_incident_id not in {incident.incident_id for incident in dataset.incidents}:
            errors.append(f"service impact references unknown incident: {impact.related_incident_id}")
    kpi_records: list[tuple[str, Sequence[KPIRecord]]] = [
        ("ran_kpis", dataset.ran_kpis),
        ("core_kpis", dataset.core_kpis),
        ("transport_kpis", dataset.transport_kpis),
        ("cloud_kpis", dataset.cloud_kpis),
        ("oss_kpis", dataset.oss_kpis),
    ]
    for name, records in kpi_records:
        timestamps = [record.timestamp for record in records]
        if timestamps != sorted(timestamps):
            errors.append(f"{name} timestamps are not ordered")
    return errors
