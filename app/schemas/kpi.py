from __future__ import annotations

from datetime import datetime

from pydantic import field_validator, model_validator

from app.schemas.common import Domain, EntityType, Scenario, SeverityHint, StrictBaseModel

PERCENT_METRICS = {
    "prb_utilization_pct",
    "handover_success_rate_pct",
    "call_drop_rate_pct",
    "availability_pct",
    "cell_edge_user_pct",
    "amf_registration_success_rate_pct",
    "smf_session_establishment_success_rate_pct",
    "upf_packet_loss_pct",
    "policy_control_success_rate_pct",
    "nssf_slice_selection_success_rate_pct",
    "control_plane_cpu_pct",
    "user_plane_cpu_pct",
    "interface_utilization_pct",
    "packet_loss_pct",
    "link_availability_pct",
    "pod_cpu_pct",
    "pod_memory_pct",
    "node_cpu_pct",
    "node_memory_pct",
    "nf_pod_ready_pct",
    "deployment_replicas_available_pct",
    "sla_compliance_pct",
}


class KPIRecord(StrictBaseModel):
    timestamp: datetime
    domain: Domain
    entity_id: str
    entity_type: EntityType
    metric_name: str
    metric_value: float
    unit: str
    scenario: Scenario
    severity_hint: SeverityHint = SeverityHint.normal
    synthetic: bool = True

    @field_validator("timestamp")
    @classmethod
    def utc_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("timestamp must include timezone")
        return value

    @model_validator(mode="after")
    def plausible_range(self) -> KPIRecord:
        if not self.synthetic:
            raise ValueError("KPI records must be synthetic")
        if self.metric_name in PERCENT_METRICS and not 0 <= self.metric_value <= 100:
            raise ValueError(f"{self.metric_name} must be between 0 and 100")
        if any(token in self.metric_name for token in ("latency", "jitter")) and self.metric_value < 0:
            raise ValueError("latency and jitter must be non-negative")
        if not self.metric_name.endswith(("_db", "_dbm")) and self.metric_value < 0:
            raise ValueError(f"{self.metric_name} must be non-negative")
        return self
