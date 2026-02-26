# Scenario Planning MVP

A data-engineering-focused scenario planning pipeline that runs locally with **Airflow**, **MinIO (S3-compatible object store)**, and **Postgres**.

This project demonstrates practical orchestration patterns for scenario-based planning workflows:
- deterministic synthetic data generation
- reproducible scenario simulation via business knobs
- capacity-aware cost modeling (toy solver)
- partitioned, run-traceable lake outputs in object storage

---

## Why this project

Decision-support systems often need fast "what-if" analysis: _What happens if demand rises? What if logistics costs increase?_  
This MVP operationalizes that workflow in Airflow so each run is reproducible, inspectable, and easy to compare.

---

## Current Scope (Implemented)

### Airflow DAGs

1. **`hello_scenario_planning`**
   - Single-task sanity DAG (`hello_task`) to validate scheduler/webserver setup.

2. **`minio_smoketest`**
   - Single-task DAG (`write_hello_to_minio`) that verifies MinIO write access by creating:
   - `smoketest/dt=YYYY-MM-DD/hello.txt`

3. **`scenario_planning_mvp`** (main pipeline)
   - Single-task DAG (`generate_and_publish_scenarios`) that executes end-to-end scenario generation and publishing.

### Main Pipeline Behavior (`scenario_planning_mvp`)

1. Creates run context (`run_id`, `dt`, `created_at_utc`)  
2. Generates deterministic baseline input data (`seed=7`)  
3. Defines 3 scenarios:
   - `baseline`
   - `demand_up_10`
   - `costs_up_10`
4. For each scenario:
   - applies scenario knobs
   - runs a toy capacity-aware solver
   - publishes inputs and outputs to MinIO
5. Publishes run-level metadata

### Scenario Knobs

- `demand_scale`
- `variable_cost_scale`
- `logistics_cost_scale`

### Outputs Currently Produced

Per scenario:
- `inputs/scenario_spec.json`
- `inputs/baseline_summary.json`
- `outputs/fact_production.json`
- `outputs/kpi_total.json`
- `outputs/kpi_cost_breakdown.json`

Per run:
- `run_metadata.json`

---

## Architecture Snapshot

### Runtime Stack

- **Airflow UI:** <http://localhost:8080> (`admin` / `admin`)
- **MinIO API:** <http://localhost:9000>
- **MinIO Console:** <http://localhost:9001> (`minio` / `minio12345`)
- **Postgres:** `localhost:5432` (`airflow` / `airflow` / `airflow`)

### Repository Structure

```text
.
├─ dags/
│  ├─ hello_scenario_planning.py
│  ├─ minio_smoketest.py
│  └─ scenario_planning_mvp.py
├─ src/scenarioops/
│  ├─ baseline.py
│  ├─ models.py
│  ├─ scenarios.py
│  ├─ toy_solver.py
│  └─ storage.py
├─ tests/
├─ docker-compose.yml
└─ requirements-airflow.txt
```

### Data Layout in MinIO (Bucket: `scenarioops`)

```text
runs/dt=YYYY-MM-DD/run_id=<uuid>/
  run_metadata.json
  scenario_id=<scenario>/
    inputs/
      scenario_spec.json
      baseline_summary.json
    outputs/
      fact_production.json
      kpi_total.json
      kpi_cost_breakdown.json
```

---

## Quickstart

### 1) Start services

```bash
docker compose up -d
```

### 2) Verify containers

```bash
docker compose ps
```

### 3) Trigger DAGs (Airflow UI)

Open <http://localhost:8080> and trigger:
- `hello_scenario_planning` (optional sanity)
- `minio_smoketest` (optional storage sanity)
- `scenario_planning_mvp` (main pipeline)

### 4) Validate outputs (MinIO Console)

Open <http://localhost:9001>, bucket `scenarioops`, and verify:
- `smoketest/dt=.../hello.txt` (if smoketest was run)
- `runs/dt=.../run_id=.../scenario_id=.../inputs/...`
- `runs/dt=.../run_id=.../scenario_id=.../outputs/...`
- `runs/dt=.../run_id=.../run_metadata.json`

---

## Design Notes

- The MVP intentionally keeps orchestration simple: the main pipeline currently runs inside one Airflow task.
- Reproducibility comes from deterministic baseline generation + run/scenario partitioned storage.
- Current lineage is primarily path-based (`dt`, `run_id`, `scenario_id`) and metadata-based (`run_metadata.json`).

### Current Limitations

- `scenario_planning_mvp` is monolithic at task level (limited task-level observability).
- Retries apply to the whole callable, not each internal stage.
- Extended facts/diagnostics beyond current outputs are not yet implemented.

---


## Backward-Compatibility Migration Note

DAG IDs were renamed from the old scenarioops_* naming to scenario_planning_*:

- scenarioops_mvp -> scenario_planning_mvp
- hello_scenarioops -> hello_scenario_planning

What this means operationally:
- Historical Airflow runs remain visible under old DAG IDs.
- New triggers should use the new DAG IDs.
- Any external automations (CLI scripts, API calls, bookmarks, docs) must be updated to new names.
- Task IDs inside DAGs are unchanged.
## Planned v2 Orchestration

> **Status:** planned (not yet implemented in this repository state)

### Target DAG pattern

```text
extract_baseline
  -> generate_scenarios
  -> solve_scenario (dynamic mapping per scenario)
  -> publish_scenario
  -> quality_check_scenario
  -> aggregate_run_metadata
```

### v2 goals

- Split monolithic callable into explicit Airflow tasks
- Use dynamic task mapping for per-scenario execution
- Improve retry granularity and failure isolation
- Make lineage explicit with task/scenario manifests
- Add quality gates (schema checks + KPI reconciliation)
- Improve graph-level observability and operational debugging

### Suggested quality checks

- Required output artifacts exist per scenario
- JSON schema/type validation for key outputs
- KPI reconciliation (`kpi_total` vs breakdown components)
- Non-negative and completeness checks on critical metrics

---

## Tech Stack

- Python
- Apache Airflow 2.9.x
- MinIO
- Postgres
- Docker Compose

---

## License / Usage

Internal Scenario Planning MVP scaffold for experimentation and iteration.


