from __future__ import annotations

import os
import uuid
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

# Import from src/ (we add src to PYTHONPATH via docker-compose env if needed)
from scenarioops.baseline import generate_baseline, summarize_baseline
from scenarioops.models import RunSpec, ScenarioKnobs, ScenarioSpec
from scenarioops.scenarios import apply_knobs
from scenarioops.storage import get_minio_client, lake_path, put_json, utc_now_iso
from scenarioops.toy_solver import run_toy_solver


def run_pipeline():
    bucket = os.environ.get("MINIO_BUCKET", "scenarioops")

    run_id = str(uuid.uuid4())
    run = RunSpec.now(run_id=run_id)

    client = get_minio_client()

    baseline = generate_baseline(seed=7)

    scenarios = [
        ScenarioSpec(
            scenario_id="baseline",
            created_at_utc=utc_now_iso(),
            knobs=ScenarioKnobs(1.0, 1.0, 1.0),
            notes="No changes",
        ),
        ScenarioSpec(
            scenario_id="demand_up_10",
            created_at_utc=utc_now_iso(),
            knobs=ScenarioKnobs(demand_scale=1.10, variable_cost_scale=1.0, logistics_cost_scale=1.0),
            notes="Demand +10%",
        ),
        ScenarioSpec(
            scenario_id="costs_up_10",
            created_at_utc=utc_now_iso(),
            knobs=ScenarioKnobs(demand_scale=1.0, variable_cost_scale=1.10, logistics_cost_scale=1.10),
            notes="Variable +10%, Logistics +10%",
        ),
    ]

    for spec in scenarios:
        scenario_data = apply_knobs(baseline, spec.knobs)
        out = run_toy_solver(scenario_data)

        # ---- publish inputs ----
        put_json(
            client,
            bucket,
            lake_path(run.dt, run.run_id, spec.scenario_id, "inputs", "scenario_spec.json"),
            spec,
        )
        put_json(
            client,
            bucket,
            lake_path(run.dt, run.run_id, spec.scenario_id, "inputs", "baseline_summary.json"),
            summarize_baseline(scenario_data),
        )

        # ---- publish outputs ----
        put_json(
            client,
            bucket,
            lake_path(run.dt, run.run_id, spec.scenario_id, "outputs", "fact_production.json"),
            out.fact_production,
        )
        put_json(
            client,
            bucket,
            lake_path(run.dt, run.run_id, spec.scenario_id, "outputs", "kpi_total.json"),
            out.kpi_total,
        )
        put_json(
            client,
            bucket,
            lake_path(run.dt, run.run_id, spec.scenario_id, "outputs", "kpi_cost_breakdown.json"),
            out.kpi_cost_breakdown,
        )

    # run-level metadata (one per run)
    put_json(
        client,
        bucket,
        f"runs/dt={run.dt}/run_id={run.run_id}/run_metadata.json",
        {"run_id": run.run_id, "dt": run.dt, "created_at_utc": run.created_at_utc, "scenarios": [s.scenario_id for s in scenarios]},
    )


with DAG(
    dag_id="scenario_planning_mvp",
    start_date=datetime(2026, 2, 7),
    schedule=None,
    catchup=False,
    tags=["scenario_planning", "mvp"],
) as dag:
    PythonOperator(task_id="generate_and_publish_scenarios", python_callable=run_pipeline)

