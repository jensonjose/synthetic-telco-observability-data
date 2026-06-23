from __future__ import annotations

from typer.testing import CliRunner

from app.cli import app


def test_cli_scenarios() -> None:
    result = CliRunner().invoke(app, ["scenarios"])
    assert result.exit_code == 0
    assert "ran_congestion" in result.output


def test_cli_generate_validate_summarize(tmp_path) -> None:  # type: ignore[no-untyped-def]
    runner = CliRunner()
    output_dir = tmp_path / "dataset"
    result = runner.invoke(
        app,
        [
            "generate",
            "--scenario",
            "fiber_cut",
            "--duration-hours",
            "1",
            "--interval-minutes",
            "15",
            "--output-dir",
            str(output_dir),
            "--formats",
            "jsonl,csv",
        ],
    )
    assert result.exit_code == 0, result.output
    assert runner.invoke(app, ["validate", "--input-dir", str(output_dir)]).exit_code == 0
    summary = runner.invoke(app, ["summarize", "--input-dir", str(output_dir)])
    assert summary.exit_code == 0
    assert "fiber_cut" in summary.output

