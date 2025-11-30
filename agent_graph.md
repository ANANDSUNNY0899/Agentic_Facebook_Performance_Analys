#  Agent Architecture & Data Flow (Kasparro Agentic Facebook Performance Analyst)

Below is the high-level architecture of the multi-agent system.

┌─────────────────┐
│ User Query │
└────────┬────────┘
│
▼
┌─────────────────────────┐
│ Planner Agent │
│ - Breaks query │
│ - Sets windows/params │
│ - Produces plan.json │
└────────┬────────────────┘
│
▼
┌─────────────────────────┐
│ Data Agent │
│ - Loads CSV │
│ - Computes CTR/ROAS │
│ - Compares windows │
│ - Identifies low CTR │
└────────┬────────────────┘
│ data_summary
▼
┌─────────────────────────┐
│ Insight Agent │
│ - Reads data summary │
│ - Creates hypotheses │
│ - Explains performance │
└────────┬────────────────┘
│ hypotheses
▼
┌────────────────────────────┐
│ Evaluator Agent │
│ - Validates hypotheses │
│ - Computes evidence │
│ - Assigns verdict+confidence│
└────────┬────────────────────┘
│ validated insights
▼
┌───────────────────────────┐
│ Creative Improvement Agent │
│ - Extracts messaging │
│ - Generates new creatives │
│ - Produces A/B test plan │
└────────┬───────────────────┘
│ creatives
▼
┌───────────────────────────┐
│ Report.md │
│ - Marketing summary │
│ - Insight output │
│ - Creative recommendations │
└───────────────────────────┘



---

##  Agent Roles Summary

### **1. Planner Agent**
- Converts user request into structured tasks  
- Decides: time windows, thresholds, next steps  
- Ensures consistency and reasoning structure

---

### **2. Data Agent**
- Loads dataset  
- Computes recent vs prior CTR  
- Computes ROAS, impressions, spend  
- Identifies low-performing campaigns  
- Outputs structured data summary JSON  

---

### **3. Insight Agent**
- Generates hypotheses  
- Uses campaign trends + creative metadata  
- Applies Think → Analyze → Conclude pattern  

---

### **4. Evaluator Agent**
- Quantitatively validates hypotheses  
- Computes before/after differences  
- Assigns supported / not-supported verdict  
- Produces confidence scores  

---

### **5. Creative Agent**
- Proposes new creative concepts  
- Based on messaging + performance  
- Generates 5 variants per campaign  
- Adds A/B testing plan  

---

##  Final Output
- insights.json  
- creatives.json  
- report.md  
- logs per run  

This covers the system end-to-end.

