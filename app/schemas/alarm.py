from __future__ import annotations

from datetime import datetime

from pydantic import Field, model_validator

from app.schemas.common import Domain, EntityType, Scenario, Severity, StrictBaseModel


class AlarmRecord(StrictBaseModel):
    timestamp: datetime
    alarm_id: str
    domain: Domain
    entity_id: str
    entity_type: EntityType
    severity: Severity
    probable_cause: str
    specific_problem: str
    description: str
    correlation_id: str
    scenario: Scenario
    synthetic: bool = True

    @model_validator(mode="after")
    def require_synthetic_alarm(self) -> AlarmRecord:
        if not self.alarm_id.startswith("syn-alarm-"):
            raise ValueError("alarm_id must use syn-alarm- prefix")
        if not self.correlation_id.startswith("syn-corr-"):
            raise ValueError("correlation_id must use syn-corr- prefix")
        if not self.synthetic:
            raise ValueError("alarm records must be synthetic")
        return self


class AlarmList(StrictBaseModel):
    records: list[AlarmRecord] = Field(default_factory=list)

