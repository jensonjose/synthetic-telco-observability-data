from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Domain(StrEnum):
    ran = "ran"
    core = "core"
    transport = "transport"
    cloud = "cloud"
    oss = "oss"


class EntityType(StrEnum):
    region = "region"
    market = "market"
    site = "site"
    cell = "cell"
    gnodeb = "gnodeb"
    amf = "amf"
    smf = "smf"
    upf = "upf"
    pcf = "pcf"
    nssf = "nssf"
    transport_link = "transport_link"
    router = "router"
    kubernetes_cluster = "kubernetes_cluster"
    nf_pod = "nf_pod"
    service_slice = "service_slice"
    customer_segment = "customer_segment"


class OperationalStatus(StrEnum):
    active = "active"
    degraded = "degraded"
    down = "down"
    maintenance = "maintenance"


class Severity(StrEnum):
    info = "info"
    minor = "minor"
    major = "major"
    critical = "critical"


class SeverityHint(StrEnum):
    normal = "normal"
    warning = "warning"
    critical = "critical"


class Scenario(StrEnum):
    normal = "normal"
    ran_congestion = "ran_congestion"
    fiber_cut = "fiber_cut"
    upf_degradation = "upf_degradation"
    signaling_storm = "signaling_storm"
    cell_outage = "cell_outage"
    slice_degradation = "slice_degradation"

