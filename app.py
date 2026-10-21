import streamlit as st
import pandas as pd
import plotly.express as px
from html import escape

from resume_parser import extract_text
from matcher import analyze_match, suggest_projects, generate_interview_questions
from storage import init_db, save_analysis, get_history, delete_history

st.set_page_config(
    page_title="JobMatch AI | Resume Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)
init_db()

# -------------------- Professional dark SaaS theme --------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root {
  --bg:#0a0f1c; --panel:#111a2b; --panel2:#151f33; --border:#26344d;
  --text:#edf3ff; --muted:#9aabc5; --blue:#7c9cff; --green:#48d6a0; --amber:#ffc66d;
}
html, body, [class*="css"] {font-family:'DM Sans',sans-serif;}
.stApp {
  background:radial-gradient(ellipse at 8% 0%,rgba(55,91,170,.16),transparent 34%),var(--bg);
  color:var(--text);
}
[data-testid="stHeader"] {background:rgba(10,15,28,.88);}
[data-testid="stSidebar"] {background:#0d1423;border-right:1px solid var(--border);}
h1,h2,h3 {font-family:'Manrope',sans-serif!important;color:var(--text)!important;letter-spacing:-.03em;}
.brand {display:flex;align-items:center;gap:12px;padding:4px 0 18px;}
.brand-icon {display:flex;align-items:center;justify-content:center;width:43px;height:43px;border-radius:13px;background:linear-gradient(135deg,#7898ff,#536be7);font-size:23px;}
.brand-name {font-family:'Manrope',sans-serif;font-size:19px;font-weight:800;color:var(--text);}
.brand-subtitle,.muted,.section-description {color:var(--muted);}
.brand-subtitle {font-size:10px;letter-spacing:.12em;margin-top:3px;}
.eyebrow {color:var(--blue);font-weight:700;font-size:11px;letter-spacing:.14em;text-transform:uppercase;margin-bottom:8px;}
.hero {padding:30px 32px;border:1px solid #2b3c5d;border-radius:22px;background:radial-gradient(circle at 90% 20%,rgba(111,139,255,.2),transparent 28%),linear-gradient(120deg,#16233c,#101827 72%);margin:4px 0 25px;}
.hero h1 {font-size:clamp(27px,3.2vw,39px);margin:0 0 10px;line-height:1.15;}
.hero p {color:#aebdd5;font-size:15px;max-width:720px;margin:0;line-height:1.65;}
.section-heading {font-family:'Manrope',sans-serif;font-size:20px;font-weight:800;margin:12px 0 4px;color:var(--text);}
.section-description {font-size:13px;margin-bottom:16px;}
.panel {background:linear-gradient(145deg,#131e31,#101827);border:1px solid var(--border);border-radius:17px;padding:20px;margin-bottom:14px;}
.panel-label {color:var(--muted);font-size:12px;font-weight:600;margin-bottom:8px;}
.panel-value {color:var(--text);font-family:'Manrope',sans-serif;font-size:28px;font-weight:800;line-height:1.2;}
.panel-note {color:var(--muted);font-size:12px;margin-top:7px;}
.pill {display:inline-block;border-radius:999px;padding:5px 10px;margin:3px 4px 3px 0;font-size:12px;font-weight:600;background:#1b2940;border:1px solid #2c405f;color:#dbe6ff;}
.pill-green {background:rgba(72,214,160,.1);border-color:rgba(72,214,160,.3);color:#77edbd;}
.pill-amber {background:rgba(255,198,109,.1);border-color:rgba(255,198,109,.3);color:#ffd18c;}
div[data-testid="stMetric"] {background:linear-gradient(145deg,#151f33,#101827);border:1px solid var(--border);border-radius:16px;padding:17px 18px;}
div[data-testid="stMetricLabel"] {color:var(--muted);}
div[data-testid="stMetricValue"] {color:var(--text);font-family:'Manrope',sans-serif;font-weight:800;}
.stButton>button {border-radius:10px;border:1px solid #35496d;min-height:43px;font-weight:700;}
.stButton>button[kind="primary"] {background:linear-gradient(135deg,#7898ff,#5a73e9);border:none;color:white;}
.stTextInput input,.stTextArea textarea {background:#0e1728;border-color:#2a3b58;border-radius:10px;color:var(--text);}
[data-testid="stFileUploader"] {background:#0e1728;border:1px dashed #344867;border-radius:12px;padding:8px;}
[data-testid="stExpander"] {border:1px solid var(--border);border-radius:12px;background:#101827;}
hr {border-color:var(--border);}
@media(max-width:768px){.hero{padding:23px 20px}.panel-value{font-size:24px;}}
</style>
""", unsafe_allow_html=True)


def render_pills(items, variant=""):
    """Render recognized skills as visual labels."""
    if not items:
        st.caption("Nothing to show here yet.")
        return
    css = " pill-green" if variant == "green" else " pill-amber" if variant == "amber" else ""
    html = "".join(
        f'<span class="pill{css}">{escape(str(item))}</span>' for item in items
    )
    st.markdown(html, unsafe_allow_html=True)


def safe_percent(value):
    try:
        return max(0.0, min(float(value) / 100.0, 1.0))
    except (TypeError, ValueError):
        return 0.0


# -------------------- Sidebar --------------------
with st.sidebar:
    st.markdown("""
    <div class="brand">
      <div class="brand-icon">🎯</div>
      <div><div class="brand-name">JobMatch AI</div>
      <div class="brand-subtitle">RESUME INTELLIGENCE</div></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio(
        "WORKSPACE",
        ["Match Analyzer", "Application Tracker", "About & Method"],
    )
    st.markdown("---")
    st.markdown("**Built for better applications**")
    st.caption("Analyze a resume, understand skill alignment, and plan your next step.")
    st.caption("Privacy note: this version does not send resume text to an external AI API. Scores are estimates, not hiring decisions.")


# -------------------- Match Analyzer --------------------
if page == "Match Analyzer":
    st.markdown("""
    <div class="hero">
      <div class="eyebrow">RESUME · ROLE · INSIGHTS</div>
      <h1>Find your next best-fit role.</h1>
      <p>Understand how your resume aligns with a job description. Discover recognized skills,
      identify potential gaps, and turn your results into a practical action plan.</p>
    </div>
    """, unsafe_allow_html=True)

    resume_col, job_col = st.columns(2, gap="large")
    with resume_col:
        st.markdown('<div class="section-heading">01 · Your resume</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-description">Upload a document or paste your resume text.</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload PDF, DOCX, or TXT", type=["pdf", "docx", "txt"])
        pasted_resume = st.text_area("Resume text", height=225, placeholder="Paste your resume here...")
        resume_text = pasted_resume
        if uploaded is not None:
            try:
                extracted = extract_text(uploaded.getvalue(), uploaded.name)
                if extracted.strip():
                    resume_text = extracted
                    st.success(f"Resume text extracted from {uploaded.name}")
                else:
                    st.warning("No text was extracted. Try a text-based document or paste the resume text.")
            except Exception as exc:
                st.error(f"Could not read this file: {exc}")

    with job_col:
        st.markdown('<div class="section-heading">02 · Target role</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-description">Add role details and the complete job description.</div>', unsafe_allow_html=True)
        job_title = st.text_input("Job title", placeholder="e.g., Junior AI Developer")
        company = st.text_input("Company (optional)", placeholder="e.g., Example Technologies")
        job_text = st.text_area("Job description", height=225, placeholder="Paste responsibilities, required qualifications, and preferred skills...")

    st.caption("For the most useful comparison, include the full job description and its qualification headings.")
    analyze_clicked = st.button("✦  Analyze my match", type="primary", use_container_width=True)

    if analyze_clicked:
        if len(resume_text.strip()) < 40:
            st.error("Please provide a resume with at least a few sentences.")
        elif len(job_text.strip()) < 40:
            st.error("Please paste a job description with at least a few sentences.")
        else:
            try:
                with st.spinner("Analyzing resume and job requirements..."):
                    analysis = analyze_match(resume_text, job_text)
                st.session_state["last_result"] = {
                    "resume_text": resume_text,
                    "job_text": job_text,
                    "job_title": job_title,
                    "company": company,
                    "result": analysis,
                }
                st.success("Analysis complete.")
            except Exception as exc:
                st.error(f"Analysis failed: {exc}")

    if st.session_state.get("last_result"):
        current = st.session_state["last_result"]
        result = current["result"]
        st.markdown("---")
        st.markdown(f"""
        <div class="eyebrow">ANALYSIS REPORT</div>
        <h2 style="margin-bottom:4px;">{escape(current['job_title'] or 'Target role')}</h2>
        <p class="muted" style="margin-top:0;">{escape(current['company'] or 'Company not specified')} ·
        {len(current['resume_text'].split()):,} resume words · {len(current['job_text'].split()):,} job-description words</p>
        """, unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Overall match", f"{result['overall_score']}%")
        m2.metric("Skill coverage", f"{result['skill_coverage']}%")
        m3.metric("Matched skills", len(result.get("matched_skills", [])))
        m4.metric("Potential gaps", len(result.get("missing_skills", [])))

        score_col, chart_col = st.columns([0.85, 1.15], gap="large")
        with score_col:
            st.markdown('<div class="section-heading">Match overview</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="panel">
              <div class="panel-label">OVERALL MATCH SCORE</div>
              <div class="panel-value">{result['overall_score']}<span style="font-size:17px;color:#9aabc5;"> / 100</span></div>
              <div class="panel-note">Heuristic indicator based on text similarity and recognized skills.</div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(safe_percent(result["overall_score"]))
            st.caption("This is not a validated ATS score or a probability of being hired.")

        with chart_col:
            st.markdown('<div class="section-heading">Score breakdown</div>', unsafe_allow_html=True)
            component_df = pd.DataFrame({
                "Component": ["Text similarity", "Skill coverage"],
                "Score": [result["text_similarity"], result["skill_coverage"]],
            })
            fig = px.bar(component_df, x="Component", y="Score", text="Score", range_y=[0, 100], template="plotly_dark")
            fig.update_traces(texttemplate="%{text}%", textposition="outside", marker_line_width=0)
            fig.update_layout(
                height=270, margin=dict(l=5, r=5, t=25, b=5),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#dce7fa"), yaxis_title="Score (%)", xaxis_title="", showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

        matched_col, missing_col = st.columns(2, gap="large")
        with matched_col:
            st.markdown('<div class="section-heading">Matched skills</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-description">Recognized in both your resume and the job description.</div>', unsafe_allow_html=True)
            render_pills(result.get("matched_skills", []), "green")
        with missing_col:
            st.markdown('<div class="section-heading">Potential skill gaps</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-description">Recognized in the job description but not found in your resume text.</div>', unsafe_allow_html=True)
            render_pills(result.get("missing_skills", []), "amber")

        st.markdown("---")
        st.markdown('<div class="section-heading">Detailed skill analysis</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-description">Review required qualifications separately from preferred skills where the job description makes that distinction.</div>', unsafe_allow_html=True)

        detailed_fields = [
            "requirement_sections_found", "required_skills", "preferred_skills",
            "missing_required_skills", "missing_preferred_skills",
            "required_skill_coverage", "preferred_skill_coverage", "scoring_method",
        ]
        detailed_available = all(field in result for field in detailed_fields)

        if detailed_available and result["requirement_sections_found"]:
            req_col, pref_col = st.columns(2, gap="large")
            with req_col:
                st.markdown('<div class="panel-label">REQUIRED SKILLS</div>', unsafe_allow_html=True)
                required = result.get("required_skills", [])
                render_pills(required)
                coverage = result.get("required_skill_coverage")
                if coverage is not None:
                    st.metric("Recognized required-skill coverage", f"{coverage}%")
                    st.progress(safe_percent(coverage))
                missing_required = result.get("missing_required_skills", [])
                if missing_required:
                    st.warning("Potential required-skill gaps: " + ", ".join(missing_required))
                elif required:
                    st.success("No missing required skills were identified by the prototype.")

            with pref_col:
                st.markdown('<div class="panel-label">PREFERRED SKILLS</div>', unsafe_allow_html=True)
                preferred = result.get("preferred_skills", [])
                render_pills(preferred)
                coverage = result.get("preferred_skill_coverage")
                if coverage is not None:
                    st.metric("Recognized preferred-skill coverage", f"{coverage}%")
                    st.progress(safe_percent(coverage))
                missing_preferred = result.get("missing_preferred_skills", [])
                if missing_preferred:
                    st.info("Potential preferred-skill gaps: " + ", ".join(missing_preferred))
                elif preferred:
                    st.success("No missing preferred skills were identified by the prototype.")

            st.caption("Classification uses job-description wording and headings. Review the lists; the prototype may misclassify skills.")
        else:
            st.info("No explicit required/preferred sections were detected, or the matcher does not return detailed fields. General skill analysis remains available above.")

        if detailed_available:
            st.caption("Scoring method: " + str(result["scoring_method"]))

        st.markdown("---")
        st.markdown('<div class="section-heading">Your action plan</div>', unsafe_allow_html=True)
        recommendations = result.get("recommendations", [])
        if recommendations:
            for index, item in enumerate(recommendations, 1):
                st.markdown(f"**{index}.** {item}")
        else:
            st.info("No recommendations were generated.")

        with st.expander("Explore portfolio project ideas", expanded=True):
            projects = suggest_projects(result.get("missing_skills", []))
            if projects:
                for project in projects:
                    st.markdown(f"**{project['title']}**")
                    st.write(project["description"])
            else:
                st.info("No project suggestions are available for the recognized gaps.")

        with st.expander("Practice interview questions"):
            questions = generate_interview_questions(
                current["job_title"],
                result.get("matched_skills", []),
                result.get("missing_skills", []),
            )
            if questions:
                for index, question in enumerate(questions, 1):
                    st.markdown(f"{index}. {question}")
            else:
                st.info("No interview questions were generated.")

        with st.expander("Recognized skills and scoring details"):
            st.write("**Resume skills recognized:**", ", ".join(result.get("resume_skills", [])) or "None")
            st.write("**Job skills recognized:**", ", ".join(result.get("job_skills", [])) or "None")
            st.write("**Scoring formula:** 60% TF-IDF cosine similarity + 40% recognized skill coverage.")
            st.write("**Skill coverage:** matched recognized job skills divided by all recognized job skills.")
            st.caption("TF-IDF measures text overlap; it does not provide semantic understanding like a language model.")

        st.markdown("---")
        save_col, note_col = st.columns([1, 2], vertical_alignment="center")
        with save_col:
            if st.button("Save to application tracker", type="primary", use_container_width=True):
                try:
                    save_analysis(
                        current["job_title"], current["company"], result["overall_score"],
                        result.get("matched_skills", []), result.get("missing_skills", []),
                    )
                    st.success("Analysis saved to your local tracker.")
                except Exception as exc:
                    st.error(f"Could not save this analysis: {exc}")
        with note_col:
            st.caption("Saved analyses are stored in the project's local SQLite database.")


# -------------------- Application Tracker --------------------
elif page == "Application Tracker":
    st.markdown("""
    <div class="hero">
      <div class="eyebrow">YOUR JOB SEARCH</div>
      <h1>Application tracker</h1>
      <p>Keep your resume analyses in one place, review previous match scores, and export your history.</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        history = get_history()
        if history.empty:
            st.info("No saved analyses yet. Run an analysis and choose 'Save to application tracker'.")
        else:
            st.markdown('<div class="section-heading">Saved analyses</div>', unsafe_allow_html=True)
            st.dataframe(history, use_container_width=True, hide_index=True)
            dl_col, clear_col = st.columns(2, gap="large")
            with dl_col:
                csv_data = history.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download history as CSV", csv_data,
                    "jobmatch_application_tracker.csv", "text/csv",
                    use_container_width=True,
                )
            with clear_col:
                with st.expander("Clear saved history"):
                    st.warning("This deletes all saved analysis history from the local database.")
                    confirmed = st.checkbox("I understand this cannot be undone.")
                    if st.button("Delete all history", type="secondary"):
                        if confirmed:
                            delete_history()
                            st.success("Application history cleared.")
                            st.rerun()
                        else:
                            st.warning("Confirm the deletion before continuing.")
    except Exception as exc:
        st.error(f"Could not load application history: {exc}")


# -------------------- About & Method --------------------
else:
    st.markdown("""
    <div class="hero">
      <div class="eyebrow">TRANSPARENCY FIRST</div>
      <h1>About JobMatch AI</h1>
      <p>A resume-to-job comparison prototype to help job seekers understand recognized skill alignment and plan improvements.</p>
    </div>
    """, unsafe_allow_html=True)

    about_col, method_col = st.columns(2, gap="large")
    with about_col:
        st.markdown('<div class="section-heading">How it works</div>', unsafe_allow_html=True)
        st.markdown("""
        1. Extracts text from PDF, DOCX, or TXT resumes.
        2. Uses TF-IDF and cosine similarity to compare resume and job-description text.
        3. Identifies skills from a built-in skill dictionary.
        4. Estimates required and preferred skills from headings and wording.
        5. Suggests next steps, portfolio projects, and interview questions.
        6. Optionally stores analyses in a local SQLite database.
        """)
    with method_col:
        st.markdown('<div class="section-heading">Scoring method</div>', unsafe_allow_html=True)
        st.markdown("""
        - **60% text similarity:** estimates textual overlap.
        - **40% skill coverage:** estimates coverage of recognized job skills.
        - Required/preferred coverage is shown separately when the matcher identifies those sections.
        """)
    st.markdown("---")
    st.markdown('<div class="section-heading">Important limitations</div>', unsafe_allow_html=True)
    st.markdown("""
    - This is a portfolio prototype, not a commercial ATS replica.
    - Text similarity can reward similar wording and miss relevant experience expressed differently.
    - The built-in skill dictionary may miss synonyms, unfamiliar technologies, and qualifications.
    - Required/preferred classification is heuristic and should be reviewed.
    - The app cannot reliably verify proficiency or years of experience from resume text alone.
    - Scanned PDFs may require OCR.
    - Do not use the score as the sole basis for employment decisions.
    """)
    st.markdown("---")
    st.markdown("**Run locally**")
    st.code("streamlit run app.py", language="bash")
