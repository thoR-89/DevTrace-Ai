from pymongo import MongoClient
from datetime import datetime
from config import Config


# MongoDB Client
client = MongoClient(Config.MONGO_URI)

# Database
db = client[Config.DATABASE_NAME]

# Collections
users_collection = db["users"]
search_collection = db["search_history"]


def check_connection():
    try:
        client.admin.command("ping")
        return True

    except Exception as e:
        print("MongoDB Error:", e)
        return False


def get_database():
    """
    Return database instance.
    """
    return db


def save_search_history(data):
    """
    Save developer search history.
    """

    try:

        data["created_at"] = datetime.now()

        search_collection.insert_one(data)

        return True

    except Exception as e:

        print("Search History Error:", e)

        return False


def get_search_history(limit=20):
    """
    Return latest search history.
    """

    try:

        history = list(
            search_collection
            .find({})
            .sort("created_at", -1)
            .limit(limit)
        )

        return history

    except Exception as e:

        print("History Fetch Error:", e)

        return []