from __future__ import annotations

from app.schemas.export import GeneratedDataset


def _metric_values(dataset: GeneratedDataset, metric: str) -> list[float]:
    records = dataset.ran_kpis + dataset.core_kpis + dataset.transport_kpis + dataset.cloud_kpis + dataset.oss_kpis
    return [record.metric_value for record in records if record.metric_name == metric]


def validate_scenario_behavior(dataset: GeneratedDataset, scenario: str | None) -> list[str]:
    if scenario is None:
        return ["unable to infer scenario"]
    errors: list[str] = []
    if scenario == "normal":
        if any(incident.severity.value in {"major", "critical"} for incident in dataset.incidents):
            errors.append("normal scenario must not contain major or critical incidents")
        return errors
    if not dataset.incidents:
        errors.append(f"{scenario} must generate at least one incident")
    if not dataset.service_impact:
        errors.append(f"{scenario} must generate service impact records")
    max_checks = {
        "ran_congestion": ("prb_utilization_pct", 80.0),
        "fiber_cut": ("packet_loss_pct", 20.0),
        "upf_degradation": ("upf_latency_ms", 80.0),
        "signaling_storm": ("control_plane_cpu_pct", 80.0),
    }
    min_checks = {
        "cell_outage": ("availability_pct", 20.0),
        "slice_degradation": ("sla_compliance_pct", 90.0),
    }
    if scenario in max_checks:
        metric, threshold = max_checks[scenario]
        values = _metric_values(dataset, metric)
        observed = max(values) if values else 0
        if observed < threshold:
            errors.append(f"{scenario} expected elevated {metric}, observed {observed}")
    if scenario in min_checks:
        metric, threshold = min_checks[scenario]
        values = _metric_values(dataset, metric)
        observed = min(values) if values else 100
        if observed > threshold:
            errors.append(f"{scenario} expected low {metric}, observed {observed}")
    return errors
