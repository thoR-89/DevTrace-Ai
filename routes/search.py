from flask import Blueprint, render_template, request

from database.mongodb import save_search_history

from services.discovery_engine import discover_profiles
from services.ai_matcher import find_best_match
from services.github_utils import search_by_username


search = Blueprint("search", __name__)


@search.route("/search", methods=["POST"])
def search_developer():

    name = request.form.get("name", "").strip()
    college = request.form.get("college", "").strip()
    city = request.form.get("city", "").strip()

    github_username = request.form.get(
        "github_username",
        ""
    ).strip()

    github = None
    linkedin = None
    leetcode = None
    hackerrank = None

    # ----------------------------------
    # Search Mode 2
    # GitHub Username
    # ----------------------------------

    if github_username:

        github = search_by_username(
            github_username
        )

        if github:
            github["confidence"] = 100

        overall = 100 if github else 0
        platforms_found = 1 if github else 0

        save_search_history({

            "search_type": "GitHub Username",

            "name": github.get("name", github_username) if github else github_username,

            "college": "",

            "city": "",

            "github_username": github_username,

            "overall_confidence": overall,

            "platforms_found": platforms_found

        })

        return render_template(

            "result.html",

            name=github.get("name", github_username) if github else github_username,

            college="",

            city="",

            github=github,

            linkedin=None,

            leetcode=None,

            hackerrank=None,

            overall=overall,

            platforms_found=platforms_found

        )

    # ----------------------------------
    # Search Mode 1
    # Name + College + City
    # ----------------------------------

    if not name:

        return render_template(

            "result.html",

            error="Please enter a Name or GitHub Username.",

            name="",

            college="",

            city="",

            github=None,

            linkedin=None,

            leetcode=None,

            hackerrank=None,

            overall=0,

            platforms_found=0

        )

    profiles = discover_profiles(

        name,

        college,

        city

    )

    github = find_best_match(

        name,

        college,

        city,

        profiles.get("github", [])

    )

    linkedin = find_best_match(

        name,

        college,

        city,

        profiles.get("linkedin", [])

    )

    leetcode = find_best_match(

        name,

        college,

        city,

        profiles.get("leetcode", [])

    )

    hackerrank = find_best_match(

        name,

        college,

        city,

        profiles.get("hackerrank", [])

    )

    scores = []

    for profile in [

        github,

        linkedin,

        leetcode,

        hackerrank

    ]:

        if profile:

            scores.append(

                profile["confidence"]

            )

    overall = round(

        sum(scores) / len(scores)

    ) if scores else 0

    platforms_found = sum(

        profile is not None

        for profile in [

            github,

            linkedin,

            leetcode,

            hackerrank

        ]

    )

    save_search_history({

        "search_type": "Identity Search",

        "name": name,

        "college": college,

        "city": city,

        "overall_confidence": overall,

        "platforms_found": platforms_found

    })

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

        platforms_found=platforms_found

    )