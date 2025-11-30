
# src/agents/insight_agent.py
import logging
from typing import Dict, Any, List

CTR_LOW_THRESHOLD = 0.01  # 1% CTR threshold

class InsightAgent:
    def __init__(self, config=None, logs_dir=None, metrics=None):
        self.config = config or {}
        self.logs_dir = logs_dir
        self.metrics = metrics

    def generate(self, plan: Dict[str, Any], data_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Produce a hypotheses list for each canonical campaign.
        Hypothesis format:
          { campaign, hypothesis, reason, metric: {ctr, impressions, clicks} }
        """
        logging.info("Generating hypotheses for campaigns...")
        hyps = []
        campaigns = data_summary.get("campaigns", [])
        for c in campaigns:
            ctr = c.get("ctr")
            imps = c.get("impressions", 0)
            # default hypothesis
            if ctr is None:
                reason = "No impressions / insufficient data"
                hyps.append({
                    "campaign": c["campaign"],
                    "hypothesis": "CTR insufficient data",
                    "reason": reason,
                    "metric": {"ctr": None, "impressions": imps, "clicks": c.get("clicks", 0)}
                })
                continue

            if ctr < CTR_LOW_THRESHOLD:
                hyps.append({
                    "campaign": c["campaign"],
                    "hypothesis": f"CTR below {CTR_LOW_THRESHOLD*100:.1f}%",
                    "reason": "Low CTR may drive low ROAS",
                    "metric": {"ctr": ctr, "impressions": imps, "clicks": c.get("clicks", 0)}
                })
            else:
                hyps.append({
                    "campaign": c["campaign"],
                    "hypothesis": "CTR healthy",
                    "reason": "CTR above threshold",
                    "metric": {"ctr": ctr, "impressions": imps, "clicks": c.get("clicks", 0)}
                })

        if self.metrics:
            self.metrics.gauge("hypotheses.generated", len(hyps))

        logging.info("✔ Hypotheses generated.")
        return hyps
