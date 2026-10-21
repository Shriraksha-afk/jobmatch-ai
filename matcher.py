import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# --------------------------------------------------
# SKILL DATABASE
# --------------------------------------------------

SKILL_ALIASES = {
    "python": ["python", "python programming"],
    "sql": ["sql", "structured query language"],
    "mysql": ["mysql", "my sql"],
    "postgresql": ["postgresql", "postgres"],
    "excel": ["excel", "microsoft excel"],
    "power bi": ["power bi", "powerbi"],
    "tableau": ["tableau"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning"],
    "natural language processing": [
        "natural language processing",
        "nlp"
    ],
    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch", "py torch"],
    "streamlit": ["streamlit"],
    "fastapi": ["fastapi", "fast api"],
    "flask": ["flask"],
    "rest api": ["rest api", "restful api"],
    "api": ["api", "apis", "application programming interface"],
    "git": ["git", "version control"],
    "github": ["github", "git hub"],
    "docker": ["docker", "containerization"],
    "aws": ["aws", "amazon web services"],
    "azure": ["azure", "microsoft azure"],
    "gcp": ["gcp", "google cloud platform"],
    "statistics": ["statistics", "statistical analysis"],
    "data visualization": ["data visualization", "data visualisation"],
    "data analysis": ["data analysis", "data analytics"],
    "data cleaning": ["data cleaning", "data cleansing"],
    "etl": ["etl", "extract transform load"],
    "airflow": ["airflow", "apache airflow"],
    "spark": ["spark", "apache spark"],
    "java": ["java"],
    "javascript": ["javascript", "js"],
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "react": ["react", "react.js", "reactjs"],
    "linux": ["linux"],
    "testing": ["testing", "software testing", "unit testing"],
    "ci/cd": ["ci/cd", "continuous integration", "continuous deployment"],
    "llm": ["llm", "large language model", "large language models"],
    "prompt engineering": ["prompt engineering"],
    "generative ai": ["generative ai", "gen ai"],
    "vector database": ["vector database", "vector databases"],
    "embedding": ["embedding", "embeddings"],
    "communication": ["communication", "communication skills"],
    "problem solving": ["problem solving", "problem-solving"],
    "agile": ["agile", "agile methodology"],
    "project management": ["project management"],
}


# --------------------------------------------------
# PROJECT IDEAS
# --------------------------------------------------

PROJECTS = {
    "sql": (
        "SQL Analytics Case Study",
        "Analyze a business dataset using SQL queries and explain the findings."
    ),
    "python": (
        "Python Data Pipeline",
        "Build a tested Python script that cleans and summarizes raw data."
    ),
    "machine learning": (
        "Model Comparison Lab",
        "Compare machine learning models and document evaluation metrics."
    ),
    "pandas": (
        "Data Cleaning Toolkit",
        "Build reusable data-cleaning functions with quality reports."
    ),
    "power bi": (
        "Business KPI Dashboard",
        "Build an interactive dashboard with useful business metrics."
    ),
    "tableau": (
        "Interactive BI Dashboard",
        "Create a dashboard that communicates business trends."
    ),
    "natural language processing": (
        "Text Classification Explorer",
        "Train and evaluate a text classification model."
    ),
    "streamlit": (
        "Interactive Analytics App",
        "Build a Streamlit app with charts, validation, and documentation."
    ),
    "rest api": (
        "Documented REST API",
        "Create an API with validation, error handling, and tests."
    ),
    "generative ai": (
        "Grounded Q&A Assistant",
        "Build a document question-answering prototype with source references."
    ),
    "docker": (
        "Containerized Python Service",
        "Package a Python application and document its setup."
    ),
    "aws": (
        "Cloud Deployment Project",
        "Deploy a small application to AWS and document the architecture."
    ),
}


# --------------------------------------------------
# TEXT HELPERS
# --------------------------------------------------

def _normalize(text: str) -> str:
    """Normalize text for consistent matching."""
    text = (text or "").lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _contains_phrase(text: str, phrase: str) -> bool:
    """Find a phrase without matching it inside unrelated words."""
    pattern = (
        r"(?<![a-z0-9+#])"
        + re.escape(phrase.lower())
        + r"(?![a-z0-9+#])"
    )
    return re.search(pattern, text) is not None


# --------------------------------------------------
# SKILL EXTRACTION
# --------------------------------------------------

def find_skills(text: str) -> list[str]:
    """Return recognized skills using canonical names and aliases."""
    normalized = _normalize(text)
    found = []

    for canonical, aliases in SKILL_ALIASES.items():
        if any(_contains_phrase(normalized, alias) for alias in aliases):
            found.append(canonical)

    return sorted(set(found))


# --------------------------------------------------
# SKILL REQUIREMENT CLASSIFICATION
# --------------------------------------------------

def classify_job_skills(job_text: str) -> dict:
    """
    Estimate which skills appear in explicitly required or preferred
    sections of a job description.

    This is a rule-based estimate, not a guarantee of employer intent.
    """
    normalized = _normalize(job_text)
    all_skills = find_skills(normalized)

    required_markers = [
        "required qualifications",
        "minimum qualifications",
        "requirements",
        "required skills",
        "must have",
        "must-have",
        "you must have",
        "essential skills",
    ]

    preferred_markers = [
        "preferred qualifications",
        "preferred skills",
        "nice to have",
        "nice-to-have",
        "bonus points",
        "desired qualifications",
        "bonus skills",
    ]

    required_section = ""
    preferred_section = ""

    required_positions = [
        normalized.find(marker)
        for marker in required_markers
        if normalized.find(marker) >= 0
    ]

    preferred_positions = [
        normalized.find(marker)
        for marker in preferred_markers
        if normalized.find(marker) >= 0
    ]

    if required_positions:
        start = min(required_positions)
        next_positions = [
            p for p in preferred_positions if p > start
        ]
        end = min(next_positions) if next_positions else len(normalized)
        required_section = normalized[start:end]

    if preferred_positions:
        start = min(preferred_positions)
        preferred_section = normalized[start:]

    required_skills = set(find_skills(required_section))
    preferred_skills = set(find_skills(preferred_section))

    # Skills can appear in both sections if the description is ambiguous.
    preferred_skills -= required_skills

    return {
        "all_skills": all_skills,
        "required_skills": sorted(required_skills),
        "preferred_skills": sorted(preferred_skills),
        "requirement_sections_found": bool(
            required_positions or preferred_positions
        ),
    }


# --------------------------------------------------
# MATCH ANALYSIS
# --------------------------------------------------

def analyze_match(resume_text: str, job_text: str) -> dict:
    """
    Calculate text similarity and skill coverage.

    The overall score is a heuristic alignment indicator, not a hiring
    probability. Existing result keys are preserved for app.py.
    """
    resume = _normalize(resume_text)
    job = _normalize(job_text)

    # 1. Text similarity
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=12000,
    )

    try:
        matrix = vectorizer.fit_transform([resume, job])
        similarity = (
            float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
            * 100
        )
    except ValueError:
        similarity = 0.0

    # 2. Skills
    resume_skills = find_skills(resume_text)
    job_analysis = classify_job_skills(job_text)
    job_skills = job_analysis["all_skills"]

    resume_set = set(resume_skills)
    job_set = set(job_skills)

    matched = sorted(resume_set & job_set)
    missing = sorted(job_set - resume_set)

    coverage = (
        len(matched) / len(job_set) * 100
        if job_set
        else 0.0
    )

    # 3. Skill coverage for explicitly marked sections
    required_skills = job_analysis["required_skills"]
    preferred_skills = job_analysis["preferred_skills"]

    missing_required = sorted(set(required_skills) - resume_set)
    missing_preferred = sorted(set(preferred_skills) - resume_set)

    required_coverage = (
        (
            len(set(required_skills) & resume_set)
            / len(set(required_skills))
        ) * 100
        if required_skills
        else None
    )

    preferred_coverage = (
        (
            len(set(preferred_skills) & resume_set)
            / len(set(preferred_skills))
        ) * 100
        if preferred_skills
        else None
    )

    # 4. Overall score, preserving the original weighting
    overall = round(0.60 * similarity + 0.40 * coverage)

    # 5. Recommendations
    recommendations = []

    if missing_required:
        recommendations.append(
            "Review the potentially missing required skills: "
            + ", ".join(missing_required)
            + ". Learn and demonstrate these skills if they are genuinely "
              "relevant to your experience."
        )

    if missing_preferred:
        recommendations.append(
            "Consider developing these preferred skills when they align "
            "with your career goals: "
            + ", ".join(missing_preferred)
            + "."
        )

    if missing and not missing_required and not missing_preferred:
        recommendations.append(
            "Review the missing listed skills and identify which are "
            "actually important for the role."
        )

    if similarity < 25:
        recommendations.append(
            "Make your resume more relevant by clearly describing "
            "your role, technical approach, and project outcomes."
        )

    if len((resume_text or "").split()) < 180:
        recommendations.append(
            "Consider adding relevant project details, certifications, "
            "and measurable outcomes where they strengthen your application."
        )

    if not recommendations:
        recommendations.append(
            "Review the job description for domain knowledge, experience "
            "level, and responsibilities that a skill scan may not capture."
        )

    recommendations.append(
        "Only include skills and accomplishments you can honestly "
        "demonstrate and explain in an interview."
    )

    return {
        # Original keys used by app.py
        "overall_score": max(0, min(100, overall)),
        "text_similarity": round(similarity),
        "skill_coverage": round(coverage),
        "resume_skills": resume_skills,
        "job_skills": job_skills,
        "matched_skills": matched,
        "missing_skills": missing,
        "recommendations": recommendations,

        # New analysis fields
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "missing_required_skills": missing_required,
        "missing_preferred_skills": missing_preferred,
        "required_skill_coverage": (
            round(required_coverage)
            if required_coverage is not None
            else None
        ),
        "preferred_skill_coverage": (
            round(preferred_coverage)
            if preferred_coverage is not None
            else None
        ),
        "requirement_sections_found": (
            job_analysis["requirement_sections_found"]
        ),
        "scoring_method": (
            "60% TF-IDF text similarity + 40% recognized skill coverage"
        ),
    }


# --------------------------------------------------
# PROJECT RECOMMENDATIONS
# --------------------------------------------------

def suggest_projects(missing_skills: list[str]) -> list[dict]:
    result = []
    seen = set()

    for skill in missing_skills:
        key = skill.lower()

        if key in PROJECTS:
            title, description = PROJECTS[key]

            if title not in seen:
                result.append({
                    "title": title,
                    "description": description,
                })
                seen.add(title)

        if len(result) >= 4:
            break

    if not result:
        result.append({
            "title": "Role-Relevant Portfolio Case Study",
            "description": (
                "Choose a realistic problem related to the role, define "
                "success metrics, and publish a documented solution "
                "with tests."
            ),
        })

    return result


# --------------------------------------------------
# INTERVIEW QUESTIONS
# --------------------------------------------------

def generate_interview_questions(
    job_title: str,
    matched: list[str],
    missing: list[str],
) -> list[str]:
    role = job_title.strip() or "this role"

    questions = [
        f"Walk me through a project that demonstrates your fit for {role}.",
        (
            "Describe a technical problem you encountered, "
            "how you investigated it, and what you learned."
        ),
    ]

    if matched:
        questions.append(
            f"How have you used {matched[0]} in a practical project?"
        )

    if missing:
        questions.append(
            f"This role mentions {missing[0]}. "
            "How would you develop practical experience with it?"
        )

    questions.append(
        "How would you test your solution and explain its limitations?"
    )

    return questions[:5]