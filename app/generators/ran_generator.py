from __future__ import annotations

import random
from datetime import datetime

from app.config import GenerationConfig
from app.generators.metrics import jitter, severity, unit_for
from app.schemas.common import Domain, EntityType, Scenario
from app.schemas.kpi import KPIRecord
from app.schemas.topology import Entity


def _value(metric: str, affected: bool, scenario: str, rng: random.Random) -> float:
    if metric == "prb_utilization_pct":
        return jitter(rng, 92 if affected and scenario == "ran_congestion" else 48, 4)
    if metric == "rrc_connected_users":
        return round(jitter(rng, 920 if affected and scenario == "ran_congestion" else 260, 35, 0, 2000), 0)
    if metric == "active_users":
        if affected and scenario == "cell_outage":
            return 0
        return round(jitter(rng, 760 if affected and scenario == "ran_congestion" else 180, 30, 0, 2000), 0)
    if metric == "downlink_throughput_mbps":
        return jitter(rng, 24 if affected and scenario in {"ran_congestion", "cell_outage"} else 145, 10, 0, 1000)
    if metric == "uplink_throughput_mbps":
        return jitter(rng, 8 if affected and scenario in {"ran_congestion", "cell_outage"} else 45, 6, 0, 500)
    if metric == "sinr_db":
        return jitter(rng, 8 if affected and scenario == "ran_congestion" else 21, 2, -10, 40)
    if metric == "rsrp_dbm":
        return jitter(rng, -111 if affected and scenario == "cell_outage" else -88, 4, -130, -60)
    if metric == "handover_success_rate_pct":
        return jitter(rng, 82 if affected and scenario == "ran_congestion" else 98, 1.5)
    if metric == "call_drop_rate_pct":
        return jitter(rng, 6.5 if affected and scenario in {"ran_congestion", "cell_outage"} else 0.35, 0.2)
    if metric == "availability_pct":
        return jitter(rng, 1 if affected and scenario == "cell_outage" else 99.95, 0.1)
    if metric == "cell_edge_user_pct":
        return jitter(rng, 34 if affected and scenario == "ran_congestion" else 12, 3)
    raise ValueError(metric)


def generate_ran_kpis(config: GenerationConfig, cells: list[Entity], times: list[datetime]) -> list[KPIRecord]:
    rng = random.Random(config.seed + 101)
    affected_id = "syn-cell-01-001-01"
    metrics = [
        "prb_utilization_pct",
        "rrc_connected_users",
        "active_users",
        "downlink_throughput_mbps",
        "uplink_throughput_mbps",
        "sinr_db",
        "rsrp_dbm",
        "handover_success_rate_pct",
        "call_drop_rate_pct",
        "availability_pct",
        "cell_edge_user_pct",
    ]
    records: list[KPIRecord] = []
    for timestamp in times:
        for cell in cells:
            affected = cell.id == affected_id or (config.scenario == "fiber_cut" and cell.id.startswith("syn-cell-01-001"))
            for metric in metrics:
                value = _value(metric, affected, config.scenario, rng)
                records.append(
                    KPIRecord(
                        timestamp=timestamp,
                        domain=Domain.ran,
                        entity_id=cell.id,
                        entity_type=EntityType.cell,
                        metric_name=metric,
                        metric_value=value,
                        unit=unit_for(metric),
                        scenario=Scenario(config.scenario),
                        severity_hint=severity(metric, value),
                    )
                )
    return records
