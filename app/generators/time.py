from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.config import GenerationConfig


def timestamps(config: GenerationConfig) -> list[datetime]:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    return [start + timedelta(minutes=config.interval_minutes * idx) for idx in range(config.periods)]

