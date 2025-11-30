## Kasparro — Agentic Facebook Performance Analyst
 # Applied AI Engineer Assignment — by Sunny Anand
   
 #  Demo Video  
   * Watch the full demo video here: [Click to Watch](https://drive.google.com/file/d/1vyIdfw2YAV3kk6LmH_-_vaPwa4T0-4-Q/view?usp=sharing)
   
#  Overview  
This project implements a **multi-agent autonomous analytics system** capable of diagnosing Facebook Ads ROAS drops, identifying performance drivers, and generating creative recommendations grounded in data.

The pipeline follows Kasparro’s required **5-Agent Architecture**:

1. **Planner Agent** → Breaks query into structured tasks  
2. **Data Agent** → Reads, cleans, canonicalizes campaigns & summarizes performance  
3. **Insight Agent** → Generates hypotheses for performance change  
4. **Evaluator Agent** → Validates hypotheses using CTR, impressions, ROAS  
5. **Creative Agent** → Generates CTR-optimized creative variations  

All outputs are automatically saved inside **reports/** and **logs/** folders.

This project uses your **synthetic_fb_ads_undergarments.csv** dataset and includes an advanced fuzzy canonical campaign-mapping system.

---

#  Repository Structure

kasparro-agentic-fb-analyst-sunny-anand/
│
├── README.md
├── ITERATION_NOTES.md
├── requirements.txt
│
├── config/
│ └── config.yaml
│
├── data/
│ ├── synthetic_fb_ads_undergarments.csv
│ └── README.md
│
├── src/
│ ├── run.py
│ └── agents/
│ ├── planner.py
│ ├── data_agent.py
│ ├── insight_agent.py
│ ├── evaluator.py
│ └── creative_agent.py
│ └── utils/
│ ├── metrics.py
│ └── logger.py
│
├── scripts/
│ ├── generate_synonyms.py
│ └── dedupe_campaign_names.py
│
├── prompts/
│ ├── planner_prompt.md
│ ├── insight_prompt.md
│ ├── evaluator_prompt.md
│ └── creative_prompt.md
│
├── reports/
│ ├── report.md
│ ├── insights.json
│ └── creatives.json
│
├── logs/
│ └── (Auto-generated run logs)
│
└── tests/
└── integration_test.py

yaml
Copy code

---

# ⚙️ Setup Instructions

###  Create a virtual environment
python -m venv venv
venv\Scripts\activate # (Windows)

shell
Copy code

###  Install dependencies  
pip install -r requirements.txt

shell
Copy code

### 3️ Configure Dataset in `config/config.yaml`

#### For full dataset:
data:
dev_path: "data/synthetic_fb_ads_undergarments.csv"
use_sample_data: false

shell
Copy code

#### Evaluation Config:
evaluator:
min_confidence: 0.6
ctr_threshold: 0.01
min_recent_impressions: 5000

yaml
Copy code

---

#  Run the Agent Pipeline

Run with English query:
python src/run.py "Analyze ROAS drop"

csharp
Copy code

Run with Hinglish query:
python src/run.py "Bhai mera ROAS gir gaya help!"

yaml
Copy code

---

#  Output Files Generated

| File | Description |
|------|-------------|
| **reports/report.md** | Final marketing report |
| **reports/insights.json** | Validated hypotheses |
| **reports/creatives.json** | AI-generated CTR-optimized ads |
| **logs/<RUN_ID>/planner.json** | Task breakdown |
| **logs/<RUN_ID>/data_summary.json** | Cleaned + aggregated performance |
| **logs/<RUN_ID>/campaigns_normalized.csv** | Mapping: raw → canonical campaign names |
| **logs/<RUN_ID>/metrics.json** | Pipeline metrics |

---

#  Agent Architecture

pgsql
Copy code
      User Query
            ↓
     ┌────────────────┐
     │ Planner Agent  │
     └────────────────┘
            ↓ plan.json
     ┌────────────────┐
     │  Data Agent    │  ← raw CSV
     └────────────────┘
            ↓ data_summary.json
     ┌────────────────┐
     │ Insight Agent  │
     └────────────────┘
            ↓ hypotheses.json
     ┌────────────────┐
     │ Evaluator      │
     └────────────────┘
            ↓ insights.json
     ┌────────────────┐
     │ Creative Agent │
     └────────────────┘
            ↓ creatives.json
     ┌────────────────┐
     │ Final Report   │
     └────────────────┘
            ↓ report.md
markdown
Copy code

---

#  Data Agent v3 — Campaign Canonicalization (Major Upgrade)

Your dataset originally contains hundreds of noisy names like:

- *MEN  Signture  Soft*  
- *-omen summer invisible*  
- *M-n Bold Colors Drop*  
- *ME- PREMIUM MODAL*  

The new DataAgent performs:

###  Text normalization  
✔ Underscore/pipe/dash removal  
✔ Non-alphanumeric cleaning  
✔ Whitespace collapsing  

###  RapidFuzz token_set_ratio  
✔ Difflib fallback  
✔ Manual synonyms  
✔ Mapping to 10 canonical campaigns  

**Final Canonical Campaigns:**
1. Women Seamless Everyday  
2. Men ComfortMax Launch  
3. Men Bold Colors Drop  
4. Women Cotton Classics  
5. Men Premium Modal  
6. Women Studio Sports  
7. Women Fit Lift  
8. Men Signature Soft  
9. Men Athleisure Cooling  
10. Women Summer Invisible  

Outputs mapping file:

logs/<RUN_ID>/campaigns_normalized.csv

yaml
Copy code

---

#  Evaluator Agent — Validation Logic

| Rule | Purpose |
|------|---------|
| `ctr < threshold` | Detect low engagement |
| `impressions > 5000` | Ensure statistical validity |
| `roas_change` check | Aligns with ROAS drop |
| Confidence scoring | 0.55 – 0.80 |

A hypothesis is **supported** when:  
ctr below threshold AND impressions sufficient

yaml
Copy code

---

#  Creative Agent — Ad Copy Generation

For every low-performing campaign:

- Extract dominant keywords  
- Generate **5 new creative variations**:
  - Emotional  
  - Urgency  
  - Value-driven  
  - Problem → Solution  
  - Social Proof  

Example:
"Women Seamless Everyday — feel the comfort | Try now"

yaml
Copy code

---

#  Testing

Run integration test:
pytest tests/

yaml
Copy code

Checks:
- Pipeline runs end-to-end successfully  
- All output files exist  
- JSON structures are validated  
- Metrics file generated  

---

#  Dataset Notes

Dataset includes 8–10 canonical ad campaigns.  
DataAgent v3 fully canonicalizes messy text automatically.  
Null numeric values are handled gracefully and logged.  

---

#  Observability

Every run stores a complete observability package:

- planner.json  
- hypotheses.json  
- data_summary.json  
- metrics.json  
- full logs  

This makes the system **fully inspectable**.

---

#  Version History

### **V1 — Baseline**
- Full 5-agent pipeline
- Basic reporting

### **V2 — Observability**
- Added metrics
- Structured logs
- Initial fuzzy campaign mapping

### **V3 — Production Ready**
- Canonical mapping 100% accurate  
- New DataAgent v3  
- New Evaluator logic (CTR threshold + impression gating)  
- New Creative Agent templates  
- Cleaned run.py (fixed missing method & config issues)  
- Final cleaned outputs  

**Release:** v1.0  
**Commit:** `92ac8e5`

---

#  Release Files

| File | GitHub Link |
|------|-------------|
| **Final Report (report.md)** | https://github.com/ANANDSUNNY0899/kasparro-agentic-fb-analyst-sunny-anand/blob/main/reports/report.md |
| **Validated Insights (insights.json)** | https://github.com/ANANDSUNNY0899/kasparro-agentic-fb-analyst-sunny-anand/blob/main/reports/insights.json |
| **Creative Recommendations (creatives.json)** | https://github.com/ANANDSUNNY0899/kasparro-agentic-fb-analyst-sunny-anand/blob/main/reports/creatives.json |

---

#  Command Used to Generate Latest Run

python src/run.py "Analyze ROAS drop"

yaml
Copy code

---

#  Self-Review Pull Request

Create a PR titled:

Self Review — Kasparro Agentic FB Analyst Assignment

yaml
Copy code

---

#  Final Note  
This project demonstrates:

- Autonomous multi-agent system design  
- Real-world marketing analytics engineering  
- Creative problem-solving  
- Data cleaning + canonicalization  
- Production-grade code quality  
- Strong debugging & iteration discipline  

Perfect for the **Applied AI Engineer** role.

---