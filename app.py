"""
AI Output Validation Framework — Streamlit UI
Run: streamlit run app.py
"""

import streamlit as st
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from validator import validate, batch_validate, generate_report, VALIDATION_DIMENSIONS, DIMENSION_DESCRIPTIONS

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Validation Framework",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

/* Dark industrial background */
.stApp {
    background-color: #0e0e11;
    color: #e8e6e0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #141418;
    border-right: 1px solid #2a2a35;
}

/* Main header */
.main-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2rem;
    font-weight: 600;
    color: #f0ede6;
    letter-spacing: -0.02em;
    margin-bottom: 0.2rem;
}
.main-sub {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
    color: #5a5a72;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 2rem;
}

/* Score card */
.score-card {
    background: #16161c;
    border: 1px solid #2a2a35;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.score-card.passed { border-left: 3px solid #3ecf8e; }
.score-card.failed { border-left: 3px solid #e05c5c; }

.score-number {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 3rem;
    font-weight: 600;
    line-height: 1;
}
.score-number.pass { color: #3ecf8e; }
.score-number.fail { color: #e05c5c; }
.score-number.warn { color: #f5a623; }

.dim-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #5a5a72;
    margin-bottom: 0.3rem;
}
.dim-justification {
    font-size: 0.82rem;
    color: #8e8eaa;
    font-style: italic;
    margin-top: 0.3rem;
}

/* Recommendation banner */
.rec-approve {
    background: #0d2e1e;
    border: 1px solid #3ecf8e;
    color: #3ecf8e;
    padding: 0.8rem 1.2rem;
    border-radius: 6px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    margin-top: 1rem;
}
.rec-revise {
    background: #2e1e00;
    border: 1px solid #f5a623;
    color: #f5a623;
    padding: 0.8rem 1.2rem;
    border-radius: 6px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    margin-top: 1rem;
}
.rec-reject {
    background: #2e0d0d;
    border: 1px solid #e05c5c;
    color: #e05c5c;
    padding: 0.8rem 1.2rem;
    border-radius: 6px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    margin-top: 1rem;
}

/* Issue tag */
.issue-tag {
    background: #2e0d0d;
    color: #e05c5c;
    padding: 0.3rem 0.7rem;
    border-radius: 4px;
    font-size: 0.78rem;
    font-family: 'IBM Plex Mono', monospace;
    display: inline-block;
    margin: 0.2rem 0.2rem 0.2rem 0;
}

/* Inputs */
.stTextArea textarea, .stTextInput input {
    background-color: #16161c !important;
    border: 1px solid #2a2a35 !important;
    color: #e8e6e0 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    border-radius: 6px !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #4a4a72 !important;
    box-shadow: none !important;
}

/* Button */
.stButton > button {
    background-color: #e8e6e0 !important;
    color: #0e0e11 !important;
    border: none !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.06em !important;
    padding: 0.6rem 1.5rem !important;
    border-radius: 6px !important;
    width: 100%;
}
.stButton > button:hover {
    background-color: #ffffff !important;
}

/* Multiselect tags */
.stMultiSelect [data-baseweb="tag"] {
    background-color: #2a2a35 !important;
    color: #e8e6e0 !important;
}

/* Divider */
hr { border-color: #2a2a35; }

/* Section labels */
.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: #5a5a72;
    margin-bottom: 0.5rem;
    margin-top: 1.5rem;
}

/* Progress bar override */
.stProgress > div > div {
    background-color: #3ecf8e !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 AI Validation Framework")
    st.markdown('<p style="font-size:0.75rem;color:#5a5a72;font-family:IBM Plex Mono,monospace;">by Albina Urubkina</p>', unsafe_allow_html=True)
    st.divider()

    api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
    if api_key:
        os.environ["ANTHROPIC_API_KEY"] = api_key

    st.divider()
    st.markdown('<p class="dim-label">Dimensions to evaluate</p>', unsafe_allow_html=True)
    
    dim_labels = {
        "consistency": "Consistency",
        "completeness": "Completeness",
        "tone_of_voice": "Tone of Voice",
        "hallucination_absence": "Hallucination Absence",
        "business_logic": "Business Logic",
        "structure_format": "Structure & Format",
    }

    selected_dims = []
    for key, label in dim_labels.items():
        if st.checkbox(label, value=True, key=f"dim_{key}"):
            selected_dims.append(key)

    st.divider()
    st.markdown('<p class="dim-label">Pass threshold</p>', unsafe_allow_html=True)
    threshold = st.slider("Min score to pass", 5.0, 9.0, 7.0, 0.5)

    st.divider()
    mode = st.radio("Mode", ["Single validation", "Batch (JSON)"], index=0)

# ─── Header ─────────────────────────────────────────────────────────────────
st.markdown('<p class="main-header">AI Output Validator</p>', unsafe_allow_html=True)
st.markdown('<p class="main-sub">LLM-as-Judge · 6 quality dimensions · Claude API</p>', unsafe_allow_html=True)

# ─── Single mode ────────────────────────────────────────────────────────────
if mode == "Single validation":
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<p class="section-label">Original prompt</p>', unsafe_allow_html=True)
        prompt = st.text_area("", height=160, placeholder="The prompt that was sent to the LLM...", key="prompt", label_visibility="collapsed")

        st.markdown('<p class="section-label">AI output to evaluate</p>', unsafe_allow_html=True)
        ai_output = st.text_area("", height=200, placeholder="The LLM response you want to validate...", key="output", label_visibility="collapsed")

    with col2:
        st.markdown('<p class="section-label">Context / domain info (optional)</p>', unsafe_allow_html=True)
        context = st.text_area("", height=80, placeholder="e.g. B2B SaaS product, financial services, customer support bot...", key="context", label_visibility="collapsed")

        st.markdown('<p class="section-label">Expected tone (optional)</p>', unsafe_allow_html=True)
        tone = st.text_input("", placeholder="e.g. formal, professional, data-driven, no fluff", key="tone", label_visibility="collapsed")

        st.markdown('<p class="section-label">Business rules (optional)</p>', unsafe_allow_html=True)
        rules = st.text_area("", height=100, placeholder="e.g. Max 3 bullets. No personal emails. Must be factual.", key="rules", label_visibility="collapsed")

    st.markdown("")
    run = st.button("▶ RUN VALIDATION", use_container_width=True)

    if run:
        if not prompt or not ai_output:
            st.error("Please fill in the prompt and AI output fields.")
        elif not os.environ.get("ANTHROPIC_API_KEY"):
            st.error("Please enter your Anthropic API key in the sidebar.")
        elif not selected_dims:
            st.error("Select at least one dimension.")
        else:
            with st.spinner("Evaluating with Claude..."):
                result = validate(
                    prompt=prompt,
                    ai_output=ai_output,
                    context=context,
                    tone_target=tone,
                    business_rules=rules,
                    dimensions=selected_dims,
                )
                result.passed = result.overall_score >= threshold

            st.divider()
            st.markdown("### Results")

            # Overall score
            oc1, oc2, oc3 = st.columns([1, 2, 1])
            with oc1:
                score_class = "pass" if result.overall_score >= threshold else ("warn" if result.overall_score >= 5 else "fail")
                status_text = "✅ PASSED" if result.passed else "❌ FAILED"
                st.markdown(f"""
                <div class="score-card {'passed' if result.passed else 'failed'}">
                    <div class="dim-label">Overall Score</div>
                    <div class="score-number {score_class}">{result.overall_score}</div>
                    <div style="font-family:IBM Plex Mono,monospace;font-size:0.8rem;margin-top:0.5rem;color:#8e8eaa;">{status_text}</div>
                </div>
                """, unsafe_allow_html=True)

            with oc2:
                rec = result.recommendation
                rec_class = "rec-approve" if "APPROVE" in rec.upper() else ("rec-reject" if "REJECT" in rec.upper() else "rec-revise")
                st.markdown(f'<div class="{rec_class}">📋 {rec}</div>', unsafe_allow_html=True)

                if result.critical_issues:
                    st.markdown('<p class="section-label" style="margin-top:1rem;">Critical issues</p>', unsafe_allow_html=True)
                    for issue in result.critical_issues:
                        st.markdown(f'<span class="issue-tag">⚠ {issue}</span>', unsafe_allow_html=True)

            # Per-dimension scores
            st.markdown('<p class="section-label" style="margin-top:1.5rem;">Dimension breakdown</p>', unsafe_allow_html=True)

            dims = list(result.scores.items())
            rows = [dims[i:i+3] for i in range(0, len(dims), 3)]

            for row in rows:
                cols = st.columns(len(row), gap="medium")
                for col, (dim, data) in zip(cols, row):
                    with col:
                        passed_dim = data["score"] >= threshold
                        score_c = "pass" if data["score"] >= threshold else ("warn" if data["score"] >= 5 else "fail")
                        st.markdown(f"""
                        <div class="score-card {'passed' if passed_dim else 'failed'}">
                            <div class="dim-label">{dim_labels.get(dim, dim)}</div>
                            <div class="score-number {score_c}" style="font-size:2rem;">{data['score']}/10</div>
                            <div style="margin:0.4rem 0;">
                                <progress value="{data['score']}" max="10" style="width:100%;height:4px;accent-color:{'#3ecf8e' if passed_dim else '#e05c5c'};"></progress>
                            </div>
                            <div class="dim-justification">{data['justification']}</div>
                        </div>
                        """, unsafe_allow_html=True)

            # Export
            st.divider()
            export = json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
            st.download_button(
                "⬇ Download JSON report",
                data=export,
                file_name="validation_result.json",
                mime="application/json",
            )

# ─── Batch mode ─────────────────────────────────────────────────────────────
else:
    st.markdown('<p class="section-label">Paste JSON array of cases</p>', unsafe_allow_html=True)
    
    with open("examples/sample_cases.json", encoding="utf-8") as f:
        sample_json = f.read()

    batch_input = st.text_area(
        "",
        value=sample_json,
        height=300,
        label_visibility="collapsed",
        key="batch_input"
    )

    run_batch = st.button("▶ RUN BATCH VALIDATION", use_container_width=True)

    if run_batch:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            st.error("Please enter your Anthropic API key in the sidebar.")
        else:
            try:
                cases = json.loads(batch_input)
            except Exception as e:
                st.error(f"Invalid JSON: {e}")
                st.stop()

            results = []
            progress = st.progress(0, text="Starting...")
            for i, case in enumerate(cases):
                progress.progress((i) / len(cases), text=f"Validating case {i+1}/{len(cases)}...")
                r = validate(
                    prompt=case["prompt"],
                    ai_output=case["ai_output"],
                    context=case.get("context", ""),
                    tone_target=case.get("tone_target", ""),
                    business_rules=case.get("business_rules", ""),
                    dimensions=selected_dims,
                )
                r.passed = r.overall_score >= threshold
                results.append(r)
            progress.progress(1.0, text="Done!")

            st.divider()

            # Summary stats
            total = len(results)
            passed = sum(1 for r in results if r.passed)
            avg = round(sum(r.overall_score for r in results) / total, 1)

            s1, s2, s3 = st.columns(3)
            s1.metric("Cases validated", total)
            s2.metric("Passed", f"{passed} / {total} ({round(passed/total*100)}%)")
            s3.metric("Avg score", f"{avg} / 10")

            st.divider()

            for i, (case, result) in enumerate(zip(cases, results)):
                name = case.get("name", f"Case {i+1}")
                score_color = "#3ecf8e" if result.passed else "#e05c5c"
                with st.expander(f"{'✅' if result.passed else '❌'} {name} — {result.overall_score}/10"):
                    for dim, data in result.scores.items():
                        st.markdown(
                            f"**{dim_labels.get(dim, dim)}** — `{data['score']}/10`  \n"
                            f"*{data['justification']}*"
                        )
                    st.markdown(f"**Recommendation:** {result.recommendation}")
                    if result.critical_issues:
                        for issue in result.critical_issues:
                            st.markdown(f'<span class="issue-tag">⚠ {issue}</span>', unsafe_allow_html=True)

            # Export all
            export_all = json.dumps([r.to_dict() for r in results], ensure_ascii=False, indent=2)
            st.download_button(
                "⬇ Download full batch report (JSON)",
                data=export_all,
                file_name="batch_validation_results.json",
                mime="application/json",
            )
