# Synthetic Telco Observability Data

I built this repo to generate realistic-looking synthetic telecom observability data for AI-assisted network assurance experiments.

The generator creates synthetic topology, KPIs, alarms, incidents, and service-impact records across RAN, 5G Core, Transport, Cloud/Kubernetes, OSS, and service assurance. The goal is to have data that feels close enough to real telco operations to test ideas like RCA, anomaly detection, NWDAF-inspired analytics, and closed-loop automation, without touching real operator or customer data.

This is intentionally a data foundation, not a production telecom platform.

## What This Is

- A Docker-first Python tool for generating synthetic telco observability datasets.
- A small CLI and local UI for creating and previewing data.
- A safe way to prototype AI network automation workflows without real network data.
- A standards-inspired lab project, not a certified implementation of any telecom standard.

## What This Is Not

- Not a real NWDAF.
- Not a real OSS, BSS, EMS, NMS, or network simulator.
- Not based on any operator, subscriber, customer, or proprietary dataset.
- Not something that should be used for production network operations.

## Safety Note

Everything generated here is synthetic and marked with `synthetic: true`.

The project does not scrape telecom datasets and does not include real IMSI, MSISDN, subscriber IDs, customer data, IP addresses, site data, or operator topology. Names, IDs, coordinates, incidents, and KPI values are fabricated for local lab use.

## Why I Built This

Real telecom observability data is hard to use in public demos, blogs, experiments, or hiring conversations. It is sensitive, fragmented, noisy, and often locked inside operational systems. At the same time, AI-assisted assurance and autonomous-network ideas need realistic data shapes to be tested properly.

This repo gives me a safe dataset generator I can use to explore those ideas without pretending the data came from a real network.

## Quickstart With Docker

```bash
docker compose build
docker compose run --rm app python -m app.cli scenarios
docker compose run --rm app python -m app.cli generate --scenario ran_congestion --duration-hours 2 --interval-minutes 5 --seed 42 --output-dir ./output --formats jsonl,csv
docker compose run --rm app python -m app.cli validate --input-dir ./output
docker compose run --rm app python -m app.cli summarize --input-dir ./output
docker compose up
```

When the UI is running, open `http://localhost:8000`.

## Quickstart Without Docker

```bash
python -m pip install -e ".[dev]"
make generate-example
make validate-example
make summarize-example
```

## CLI Examples

List the supported scenarios:

```bash
python -m app.cli scenarios
```

Generate a dataset:

```bash
python -m app.cli generate \
  --scenario upf_degradation \
  --duration-hours 6 \
  --interval-minutes 5 \
  --regions 2 \
  --sites-per-region 5 \
  --cells-per-site 3 \
  --seed 42 \
  --output-dir ./output \
  --formats jsonl,csv
```

Validate and summarize it:

```bash
python -m app.cli validate --input-dir ./output
python -m app.cli summarize --input-dir ./output
```

## What Gets Generated

- `topology.json`: synthetic regions, markets, sites, cells, core NFs, transport links, routers, Kubernetes clusters, NF pods, slices, and customer segments.
- `ran_kpis.jsonl`, `core_kpis.jsonl`, `transport_kpis.jsonl`, `cloud_kpis.jsonl`, `oss_kpis.jsonl`: time-series KPI records.
- `alarms.jsonl`: synthetic alarms with correlation IDs.
- `incidents.jsonl`: scenario incidents for non-normal scenarios.
- `service_impact.jsonl`: service-impact records linked to incidents.
- `validation_report.json`: validation status, counts, warnings, and errors.
- CSV versions when `--formats jsonl,csv` is used.

## Scenarios

- `normal`: healthy baseline with small random noise.
- `ran_congestion`: high PRB utilization, more active users, lower throughput, and worse experience.
- `fiber_cut`: high transport packet loss, low availability, and correlated downstream alarms.
- `upf_degradation`: user-plane latency and packet-loss degradation around a UPF.
- `signaling_storm`: AMF/SMF CPU pressure with lower registration and session success rates.
- `cell_outage`: near-zero availability on an affected cell.
- `slice_degradation`: SLA and experience degradation for a synthetic service slice.

## Validation

I wanted the generated data to be more than random CSV rows, so the tool validates it at multiple levels:

- Pydantic schemas for record shape and enum values.
- Topology reference checks for KPIs, alarms, incidents, and service impact.
- Timestamp ordering checks.
- Synthetic flag checks.
- Plausible metric ranges.
- Scenario checks, such as elevated packet loss for `fiber_cut` or low availability for `cell_outage`.

## Useful For

- Anomaly detection experiments.
- AI-assisted root-cause analysis.
- NWDAF-inspired analytics prototypes.
- Closed-loop automation lab workflows.
- AI agent evaluation with safe synthetic incidents.
- Policy guardrail testing before connecting anything to real systems.

## Quality Commands

```bash
make test
make lint
make typecheck
make generate-example
make validate-example
make summarize-example
```

## Current Limitations

This generator models plausible observability patterns. It does not model full protocol behavior, real RF propagation, real transport routing, or actual operator topology. Scenario propagation is intentionally simple and deterministic so the output is easy to inspect and test.

## Roadmap Ideas

- Optional Parquet export.
- More topology-aware scenario propagation.
- Notebook examples for NWDAF-style analytics.
- Closed-loop policy guardrail examples.
- More domain-specific validators.
