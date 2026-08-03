import requests

from config import Config

GITHUB_USER_API = "https://api.github.com/users/{}"


def _headers():

    headers = {
        "Accept": "application/vnd.github+json"
    }

    if Config.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {Config.GITHUB_TOKEN}"

    return headers


def get_github_profile(username):

    try:

        response = requests.get(
            GITHUB_USER_API.format(username),
            headers=_headers(),
            timeout=15
        )

        if response.status_code != 200:

            print(
                f"GitHub Profile Error [{username}]: "
                f"status={response.status_code} body={response.text[:200]}"
            )

            return None

        data = response.json()

        return {

            "platform": "GitHub",

            "username": data.get("login", ""),

            "name": data.get("name", ""),

            "bio": data.get("bio", ""),

            "location": data.get("location", ""),

            "company": data.get("company", ""),

            "blog": data.get("blog", ""),

            "followers": data.get("followers", 0),

            "following": data.get("following", 0),

            "repositories": data.get("public_repos", 0),

            "avatar": data.get("avatar_url"),

            "profile": data.get("html_url")

        }

    except Exception as e:

        print("GitHub Detail Error:", e)

        return None


def search_by_username(username):

    return get_github_profile(username)