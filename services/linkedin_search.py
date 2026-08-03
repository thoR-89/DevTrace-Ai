import re
from services.serpapi_client import SerpAPIClient

client = SerpAPIClient()


def search_linkedin(name, college="", city=""):
    """
    Search LinkedIn candidate profiles using SerpAPI Google Search indexing.
    Extracts profile link, title headline, snippet description, and location cues.
    """
    clean_name = str(name).strip()
    if not clean_name:
        return []

    query_parts = [f'"{clean_name}"', "site:linkedin.com/in/"]
    if college:
        query_parts.append(f'"{college}"')
    if city:
        query_parts.append(f'"{city}"')

    query = " ".join(query_parts)
    data = client.search(query, num_results=10)

    if not data:
        return []

    profiles = []
    seen_links = set()

    for result in data.get("organic_results", []):
        link = result.get("link", "")
        clean_link = link.split("?")[0].rstrip("/")

        if "linkedin.com/in/" not in clean_link.lower() or clean_link in seen_links:
            continue

        seen_links.add(clean_link)
        title = result.get("title", "").replace(" - LinkedIn", "").replace(" | LinkedIn", "")
        snippet = result.get("snippet", "")

        # Extract handle from link
        match = re.search(r"linkedin\.com/in/([a-zA-Z0-9_-]+)", clean_link)
        username = match.group(1) if match else clean_name.lower().replace(" ", "")

        profiles.append({
            "platform": "LinkedIn",
            "name": clean_name,
            "username": username,
            "title": title,
            "link": clean_link,
            "snippet": snippet,
            "bio": snippet
        })

    return profiles