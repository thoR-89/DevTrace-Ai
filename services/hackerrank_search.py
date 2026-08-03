import re
from services.serpapi_client import SerpAPIClient

client = SerpAPIClient()


def search_hackerrank(name, college="", city=""):
    """
    Search HackerRank candidate profiles using SerpAPI Google Search indexing.
    Extracts HackerRank handle, title, snippet information.
    """
    clean_name = str(name).strip()
    if not clean_name:
        return []

    query = f'"{clean_name}" site:hackerrank.com/profile/ OR site:hackerrank.com/'.strip()
    data = client.search(query, num_results=10)

    if not data:
        return []

    profiles = []
    seen_links = set()

    for result in data.get("organic_results", []):
        link = result.get("link", "")
        clean_link = link.split("?")[0].rstrip("/")

        if "hackerrank.com" not in clean_link.lower() or clean_link in seen_links:
            continue

        # Skip non-profile pages like /challenges/ or /domains/
        if any(x in clean_link.lower() for x in ["/challenges/", "/domains/", "/dashboard", "/skills/"]):
            continue

        seen_links.add(clean_link)
        title = result.get("title", "").replace(" - HackerRank", "").replace(" | HackerRank", "")
        snippet = result.get("snippet", "")

        # Extract handle
        match = re.search(r"hackerrank\.com/(?:profile/)?([a-zA-Z0-9_-]+)", clean_link)
        username = match.group(1) if match else clean_name.lower().replace(" ", "")

        profiles.append({
            "platform": "HackerRank",
            "name": title if title else clean_name,
            "username": username,
            "title": title,
            "link": clean_link,
            "snippet": snippet,
            "bio": snippet
        })

    return profiles