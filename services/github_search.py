import sys
import re
import requests
from config import Config
from services.serpapi_client import SerpAPIClient
from services.github_utils import get_github_profile, _headers

GITHUB_SEARCH_API = "https://api.github.com/search/users"


def extract_username(url):
    """
    Extract clean GitHub username from profile or repository URLs.
    """
    if not url:
        return None
    match = re.search(r"github\.com/([a-zA-Z0-9_-]+)", url)
    if match:
        username = match.group(1).strip()
        if username.lower() not in ["features", "topics", "collections", "trending", "pricing", "login", "signup", "about"]:
            return username
    return None


def search_github(name, college="", city="", company="", github_username=""):
    """
    Search GitHub using the GitHub username only when provided.
    If no username is provided, fall back to a name-based search.
    """
    profiles = []
    seen_usernames = set()

    clean_name = str(name).strip()
    clean_username = str(github_username or "").strip()

    if clean_username:
        profile = get_github_profile(clean_username)
        if profile:
            profiles.append(profile)
        return profiles

    if not clean_name:
        return profiles

    try:
        search_terms = [clean_name, company, college, city]
        enriched_terms = [part for part in search_terms if part]
        search_queries = [
            f"{clean_name} in:name",
            " ".join(enriched_terms),
            f"{clean_name} developer {' '.join(enriched_terms[1:])}".strip(),
            f"{clean_name} software engineer {' '.join(enriched_terms[1:])}".strip(),
        ]

        for q in search_queries:
            if len(seen_usernames) >= Config.MAX_GITHUB_CANDIDATES:
                break
            response = requests.get(
                GITHUB_SEARCH_API,
                params={"q": q, "per_page": 10},
                headers=_headers(),
                timeout=10,
            )

            if response.status_code == 200:
                items = response.json().get("items", [])
                for user in items:
                    username = user.get("login")
                    if username and username not in seen_usernames:
                        seen_usernames.add(username)
                        prof = get_github_profile(username)
                        if prof:
                            profiles.append(prof)
            else:
                print(f"[!] GitHub Search API HTTP {response.status_code} for query '{q}'", file=sys.stderr)

    except Exception as e:
        print(f"[!] GitHub Search API Exception: {e}", file=sys.stderr)

    if len(profiles) < 3 and Config.SERPAPI_KEY:
        try:
            serp = SerpAPIClient()
            google_query = " ".join(filter(None, [f'"{clean_name}"', company, college, city, "site:github.com"])).strip()
            result = serp.search(google_query, num_results=10)

            if result:
                for item in result.get("organic_results", []):
                    link = item.get("link", "")
                    username = extract_username(link)
                    if username and username not in seen_usernames:
                        seen_usernames.add(username)
                        prof = get_github_profile(username)
                        if prof:
                            profiles.append(prof)

        except Exception as e:
            print(f"[!] GitHub SerpAPI Search Exception: {e}", file=sys.stderr)

    return profiles