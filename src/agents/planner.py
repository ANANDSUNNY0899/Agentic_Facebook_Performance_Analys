
# # src/agents/planner.py
# import os
# import json
# import logging
# from typing import Dict, Any


# class PlannerAgent:
#     def __init__(self, config: Dict[str, Any] = None, logs_dir: str = None):
#         if not isinstance(config, dict):
#             raise ValueError("PlannerAgent requires a config dictionary.")
#         self.config = config
#         self.logs_dir = logs_dir or "logs"

#     def create_plan(self, query: str) -> Dict[str, Any]:
#         """Create a simple plan and include config items needed by downstream agents."""
#         plan = {
#             "query": query,
#             "tasks": [
#                 "load_data",
#                 "summarize_data",
#                 "generate_hypotheses",
#                 "evaluate_hypotheses",
#                 "generate_creatives",
#                 "produce_report"
#             ],
#             "data_path": self.config.get("data_path"),
#             "confidence_min": self.config.get("confidence_min", 0.6),
#             "use_sample_data": self.config.get("use_sample_data", True)
#         }

#         # save planner.json
#         if self.logs_dir:
#             planner_path = os.path.join(self.logs_dir, "planner.json")
#             try:
#                 with open(planner_path, "w", encoding="utf-8") as f:
#                     json.dump(plan, f, indent=2, ensure_ascii=False)
#             except Exception:
#                 logging.warning("Could not write planner.json to logs dir.")
#         return plan





# src/agents/planner.py
import os
import json
import logging
from typing import Dict, Any


class PlannerAgent:
    def __init__(self, config: Dict[str, Any] = None, logs_dir: str = None):
        if not isinstance(config, dict):
            raise ValueError("PlannerAgent requires a config dictionary.")

        self.config = config
        self.logs_dir = logs_dir or "logs"

    def _select_data_path(self) -> str:
        """Select the correct dataset path based on config."""
        data_cfg = self.config.get("data", {})

        use_sample = data_cfg.get("use_sample_data", True)
        dev_path = data_cfg.get("dev_path")
        prod_path = data_cfg.get("prod_path")

        if use_sample:
            return dev_path
        return prod_path

    def create_plan(self, query: str) -> Dict[str, Any]:
        """Creates the final execution plan used across agents."""

        # Pick correct CSV path
        data_path = self._select_data_path()

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

            # Correct data path selected here
            "data_path": data_path,

            # Evaluator settings
            "confidence_min": self.config.get("evaluator", {}).get("min_confidence", 0.6),
            "ctr_threshold": self.config.get("evaluator", {}).get("ctr_threshold", 0.01),
            "min_recent_impressions": self.config.get("evaluator", {}).get("min_recent_impressions", 5000),

            # Debug info
            "use_sample_data": self.config.get("data", {}).get("use_sample_data", True),
        }

        # Save planner.json
        if self.logs_dir:
            planner_path = os.path.join(self.logs_dir, "planner.json")
            try:
                with open(planner_path, "w", encoding="utf-8") as f:
                    json.dump(plan, f, indent=2, ensure_ascii=False)
            except Exception as e:
                logging.warning(f"Could not write planner.json: {e}")

        return plan
