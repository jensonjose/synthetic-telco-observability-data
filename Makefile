.PHONY: install test lint format typecheck generate-example validate-example summarize-example run-ui docker-build docker-up clean

PYTHON ?= python

install:
	$(PYTHON) -m pip install -e ".[dev]"

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

format:
	$(PYTHON) -m ruff format .

typecheck:
	$(PYTHON) -m mypy app

generate-example:
	$(PYTHON) -m app.cli generate --scenario ran_congestion --duration-hours 2 --interval-minutes 15 --regions 1 --sites-per-region 2 --cells-per-site 2 --seed 42 --output-dir ./examples/small_dataset --formats jsonl,csv

validate-example:
	$(PYTHON) -m app.cli validate --input-dir ./examples/small_dataset

summarize-example:
	$(PYTHON) -m app.cli summarize --input-dir ./examples/small_dataset

run-ui:
	$(PYTHON) -m uvicorn app.ui.main:app --host 0.0.0.0 --port 8000

docker-build:
	docker compose build

docker-up:
	docker compose up --build

clean:
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in ['output', '.pytest_cache', '.ruff_cache', '.mypy_cache']]; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]"

