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
    city = sanitize_input(request.form.get("city", ""))
    github_username = sanitize_input(request.form.get("github_username", ""))

    github = None
    linkedin = None
    leetcode = None
    hackerrank = None

    # ---------------------------------------------
    # Mode A: Direct GitHub Username Search
    # ---------------------------------------------
    if github_username:
        github = search_by_username(github_username)
        if github:
            github["confidence"] = 100
            name = github.get("name") or github_username

        overall = 100 if github else 0
        platforms_found = 1 if github else 0

        ai_insight = generate_ai_summary(github, None, None, None, developer_name=name)

        search_record = {
            "user_email": user_email,
            "search_type": "GitHub Username",
            "name": name,
            "college": college,
            "city": city,
            "github_username": github_username,
            "overall_confidence": overall,
            "platforms_found": platforms_found,
            "github": github,
            "linkedin": None,
            "leetcode": None,
            "hackerrank": None,
            "ai_summary": ai_insight
        }
        save_search_history(search_record)

        return render_template(
            "result.html",
            name=name,
            college=college,
            city=city,
            github_username=github_username,
            github=github,
            linkedin=None,
            leetcode=None,
            hackerrank=None,
            overall=overall,
            platforms_found=platforms_found,
            ai_summary=ai_insight
        )

    # ---------------------------------------------
    # Mode B: Multi-field AI Identity Search
    # ---------------------------------------------
    if not name:
        return render_template(
            "result.html",
            error="Please enter a Developer Name or GitHub Username.",
            name="",
            college="",
            city="",
            github=None,
            linkedin=None,
            leetcode=None,
            hackerrank=None,
            overall=0,
            platforms_found=0,
            ai_summary=None
        )

    # Trigger discovery engine across platforms
    candidates = discover_profiles(name, college, city)

    # Run AI Weighted Matcher for each platform
    github = find_best_match(name, college, city, candidates.get("github", []))
    linkedin = find_best_match(name, college, city, candidates.get("linkedin", []))
    leetcode = find_best_match(name, college, city, candidates.get("leetcode", []))
    hackerrank = find_best_match(name, college, city, candidates.get("hackerrank", []))

    # Calculate overall confidence score
    scores = [p["confidence"] for p in [github, linkedin, leetcode, hackerrank] if p is not None]
    overall = int(round(sum(scores) / len(scores))) if scores else 0
    platforms_found = len(scores)

    # Generate AI executive summary & insights
    ai_insight = generate_ai_summary(github, linkedin, leetcode, hackerrank, developer_name=name)

    # Save to user search history in MongoDB
    search_record = {
        "user_email": user_email,
        "search_type": "Identity Search",
        "name": name,
        "college": college,
        "city": city,
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
        name=name,
        college=college,
        city=city,
        github=github,
        linkedin=linkedin,
        leetcode=leetcode,
        hackerrank=hackerrank,
        overall=overall,
        platforms_found=platforms_found,
        ai_summary=ai_insight
    )