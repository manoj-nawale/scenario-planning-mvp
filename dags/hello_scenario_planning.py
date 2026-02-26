from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator


def hello():
    print("Scenario Planning MVP: Airflow is running")


with DAG(
    dag_id="hello_scenario_planning",
    start_date=datetime(2026, 2, 7),
    schedule=None,
    catchup=False,
    tags=["scenario_planning", "mvp"],
) as dag:
    PythonOperator(task_id="hello_task", python_callable=hello)


