from __future__ import annotations

from datetime import datetime, timedelta

from app.config import GenerationConfig
from app.scenarios import get_scenario
from app.schemas.alarm import AlarmRecord
from app.schemas.common import Domain, EntityType, Scenario, Severity
from app.schemas.incident import IncidentRecord
from app.schemas.topology import Topology


def _affected(config: GenerationConfig) -> tuple[Domain, EntityType, list[str], Severity]:
    mapping: dict[str, tuple[Domain, EntityType, list[str], Severity]] = {
        "ran_congestion": (Domain.ran, EntityType.cell, ["syn-cell-01-001-01"], Severity.major),
        "fiber_cut": (Domain.transport, EntityType.transport_link, ["syn-link-01-001-01", "syn-router-01-agg-01"], Severity.critical),
        "upf_degradation": (Domain.core, EntityType.upf, ["syn-upf-01-01"], Severity.major),
        "signaling_storm": (Domain.core, EntityType.amf, ["syn-amf-01-01", "syn-smf-01-01"], Severity.major),
        "cell_outage": (Domain.ran, EntityType.cell, ["syn-cell-01-001-01"], Severity.critical),
        "slice_degradation": (Domain.oss, EntityType.service_slice, ["syn-slice-01-embb"], Severity.major),
    }
    return mapping[config.scenario]


def generate_incidents(config: GenerationConfig, start: datetime) -> list[IncidentRecord]:
    if config.scenario == "normal":
        return []
    profile = get_scenario(config.scenario)
    domain, _entity_type, entities, sev = _affected(config)
    return [
        IncidentRecord(
            incident_id=f"syn-inc-{config.scenario}-001",
            start_time=start + timedelta(minutes=config.interval_minutes),
            end_time=start + timedelta(hours=config.duration_hours),
            scenario=Scenario(config.scenario),
            affected_domain=domain,
            affected_entities=entities,
            root_cause=profile.probable_cause,
            symptoms=[profile.symptom],
            customer_impact=f"Synthetic customer experience impact for {config.scenario.replace('_', ' ')}.",
            severity=sev,
            suggested_remediation=profile.remediation,
            rollback_considerations="Validate KPI recovery, alarm clearance, and service impact before closing the loop.",
            validation_checks=[
                "Confirm affected entity KPI returns to normal range.",
                "Confirm correlated alarms stop increasing.",
                "Confirm synthetic service impact score improves.",
            ],
            correlation_id=f"syn-corr-{config.scenario}-001",
        )
    ]


def generate_alarms(config: GenerationConfig, topology: Topology, start: datetime) -> list[AlarmRecord]:
    del topology
    if config.scenario == "normal":
        return [
            AlarmRecord(
                timestamp=start,
                alarm_id="syn-alarm-normal-001",
                domain=Domain.oss,
                entity_id="syn-slice-01-embb",
                entity_type=EntityType.service_slice,
                severity=Severity.info,
                probable_cause="Routine synthetic threshold observation",
                specific_problem="Informational baseline alarm",
                description="Low-severity synthetic alarm included to model routine OSS noise.",
                correlation_id="syn-corr-normal-001",
                scenario=Scenario.normal,
            )
        ]
    profile = get_scenario(config.scenario)
    domain, entity_type, entities, sev = _affected(config)
    probable_cause = profile.probable_cause
    alarms: list[AlarmRecord] = []
    for idx, entity_id in enumerate(entities, start=1):
        alarms.append(
            AlarmRecord(
                timestamp=start + timedelta(minutes=config.interval_minutes * idx),
                alarm_id=f"syn-alarm-{config.scenario}-{idx:03d}",
                domain=domain,
                entity_id=entity_id,
                entity_type=entity_type if idx == 1 else (EntityType.router if entity_id.startswith("syn-router") else entity_type),
                severity=sev,
                probable_cause=probable_cause,
                specific_problem=profile.symptom,
                description=f"Synthetic {config.scenario.replace('_', ' ')} alarm for {entity_id}.",
                correlation_id=f"syn-corr-{config.scenario}-001",
                scenario=Scenario(config.scenario),
            )
        )
    if config.scenario == "fiber_cut":
        alarms.append(
            AlarmRecord(
                timestamp=start + timedelta(minutes=config.interval_minutes * 2),
                alarm_id="syn-alarm-fiber_cut-003",
                domain=Domain.ran,
                entity_id="syn-cell-01-001-01",
                entity_type=EntityType.cell,
                severity=Severity.major,
                probable_cause="Downstream RAN impact from transport failure",
                specific_problem="Cell backhaul impairment",
                description="Synthetic correlated RAN impact from a transport fiber cut.",
                correlation_id="syn-corr-fiber_cut-001",
                scenario=Scenario.fiber_cut,
            )
        )
    return alarms

