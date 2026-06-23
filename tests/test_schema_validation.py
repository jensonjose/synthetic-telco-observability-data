from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.schemas.common import Domain, EntityType, Scenario
from app.schemas.kpi import KPIRecord


def test_invalid_percentage_fails_schema() -> None:
    with pytest.raises(ValidationError):
        KPIRecord(
            timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            domain=Domain.ran,
            entity_id="syn-cell-x",
            entity_type=EntityType.cell,
            metric_name="availability_pct",
            metric_value=150,
            unit="%",
            scenario=Scenario.normal,
        )

