# Autonomous Network Use Cases

This repo is not an autonomous network. I think of it as a safe dataset layer for autonomous-network experiments.

## NWDAF-Inspired Analytics

The generated KPIs, alarms, and service-impact records can be used to prototype NWDAF-style analytics ideas in a lab. I am using "NWDAF-inspired" carefully here; this is not a standards-compliant NWDAF implementation.

## AI-Assisted RCA

The data includes topology relationships, correlated alarms, scenario incidents, and service impact. That makes it useful for testing whether an AI workflow can move from symptoms to a plausible root cause.

## Closed-Loop Automation

The incident records include suggested remediation, rollback considerations, and validation checks. That gives a closed-loop lab something to reason over before any real-world integration exists.

## Intent-to-Action Simulation

Synthetic incidents can be mapped to candidate actions and guardrails. For example, an agent can propose a UPF scale-out, but it should also explain what it would validate before and after the action.

## Policy Guardrail Testing

Because the data is synthetic, it is a safer place to test whether an AI agent stays cautious, avoids unsupported claims, and asks for validation before recommending actions.

## AIOps Evaluation

The generated records can be used to benchmark anomaly detection, incident clustering, summarization, triage, and RCA prompts.
