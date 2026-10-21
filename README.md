# 🎯 JobMatch AI — Intelligent Resume & Job Matching Platform

JobMatch AI is a portfolio-ready Streamlit application that compares resume content with a job description, identifies recognized skill overlaps and gaps, suggests practical next steps, and optionally tracks analyses locally.

> **Important:** This is a transparent prototype, not an ATS replica, validated hiring test, or probability of being hired. Never use its score as the sole basis for employment decisions.

## Features

- Upload PDF, DOCX, or TXT resumes, or paste resume text.
- Compare resume and job-description text with TF-IDF + cosine similarity.
- Detect skills using an editable skill dictionary.
- Calculate skill coverage and a heuristic overall score.
- Suggest next steps and project ideas for potential gaps.
- Generate interview-practice questions.
- Save role analyses to a local SQLite tracker.
- Export saved application history as CSV.
- No external AI API required; resume text is not sent to an LLM service.

## Tech stack

Python · Streamlit · scikit-learn · Pandas · Plotly · SQLite · pypdf · python-docx

## Quick start

Python 3.10+ recommended.

```bash
git clone https://github.com/YOUR-USERNAME/jobmatch-ai.git
cd jobmatch-ai
python -m venv .venv
```

Activate the environment:

**macOS/Linux**
```bash
source .venv/bin/activate
```

**Windows**
```powershell
.venv\Scripts\activate
```

Install dependencies and run:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

The app should open in your browser. The local SQLite history database is created automatically after first run.

## How scoring works

The score is a simple heuristic:

- **60% text similarity:** TF-IDF vectorization with unigrams and bigrams, compared using cosine similarity.
- **40% skill coverage:** number of recognized job-description skills also found in the resume divided by recognized job-description skills.

`overall_score = round(0.60 × text_similarity + 0.40 × skill_coverage)`

This score is designed for learning and comparison, not as a validated ATS score. It may be affected by wording overlap, the skill dictionary, resume formatting, and job-description length. It does not assess the quality of a candidate's work or prove proficiency.

## Project structure

```text
jobmatch-ai/
├── app.py
├── matcher.py
├── resume_parser.py
├── storage.py
├── requirements.txt
├── README.md
├── .gitignore
└── tests/
    └── test_matcher.py
```

## Limitations and responsible use

- Scanned PDFs may not contain extractable text; OCR must be run separately.
- The built-in skill list is incomplete. Edit `SKILLS` in `matcher.py` to add role-specific skills and synonyms.
- A listed skill is not proof of proficiency.
- Similarity scores can overvalue keyword overlap and undervalue transferable skills.
- Keep personal resume data private. This version does not call external AI APIs, but files and text are processed by the running app and saved analyses include role/company and skill names.
- Do not commit resumes, API keys, credentials, or private datasets to GitHub.
- Review outputs and edit recommendations before acting on them.

## Suggested roadmap

- [ ] Add a configurable skill dictionary and synonym groups.
- [ ] Add unit tests and GitHub Actions CI.
- [ ] Add OCR as an optional, documented workflow.
- [ ] Add multiple job comparisons and a side-by-side report.
- [ ] Add evidence snippets showing where each recognized skill appears.
- [ ] Add accessible UI tests and deployment instructions.
- [ ] Evaluate score behavior on a consented, anonymized sample set before making any performance claims.

## License

MIT — see `LICENSE`.
