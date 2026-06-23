from __future__ import annotations

from datetime import datetime

from app.config import GenerationConfig
from app.scenarios import get_scenario
from app.schemas.service import ServiceImpactRecord
from app.schemas.topology import Entity


def generate_service_impact(config: GenerationConfig, slices: list[Entity], segments: list[Entity], times: list[datetime]) -> list[ServiceImpactRecord]:
    if config.scenario == "normal":
        return []
    profile = get_scenario(config.scenario)
    service_slice = next((entity for entity in slices if entity.id == "syn-slice-01-embb"), slices[0])
    segment = next((entity for entity in segments if entity.parent_id == service_slice.id), segments[0])
    score_by_scenario = {
        "ran_congestion": 72,
        "fiber_cut": 38,
        "upf_degradation": 64,
        "signaling_storm": 67,
        "cell_outage": 25,
        "slice_degradation": 52,
    }
    users_by_scenario = {
        "ran_congestion": 1800,
        "fiber_cut": 6200,
        "upf_degradation": 4200,
        "signaling_storm": 3000,
        "cell_outage": 2100,
        "slice_degradation": 5200,
    }
    return [
        ServiceImpactRecord(
            timestamp=times[-1],
            service_name=f"Synthetic {str(service_slice.attributes.get('slice_type', 'embb')).upper()} Service",
            service_slice=service_slice.id,
            region=service_slice.region,
            affected_customer_segment=str(segment.attributes.get("segment", "consumer")),
            impacted_users_estimate=users_by_scenario[config.scenario],
            experience_score=score_by_scenario[config.scenario],
            sla_status="breached" if score_by_scenario[config.scenario] < 60 else "at_risk",
            primary_symptom=profile.symptom,
            related_incident_id=f"syn-inc-{config.scenario}-001",
        )
    ]
