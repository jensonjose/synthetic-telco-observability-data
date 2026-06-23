from __future__ import annotations

import random

from app.config import GenerationConfig
from app.schemas.common import EntityType, OperationalStatus
from app.schemas.topology import Entity, Relationship, Topology


def _coords(rng: random.Random, region_idx: int) -> dict[str, float]:
    return {
        "latitude": round(10.0 + region_idx * 4.5 + rng.uniform(-0.25, 0.25), 5),
        "longitude": round(70.0 + region_idx * 2.5 + rng.uniform(-0.25, 0.25), 5),
    }


def _entity(
    entity_id: str,
    entity_type: EntityType,
    name: str,
    region: str,
    parent_id: str | None = None,
    capacity: dict[str, float | int | str] | None = None,
    coordinates: dict[str, float] | None = None,
    attributes: dict[str, float | int | str | bool] | None = None,
) -> Entity:
    return Entity(
        id=entity_id,
        type=entity_type,
        name=name,
        region=region,
        parent_id=parent_id,
        capacity=capacity or {},
        coordinates=coordinates,
        attributes=attributes or {},
    )


def _link(
    entities: dict[str, Entity], relationships: list[Relationship], source_id: str, target_id: str, relationship: str
) -> None:
    source = entities[source_id]
    if target_id not in source.child_ids:
        source.child_ids.append(target_id)
    relationships.append(Relationship(source_id=source_id, target_id=target_id, relationship=relationship))


def generate_topology(config: GenerationConfig) -> Topology:
    rng = random.Random(config.seed)
    entities: dict[str, Entity] = {}
    relationships: list[Relationship] = []

    def add(entity: Entity) -> None:
        entities[entity.id] = entity

    for r in range(1, config.regions + 1):
        region_id = f"syn-region-{r:02d}"
        region_name = f"Synthetic Region {r}"
        add(_entity(region_id, EntityType.region, region_name, region_name, coordinates=_coords(rng, r)))

        market_id = f"syn-market-{r:02d}-01"
        add(_entity(market_id, EntityType.market, f"Synthetic Market {r}", region_name, region_id))
        _link(entities, relationships, region_id, market_id, "contains")

        router_id = f"syn-router-{r:02d}-agg-01"
        add(_entity(router_id, EntityType.router, f"Aggregation Router {r}", region_name, region_id, {"gbps": 400}))
        _link(entities, relationships, region_id, router_id, "contains")

        cluster_id = f"syn-k8s-{r:02d}-edge"
        add(_entity(cluster_id, EntityType.kubernetes_cluster, f"Edge Kubernetes Cluster {r}", region_name, region_id))
        _link(entities, relationships, region_id, cluster_id, "hosts")

        core_ids: dict[EntityType, str] = {}
        for nf_type in [EntityType.amf, EntityType.smf, EntityType.upf, EntityType.pcf, EntityType.nssf]:
            nf_id = f"syn-{nf_type.value}-{r:02d}-01"
            core_ids[nf_type] = nf_id
            add(_entity(nf_id, nf_type, f"{nf_type.value.upper()} {r}", region_name, cluster_id, {"sessions": 100000}))
            _link(entities, relationships, cluster_id, nf_id, "runs")
            for pod_idx in range(1, 3):
                pod_id = f"syn-pod-{nf_type.value}-{r:02d}-{pod_idx:02d}"
                add(_entity(pod_id, EntityType.nf_pod, f"{nf_type.value.upper()} Pod {pod_idx}", region_name, nf_id, {"cpu_cores": 4, "memory_gb": 16}, attributes={"nf_type": nf_type.value}))
                _link(entities, relationships, nf_id, pod_id, "has_pod")

        _link(entities, relationships, core_ids[EntityType.upf], core_ids[EntityType.smf], "served_by")
        _link(entities, relationships, core_ids[EntityType.smf], core_ids[EntityType.amf], "controlled_by")

        for s in range(1, config.sites_per_region + 1):
            site_id = f"syn-site-{r:02d}-{s:03d}"
            add(_entity(site_id, EntityType.site, f"Synthetic Site R{r}S{s}", region_name, market_id, {"sectors": config.cells_per_site}, _coords(rng, r)))
            _link(entities, relationships, market_id, site_id, "contains")
            gnb_id = f"syn-gnb-{r:02d}-{s:03d}"
            add(_entity(gnb_id, EntityType.gnodeb, f"gNodeB R{r}S{s}", region_name, site_id, {"cells": config.cells_per_site}))
            _link(entities, relationships, site_id, gnb_id, "hosts")

            for c in range(1, config.cells_per_site + 1):
                cell_id = f"syn-cell-{r:02d}-{s:03d}-{c:02d}"
                add(_entity(cell_id, EntityType.cell, f"Cell R{r}S{s}C{c}", region_name, gnb_id, {"bandwidth_mhz": 100, "max_users": 1200}, _coords(rng, r)))
                _link(entities, relationships, gnb_id, cell_id, "serves")
                link_id = f"syn-link-{r:02d}-{s:03d}-{c:02d}"
                add(_entity(link_id, EntityType.transport_link, f"Backhaul Link R{r}S{s}C{c}", region_name, cell_id, {"gbps": 10}))
                _link(entities, relationships, cell_id, link_id, "uses_backhaul")
                _link(entities, relationships, link_id, router_id, "connects_to")
                _link(entities, relationships, router_id, core_ids[EntityType.upf], "connects_to")

        for slice_idx, slice_name in enumerate(["embb", "urllc", "miot"], start=1):
            slice_id = f"syn-slice-{r:02d}-{slice_name}"
            add(_entity(slice_id, EntityType.service_slice, f"Synthetic {slice_name.upper()} Slice", region_name, core_ids[EntityType.upf], {"sla_target_pct": 99.5}, attributes={"slice_type": slice_name}))
            for nf_id in [core_ids[EntityType.upf], core_ids[EntityType.smf], core_ids[EntityType.pcf], core_ids[EntityType.nssf]]:
                _link(entities, relationships, slice_id, nf_id, "depends_on")
            segment_id = f"syn-segment-{r:02d}-{slice_idx:02d}"
            add(_entity(segment_id, EntityType.customer_segment, f"Synthetic Customer Segment {slice_idx}", region_name, slice_id, attributes={"segment": ["consumer", "enterprise", "iot"][slice_idx - 1]}))
            _link(entities, relationships, slice_id, segment_id, "serves")

    if config.scenario == "cell_outage":
        entities["syn-cell-01-001-01"].status = OperationalStatus.down
    elif config.scenario in {"ran_congestion", "upf_degradation", "fiber_cut", "signaling_storm", "slice_degradation"}:
        affected_id_by_scenario = {
            "ran_congestion": "syn-cell-01-001-01",
            "upf_degradation": "syn-upf-01-01",
            "fiber_cut": "syn-link-01-001-01",
            "signaling_storm": "syn-amf-01-01",
            "slice_degradation": "syn-slice-01-embb",
        }
        entities[affected_id_by_scenario[config.scenario]].status = OperationalStatus.degraded

    ordered = [entities[key] for key in sorted(entities)]
    for entity in ordered:
        entity.child_ids = sorted(entity.child_ids)
    return Topology(entities=ordered, relationships=sorted(relationships, key=lambda rel: (rel.source_id, rel.target_id, rel.relationship)))

