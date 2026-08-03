import sys
import requests
from config import Config

GITHUB_USER_API = "https://api.github.com/users/{}"
GITHUB_REPOS_API = "https://api.github.com/users/{}/repos"


def _headers():
    """
    Get HTTP headers for GitHub API requests, incorporating Authorization Bearer token if available.
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "DevTrace-AI-Identity-Engine"
    }

    if Config.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {Config.GITHUB_TOKEN}"

    return headers


def get_github_profile(username):
    """
    Fetch comprehensive GitHub user profile metrics, repositories, language breakdown, and top projects.
    """
    clean_username = str(username).strip()
    if not clean_username:
        return None

    try:
        # Fetch User Object
        res = requests.get(
            GITHUB_USER_API.format(clean_username),
            headers=_headers(),
            timeout=12
        )

        if res.status_code != 200:
            print(f"[!] GitHub Profile Fetch Warning [{clean_username}]: HTTP {res.status_code}", file=sys.stderr)
            return None

        data = res.json()

        # Fetch Public Repositories for Languages & Stars calculation
        languages_count = {}
        total_stars = 0
        top_projects = []

        try:
            repos_res = requests.get(
                GITHUB_REPOS_API.format(clean_username),
                headers=_headers(),
                params={"sort": "updated", "per_page": 30},
                timeout=12
            )

            if repos_res.status_code == 200:
                repos = repos_res.json()
                for r in repos:
                    if r.get("fork"):
                        continue  # Skip forked repos for accurate stats

                    lang = r.get("language")
                    if lang:
                        languages_count[lang] = languages_count.get(lang, 0) + 1

                    stars = r.get("stargazers_count", 0)
                    total_stars += stars

                    # Collect top projects based on stars and description
                    top_projects.append({
                        "name": r.get("name"),
                        "description": r.get("description") or "No description provided",
                        "stars": stars,
                        "forks": r.get("forks_count", 0),
                        "language": lang or "Other",
                        "url": r.get("html_url")
                    })

                # Sort projects by star count
                top_projects.sort(key=lambda x: x["stars"], reverse=True)
                top_projects = top_projects[:5]  # Keep top 5

        except Exception as e:
            print(f"[!] GitHub Repos Fetch Exception [{clean_username}]: {e}", file=sys.stderr)

        # Sort programming languages by frequency
        sorted_languages = sorted(languages_count.items(), key=lambda item: item[1], reverse=True)
        top_languages = [lang[0] for lang in sorted_languages[:6]]

        return {
            "platform": "GitHub",
            "username": data.get("login", clean_username),
            "name": data.get("name", "") or clean_username,
            "bio": data.get("bio", "") or "",
            "location": data.get("location", "") or "",
            "company": data.get("company", "") or "",
            "blog": data.get("blog", "") or "",
            "email": data.get("email", "") or "",
            "followers": data.get("followers", 0),
            "following": data.get("following", 0),
            "repositories": data.get("public_repos", 0),
            "total_stars": total_stars,
            "languages": top_languages,
            "language_counts": languages_count,
            "top_projects": top_projects,
            "avatar": data.get("avatar_url"),
            "profile": data.get("html_url"),
            "created_at": data.get("created_at", "")[:10]
        }

    except Exception as e:
        print(f"[X] GitHub Detail Error [{clean_username}]: {e}", file=sys.stderr)
        return None


def search_by_username(username):
    """
    Direct lookup of a developer by exact GitHub Username.
    """
    return get_github_profile(username)