


# src/agents/data_agent.py

import os
import re
import json
import logging
from typing import Dict, Any, List, Optional

import pandas as pd
from difflib import get_close_matches

# Try fast fuzzy matching
try:
    from rapidfuzz import fuzz, process
    _HAS_RAPIDFUZZ = True
except Exception:
    _HAS_RAPIDFUZZ = False


# -------------------------
# FINAL — 9 CANONICAL CAMPAIGNS
# -------------------------
CANONICAL_CAMPAIGNS = [
    "Women Seamless Everyday",
    "Men ComfortMax Launch",
    "Men Bold Colors Drop",
    "Women Cotton Classics",
    "Men Premium Modal",
    "Women Studio Sports",
    "Women Fit Lift",
    "Men Signature Soft",
    "Women Summer Invisible",
]

_CANONICAL_KEYS = {c.lower(): c for c in CANONICAL_CAMPAIGNS}


# -------------------------
# Manual synonyms (better detection)
# -------------------------
MANUAL_SYNONYMS = {
    "women seamless": "Women Seamless Everyday",
    "seamless everyday": "Women Seamless Everyday",

    "comfortmax": "Men ComfortMax Launch",
    "comfort max": "Men ComfortMax Launch",
    "men comfort max": "Men ComfortMax Launch",

    "men bold colors": "Men Bold Colors Drop",

    "cotton classics": "Women Cotton Classics",
    "women cotton": "Women Cotton Classics",

    "premium modal": "Men Premium Modal",

    "studio sports": "Women Studio Sports",

    "fit lift": "Women Fit Lift",

    "signature soft": "Men Signature Soft",

    "summer invisible": "Women Summer Invisible",
}


# -------------------------
# Required CSV columns
# -------------------------
REQUIRED_COLUMNS = [
    "date",
    "campaign_name",
    "impressions",
    "clicks",
    "spend",
    "purchases",
    "revenue",
    "creative_message",
]


# -------------------------
# Helpers
# -------------------------
def normalize_text(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    if not isinstance(s, str):
        s = str(s)

    s = s.lower().strip()
    s = re.sub(r"[_|\-]+", " ", s)
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s



def fuzzy_match_to_canonical(s: str, cutoff: int = 75) -> Optional[str]:
    """Map normalized text to canonical campaign."""
    if not s:
        return None

    key = s.strip().lower()

    # Manual synonyms
    if key in MANUAL_SYNONYMS:
        return MANUAL_SYNONYMS[key]

    # Exact canonical
    if key in _CANONICAL_KEYS:
        return _CANONICAL_KEYS[key]

    # RapidFuzz
    if _HAS_RAPIDFUZZ:
        candidates = list(_CANONICAL_KEYS.keys())
        best = process.extractOne(key, candidates, scorer=fuzz.token_set_ratio)

        if best and best[1] >= cutoff:
            return _CANONICAL_KEYS[best[0]]

        syn_keys = list(MANUAL_SYNONYMS.keys())
        best_syn = process.extractOne(key, syn_keys, scorer=fuzz.token_set_ratio)

        if best_syn and best_syn[1] >= cutoff:
            return MANUAL_SYNONYMS[best_syn[0]]

    # difflib fallback
    candidates = list(_CANONICAL_KEYS.keys()) + list(MANUAL_SYNONYMS.keys())
    match = get_close_matches(key, candidates, n=1, cutoff=cutoff / 100.0)

    if match:
        m = match[0]
        if m in _CANONICAL_KEYS:
            return _CANONICAL_KEYS[m]
        if m in MANUAL_SYNONYMS:
            return MANUAL_SYNONYMS[m]

    return None



# -----------------------------------------------------------
# DataAgent — FINAL VERSION
# -----------------------------------------------------------
class DataAgent:
    def __init__(self, logs_dir: str = None, metrics: Any = None, config: Dict[str, Any] = None):
        self.logs_dir = logs_dir
        self.metrics = metrics
        self.config = config or {}
        self.fuzzy_cutoff = int(self.config.get("data", {}).get("fuzzy_cutoff", 75))

    # -------------------------
    # Validation
    # -------------------------
    def _ensure_required_columns_present(self, df: pd.DataFrame):
        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            logging.error(f"❌ Missing required columns: {missing}")
            raise ValueError(f"Dataset missing required columns: {missing}")
        logging.info("✔ All required columns are present.")

    def _coerce_numeric(self, df: pd.DataFrame):
        for col in ["impressions", "clicks", "spend", "revenue", "purchases"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
                if df[col].isna().sum() > 0:
                    logging.warning(f"⚠ Column '{col}' has {df[col].isna().sum()} invalid numeric values.")
                    df[col] = df[col].fillna(0)
        return df

    def validate_dataset(self, df: pd.DataFrame):
        logging.info("Running dataset validation...")
        self._ensure_required_columns_present(df)

        for col, cnt in df.isnull().sum().to_dict().items():
            if cnt > 0:
                logging.warning(f"⚠ Column '{col}' contains {cnt} null values.")

        df = self._coerce_numeric(df)
        logging.info("✔ Type checks completed.")
        return True


    # -------------------------
    # Main pipeline: summarize()
    # -------------------------
    def summarize(self, plan: Dict[str, Any]) -> Dict[str, Any]:

        path = plan.get("data_path") or self.config.get("data", {}).get("dev_path")
        if not path:
            raise ValueError("No data path found in config/plan.")

        if not os.path.exists(path):
            raise FileNotFoundError(f"CSV not found: {path}")

        logging.info(f"Reading dataset: {path}")
        df = pd.read_csv(path)

        self.validate_dataset(df)

        # Fix dates
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        bad = df["date"].isna().sum()
        if bad > 0:
            logging.warning(f"⚠ Dropping {bad} invalid date rows.")
            df = df.dropna(subset=["date"])

        # Normalize + Map campaigns
        df["campaign_normalized_raw"] = df["campaign_name"].apply(lambda x: normalize_text(x) or "")
        df["campaign_canonical"] = df["campaign_normalized_raw"].apply(
            lambda x: fuzzy_match_to_canonical(x, cutoff=self.fuzzy_cutoff) or ""
        )

        # If no canonical match → fallback to readable Title Case
        df["campaign_canonical"] = df.apply(
            lambda r: r["campaign_canonical"] if r["campaign_canonical"] else r["campaign_normalized_raw"].title(),
            axis=1
        )

        # -------- Aggregate --------
        agg = df.groupby("campaign_canonical").agg(
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            spend=("spend", "sum"),
            revenue=("revenue", "sum"),
            rows=("campaign_name", "count")
        ).reset_index()

        # Build final canonical-first summary
        final_map: Dict[str, Dict[str, Any]] = {
            c: {"campaign": c, "impressions": 0, "clicks": 0, "spend": 0.0, "revenue": 0.0, "rows": 0}
            for c in CANONICAL_CAMPAIGNS
        }

        # Assign aggregates to canonical or fallback own bucket
        for _, row in agg.iterrows():
            camp = row["campaign_canonical"]
            camp_key = camp.lower()

            # Canonical
            if camp_key in _CANONICAL_KEYS:
                canon = _CANONICAL_KEYS[camp_key]
                bucket = final_map[canon]
            else:
                # Non-canonical bucket
                if camp not in final_map:
                    final_map[camp] = {"campaign": camp, "impressions": 0, "clicks": 0, "spend": 0.0, "revenue": 0.0, "rows": 0}
                bucket = final_map[camp]

            bucket["impressions"] += int(row["impressions"])
            bucket["clicks"] += int(row["clicks"])
            bucket["spend"] += float(row["spend"])
            bucket["revenue"] += float(row["revenue"])
            bucket["rows"] += int(row["rows"])

        # Build final ordered list
        final_list: List[Dict[str, Any]] = []

        # First canonical order
        for c in CANONICAL_CAMPAIGNS:
            b = final_map[c]
            ctr = (b["clicks"] / b["impressions"]) if b["impressions"] > 0 else None
            b["ctr"] = ctr
            final_list.append(b)

        # Then non-canonical
        non_canonical = [v for k, v in final_map.items() if k not in CANONICAL_CAMPAIGNS]
        non_canonical = sorted(non_canonical, key=lambda x: x["impressions"], reverse=True)

        for b in non_canonical:
            ctr = (b["clicks"] / b["impressions"]) if b["impressions"] > 0 else None
            b["ctr"] = ctr
            final_list.append(b)

        # Summary
        summary = {
            "date_range": {
                "start": str(df["date"].min()),
                "end": str(df["date"].max())
            },
            "total_rows": int(len(df)),
            "total_impressions": int(df["impressions"].sum()),
            "total_clicks": int(df["clicks"].sum()),
            "total_spend": float(df["spend"].sum()),
            "total_revenue": float(df["revenue"].sum()),
            "campaigns": final_list
        }

        # Debug mapping file
        if self.logs_dir:
            try:
                os.makedirs(self.logs_dir, exist_ok=True)
                out_path = os.path.join(self.logs_dir, "campaigns_normalized.csv")
                df[["campaign_name", "campaign_normalized_raw", "campaign_canonical"]].drop_duplicates().to_csv(out_path, index=False)
                logging.info(f"Normalized campaign mapping written → {out_path}")
            except Exception as e:
                logging.warning(f"Could not write mapping CSV: {e}")

        return summary
