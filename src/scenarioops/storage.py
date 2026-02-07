from __future__ import annotations

import json
import os
from dataclasses import asdict
from datetime import datetime
from io import BytesIO
from typing import Any

from minio import Minio


def get_minio_client() -> Minio:
    endpoint = os.environ.get("MINIO_ENDPOINT", "http://minio:9000")
    access_key = os.environ.get("MINIO_ACCESS_KEY", "minio")
    secret_key = os.environ.get("MINIO_SECRET_KEY", "minio12345")

    return Minio(
        endpoint.replace("http://", "").replace("https://", ""),
        access_key=access_key,
        secret_key=secret_key,
        secure=endpoint.startswith("https://"),
    )


def ensure_bucket(client: Minio, bucket: str) -> None:
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)


def put_bytes(client: Minio, bucket: str, object_name: str, data: bytes, content_type: str) -> None:
    ensure_bucket(client, bucket)
    client.put_object(
        bucket_name=bucket,
        object_name=object_name,
        data=BytesIO(data),
        length=len(data),
        content_type=content_type,
    )


def put_json(client: Minio, bucket: str, object_name: str, payload: Any) -> None:
    if hasattr(payload, "__dataclass_fields__"):
        payload = asdict(payload)
    data = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
    put_bytes(client, bucket, object_name, data, "application/json")


def lake_path(run_dt: str, run_id: str, scenario_id: str, layer: str, name: str) -> str:
    """
    Standard object layout (S3/MinIO):
    runs/dt=YYYY-MM-DD/run_id=<uuid>/scenario_id=<scenario>/<layer>/<name>
    """
    return f"runs/dt={run_dt}/run_id={run_id}/scenario_id={scenario_id}/{layer}/{name}"


def utc_now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"
