from __future__ import annotations

import os
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from io import BytesIO

def write_to_minio():
    # MinIO connection details (local)
    # In docker-compose, MinIO is reachable from containers by service name "minio"
    endpoint = os.environ.get("MINIO_ENDPOINT", "http://minio:9000")
    access_key = os.environ.get("MINIO_ACCESS_KEY", "minio")
    secret_key = os.environ.get("MINIO_SECRET_KEY", "minio12345")
    bucket = os.environ.get("MINIO_BUCKET", "scenarioops")

    # Lazy import so the DAG still loads even if deps aren't installed yet
    from minio import Minio

    client = Minio(
        endpoint.replace("http://", "").replace("https://", ""),
        access_key=access_key,
        secret_key=secret_key,
        secure=endpoint.startswith("https://"),
    )

    # Ensure bucket exists (idempotent)
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)

    content = f"MinIO smoketest OK at {datetime.utcnow().isoformat()}Z\n".encode("utf-8")
    data = BytesIO(content)

    object_name = f"smoketest/dt={datetime.utcnow().date().isoformat()}/hello.txt"
    client.put_object(
        bucket_name=bucket,
        object_name=object_name,
        data=data,
        length=len(content),
        content_type="text/plain",
    )


with DAG(
    dag_id="minio_smoketest",
    start_date=datetime(2026, 2, 7),
    schedule=None,
    catchup=False,
    tags=["scenario_planning", "mvp", "minio"],
) as dag:
    PythonOperator(task_id="write_hello_to_minio", python_callable=write_to_minio)

