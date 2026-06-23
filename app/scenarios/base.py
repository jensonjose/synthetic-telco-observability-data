from __future__ import annotations

from dataclasses import dataclass

from app.schemas.common import Domain


@dataclass(frozen=True)
class ScenarioProfile:
    name: str
    description: str
    affected_domain: Domain | None
    probable_cause: str
    remediation: str
    symptom: str


SCENARIOS: dict[str, ScenarioProfile] = {
    "normal": ScenarioProfile(
        "normal",
        "Healthy synthetic network baseline with minor noise.",
        None,
        "No material fault",
        "Continue monitoring synthetic baseline.",
        "Nominal service behavior",
    ),
    "ran_congestion": ScenarioProfile(
        "ran_congestion",
        "Busy RAN cell or site with elevated PRB utilization and reduced experience.",
        Domain.ran,
        "High PRB utilization",
        "Review capacity, tune scheduler parameters, and validate neighbor load before changes.",
        "Reduced radio throughput and elevated call drops",
    ),
    "fiber_cut": ScenarioProfile(
        "fiber_cut",
        "Transport link failure affecting downstream RAN and service quality.",
        Domain.transport,
        "Fiber cut suspected",
        "Reroute traffic, dispatch field repair, and validate transport convergence.",
        "Packet loss and loss of link availability",
    ),
    "upf_degradation": ScenarioProfile(
        "upf_degradation",
        "User-plane latency and packet loss degradation around an affected UPF.",
        Domain.core,
        "UPF latency degradation",
        "Scale out UPF, reroute sessions, or run UPF health checks with rollback validation.",
        "Elevated user-plane latency and packet loss",
    ),
    "signaling_storm": ScenarioProfile(
        "signaling_storm",
        "Control-plane overload with AMF/SMF CPU pressure and lower success rates.",
        Domain.core,
        "Signaling storm suspected",
        "Apply rate limiting, traffic filtering, and investigate abnormal source patterns.",
        "Registration and session establishment failures",
    ),
    "cell_outage": ScenarioProfile(
        "cell_outage",
        "Affected cell becomes unavailable while neighbors absorb additional load.",
        Domain.ran,
        "Cell unavailable",
        "Validate cell health, power, backhaul, and configuration before restoring service.",
        "Cell availability near zero",
    ),
    "slice_degradation": ScenarioProfile(
        "slice_degradation",
        "Service slice SLA and experience degradation tied to synthetic services.",
        Domain.oss,
        "Slice SLA degradation",
        "Inspect slice policy, impacted domains, and guardrails before remediation.",
        "Service experience score degradation",
    ),
}


def get_scenario(name: str) -> ScenarioProfile:
    try:
        return SCENARIOS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown scenario: {name}") from exc

