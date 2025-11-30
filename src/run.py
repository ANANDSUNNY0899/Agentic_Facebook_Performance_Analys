
# # src/run.py
# import argparse
# import json
# import os
# import datetime
# import logging
# import yaml

# from src.utils.metrics import Metrics
# from src.agents.data_agent import DataAgent
# from src.agents.insight_agent import InsightAgent
# from src.agents.evaluator import EvaluatorAgent
# from src.agents.creative_agent import CreativeAgent


# # -------------------------
# # Helpers
# # -------------------------
# def ensure_dirs(path: str):
#     if not os.path.exists(path):
#         os.makedirs(path)

# def init_logging(run_id: str):
#     log_dir = f"logs/{run_id}"
#     ensure_dirs(log_dir)
#     log_file = os.path.join(log_dir, "system.log")
#     root = logging.getLogger()
#     root.setLevel(logging.INFO)
#     # clear handlers if rerunning in same interpreter
#     if root.handlers:
#         root.handlers = []
#     fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
#     fh = logging.FileHandler(log_file, encoding="utf-8")
#     fh.setLevel(logging.INFO)
#     fh.setFormatter(fmt)
#     root.addHandler(fh)
#     ch = logging.StreamHandler()
#     ch.setLevel(logging.INFO)
#     ch.setFormatter(fmt)
#     root.addHandler(ch)
#     logging.getLogger("urllib3").setLevel(logging.WARNING)
#     return log_dir

# def load_config():
#     cfg_path = "config/config.yaml"
#     if os.path.exists(cfg_path):
#         with open(cfg_path, "r", encoding="utf-8") as f:
#             try:
#                 return yaml.safe_load(f) or {}
#             except Exception:
#                 logging.warning("Failed to parse config/config.yaml, using defaults.")
#                 return {}
#     else:
#         return {}

# # -------------------------
# # Pipeline
# # -------------------------

# def run_pipeline(query: str):
#     RUN_ID = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
#     log_dir = init_logging(RUN_ID)
#     logging.info("===== Run Started =====")
#     logging.info(f"RUN_ID: {RUN_ID}")
#     logging.info(f"User Query: {query}")

#     ensure_dirs("reports")
#     config = load_config()
#     logging.info("Config file loaded successfully." if config else "No config file found — using defaults.")

#     metrics = Metrics()
#     metrics.start_timer("pipeline.total")

#     # Initialize agents (pass logs_dir and metrics)
#     data_agent = DataAgent(logs_dir=log_dir, metrics=metrics)
#     insight_agent = InsightAgent(logs_dir=log_dir, metrics=metrics)
#     evaluator = EvaluatorAgent(logs_dir=log_dir, metrics=metrics)
#     creative_agent = CreativeAgent(logs_dir=log_dir, metrics=metrics)

#     # Planner (simple plan)
#     plan = {
#         "query": query,
#         "data_path": config.get("data_path", "data/synthetic_fb_ads_undergarments.csv"),
#         "confidence_min": config.get("confidence_min", 0.6),
#         "random_seed": config.get("random_seed", 42)
#     }
#     with open(os.path.join(log_dir, "planner.json"), "w", encoding="utf-8") as f:
#         json.dump(plan, f, indent=2)

#     logging.info("PlannerAgent completed. Saved planner.json")

#     # 1. DataAgent
#     metrics.start_timer("agent.data")
#     data_summary = data_agent.summarize(plan)
#     metrics.stop_timer("agent.data")
#     with open(os.path.join(log_dir, "data_summary.json"), "w", encoding="utf-8") as f:
#         json.dump(data_summary, f, indent=2)
#     logging.info("DataAgent summary complete. Saved data_summary.json")

#     # 2. InsightAgent
#     metrics.start_timer("agent.insight")
#     hypotheses = insight_agent.generate(plan, data_summary)
#     metrics.stop_timer("agent.insight")
#     with open(os.path.join(log_dir, "hypotheses.json"), "w", encoding="utf-8") as f:
#         json.dump(hypotheses, f, indent=2)
#     logging.info("InsightAgent generated hypotheses. Saved hypotheses.json")

#     # 3. EvaluatorAgent
#     metrics.start_timer("agent.evaluator")
#     validated = evaluator.validate(plan, hypotheses, data_summary)
#     metrics.stop_timer("agent.evaluator")
#     insights_path = os.path.join("reports", "insights.json")
#     with open(insights_path, "w", encoding="utf-8") as f:
#         json.dump(validated, f, indent=2)
#     logging.info("EvaluatorAgent completed. Saved reports/insights.json")

#     # 4. CreativeAgent
#     metrics.start_timer("agent.creative")
#     creatives = creative_agent.generate(plan, data_summary, validated)
#     metrics.stop_timer("agent.creative")
#     creatives_path = os.path.join("reports", "creatives.json")
#     with open(creatives_path, "w", encoding="utf-8") as f:
#         json.dump(creatives, f, indent=2)
#     logging.info("CreativeAgent completed. Saved reports/creatives.json")

#     # 5. Final report
#     metrics.start_timer("agent.report")
#     report_text = evaluator.generate_report_text(query, data_summary, validated, creatives)
#     report_path = os.path.join("reports", "report.md")
#     with open(report_path, "w", encoding="utf-8") as f:
#         f.write(report_text)
#     metrics.stop_timer("agent.report")
#     logging.info(f"Final Report generated → {report_path}")

#     metrics.stop_timer("pipeline.total")
#     metrics.dump(os.path.join(log_dir, "metrics.json"))
#     logging.info("Metrics written.")

#     logging.info("===== Run Completed Successfully =====")
#     logging.info(f"Logs Folder: {log_dir}")
#     return {
#         "run_id": RUN_ID,
#         "log_dir": log_dir,
#         "report_path": report_path,
#         "insights_path": insights_path,
#         "creatives_path": creatives_path,
#     }


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument("query", help="User query to analyze")
#     args = parser.parse_args()
#     run_pipeline(args.query)




# # src/run.py
# import argparse
# import json
# import os
# import datetime
# import logging
# import yaml
# import sys

# # ensure repo root on path (so tests can import src.*)
# ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# if ROOT not in sys.path:
#     sys.path.insert(0, ROOT)

# from src.utils.metrics import Metrics
# from src.utils.retry import retry
# from src.agents.data_agent import DataAgent
# from src.agents.insight_agent import InsightAgent
# from src.agents.evaluator import EvaluatorAgent
# from src.agents.creative_agent import CreativeAgent


# # ---------------------------
# # Logging helper
# # ---------------------------
# def init_logging(run_id: str, log_dir_base="logs"):
#     log_dir = os.path.join(log_dir_base, run_id)
#     os.makedirs(log_dir, exist_ok=True)

#     root = logging.getLogger()
#     # avoid adding duplicate handlers when called multiple times
#     if not root.handlers:
#         root.setLevel(logging.INFO)
#         fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
#         fh = logging.FileHandler(os.path.join(log_dir, "system.log"), encoding="utf-8")
#         fh.setFormatter(fmt)
#         root.addHandler(fh)

#         ch = logging.StreamHandler()
#         ch.setFormatter(fmt)
#         root.addHandler(ch)

#     return log_dir

# # ---------------------------
# # Config loader
# # ---------------------------
# def load_config(path="config/config.yaml"):
#     if not os.path.exists(path):
#         raise FileNotFoundError("Config file not found: " + path)
#     with open(path, "r", encoding="utf-8") as f:
#         cfg = yaml.safe_load(f)
#     return cfg

# # ---------------------------
# # Run pipeline (callable from tests)
# # ---------------------------
# def run_pipeline(query: str, config_path="config/config.yaml"):
#     run_id = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
#     log_dir = init_logging(run_id)
#     logging.info("===== Run Started =====")
#     logging.info(f"RUN_ID: {run_id}")
#     logging.info(f"User Query: {query}")

#     cfg = load_config(config_path)
#     logging.info("Config file loaded successfully.")

#     # choose data path by env
#     env = cfg.get("env", "dev")
#     data_cfg = cfg.get("data", {})
#     data_path = data_cfg.get("dev_path") if env == "dev" or data_cfg.get("use_sample_data", True) else data_cfg.get("prod_path")
#     if not data_path:
#         raise ValueError("data_path not configured in config.yaml")

#     # metrics
#     metrics = Metrics()
#     metrics.time_start("pipeline_total")

#     # init agents - pass config & metrics where relevant
#     planner_cfg = cfg  # if planner needs more config later
#     data_agent = DataAgent(logs_dir=log_dir, metrics=metrics, config=cfg)
#     insight_agent = InsightAgent(config=cfg, logs_dir=log_dir, metrics=metrics)
#     evaluator = EvaluatorAgent(config=cfg, logs_dir=log_dir, metrics=metrics)
#     creative_agent = CreativeAgent(config=cfg, logs_dir=log_dir, metrics=metrics)

#     ensure_reports_dir = lambda: os.makedirs("reports", exist_ok=True)
#     ensure_reports_dir()

#     # 1. Planner (simple plan object)
#     plan = {
#         "query": query,
#         "tasks": [
#             "load_data", "summarize_data", "generate_hypotheses",
#             "evaluate_hypotheses", "generate_creatives", "produce_report"
#         ],
#         "data_path": data_path,
#         "confidence_min": cfg.get("evaluator", {}).get("min_confidence", 0.6),
#         "ctr_threshold": cfg.get("evaluator", {}).get("ctr_threshold", 0.01)
#     }
#     # persist planner
#     with open(os.path.join(log_dir, "planner.json"), "w", encoding="utf-8") as f:
#         json.dump(plan, f, indent=2)

#     logging.info("PlannerAgent completed. Saved planner.json")

#     # 2. DataAgent: summarize (wrapped by retry inside DataAgent)
#     data_summary = data_agent.summarize(plan)
#     with open(os.path.join(log_dir, "data_summary.json"), "w", encoding="utf-8") as f:
#         json.dump(data_summary, f, indent=2)
#     logging.info("DataAgent summary complete. Saved data_summary.json")

#     # 3. InsightAgent
#     hypotheses = insight_agent.generate(plan, data_summary)
#     with open(os.path.join(log_dir, "hypotheses.json"), "w", encoding="utf-8") as f:
#         json.dump(hypotheses, f, indent=2)
#     logging.info("InsightAgent generated hypotheses. Saved hypotheses.json")

#     # 4. Evaluator
#     validated = evaluator.validate(plan, hypotheses, data_summary)
#     with open("reports/insights.json", "w", encoding="utf-8") as f:
#         json.dump(validated, f, indent=2)
#     logging.info("EvaluatorAgent completed. Saved reports/insights.json")

#     # 5. Creative Agent
#     creatives = creative_agent.generate(plan, data_summary, validated)
#     with open("reports/creatives.json", "w", encoding="utf-8") as f:
#         json.dump(creatives, f, indent=2)
#     logging.info("CreativeAgent completed. Saved reports/creatives.json")

#     # 6. Final Report
#     report_text = evaluator.generate_report(query, data_summary, validated, creatives)
#     report_path = "reports/report.md"
#     with open(report_path, "w", encoding="utf-8") as f:
#         f.write(report_text)
#     logging.info(f"Final Report generated → {report_path}")

#     # metrics finalize & write
#     metrics.time_end("pipeline_total")
#     metrics_path = os.path.join(log_dir, "metrics.json")
#     metrics.dump(metrics_path)
#     logging.info(f"Metrics dumped → {metrics_path}")

#     logging.info("===== Run Completed Successfully =====")
#     return {
#         "report_path": report_path,
#         "insights_path": "reports/insights.json",
#         "creatives_path": "reports/creatives.json",
#         "metrics_path": metrics_path,
#         "log_dir": log_dir,
#         "run_id": run_id
#     }

# # small helper
# def ensure_dir(path):
#     if not os.path.exists(path):
#         os.makedirs(path, exist_ok=True)

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument("query", help="User query to analyze")
#     args = parser.parse_args()
#     run_pipeline(args.query)



# src/run.py
import argparse
import json
import os
import datetime
import logging
import yaml
import sys

# ensure repo root on path (so tests can import src.*)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.utils.metrics import Metrics
from src.agents.data_agent import DataAgent
from src.agents.insight_agent import InsightAgent
from src.agents.evaluator import EvaluatorAgent
from src.agents.creative_agent import CreativeAgent


# ---------------------------
# Logging helper
# ---------------------------
def init_logging(run_id: str, log_dir_base="logs"):
    log_dir = os.path.join(log_dir_base, run_id)
    os.makedirs(log_dir, exist_ok=True)

    root = logging.getLogger()
    if not root.handlers:
        root.setLevel(logging.INFO)
        fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

        fh = logging.FileHandler(os.path.join(log_dir, "system.log"), encoding="utf-8")
        fh.setFormatter(fmt)
        root.addHandler(fh)

        ch = logging.StreamHandler()
        ch.setFormatter(fmt)
        root.addHandler(ch)

    return log_dir


# ---------------------------
# Config loader
# ---------------------------
def load_config(path="config/config.yaml"):
    if not os.path.exists(path):
        raise FileNotFoundError("Config file not found: " + path)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------
# Resolve data path correctly
# ---------------------------
def resolve_data_path(cfg):
    data_cfg = cfg.get("data", {})
    env = cfg.get("env", "dev")

    use_sample = data_cfg.get("use_sample_data", False)

    if use_sample:
        # Use dev sample dataset
        return data_cfg.get("dev_path")

    # Otherwise use production path
    if env == "prod":
        return data_cfg.get("prod_path")
    else:
        return data_cfg.get("dev_path")


# ---------------------------
# Run pipeline
# ---------------------------
def run_pipeline(query: str, config_path="config/config.yaml"):
    run_id = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    log_dir = init_logging(run_id)

    logging.info("===== Run Started =====")
    logging.info(f"RUN_ID: {run_id}")
    logging.info(f"User Query: {query}")

    cfg = load_config(config_path)
    logging.info("Config file loaded successfully.")

    # Correct path selection
    data_path = resolve_data_path(cfg)
    logging.info(f"Resolved data path: {data_path}")

    if not data_path:
        raise ValueError("data_path could not be resolved from the config.yaml")

    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file does not exist: {data_path}")

    # Init metrics
    metrics = Metrics()
    metrics.time_start("pipeline_total")

    # Init agents
    data_agent = DataAgent(config=cfg, logs_dir=log_dir, metrics=metrics)
    insight_agent = InsightAgent(config=cfg, logs_dir=log_dir, metrics=metrics)
    evaluator = EvaluatorAgent(config=cfg, logs_dir=log_dir, metrics=metrics)
    creative_agent = CreativeAgent(config=cfg, logs_dir=log_dir, metrics=metrics)

    os.makedirs("reports", exist_ok=True)

    # 1. Planner (now correct)
    plan = {
        "query": query,
        "tasks": [
            "load_data",
            "summarize_data",
            "generate_hypotheses",
            "evaluate_hypotheses",
            "generate_creatives",
            "produce_report"
        ],
        "data_path": data_path,
        "confidence_min": cfg.get("evaluator", {}).get("min_confidence", 0.6),
        "ctr_threshold": cfg.get("evaluator", {}).get("ctr_threshold", 0.01),
    }

    with open(os.path.join(log_dir, "planner.json"), "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2)
    logging.info("PlannerAgent completed. Saved planner.json")

    # 2. Data summary
    data_summary = data_agent.summarize(plan)
    with open(os.path.join(log_dir, "data_summary.json"), "w", encoding="utf-8") as f:
        json.dump(data_summary, f, indent=2)
    logging.info("Data summary saved.")

    # 3. Insight generation
    hypotheses = insight_agent.generate(plan, data_summary)
    with open(os.path.join(log_dir, "hypotheses.json"), "w", encoding="utf-8") as f:
        json.dump(hypotheses, f, indent=2)
    logging.info("Hypotheses saved.")

    # 4. Evaluation
    validated = evaluator.validate(plan, hypotheses, data_summary)
    with open("reports/insights.json", "w", encoding="utf-8") as f:
        json.dump(validated, f, indent=2)
    logging.info("Insights saved.")

    # 5. Creative generation
    creatives = creative_agent.generate(plan, data_summary, validated)
    with open("reports/creatives.json", "w", encoding="utf-8") as f:
        json.dump(creatives, f, indent=2)
    logging.info("Creatives saved.")

    # 6. Final report
    report_text = evaluator.generate_report_text(
    query, data_summary, validated, creatives)

    report_path = "reports/report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    logging.info(f"Final Report generated → {report_path}")

    metrics.time_end("pipeline_total")

    metrics_path = os.path.join(log_dir, "metrics.json")
    metrics.dump(metrics_path)
    logging.info(f"Metrics saved → {metrics_path}")

    logging.info("===== Run Completed Successfully =====")

    return {
        "report_path": report_path,
        "insights_path": "reports/insights.json",
        "creatives_path": "reports/creatives.json",
        "metrics_path": metrics_path,
        "log_dir": log_dir,
        "run_id": run_id
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="User query to analyze")
    args = parser.parse_args()
    run_pipeline(args.query)
