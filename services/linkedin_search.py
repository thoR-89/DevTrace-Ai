from services.serpapi_client import SerpAPIClient

client = SerpAPIClient()


def search_linkedin(name, college="", city=""):

    query = f"{name} {college} {city} LinkedIn"

    data = client.search(query)

    if not data:
        return []

    profiles = []

    for result in data.get("organic_results", []):

        link = result.get("link", "")

        if "linkedin.com" not in link.lower():
            continue

        profiles.append({

            "platform": "LinkedIn",
            "title": result.get("title", ""),
            "link": link,
            "snippet": result.get("snippet", "")

        })

    return profiles