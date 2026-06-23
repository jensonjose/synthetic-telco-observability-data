from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from app.config import GenerationConfig
from app.exporters import export_csv, export_jsonl
from app.generators import generate_dataset
from app.scenarios import SCENARIOS
from app.validators import load_and_validate_directory

app = typer.Typer(help="Generate and validate synthetic telecom observability datasets.")
console = Console()


def _parse_formats(value: str) -> list[str]:
    return [item.strip().lower() for item in value.split(",") if item.strip()]


@app.command()
def generate(
    scenario: Annotated[str, typer.Option(help="Scenario profile name.")] = "normal",
    duration_hours: Annotated[int, typer.Option(help="Synthetic time-series duration in hours.")] = 1,
    interval_minutes: Annotated[int, typer.Option(help="KPI interval in minutes.")] = 15,
    regions: Annotated[int, typer.Option(help="Number of synthetic regions.")] = 1,
    sites_per_region: Annotated[int, typer.Option(help="Sites per synthetic region.")] = 2,
    cells_per_site: Annotated[int, typer.Option(help="Cells per site.")] = 3,
    seed: Annotated[int, typer.Option(help="Deterministic random seed.")] = 42,
    output_dir: Annotated[Path, typer.Option(help="Output directory.")] = Path("./output"),
    formats: Annotated[str, typer.Option(help="Comma-separated export formats: jsonl,csv.")] = "jsonl",
) -> None:
    """Generate a complete synthetic observability dataset."""
    config = GenerationConfig(
        scenario=scenario,  # type: ignore[arg-type]
        duration_hours=duration_hours,
        interval_minutes=interval_minutes,
        regions=regions,
        sites_per_region=sites_per_region,
        cells_per_site=cells_per_site,
        seed=seed,
        formats=_parse_formats(formats),  # type: ignore[arg-type]
    )
    dataset = generate_dataset(config)
    if "jsonl" in config.formats:
        export_jsonl(dataset, output_dir)
    if "csv" in config.formats:
        export_csv(dataset, output_dir)
    report = dataset.validation_report
    status = "valid" if report and report.valid else "invalid"
    console.print(f"[bold green]Generated[/bold green] {config.scenario} dataset in {output_dir} ({status}).")
    if report and report.errors:
        for error in report.errors:
            console.print(f"[red]- {error}[/red]")
        raise typer.Exit(code=1)


@app.command()
def validate(input_dir: Annotated[Path, typer.Option(help="Generated dataset directory.")] = Path("./output")) -> None:
    """Validate a generated dataset directory."""
    report = load_and_validate_directory(input_dir)
    if report.valid:
        console.print(f"[bold green]Validation passed[/bold green] for {input_dir}")
    else:
        console.print(f"[bold red]Validation failed[/bold red] for {input_dir}")
        for error in report.errors:
            console.print(f"[red]- {error}[/red]")
        raise typer.Exit(code=1)


@app.command()
def summarize(input_dir: Annotated[Path, typer.Option(help="Generated dataset directory.")] = Path("./output")) -> None:
    """Print record counts and validation status for a generated dataset."""
    report = load_and_validate_directory(input_dir)
    table = Table(title=f"Synthetic Telco Dataset Summary: {input_dir}")
    table.add_column("Item")
    table.add_column("Value", justify="right")
    table.add_row("scenario", report.scenario or "unknown")
    table.add_row("validation", "passed" if report.valid else "failed")
    for key, value in sorted(report.counts.items()):
        table.add_row(key, str(value))
    console.print(table)
    if report.errors:
        console.print("[bold red]Errors[/bold red]")
        for error in report.errors:
            console.print(f"- {error}")


@app.command(name="scenarios")
def list_scenarios() -> None:
    """List available synthetic scenario profiles."""
    table = Table(title="Available Synthetic Telco Scenarios")
    table.add_column("Scenario")
    table.add_column("Description")
    for profile in SCENARIOS.values():
        table.add_row(profile.name, profile.description)
    console.print(table)


if __name__ == "__main__":
    app()

