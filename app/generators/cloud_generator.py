from __future__ import annotations

import random
from datetime import datetime

from app.config import GenerationConfig
from app.generators.metrics import jitter, severity, unit_for
from app.schemas.common import Domain, EntityType, Scenario
from app.schemas.kpi import KPIRecord
from app.schemas.topology import Entity


def generate_cloud_kpis(config: GenerationConfig, pods: list[Entity], clusters: list[Entity], times: list[datetime]) -> list[KPIRecord]:
    rng = random.Random(config.seed + 404)
    records: list[KPIRecord] = []
    for timestamp in times:
        for pod in pods:
            affected = config.scenario == "signaling_storm" and pod.attributes.get("nf_type") in {"amf", "smf"}
            pod_metrics = {
                "pod_restart_count": round(jitter(rng, 3 if affected else 0.05, 0.2, 0, 20), 0),
                "pod_cpu_pct": jitter(rng, 92 if affected else 38, 4),
                "pod_memory_pct": jitter(rng, 84 if affected else 45, 5),
                "container_network_latency_ms": jitter(rng, 65 if affected else 8, 2, 0, 200),
                "nf_pod_ready_pct": jitter(rng, 82 if affected else 100, 0.2),
            }
            for metric, value in pod_metrics.items():
                records.append(KPIRecord(timestamp=timestamp, domain=Domain.cloud, entity_id=pod.id, entity_type=EntityType.nf_pod, metric_name=metric, metric_value=value, unit=unit_for(metric), scenario=Scenario(config.scenario), severity_hint=severity(metric, value)))
        for cluster in clusters:
            cluster_metrics = {
                "node_cpu_pct": jitter(rng, 72 if config.scenario == "signaling_storm" else 44, 4),
                "node_memory_pct": jitter(rng, 68 if config.scenario == "signaling_storm" else 47, 4),
                "deployment_replicas_available_pct": jitter(rng, 92 if config.scenario == "signaling_storm" else 100, 0.4),
            }
            for metric, value in cluster_metrics.items():
                records.append(KPIRecord(timestamp=timestamp, domain=Domain.cloud, entity_id=cluster.id, entity_type=EntityType.kubernetes_cluster, metric_name=metric, metric_value=value, unit=unit_for(metric), scenario=Scenario(config.scenario), severity_hint=severity(metric, value)))
    return records

