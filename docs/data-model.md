# Data Model

The data model is shaped around the things I usually want when testing network-assurance workflows: topology, time-series KPIs, alarms, incidents, and service impact.

## Topology

The topology includes synthetic regions, markets, sites, gNodeBs, cells, AMF, SMF, UPF, PCF, NSSF, transport links, routers, Kubernetes clusters, NF pods, service slices, and customer segments.

Each entity has:

- A synthetic `syn-` ID.
- An entity type.
- A synthetic name.
- A region.
- Operational status.
- Parent-child metadata.
- Optional capacity fields.
- Optional fabricated coordinates.
- `synthetic: true`.

The topology is not meant to represent a real operator. It is there so KPIs, alarms, incidents, and service impact can point to known entities instead of floating around as disconnected records.

## KPI Records

KPI records are time-series observations. Each one has a timestamp, domain, entity ID, entity type, metric name, metric value, unit, scenario, severity hint, and synthetic flag.

The domains are:

- `ran`
- `core`
- `transport`
- `cloud`
- `oss`

The values are generated to be plausible for the scenario, not to reproduce exact vendor behavior.

## Alarm Records

Alarms include severity, probable cause, specific problem, description, correlation ID, scenario, affected entity, and synthetic flag.

The correlation ID is useful for RCA experiments because several alarms can point back to the same synthetic incident.

## Incident Records

Incidents capture the story behind a scenario: start/end time, affected domain, affected entities, root cause, symptoms, customer impact, suggested remediation, rollback considerations, validation checks, and correlation ID.

The remediation text is intentionally cautious. It is meant for lab workflows, not for driving a real network.

## Service Impact Records

Service impact records connect the technical symptoms to service-level language: service name, slice, region, customer segment, impacted-user estimate, experience score, SLA status, primary symptom, and related incident.

These records are useful when testing AI workflows that need to explain impact in a way that is closer to service assurance than raw metrics.
