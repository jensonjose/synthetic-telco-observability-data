from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, field_validator

ScenarioName = Literal[
    "normal",
    "ran_congestion",
    "fiber_cut",
    "upf_degradation",
    "signaling_storm",
    "cell_outage",
    "slice_degradation",
]

ExportFormat = Literal["jsonl", "csv"]


def default_formats() -> list[ExportFormat]:
    return ["jsonl"]


class GenerationConfig(BaseModel):
    scenario: ScenarioName = "normal"
    duration_hours: int = Field(default=1, ge=1, le=168)
    interval_minutes: int = Field(default=15, ge=1, le=1440)
    regions: int = Field(default=1, ge=1, le=20)
    sites_per_region: int = Field(default=2, ge=1, le=200)
    cells_per_site: int = Field(default=3, ge=1, le=12)
    seed: int = Field(default=42, ge=0)
    formats: list[ExportFormat] = Field(default_factory=default_formats)

    @field_validator("formats")
    @classmethod
    def normalize_formats(cls, value: list[str]) -> list[str]:
        cleaned = sorted({item.strip().lower() for item in value if item.strip()})
        if not cleaned:
            return ["jsonl"]
        invalid = set(cleaned) - {"jsonl", "csv"}
        if invalid:
            raise ValueError(f"Unsupported export formats: {', '.join(sorted(invalid))}")
        return cleaned

    @property
    def periods(self) -> int:
        return max(1, int(self.duration_hours * 60 / self.interval_minutes))


def load_config(path: Path) -> GenerationConfig:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return GenerationConfig.model_validate(data)
