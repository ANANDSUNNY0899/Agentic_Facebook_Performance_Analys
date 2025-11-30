#  Design Rationale — Kasparro Agentic Facebook Performance Analyst

This document explains **why** each design decision was made.

---

#  Problem Understanding
The goal is to build an **autonomous agentic system** that:
- detects ROAS and CTR changes,
- diagnoses root causes,
- evaluates hypotheses with data,
- and proposes new creative ideas grounded in existing messaging.

The system must be:
- modular,
- explainable,
- deterministic in flow,
- and agentic (each component has a focused responsibility).

---

#  Why Multi-Agent Architecture?

##  Modularity  
Each agent handles a **single responsibility**:
- Planning  
- Data processing  
- Insight generation  
- Statistical evaluation  
- Creative generation  

Clear separation improves transparency.

##  Reasoning Clarity  
Each agent produces structured JSON + logs.  
Recruiters can see your **thought flow**.

##  Debuggability  
If anything breaks, you know exactly which agent caused it.

---

#  Why These Specific Agents?

## **1. Planner Agent**
We need a deterministic “brain” to:
- interpret queries  
- define time windows  
- set thresholds  
- define workflow steps  

**Without a planner, the system becomes chaotic.**

---

## **2. Data Agent**
Facebook Ads performance cannot be analyzed without:
- recent vs prior windows  
- CTR & ROAS  
- impression filtering  
- percentile-based thresholds

This agent ensures **clean, structured, ready-to-use data**.

---

## **3. Insight Agent**
Insights must be:
- hypothesis-driven  
- explainable  
- not hallucinated

Using structured reasoning  
**Think → Analyze → Conclude**  
keeps hypotheses grounded.

---

## **4. Evaluator Agent**
Hypotheses must be tested with real evidence.

Evaluator provides:
- before/after CTR comparison  
- % drop calculation  
- confidence scoring  
- verdict: supported / not supported / inconclusive  

This improves trustworthiness.

---

## **5. Creative Agent**
Low-CTR campaigns require fresh creative ideas.

Agent produces:
- 5 variants per campaign  
- messaging based on product category  
- CTAs  
- A/B testing plan  

---

#  Why JSON Everywhere?
Structured JSON ensures:
- machine-readability  
- reusable logs  
- easy evaluation  
- deterministic output format  

---

#  Why Confidence Scores?
Because:
- not every insight is equally strong  
- confidence gating prevents weak conclusions  
- system becomes more reliable  

---

#  Why report.md?
To communicate findings to marketers in a:
- simple,
- actionable,
- human-readable

format.

---

#  Final Notes
This system combines:
- agentic reasoning  
- statistical evidence  
- creative generation  
- and clear explanations  

This is EXACTLY what companies like Kasparro expect in an applied AI engineer challenge.

