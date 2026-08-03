from services.github_search import search_github
from services.linkedin_search import search_linkedin
from services.leetcode_search import search_leetcode
from services.hackerrank_search import search_hackerrank


def discover_profiles(name, college="", city=""):

    profiles = {

        # GitHub API
        "github": search_github(name),

        # SerpAPI Searches
        "linkedin": search_linkedin(
            name,
            college,
            city
        ),

        "leetcode": search_leetcode(
            name,
            college,
            city
        ),

        "hackerrank": search_hackerrank(
            name,
            college,
            city
        )

    }

    return profiles