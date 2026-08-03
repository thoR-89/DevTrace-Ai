import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    DevTrace AI Application Configuration
    Centralized settings for Flask, MongoDB, External APIs, and Security.
    """

    # Secret Key for Session Encryption
    SECRET_KEY = os.getenv("SECRET_KEY", "devtrace_super_secret_ai_key_2026")

    # MongoDB Configuration
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "devtrace_ai")

    # External APIs
    SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

    # Flask Session & Security Settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = True
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max payload limit

    # AI & Search Limits
    MAX_GITHUB_CANDIDATES = 15
    SEARCH_CACHE_TIMEOUT = 3600  # 1 hour cache timeout in seconds