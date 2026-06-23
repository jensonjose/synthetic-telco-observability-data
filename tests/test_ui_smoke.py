from __future__ import annotations

from fastapi.testclient import TestClient

from app.ui.main import app


def test_ui_home_loads() -> None:
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert "Synthetic Telco Observability Data" in response.text


def test_ui_can_generate_dataset() -> None:
    response = TestClient(app).post(
        "/generate",
        data={
            "scenario": "upf_degradation",
            "duration_hours": 1,
            "interval_minutes": 15,
            "regions": 1,
            "sites_per_region": 1,
            "cells_per_site": 1,
            "seed": 42,
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Validation:" in response.text
    assert "upf_degradation" in response.text
