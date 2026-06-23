from __future__ import annotations

from app.schemas.common import EntityType
from app.schemas.topology import Topology


def validate_topology(topology: Topology) -> list[str]:
    errors: list[str] = []
    required = {
        EntityType.region,
        EntityType.market,
        EntityType.site,
        EntityType.cell,
        EntityType.gnodeb,
        EntityType.amf,
        EntityType.smf,
        EntityType.upf,
        EntityType.transport_link,
        EntityType.router,
        EntityType.kubernetes_cluster,
        EntityType.nf_pod,
        EntityType.service_slice,
        EntityType.customer_segment,
    }
    present = {entity.type for entity in topology.entities}
    missing = required - present
    if missing:
        errors.append(f"topology missing entity types: {', '.join(sorted(item.value for item in missing))}")
    return errors

