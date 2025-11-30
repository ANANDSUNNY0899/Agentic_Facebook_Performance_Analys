
# src/agents/creative_agent.py
import logging
from typing import Dict, Any, List

class CreativeAgent:
    def __init__(self, config=None, logs_dir=None, metrics=None):
        self.config = config or {}
        self.logs_dir = logs_dir
        self.metrics = metrics

    def generate(self, plan: Dict[str, Any], data_summary: Dict[str, Any], validated_insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        For each canonical campaign produce 4 short creative lines.
        """
        logging.info("Generating creatives...")
        creatives = []
        for v in validated_insights:
            camp = v["campaign"]
            # simple template-based variants
            variants = [
                f"{camp} — feel the comfort | Try now",
                f"{camp} — limited time offer | Shop today",
                f"{camp} — customer favorite | Rated 4.8★",
                f"{camp} — save more with bundle | Buy now"
            ]
            creatives.append({
                "campaign": camp,
                "variants": variants
            })

        if self.metrics:
            self.metrics.gauge("creatives.generated", len(creatives))

        logging.info("✔ Creatives generated.")
        return creatives
