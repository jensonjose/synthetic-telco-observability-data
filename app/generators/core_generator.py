from __future__ import annotations

import random
from datetime import datetime

from app.config import GenerationConfig
from app.generators.metrics import jitter, severity, unit_for
from app.schemas.common import Domain, EntityType, Scenario
from app.schemas.kpi import KPIRecord
from app.schemas.topology import Entity


def _metrics_for(entity_type: EntityType) -> list[str]:
    if entity_type == EntityType.amf:
        return ["amf_registration_success_rate_pct", "control_plane_cpu_pct", "session_release_rate"]
    if entity_type == EntityType.smf:
        return ["smf_session_establishment_success_rate_pct", "control_plane_cpu_pct", "session_release_rate"]
    if entity_type == EntityType.upf:
        return ["upf_latency_ms", "upf_packet_loss_pct", "pdu_session_count", "user_plane_cpu_pct"]
    if entity_type == EntityType.pcf:
        return ["policy_control_success_rate_pct", "control_plane_cpu_pct"]
    if entity_type == EntityType.nssf:
        return ["nssf_slice_selection_success_rate_pct", "control_plane_cpu_pct"]
    return []


def _value(metric: str, affected: bool, scenario: str, rng: random.Random) -> float:
    storm = affected and scenario == "signaling_storm"
    upf_bad = affected and scenario == "upf_degradation"
    if metric == "amf_registration_success_rate_pct":
        return jitter(rng, 76 if storm else 99.2, 1.5)
    if metric == "smf_session_establishment_success_rate_pct":
        return jitter(rng, 78 if storm else 98.9, 1.5)
    if metric == "upf_latency_ms":
        return jitter(rng, 145 if upf_bad else 18, 4, 0, 500)
    if metric == "upf_packet_loss_pct":
        return jitter(rng, 7.0 if upf_bad else 0.08, 0.2)
    if metric == "pdu_session_count":
        return round(jitter(rng, 64000, 2500, 0, 200000), 0)
    if metric == "policy_control_success_rate_pct":
        return jitter(rng, 91 if storm else 99.1, 1.0)
    if metric == "nssf_slice_selection_success_rate_pct":
        return jitter(rng, 90 if storm else 99.3, 1.0)
    if metric == "control_plane_cpu_pct":
        return jitter(rng, 93 if storm else 43, 4)
    if metric == "user_plane_cpu_pct":
        return jitter(rng, 88 if upf_bad else 52, 4)
    if metric == "session_release_rate":
        return jitter(rng, 9.5 if storm else 1.2, 0.5, 0, 100)
    raise ValueError(metric)


def generate_core_kpis(config: GenerationConfig, core_entities: list[Entity], times: list[datetime]) -> list[KPIRecord]:
    rng = random.Random(config.seed + 202)
    records: list[KPIRecord] = []
    for timestamp in times:
        for entity in core_entities:
            affected = entity.id in {"syn-upf-01-01", "syn-amf-01-01", "syn-smf-01-01"}
            for metric in _metrics_for(entity.type):
                value = _value(metric, affected, config.scenario, rng)
                records.append(
                    KPIRecord(
                        timestamp=timestamp,
                        domain=Domain.core,
                        entity_id=entity.id,
                        entity_type=entity.type,
                        metric_name=metric,
                        metric_value=value,
                        unit=unit_for(metric),
                        scenario=Scenario(config.scenario),
                        severity_hint=severity(metric, value),
                    )
                )
    return records

