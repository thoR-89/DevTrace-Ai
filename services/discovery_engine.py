import sys
from services.github_search import search_github
from services.linkedin_search import search_linkedin
from services.leetcode_search import search_leetcode
from services.hackerrank_search import search_hackerrank


def discover_profiles(name, college="", city=""):
    """
    Central discovery engine orchestrating multi-platform candidate retrieval across:
    - GitHub (REST API + SerpAPI search)
    - LinkedIn (SerpAPI Google Search)
    - LeetCode (SerpAPI Google Search)
    - HackerRank (SerpAPI Google Search)
    Returns structured candidate profiles dictionary by platform.
    """
    print(f"[*] Initiating Discovery Engine for: '{name}' | College: '{college}' | City: '{city}'", file=sys.stderr)

    profiles = {
        "github": search_github(name, college, city),
        "linkedin": search_linkedin(name, college, city),
        "leetcode": search_leetcode(name, college, city),
        "hackerrank": search_hackerrank(name, college, city)
    }

    counts = {k: len(v) for k, v in profiles.items()}
    print(f"[*] Discovery Engine Summary: Candidates Found -> {counts}", file=sys.stderr)

    return profiles