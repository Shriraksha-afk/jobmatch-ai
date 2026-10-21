from matcher import analyze_match, find_skills, suggest_projects

def test_find_skills_recognizes_common_skills():
    found = find_skills("I use Python, SQL, and Pandas for data analysis.")
    assert "python" in found
    assert "sql" in found
    assert "pandas" in found

def test_match_score_is_bounded():
    result = analyze_match(
        "Python SQL Pandas built a data analysis project and dashboard.",
        "Looking for Python SQL and Pandas skills for data analysis."
    )
    assert 0 <= result["overall_score"] <= 100
    assert result["matched_skills"]

def test_missing_skills_detected():
    result = analyze_match("Python and Pandas", "Python, SQL, Docker, and REST API experience required.")
    assert "sql" in result["missing_skills"]
    assert "docker" in result["missing_skills"]

def test_project_suggestions_not_empty():
    assert suggest_projects(["sql"])
