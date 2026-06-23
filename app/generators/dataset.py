from __future__ import annotations

from app.config import GenerationConfig
from app.generators.cloud_generator import generate_cloud_kpis
from app.generators.core_generator import generate_core_kpis
from app.generators.incident_generator import generate_alarms, generate_incidents
from app.generators.oss_generator import generate_oss_kpis
from app.generators.ran_generator import generate_ran_kpis
from app.generators.service_impact_generator import generate_service_impact
from app.generators.time import timestamps
from app.generators.topology_generator import generate_topology
from app.generators.transport_generator import generate_transport_kpis
from app.schemas.common import EntityType
from app.schemas.export import GeneratedDataset
from app.validators.schema_validator import validate_dataset


def generate_dataset(config: GenerationConfig) -> GeneratedDataset:
    topology = generate_topology(config)
    times = timestamps(config)
    cells = topology.by_type(EntityType.cell)
    core_entities = [
        *topology.by_type(EntityType.amf),
        *topology.by_type(EntityType.smf),
        *topology.by_type(EntityType.upf),
        *topology.by_type(EntityType.pcf),
        *topology.by_type(EntityType.nssf),
    ]
    links = topology.by_type(EntityType.transport_link)
    routers = topology.by_type(EntityType.router)
    pods = topology.by_type(EntityType.nf_pod)
    clusters = topology.by_type(EntityType.kubernetes_cluster)
    slices = topology.by_type(EntityType.service_slice)
    segments = topology.by_type(EntityType.customer_segment)

    dataset = GeneratedDataset(
        topology=topology,
        ran_kpis=generate_ran_kpis(config, cells, times),
        core_kpis=generate_core_kpis(config, core_entities, times),
        transport_kpis=generate_transport_kpis(config, links, routers, times),
        cloud_kpis=generate_cloud_kpis(config, pods, clusters, times),
        oss_kpis=generate_oss_kpis(config, slices, times),
        alarms=generate_alarms(config, topology, times[0]),
        incidents=generate_incidents(config, times[0]),
        service_impact=generate_service_impact(config, slices, segments, times),
    )
    dataset.validation_report = validate_dataset(dataset, scenario=config.scenario)
    return dataset

