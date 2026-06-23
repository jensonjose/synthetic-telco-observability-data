from __future__ import annotations

from pydantic import Field

from app.schemas.alarm import AlarmRecord
from app.schemas.common import StrictBaseModel
from app.schemas.incident import IncidentRecord
from app.schemas.kpi import KPIRecord
from app.schemas.service import ServiceImpactRecord
from app.schemas.topology import Topology


class ValidationReport(StrictBaseModel):
    valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    counts: dict[str, int] = Field(default_factory=dict)
    scenario: str | None = None
    synthetic: bool = True


class GeneratedDataset(StrictBaseModel):
    topology: Topology
    ran_kpis: list[KPIRecord] = Field(default_factory=list)
    core_kpis: list[KPIRecord] = Field(default_factory=list)
    transport_kpis: list[KPIRecord] = Field(default_factory=list)
    cloud_kpis: list[KPIRecord] = Field(default_factory=list)
    oss_kpis: list[KPIRecord] = Field(default_factory=list)
    alarms: list[AlarmRecord] = Field(default_factory=list)
    incidents: list[IncidentRecord] = Field(default_factory=list)
    service_impact: list[ServiceImpactRecord] = Field(default_factory=list)
    validation_report: ValidationReport | None = None

