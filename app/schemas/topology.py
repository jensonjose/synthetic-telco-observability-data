from __future__ import annotations

from pydantic import Field, field_validator, model_validator

from app.schemas.common import EntityType, OperationalStatus, StrictBaseModel


class Entity(StrictBaseModel):
    id: str
    type: EntityType
    name: str
    region: str
    status: OperationalStatus = OperationalStatus.active
    parent_id: str | None = None
    child_ids: list[str] = Field(default_factory=list)
    capacity: dict[str, float | int | str] = Field(default_factory=dict)
    coordinates: dict[str, float] | None = None
    attributes: dict[str, float | int | str | bool] = Field(default_factory=dict)
    synthetic: bool = True

    @field_validator("id")
    @classmethod
    def synthetic_id(cls, value: str) -> str:
        if not value.startswith("syn-"):
            raise ValueError("entity id must start with syn-")
        return value

    @model_validator(mode="after")
    def require_synthetic(self) -> Entity:
        if not self.synthetic:
            raise ValueError("topology entities must be synthetic")
        return self


class Relationship(StrictBaseModel):
    source_id: str
    target_id: str
    relationship: str


class Topology(StrictBaseModel):
    entities: list[Entity]
    relationships: list[Relationship]
    synthetic: bool = True

    @model_validator(mode="after")
    def validate_relationships(self) -> Topology:
        ids = {entity.id for entity in self.entities}
        if len(ids) != len(self.entities):
            raise ValueError("entity ids must be unique")
        missing = [
            (rel.source_id, rel.target_id)
            for rel in self.relationships
            if rel.source_id not in ids or rel.target_id not in ids
        ]
        if missing:
            raise ValueError(f"relationships reference unknown entities: {missing[:3]}")
        if not self.synthetic:
            raise ValueError("topology must be synthetic")
        return self

    def by_type(self, entity_type: EntityType) -> list[Entity]:
        return [entity for entity in self.entities if entity.type == entity_type]

    def entity_ids(self) -> set[str]:
        return {entity.id for entity in self.entities}

