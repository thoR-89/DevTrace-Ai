import os
from dotenv import load_dotenv


load_dotenv()


class Config:

    SECRET_KEY = os.getenv("SECRET_KEY")
    MONGO_URI = os.getenv("MONGO_URI")
    DATABASE_NAME = os.getenv("DATABASE_NAME")
    SERPAPI_KEY = os.getenv("SERPAPI_KEY")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")