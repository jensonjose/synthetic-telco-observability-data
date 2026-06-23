from __future__ import annotations

import random
from datetime import datetime

from app.config import GenerationConfig
from app.generators.metrics import jitter, severity, unit_for
from app.schemas.common import Domain, EntityType, Scenario
from app.schemas.kpi import KPIRecord
from app.schemas.topology import Entity


def generate_transport_kpis(config: GenerationConfig, links: list[Entity], routers: list[Entity], times: list[datetime]) -> list[KPIRecord]:
    rng = random.Random(config.seed + 303)
    records: list[KPIRecord] = []
    entities = [(link, EntityType.transport_link) for link in links] + [(router, EntityType.router) for router in routers]
    metrics = ["interface_utilization_pct", "packet_loss_pct", "jitter_ms", "latency_ms", "crc_error_rate", "link_availability_pct", "dropped_packets_per_sec"]
    for timestamp in times:
        for entity, entity_type in entities:
            affected = config.scenario == "fiber_cut" and entity.id in {"syn-link-01-001-01", "syn-router-01-agg-01"}
            for metric in metrics:
                if metric == "interface_utilization_pct":
                    value = jitter(rng, 96 if affected else 42, 3)
                elif metric == "packet_loss_pct":
                    value = jitter(rng, 42 if affected else 0.05, 0.2)
                elif metric == "jitter_ms":
                    value = jitter(rng, 88 if affected else 5, 2, 0, 300)
                elif metric == "latency_ms":
                    value = jitter(rng, 180 if affected else 12, 3, 0, 500)
                elif metric == "crc_error_rate":
                    value = jitter(rng, 8 if affected else 0.01, 0.05)
                elif metric == "link_availability_pct":
                    value = jitter(rng, 3 if affected else 99.98, 0.1)
                else:
                    value = round(jitter(rng, 20000 if affected else 2, 4, 0, 100000), 0)
                records.append(
                    KPIRecord(
                        timestamp=timestamp,
                        domain=Domain.transport,
                        entity_id=entity.id,
                        entity_type=entity_type,
                        metric_name=metric,
                        metric_value=value,
                        unit=unit_for(metric),
                        scenario=Scenario(config.scenario),
                        severity_hint=severity(metric, value),
                    )
                )
    return records

