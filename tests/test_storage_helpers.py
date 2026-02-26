import os
import sys
import types
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

# storage.py imports Minio at module import time; provide a lightweight stub for unit tests
if "minio" not in sys.modules:
    minio_stub = types.ModuleType("minio")

    class _MinioStub:  # pragma: no cover
        pass

    minio_stub.Minio = _MinioStub
    sys.modules["minio"] = minio_stub

from scenarioops.storage import lake_path


class TestStorageHelpers(unittest.TestCase):
    def test_lake_path_format(self):
        p = lake_path("2026-02-26", "abc-123", "baseline", "outputs", "kpi_total.json")
        self.assertEqual(
            p,
            "runs/dt=2026-02-26/run_id=abc-123/scenario_id=baseline/outputs/kpi_total.json",
        )


if __name__ == "__main__":
    unittest.main()
