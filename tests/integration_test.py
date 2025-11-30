# tests/integration_test.py
import os
from src.run import run_pipeline

def test_pipeline_runs_and_outputs():
    res = run_pipeline("integration test run")
    assert "report_path" in res
    assert os.path.exists(res["report_path"])
    assert os.path.exists(res["insights_path"])
    assert os.path.exists(res["creatives_path"])
    assert os.path.exists(os.path.join(res["log_dir"], "metrics.json"))
