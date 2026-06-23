# Scenario Design

Each scenario starts from the same basic topology and then pushes a small set of metrics in a direction that matches the story. I kept the behavior simple enough to inspect, but structured enough that validators can prove the expected signal exists.

## Normal

The normal scenario generates healthy KPI ranges with small random noise. It may include low-severity operational noise, but it should not create major or critical incidents.

## RAN Congestion

This scenario makes one synthetic cell busy. PRB utilization and active users go up, throughput drops, SINR can degrade, handover success drops, and call drops increase.

The point is to create the kind of pattern an RCA or anomaly-detection workflow should connect back to radio congestion.

## Fiber Cut

This scenario makes a synthetic transport link look badly impaired. Availability drops, packet loss rises sharply, latency and jitter rise, and downstream RAN symptoms appear through correlated alarms.

It is useful for testing whether a workflow can avoid blaming the first visible cell symptom and instead identify transport as the likely source.

## UPF Degradation

This scenario focuses on user-plane quality. UPF latency and packet loss increase, user-plane CPU rises, and service experience drops while sessions can still remain active.

The remediation language includes scale-out, reroute, and health-check options, but with validation and rollback checks.

## Signaling Storm

This scenario stresses the control plane. AMF/SMF CPU rises, registration and session success rates fall, and session-release behavior increases.

It is meant for testing control-plane RCA, rate-limiting suggestions, and investigation workflows.

## Cell Outage

This scenario drives one cell close to unavailable. Connected users drop, availability falls near zero, and a critical cell alarm is generated.

The service impact is linked back to the affected synthetic cell/site area.

## Slice SLA Degradation

This scenario lowers SLA compliance and service experience for a synthetic eMBB slice.

It is useful for testing workflows where the symptom is service-level degradation rather than a single obvious infrastructure failure.
