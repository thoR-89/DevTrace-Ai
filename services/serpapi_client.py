import sys
import requests
from config import Config


class SerpAPIClient:
    """
    Robust client wrapper for Google SerpAPI searches.
    Handles rate limits, timeouts, and error handling gracefully.
    """

    BASE_URL = "https://serpapi.com/search.json"

    def __init__(self):
        self.api_key = Config.SERPAPI_KEY

    def search(self, query, num_results=10):
        """
        Execute Google search via SerpAPI.
        Returns parsed JSON object or None on error.
        """
        if not self.api_key:
            print("[!] SerpAPI Key is missing in Config! Skipping Google SerpAPI search.", file=sys.stderr)
            return None

        params = {
            "engine": "google",
            "q": query,
            "api_key": self.api_key,
            "num": num_results
        }

        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=20
            )

            if response.status_code != 200:
                print(f"[!] SerpAPI Error [{response.status_code}]: {response.text[:200]}", file=sys.stderr)
                return None

            return response.json()

        except Exception as e:
            print(f"[X] SerpAPI Connection Error: {e}", file=sys.stderr)
            return None