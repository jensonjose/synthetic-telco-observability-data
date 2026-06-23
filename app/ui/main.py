from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import GenerationConfig
from app.exporters import export_csv, export_jsonl
from app.generators import generate_dataset
from app.scenarios import SCENARIOS
from app.validators import load_and_validate_directory

OUTPUT_DIR = Path("output/ui_dataset")
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Synthetic Telco Observability Data")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def _preview_file(path: Path, limit: int = 20) -> list[dict[str, object]]:
    if not path.exists():
        return []
    if path.suffix == ".jsonl":
        rows: list[dict[str, object]] = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if len(rows) >= limit:
                    break
                rows.append(json.loads(line))
        return rows
    if path.name == "topology.json":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cast(list[dict[str, object]], data.get("entities", [])[:limit])
    if path.name == "validation_report.json":
        return [cast(dict[str, object], json.loads(path.read_text(encoding="utf-8")))]
    return []


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "index.html",
        {"scenarios": SCENARIOS.values(), "output_dir": OUTPUT_DIR},
    )


@app.post("/generate")
def generate_from_form(
    scenario: str = Form("normal"),
    duration_hours: int = Form(1),
    interval_minutes: int = Form(15),
    regions: int = Form(1),
    sites_per_region: int = Form(2),
    cells_per_site: int = Form(3),
    seed: int = Form(42),
) -> RedirectResponse:
    config = GenerationConfig(
        scenario=scenario,  # type: ignore[arg-type]
        duration_hours=duration_hours,
        interval_minutes=interval_minutes,
        regions=regions,
        sites_per_region=sites_per_region,
        cells_per_site=cells_per_site,
        seed=seed,
        formats=["jsonl", "csv"],
    )
    dataset = generate_dataset(config)
    export_jsonl(dataset, OUTPUT_DIR)
    export_csv(dataset, OUTPUT_DIR)
    return RedirectResponse("/dataset", status_code=303)


@app.get("/dataset", response_class=HTMLResponse)
def dataset(request: Request) -> HTMLResponse:
    report = load_and_validate_directory(OUTPUT_DIR) if OUTPUT_DIR.exists() else None
    files = sorted(path.name for path in OUTPUT_DIR.glob("*")) if OUTPUT_DIR.exists() else []
    previews = {name: _preview_file(OUTPUT_DIR / name, 5) for name in files if name.endswith((".jsonl", ".json"))}
    return templates.TemplateResponse(
        request,
        "dataset.html",
        {"report": report, "files": files, "previews": previews},
    )


@app.get("/topology", response_class=HTMLResponse)
def topology(request: Request) -> HTMLResponse:
    rows = _preview_file(OUTPUT_DIR / "topology.json", 200)
    counts: dict[str, int] = {}
    for row in rows:
        entity_type = str(row.get("type", "unknown"))
        counts[entity_type] = counts.get(entity_type, 0) + 1
    return templates.TemplateResponse(request, "topology.html", {"counts": counts, "entities": rows[:50]})


@app.get("/download/{file_name}")
def download(file_name: str) -> FileResponse:
    path = OUTPUT_DIR / file_name
    return FileResponse(path, filename=file_name)
