import requests
import re

from config import Config
from services.serpapi_client import SerpAPIClient
from services.github_utils import get_github_profile

GITHUB_SEARCH_API = "https://api.github.com/search/users"


def _headers():

    headers = {
        "Accept": "application/vnd.github+json"
    }

    if Config.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {Config.GITHUB_TOKEN}"

    return headers


def extract_username(url):

    match = re.search(r"github\.com/([^/?#]+)", url)

    if match:
        return match.group(1)

    return None


def search_github(name, college="", city=""):

    profiles = []

    usernames = set()

    # -------------------------------
    # Part 1 : GitHub Search API
    # -------------------------------

    try:

        response = requests.get(
            GITHUB_SEARCH_API,
            params={
                # "in:name" tells GitHub to match the profile's display
                # name, not just the username/login. Without this the
                # search almost always returns nothing for a real name.
                "q": f"{name} in:name",
                "per_page": 30
            },
            headers=_headers(),
            timeout=15
        )

        if response.status_code != 200:

            print(
                f"GitHub Search API Error: status={response.status_code} "
                f"body={response.text[:300]}"
            )

        else:

            users = response.json().get("items", [])

            print(f"GitHub Search API: {len(users)} candidate(s) found for '{name}'")

            for user in users:

                username = user["login"]

                if username in usernames:
                    continue

                profile = get_github_profile(username)

                if profile:

                    profiles.append(profile)

                    usernames.add(username)

    except Exception as e:

        print("GitHub Search Error:", e)

    # -------------------------------
    # Part 2 : SerpAPI Search
    # -------------------------------

    try:

        serp = SerpAPIClient()

        queries = [

            f'site:github.com "{name}"',

            f'site:github.com "{name}" {city}',

            f'site:github.com "{name}" "{college}"',

            f'site:github.com "{name}" developer',

            f'site:github.com "{name}" python',

            f'site:github.com "{name}" github',

            f'site:github.com "{name}" computer science',

            f'site:github.com "{name}" student'
        ]

        for query in queries:
            print("\n===================================")
            print("Searching:", query)
            print("===================================")
            result = serp.search(query)
            if not result:
                continue
            print("Results Found:", len(result.get("organic_results", [])))

            if not result:
                continue

            for item in result.get("organic_results", []):
                print(item.get("title"))
                print(item.get("link"))
                print("----------------")

                username = extract_username(item.get("link", ""))

                if not username:
                    continue

                if username in usernames:
                    continue

                profile = get_github_profile(username)

                if profile:

                    profiles.append(profile)

                    usernames.add(username)

    except Exception as e:

        print("SerpAPI GitHub Error:", e)

    return profiles