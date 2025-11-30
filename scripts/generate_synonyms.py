# scripts/generate_synonyms.py

import pandas as pd
import os
import difflib

INPUT_PATH = "data/synthetic_fb_ads_undergarments.csv"
OUTPUT_PATH = "scripts/proposed_synonyms.csv"

def normalize(text: str):
    if not isinstance(text, str):
        return ""
    return "".join(c.lower() for c in text if c.isalnum() or c.isspace()).strip()

def main():
    if not os.path.exists(INPUT_PATH):
        print(f"ERROR: CSV not found → {INPUT_PATH}")
        return

    df = pd.read_csv(INPUT_PATH)
    if "campaign_name" not in df.columns:
        print("ERROR: No 'campaign_name' column found.")
        return

    raw_names = sorted(df["campaign_name"].dropna().unique())
    normalized = [normalize(x) for x in raw_names]

    # Try grouping similar names
    canonical_map = []
    for i, name in enumerate(raw_names):
        norm = normalized[i]

        # Find close matches
        close = difflib.get_close_matches(norm, normalized, n=5, cutoff=0.8)

        canonical_map.append({
            "raw_name": name,
            "normalized": norm,
            "close_matches": "; ".join(close)
        })

    os.makedirs("scripts", exist_ok=True)
    pd.DataFrame(canonical_map).to_csv(OUTPUT_PATH, index=False)

    print(f"\nGenerated: {OUTPUT_PATH}")
    print("Open the CSV and share the top 20 lines with me.")

if __name__ == "__main__":
    main()
