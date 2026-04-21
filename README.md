# 🔍 AI Output Validation Framework

> A systematic, production-ready framework for evaluating LLM response quality across 6 critical business dimensions — using **Claude as an evaluator** (LLM-as-Judge pattern).

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)](https://python.org)
[![Anthropic](https://img.shields.io/badge/Powered%20by-Claude%20API-orange?logo=anthropic)](https://anthropic.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## The Problem

When LLMs are deployed in production — customer support bots, document generators, analytics tools — manual review of every output doesn't scale. You need a systematic way to catch:

- ❌ Hallucinated facts that contradict your business rules
- ❌ Tone mismatches that break brand guidelines
- ❌ Incomplete answers that miss key prompt requirements
- ❌ Format violations that break downstream systems

## The Solution

This framework runs your AI outputs through a structured evaluation pipeline. Each response is scored across **6 dimensions** by Claude acting as a quality judge, returning structured scores, justifications, and a clear APPROVE / REVISE / REJECT recommendation.

---

## Validation Dimensions

| Dimension | What It Checks | Weight |
|-----------|---------------|--------|
| **Consistency** | No internal contradictions or logical conflicts | Equal |
| **Completeness** | All prompt requirements addressed | Equal |
| **Tone of Voice** | Matches expected register (formal/friendly/expert) | Equal |
| **Hallucination Absence** | No fabricated facts, invented sources, false claims | Equal |
| **Business Logic** | Aligns with domain rules and constraints | Equal |
| **Structure & Format** | Correct output format and schema adherence | Equal |

**Pass threshold:** Overall score ≥ 7.0 / 10

---

## Quick Start

```bash
git clone https://github.com/yourusername/ai-validation-framework
cd ai-validation-framework
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
python run_validation.py
```

---

## Usage

### Single Validation

```python
from src.validator import validate

result = validate(
    prompt="Write a product description for a B2B SaaS analytics tool. Max 3 bullets. CFO audience.",
    ai_output="DataLens empowers finance leaders with real-time visibility...",
    context="B2B SaaS analytics product",
    tone_target="formal, data-driven, concise",
    business_rules="Max 3 bullet points. No company history. Facts only."
)

print(result.summary())
```

**Output:**
```
============================================================
  AI VALIDATION REPORT
============================================================
  Overall Score : 6.8/10
  Status        : ❌ FAILED
  Decision      : REVISE — output includes unsolicited company history
────────────────────────────────────────────────────────────
  Dimension Scores:
  ✅ consistency               9/10
     └─ No internal contradictions found.
  ✅ completeness              8/10
     └─ All three bullet points present, CFO framing maintained.
  ✅ tone_of_voice             8/10
     └─ Professional and data-driven throughout.
  ❌ hallucination_absence     4/10
     └─ "$12M Series A" statistic is unverified and could be false.
  ❌ business_logic            5/10
     └─ Company founding history violates the "no company history" rule.
  ✅ structure_format          8/10
     └─ Three bullet points, clean formatting.
============================================================
```

### Batch Validation

```python
from src.validator import batch_validate, generate_report

cases = [
    {"prompt": "...", "ai_output": "...", "tone_target": "formal"},
    {"prompt": "...", "ai_output": "...", "business_rules": "No personal emails."},
]

results = batch_validate(cases)
print(generate_report(results))
```

### Select Specific Dimensions

```python
result = validate(
    prompt=my_prompt,
    ai_output=my_output,
    dimensions=["hallucination_absence", "business_logic"]  # only check what you need
)
```

---

## Project Structure

```
ai-validation-framework/
├── src/
│   └── validator.py          # Core validation engine
├── notebooks/
│   └── AI_Validation_Framework.ipynb   # Interactive walkthrough
├── examples/
│   └── sample_cases.json     # Ready-to-run test cases
├── run_validation.py          # CLI runner with demos
└── requirements.txt
```

---

## Architecture

```
Input: (prompt, ai_output, context, rules)
        │
        ▼
  validator.py
  ├── Builds structured judge prompt
  ├── Calls Claude API (claude-sonnet)
  └── Parses JSON evaluation response
        │
        ▼
  ValidationResult
  ├── scores         → per-dimension score + justification
  ├── overall_score  → weighted average
  ├── critical_issues → dimensions scoring < 5
  ├── recommendation → APPROVE / REVISE / REJECT
  └── passed         → bool (threshold: 7.0)
```

**Design decisions:**
- **LLM-as-Judge pattern** — the evaluator model operates under a separate strict system prompt, acting as a detached critic rather than a collaborator
- **Structured JSON output** with schema enforcement avoids parsing ambiguity
- **Modular dimensions** — use all 6 or pick a subset relevant to your use case
- **Serializable results** — `to_dict()` on every result for logging, dashboards, or audit trails

---

## Limitations

- The evaluator model can share biases with the model being evaluated — cross-model validation is more robust
- `hallucination_absence` requires accurate `context` / `business_rules` to work effectively; it can't detect hallucinations about facts it doesn't know
- API costs scale with batch size — consider result caching for large regression suites
- Threshold of 7.0 is a starting point; calibrate per domain and risk tolerance

---

## Real-World Applications

This framework was inspired by practical experience validating LLM outputs in two production contexts:

- **Sber (GigaChat integration)** — validating personalized financial communications against multiple Tone of Voice profiles and compliance rules
- **SROI Analytics AI Service** — ensuring AI-generated social impact assessments were consistent, complete, and free of hallucinations before presenting to grant committees

---

## Author

**Albina Urubkina** — AI Product Analyst | UX Researcher | Prompt Engineer  
[LinkedIn](https://linkedin.com) · [Telegram](https://t.me/albinaina) · [Email](mailto:aurubkina@gmail.com)

*Open to roles in AI product analytics, LLM integration, and UX research.*

---

## License

MIT — use freely, attribution appreciated.
