"""
AI Output Validation Framework
================================
Validates LLM responses across 6 quality dimensions using Claude as a judge.
Author: Albina Urubkina
"""

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Optional
from anthropic import Anthropic

client = Anthropic()

VALIDATION_DIMENSIONS = [
    "consistency",
    "completeness",
    "tone_of_voice",
    "hallucination_absence",
    "business_logic",
    "structure_format",
]

DIMENSION_DESCRIPTIONS = {
    "consistency": "No internal contradictions or logical conflicts in the response",
    "completeness": "All required aspects of the prompt are addressed",
    "tone_of_voice": "Matches the requested tone (formal, friendly, expert, etc.)",
    "hallucination_absence": "No fabricated facts, invented sources, or false claims",
    "business_logic": "Aligns with the stated business rules and domain constraints",
    "structure_format": "Correct formatting, structure, and output schema adherence",
}

JUDGE_SYSTEM_PROMPT = """You are a rigorous AI output quality evaluator. Your job is to assess LLM-generated text across specific quality dimensions.

For each dimension you receive, score the AI output from 0 to 10 and provide a concise justification (1–2 sentences).

Return ONLY valid JSON in this exact format:
{
  "scores": {
    "dimension_name": {
      "score": <0-10>,
      "justification": "<1-2 sentences>",
      "passed": <true if score >= 7, else false>
    }
  },
  "overall_score": <average of all dimension scores, rounded to 1 decimal>,
  "critical_issues": ["<list any score < 5 issues>"],
  "recommendation": "<one sentence: APPROVE / REVISE / REJECT with reason>"
}

Be strict. A score of 10 means perfect. A score of 7 is the minimum passing threshold."""


@dataclass
class ValidationResult:
    prompt: str
    ai_output: str
    context: Optional[str]
    scores: dict = field(default_factory=dict)
    overall_score: float = 0.0
    critical_issues: list = field(default_factory=list)
    recommendation: str = ""
    passed: bool = False
    dimensions_evaluated: list = field(default_factory=list)

    def to_dict(self):
        return asdict(self)

    def summary(self) -> str:
        lines = [
            f"\n{'='*60}",
            f"  AI VALIDATION REPORT",
            f"{'='*60}",
            f"  Overall Score : {self.overall_score}/10",
            f"  Status        : {'✅ PASSED' if self.passed else '❌ FAILED'}",
            f"  Decision      : {self.recommendation}",
            f"{'─'*60}",
            f"  Dimension Scores:",
        ]
        for dim, data in self.scores.items():
            icon = "✅" if data["passed"] else "❌"
            lines.append(f"  {icon} {dim:<25} {data['score']}/10")
            lines.append(f"     └─ {data['justification']}")
        if self.critical_issues:
            lines.append(f"{'─'*60}")
            lines.append(f"  ⚠️  Critical Issues:")
            for issue in self.critical_issues:
                lines.append(f"     • {issue}")
        lines.append(f"{'='*60}\n")
        return "\n".join(lines)


def validate(
    prompt: str,
    ai_output: str,
    context: str = "",
    dimensions: list = None,
    tone_target: str = "",
    business_rules: str = "",
) -> ValidationResult:
    """
    Validate an LLM response using Claude as an evaluator.

    Args:
        prompt: The original prompt sent to the LLM
        ai_output: The response to evaluate
        context: Optional background context / domain info
        dimensions: List of dimensions to check (default: all 6)
        tone_target: Describe the expected tone (e.g. "formal, B2B, concise")
        business_rules: Any domain-specific rules the output must follow

    Returns:
        ValidationResult with scores, issues, and recommendation
    """
    if dimensions is None:
        dimensions = VALIDATION_DIMENSIONS

    # Build evaluation payload
    dim_block = "\n".join(
        [f"- {d}: {DIMENSION_DESCRIPTIONS[d]}" for d in dimensions if d in DIMENSION_DESCRIPTIONS]
    )

    user_message = f"""Evaluate the following AI-generated output.

ORIGINAL PROMPT:
{prompt}

AI OUTPUT TO EVALUATE:
{ai_output}

{"CONTEXT / DOMAIN INFO:" + chr(10) + context if context else ""}
{"EXPECTED TONE:" + chr(10) + tone_target if tone_target else ""}
{"BUSINESS RULES:" + chr(10) + business_rules if business_rules else ""}

DIMENSIONS TO EVALUATE:
{dim_block}

Return your evaluation as JSON only."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        system=JUDGE_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = response.content[0].text.strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    parsed = json.loads(raw)

    result = ValidationResult(
        prompt=prompt,
        ai_output=ai_output,
        context=context,
        scores=parsed.get("scores", {}),
        overall_score=parsed.get("overall_score", 0.0),
        critical_issues=parsed.get("critical_issues", []),
        recommendation=parsed.get("recommendation", ""),
        passed=parsed.get("overall_score", 0) >= 7.0,
        dimensions_evaluated=dimensions,
    )

    return result


def batch_validate(cases: list[dict]) -> list[ValidationResult]:
    """
    Validate multiple prompt/output pairs.

    Args:
        cases: List of dicts with keys: prompt, ai_output, and optionally
               context, dimensions, tone_target, business_rules

    Returns:
        List of ValidationResult objects
    """
    results = []
    for i, case in enumerate(cases):
        print(f"  Validating case {i+1}/{len(cases)}...")
        result = validate(
            prompt=case["prompt"],
            ai_output=case["ai_output"],
            context=case.get("context", ""),
            dimensions=case.get("dimensions", None),
            tone_target=case.get("tone_target", ""),
            business_rules=case.get("business_rules", ""),
        )
        results.append(result)
    return results


def generate_report(results: list[ValidationResult]) -> str:
    """Generate a summary report from multiple validation results."""
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    avg_score = round(sum(r.overall_score for r in results) / total, 1) if total else 0

    lines = [
        f"\n{'='*60}",
        f"  BATCH VALIDATION SUMMARY",
        f"{'='*60}",
        f"  Total cases   : {total}",
        f"  Passed        : {passed} ({round(passed/total*100)}%)" if total else "",
        f"  Failed        : {total - passed}",
        f"  Avg Score     : {avg_score}/10",
        f"{'─'*60}",
    ]

    # Per-dimension breakdown
    dim_totals = {}
    for r in results:
        for dim, data in r.scores.items():
            if dim not in dim_totals:
                dim_totals[dim] = []
            dim_totals[dim].append(data["score"])

    if dim_totals:
        lines.append("  Avg Scores by Dimension:")
        for dim, scores in dim_totals.items():
            avg = round(sum(scores) / len(scores), 1)
            bar = "█" * int(avg) + "░" * (10 - int(avg))
            lines.append(f"  {dim:<25} {bar} {avg}/10")

    lines.append(f"{'='*60}\n")
    return "\n".join(lines)
