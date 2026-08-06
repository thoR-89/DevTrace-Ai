import sys
from services.github_search import search_github
from services.linkedin_search import search_linkedin
from services.leetcode_search import search_leetcode
from services.hackerrank_search import search_hackerrank


def discover_profiles(name, college="", city="", company="", github_username=""):
    """
    Central discovery engine orchestrating multi-platform candidate retrieval across:
    - GitHub uses the provided GitHub username only
    - LinkedIn/LeetCode/HackerRank use the developer identity fields only
    Returns structured candidate profiles dictionary by platform.
    """
    print(
        f"[*] Initiating Discovery Engine for: '{name}' | College: '{college}' | Company: '{company}' | City: '{city}' | GitHub Username: '{github_username}'",
        file=sys.stderr,
    )

    profiles = {
        "github": search_github(name, college, city, company, github_username=github_username),
        "linkedin": search_linkedin(name, college, city, company),
        "leetcode": search_leetcode(name, college, city, company),
        "hackerrank": search_hackerrank(name, college, city, company),
    }

    counts = {k: len(v) for k, v in profiles.items()}
    print(f"[*] Discovery Engine Summary: Candidates Found -> {counts}", file=sys.stderr)

    return profiles