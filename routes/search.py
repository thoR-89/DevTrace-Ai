from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from database.mongodb import save_search_history
from services.discovery_engine import discover_profiles
from services.ai_matcher import find_best_match, generate_ai_summary
from services.github_utils import search_by_username
from utils.helpers import sanitize_input

search = Blueprint("search", __name__)


@search.route("/search", methods=["POST"])
def search_developer():
    """
    Process developer identity search across GitHub, LinkedIn, LeetCode, HackerRank.
    Supports both direct GitHub Username search and Multi-field Identity Search.
    """
    if "user" not in session:
        return redirect(url_for("auth.login"))

    user_email = session.get("user")

    name = sanitize_input(request.form.get("name", ""))
    college = sanitize_input(request.form.get("college", ""))
    company = sanitize_input(request.form.get("company", ""))
    city = sanitize_input(request.form.get("city", ""))
    github_username = sanitize_input(request.form.get("github_username", ""))

    github = None
    linkedin = None
    leetcode = None
    hackerrank = None

    github_profile = None
    if github_username:
        github_profile = search_by_username(github_username)
        if github_profile:
            github_profile["confidence"] = 100

    if not name and not github_username:
        return render_template(
            "result.html",
            error="Please enter a Developer Name or GitHub Username.",
            name="",
            college="",
            company="",
            city="",
            github=None,
            linkedin=None,
            leetcode=None,
            hackerrank=None,
            overall=0,
            platforms_found=0,
            ai_summary=None
        )

    search_name = name or (github_profile.get("name") if github_profile else "") or github_username
    search_college = college or ""
    search_company = company or (github_profile.get("company") if github_profile else "") or ""
    search_city = city or (github_profile.get("location") if github_profile else "") or ""

    candidates = discover_profiles(
        search_name,
        search_college,
        search_city,
        search_company,
        github_username=github_username,
    )

    github_candidates = candidates.get("github", []) or []
    if github_profile:
        github = github_profile
        github["confidence"] = 100
    elif github_candidates:
        github = dict(github_candidates[0])
        github["confidence"] = 100
    else:
        github = None

    linkedin = find_best_match(search_name, search_college, search_city, candidates.get("linkedin", []), target_company=search_company)
    leetcode = find_best_match(search_name, search_college, search_city, candidates.get("leetcode", []), target_company=search_company)
    hackerrank = find_best_match(search_name, search_college, search_city, candidates.get("hackerrank", []), target_company=search_company)

    scores = [p["confidence"] for p in [github, linkedin, leetcode, hackerrank] if p is not None]
    overall = int(round(sum(scores) / len(scores))) if scores else 0
    platforms_found = len(scores)

    ai_insight = generate_ai_summary(github, linkedin, leetcode, hackerrank, developer_name=name)

    search_record = {
        "user_email": user_email,
        "search_type": "Identity Search",
        "name": search_name,
        "college": search_college,
        "company": search_company,
        "city": search_city,
        "overall_confidence": overall,
        "platforms_found": platforms_found,
        "github": github,
        "linkedin": linkedin,
        "leetcode": leetcode,
        "hackerrank": hackerrank,
        "ai_summary": ai_insight
    }
    save_search_history(search_record)

    return render_template(
        "result.html",
        name=search_name,
        college=search_college,
        company=search_company,
        city=search_city,
        github=github,
        linkedin=linkedin,
        leetcode=leetcode,
        hackerrank=hackerrank,
        overall=overall,
        platforms_found=platforms_found,
        ai_summary=ai_insight
    )