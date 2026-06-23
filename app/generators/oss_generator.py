from __future__ import annotations

import random
from datetime import datetime

from app.config import GenerationConfig
from app.generators.metrics import jitter, severity, unit_for
from app.schemas.common import Domain, EntityType, Scenario
from app.schemas.kpi import KPIRecord
from app.schemas.topology import Entity


def generate_oss_kpis(config: GenerationConfig, slices: list[Entity], times: list[datetime]) -> list[KPIRecord]:
    rng = random.Random(config.seed + 505)
    scenario_bad = config.scenario != "normal"
    records: list[KPIRecord] = []
    for timestamp in times:
        for service_slice in slices:
            affected = service_slice.id == "syn-slice-01-embb" and config.scenario == "slice_degradation"
            metrics = {
                "incident_count": round(jitter(rng, 1 if scenario_bad else 0, 0.1, 0, 100), 0),
                "mttr_minutes": jitter(rng, 55 if scenario_bad else 12, 3, 0, 1000),
                "alarm_volume": round(jitter(rng, 42 if scenario_bad else 3, 2, 0, 1000), 0),
                "ticket_backlog": round(jitter(rng, 18 if scenario_bad else 4, 1, 0, 1000), 0),
                "sla_compliance_pct": jitter(rng, 82 if affected else (92 if scenario_bad else 99.6), 1.5),
                "service_experience_score": jitter(rng, 58 if affected else (75 if scenario_bad else 94), 2),
                "customer_impact_score": jitter(rng, 74 if scenario_bad else 8, 3),
            }
            for metric, value in metrics.items():
                records.append(KPIRecord(timestamp=timestamp, domain=Domain.oss, entity_id=service_slice.id, entity_type=EntityType.service_slice, metric_name=metric, metric_value=value, unit=unit_for(metric), scenario=Scenario(config.scenario), severity_hint=severity(metric, value)))
    return records

