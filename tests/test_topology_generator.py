from __future__ import annotations

from app.generators.topology_generator import generate_topology
from app.schemas.common import EntityType
from app.validators.topology_validator import validate_topology
from tests.conftest import small_config


def test_topology_contains_required_entity_types() -> None:
    topology = generate_topology(small_config())
    assert not validate_topology(topology)
    present = {entity.type for entity in topology.entities}
    assert EntityType.cell in present
    assert EntityType.upf in present
    assert EntityType.service_slice in present


def test_topology_ids_are_unique_and_deterministic() -> None:
    first = generate_topology(small_config(seed=7))
    second = generate_topology(small_config(seed=7))
    assert len(first.entity_ids()) == len(first.entities)
    assert first.model_dump(mode="json") == second.model_dump(mode="json")
