from __future__ import annotations

import random

from app.schemas.common import SeverityHint


def bounded(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return round(min(high, max(low, value)), 3)


def jitter(rng: random.Random, base: float, spread: float, low: float = 0.0, high: float = 100.0) -> float:
    return bounded(rng.gauss(base, spread), low, high)


def severity(metric: str, value: float) -> SeverityHint:
    if metric in {"availability_pct", "link_availability_pct", "nf_pod_ready_pct", "deployment_replicas_available_pct", "sla_compliance_pct"}:
        if value < 85:
            return SeverityHint.critical
        if value < 95:
            return SeverityHint.warning
        return SeverityHint.normal
    if metric.endswith("_success_rate_pct") or metric == "handover_success_rate_pct":
        if value < 80:
            return SeverityHint.critical
        if value < 94:
            return SeverityHint.warning
        return SeverityHint.normal
    if any(token in metric for token in ("loss", "drop", "crc_error")):
        if value > 5:
            return SeverityHint.critical
        if value > 1:
            return SeverityHint.warning
        return SeverityHint.normal
    if any(token in metric for token in ("latency", "jitter")):
        if value > 100:
            return SeverityHint.critical
        if value > 50:
            return SeverityHint.warning
        return SeverityHint.normal
    if value > 90:
        return SeverityHint.critical
    if value > 75:
        return SeverityHint.warning
    return SeverityHint.normal


def unit_for(metric: str) -> str:
    if metric.endswith("_pct") or metric.endswith("_rate"):
        return "%"
    if metric.endswith("_ms"):
        return "ms"
    if metric.endswith("_db"):
        return "dB"
    if metric.endswith("_dbm"):
        return "dBm"
    if metric.endswith("_mbps"):
        return "Mbps"
    if metric.endswith("_count"):
        return "count"
    if metric.endswith("_minutes"):
        return "minutes"
    if metric.endswith("_per_sec"):
        return "packets/sec"
    return "count"

