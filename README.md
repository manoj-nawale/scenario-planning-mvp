# Airflow Scenario Data Pipeline (ScenarioOps MVP)

A **data-engineering-first** project that operationalizes **scenario planning** for a planning/optimization DSS.
Runs locally using **Airflow + MinIO (S3-compatible) + Postgres** via Docker Compose.

This repo focuses on production-grade DE patterns:
- idempotent pipelines + partitioned outputs
- data contracts + quality gates
- lineage/run metadata for reproducibility
- scenario generation (3 knobs) and KPI comparison

## What it does (MVP scope)
1. Generates a **baseline input snapshot** (synthetic, shaped like a stage-2 planning dataset).
2. Creates scenario snapshots using 3 knobs:
   - Demand scaling
   - Variable cost scaling
   - Logistics cost scaling (inbound/outbound/inter-company)
3. Runs a toy “solver” step (no Gurobi required) to produce:
   - decision-style fact tables
   - cost breakdown KPIs + totals
   - capacity utilization diagnostics
4. Publishes outputs to MinIO in a lake layout:
   - `raw/clean/curated`
   - partitioned by `dt/run_id/scenario_id`

## Local stack
- Airflow UI: http://localhost:8080 (admin / admin)
- MinIO Console: http://localhost:9001 (minio / minio12345)

## Run it
```bash
docker compose up -d

## Trigger DAGs in Airflow:
- hello_scenarioops (sanity check)
- scenarioops_mvp (main pipeline)

## Expected outputs
- fact_production, fact_transport, fact_releases
- fact_overutilization, fact_additional_shift
- kpi_cost_breakdown, kpi_total
- diag_capacity_comparison 

## Output layout (MinIO bucket: scenarioops)
```bash
runs/dt=YYYY-MM-DD/run_id=<uuid>/scenario_id=<scenario>/
  inputs/...
  outputs/...
  metadata/...

