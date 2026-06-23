from __future__ import annotations

from datetime import datetime

from pydantic import Field, model_validator

from app.schemas.common import StrictBaseModel


class ServiceImpactRecord(StrictBaseModel):
    timestamp: datetime
    service_name: str
    service_slice: str
    region: str
    affected_customer_segment: str
    impacted_users_estimate: int = Field(ge=0)
    experience_score: float = Field(ge=0, le=100)
    sla_status: str
    primary_symptom: str
    related_incident_id: str | None = None
    synthetic: bool = True

    @model_validator(mode="after")
    def require_synthetic_service_impact(self) -> ServiceImpactRecord:
        if not self.synthetic:
            raise ValueError("service impact records must be synthetic")
        return self

