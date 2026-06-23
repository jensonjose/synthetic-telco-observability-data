# Validation Strategy

I added validation because synthetic data is only useful if it is internally consistent. Random-looking records are easy to generate; believable records that reference a known topology and show the expected scenario behavior are more useful.

The validator checks four things:

1. Schema correctness: Pydantic validates field types, enum values, timezone-aware timestamps, synthetic flags, and metric ranges.
2. Topology consistency: KPIs, alarms, incidents, and service-impact records must point to entities that exist in `topology.json`.
3. File and ordering checks: required files must exist and KPI timestamps must be ordered.
4. Scenario behavior: each non-normal scenario must show the signal it claims to show.

Examples:

- `fiber_cut` should produce elevated transport packet loss.
- `cell_outage` should produce low cell availability.
- `upf_degradation` should produce elevated UPF latency.
- `signaling_storm` should produce high control-plane CPU.
- `slice_degradation` should reduce SLA compliance or experience.

The CLI writes `validation_report.json` so a notebook, pipeline, or AI agent can read the validation result directly.
