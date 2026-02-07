from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator


def hello():
    print("ScenarioOps MVP: Airflow is running")


with DAG(
    dag_id="hello_scenarioops",
    start_date=datetime(2026, 2, 7),
    schedule=None,
    catchup=False,
    tags=["scenarioops", "mvp"],
) as dag:
    PythonOperator(task_id="hello_task", python_callable=hello)
