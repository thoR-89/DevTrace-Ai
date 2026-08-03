import requests
from config import Config


class SerpAPIClient:

    BASE_URL = "https://serpapi.com/search.json"

    def __init__(self):
        self.api_key = Config.SERPAPI_KEY

    def search(self, query):

        params = {
            "engine": "google",
            "q": query,
            "api_key": self.api_key,
            "num": 10
        }

        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=30
            )

            response.raise_for_status()

            return response.json()

        except Exception as e:
            print("SerpAPI Error:", e)
            return None