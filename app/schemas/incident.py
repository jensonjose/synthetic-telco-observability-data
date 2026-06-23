from __future__ import annotations

from datetime import datetime

from pydantic import Field, model_validator

from app.schemas.common import Domain, Scenario, Severity, StrictBaseModel


class IncidentRecord(StrictBaseModel):
    incident_id: str
    start_time: datetime
    end_time: datetime
    scenario: Scenario
    affected_domain: Domain
    affected_entities: list[str] = Field(min_length=1)
    root_cause: str
    symptoms: list[str] = Field(min_length=1)
    customer_impact: str
    severity: Severity
    suggested_remediation: str
    rollback_considerations: str
    validation_checks: list[str] = Field(min_length=1)
    correlation_id: str
    synthetic: bool = True

    @model_validator(mode="after")
    def validate_incident(self) -> IncidentRecord:
        if self.end_time < self.start_time:
            raise ValueError("incident end_time must not be before start_time")
        if not self.incident_id.startswith("syn-inc-"):
            raise ValueError("incident_id must use syn-inc- prefix")
        if not self.synthetic:
            raise ValueError("incident records must be synthetic")
        return self

