
# src/agents/evaluator.py
import logging
from typing import Dict, Any, List

CTR_LOW_THRESHOLD = 0.01

class EvaluatorAgent:
    def __init__(self, config=None, logs_dir=None, metrics=None):
        self.config = config or {}
        self.logs_dir = logs_dir
        self.metrics = metrics

    def validate(self, plan: Dict[str, Any], hypotheses: List[Dict[str, Any]], data_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Validate hypotheses using simple rules:
         - If ctr is None => inconclusive
         - If ctr < CTR_LOW_THRESHOLD and impressions >= 50000 => supported (conf 0.7)
         - If ctr < CTR_LOW_THRESHOLD and impressions < 50000 => supported but lower conf (0.55)
         - else => not_supported (ctr healthy)
        """
        logging.info("Validating hypotheses...")
        validated = []
        for h in hypotheses:
            ctr = h["metric"].get("ctr")
            imps = h["metric"].get("impressions", 0)

            if ctr is None:
                status = "inconclusive"
                conf = 0.35
                reason = "No impressions or insufficient data"
            elif ctr < CTR_LOW_THRESHOLD:
                if imps >= 50000:
                    status = "supported"
                    conf = 0.7
                    reason = f"CTR below threshold ({ctr:.4f}) with sufficient impressions ({imps})"
                else:
                    status = "supported"
                    conf = 0.55
                    reason = f"CTR below threshold ({ctr:.4f}) but low impressions ({imps})"
            else:
                status = "not_supported"
                conf = 0.55
                reason = f"CTR healthy ({ctr:.4f})"

            validated.append({
                "campaign": h["campaign"],
                "status": status,
                "confidence": conf,
                "evidence": h["metric"],
                "reason": reason
            })

        if self.metrics:
            self.metrics.gauge("insights.validated", len(validated))

        logging.info("✔ Validation complete.")
        return validated

    def generate_report_text(self, query: str, data_summary: Dict[str, Any], validated: List[Dict[str, Any]], creatives: List[Dict[str, Any]]) -> str:
        """
        Creates a readable markdown report.
        """
        dr = data_summary.get("date_range", {})
        start = dr.get("start", "N/A")
        end = dr.get("end", "N/A")

        lines = []
        lines.append(f"# Final Report — {query}")
        lines.append("")
        lines.append(f"Date Range: {start} → {end}")
        lines.append("")
        lines.append("## Validated Insights")
        lines.append("")

        for v in validated:
            camp = v["campaign"]
            status = v["status"]
            conf = v["confidence"]
            ev = v["evidence"]
            if ev and ev.get("ctr") is not None:
                ctr = ev["ctr"]
                imps = ev["impressions"]
                lines.append(f"- **{camp}** — *{status}* (conf {conf})")
                lines.append(f"  Evidence: ctr={ctr}, impressions={imps}")
                lines.append(f"  Reasons: {v['reason']}")
                lines.append("")
            else:
                lines.append(f"- **{camp}** — *{status}* (conf {conf})")
                lines.append(f"  Evidence: ctr=None, impressions={ev.get('impressions') if ev else 0}")
                lines.append(f"  Reasons: {v['reason']}")
                lines.append("")

        lines.append("## Creative Recommendations")
        lines.append("")
        # creatives is list of dicts {campaign, variants}
        for c in creatives:
            lines.append(f"### {c['campaign']}")
            for var in c.get("variants", []):
                lines.append(f"- {var}")
            lines.append("")

        return "\n".join(lines)
