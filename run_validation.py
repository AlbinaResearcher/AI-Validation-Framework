#!/usr/bin/env python3
"""
AI Validation Framework — Command Line Interface
Usage: python run_validation.py
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from validator import validate, batch_validate, generate_report


def run_single_demo():
    """Demo: validate a single LLM output."""
    print("\n🔍 Running single validation demo...\n")

    prompt = """Write a short product description for a B2B SaaS analytics dashboard.
    Target audience: CFOs and finance directors.
    Tone: professional, concise, data-driven.
    Include: key benefits, no more than 3 bullet points."""

    ai_output = """Introducing DataLens — your intelligent financial command center.

    DataLens empowers finance leaders with:
    • Real-time cash flow visibility across all business units
    • Automated variance analysis with AI-driven root cause detection  
    • One-click board-ready reports in IFRS and GAAP formats

    Trusted by 500+ CFOs across Europe. Free trial available — no credit card required.
    DataLens was founded in 2019 in Berlin and has raised $12M in Series A funding."""

    result = validate(
        prompt=prompt,
        ai_output=ai_output,
        context="B2B SaaS product in financial analytics space",
        tone_target="formal, professional, data-driven, no fluff",
        business_rules="Max 3 bullet points. No personal anecdotes. Must be factual.",
    )

    print(result.summary())
    return result


def run_batch_demo():
    """Demo: validate multiple outputs and generate summary report."""
    print("\n📊 Running batch validation demo...\n")

    cases = [
        {
            "prompt": "Summarize the key benefits of using LLMs in customer support.",
            "ai_output": "LLMs dramatically reduce response time by handling 80% of tier-1 queries automatically, lower support costs by up to 40%, and provide 24/7 availability without additional headcount.",
            "tone_target": "concise, professional",
            "business_rules": "Must be factual. Avoid unsupported statistics unless clearly qualified.",
        },
        {
            "prompt": "Write an onboarding welcome message for a new user of a project management tool.",
            "ai_output": "Welcome! We're glad to have you. You can create your first project by clicking the big green button on the dashboard. If you need help, our team is available 24/7 via chat. Also, Einstein said that productivity is key to success.",
            "tone_target": "friendly, warm, helpful",
            "business_rules": "No quotes from public figures. Stay on-product.",
        },
        {
            "prompt": "Explain what an API is to a non-technical business stakeholder.",
            "ai_output": "Think of an API as a waiter in a restaurant. Your app is the customer, the kitchen is another system, and the API takes your order to the kitchen and brings back what you asked for — without you needing to know how the food is prepared.",
            "tone_target": "simple, metaphor-friendly, non-technical",
        },
    ]

    results = batch_validate(cases)
    for i, r in enumerate(results):
        print(f"Case {i+1}:{r.summary()}")

    print(generate_report(results))
    return results


def save_results(results, filename="validation_results.json"):
    """Save validation results to JSON."""
    data = [r.to_dict() for r in results]
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 Results saved to {filename}")


if __name__ == "__main__":
    print("=" * 60)
    print("  AI OUTPUT VALIDATION FRAMEWORK")
    print("  by Albina Urubkina")
    print("=" * 60)

    # Run single validation
    single = run_single_demo()

    # Run batch validation
    batch = run_batch_demo()

    # Save all results
    save_results([single] + batch)
