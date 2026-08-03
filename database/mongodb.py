import sys
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.objectid import ObjectId
from config import Config

# Initialize MongoDB Client
client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)

# Database Reference
db = client[Config.DATABASE_NAME]

# Collections
users_collection = db["users"]
search_collection = db["search_history"]


def setup_indexes():
    """
    Create MongoDB indexes for performance optimization and unique constraints.
    """
    try:
        # Unique email index for users
        users_collection.create_index([("email", ASCENDING)], unique=True)
        # Compound index for fast user-specific history lookup sorted by date
        search_collection.create_index([("user_email", ASCENDING), ("created_at", DESCENDING)])
        search_collection.create_index([("created_at", DESCENDING)])
    except Exception as e:
        print(f"[!] Index Creation Warning: {e}", file=sys.stderr)


# Run index setup on module load
setup_indexes()


def check_connection():
    """
    Ping MongoDB to verify active connection status.
    Returns True if connected, False otherwise.
    """
    try:
        client.admin.command("ping")
        return True
    except Exception as e:
        print(f"[X] MongoDB Ping Failed: {e}", file=sys.stderr)
        return False


def get_database():
    """
    Return active database instance.
    """
    return db


def save_search_history(data):
    """
    Save developer search query and results to MongoDB search_history collection.
    Associated with user_email for privacy and data isolation.
    """
    try:
        data["created_at"] = datetime.now()
        result = search_collection.insert_one(data)
        return str(result.inserted_id)
    except Exception as e:
        print(f"[X] Search History Save Error: {e}", file=sys.stderr)
        return None


def get_search_history(user_email=None, limit=50):
    """
    Fetch search history entries. If user_email is provided, return only that user's history.
    """
    try:
        query = {"user_email": user_email} if user_email else {}
        history_cursor = search_collection.find(query).sort("created_at", DESCENDING).limit(limit)
        
        history_list = []
        for item in history_cursor:
            item["_id"] = str(item["_id"])
            if isinstance(item.get("created_at"), datetime):
                item["formatted_date"] = item["created_at"].strftime("%b %d, %Y %I:%M %p")
            else:
                item["formatted_date"] = "N/A"
            history_list.append(item)
            
        return history_list
    except Exception as e:
        print(f"[X] Search History Fetch Error: {e}", file=sys.stderr)
        return []


def delete_search_history_item(history_id, user_email):
    """
    Delete a specific search history item belonging to a given user.
    """
    try:
        result = search_collection.delete_one({
            "_id": ObjectId(history_id),
            "user_email": user_email
        })
        return result.deleted_count > 0
    except Exception as e:
        print(f"[X] Search History Delete Error: {e}", file=sys.stderr)
        return False


def get_analytics_stats():
    """
    Compute system-wide aggregated metrics for the Admin Dashboard:
    - Total Users
    - Total Identity Searches
    - Average Confidence Score
    - Top Searched Languages / Technologies
    - Platform Found Coverage Count
    """
    try:
        total_users = users_collection.count_documents({})
        total_searches = search_collection.count_documents({})

        # Aggregate average confidence
        avg_pipeline = [
            {"$group": {"_id": None, "avg_confidence": {"$avg": "$overall_confidence"}}}
        ]
        avg_res = list(search_collection.aggregate(avg_pipeline))
        avg_confidence = round(avg_res[0]["avg_confidence"], 1) if avg_res and avg_res[0].get("avg_confidence") else 0.0

        # Platform count distribution
        platform_pipeline = [
            {"$group": {
                "_id": None,
                "github_count": {"$sum": {"$cond": [{"$gt": ["$github", None]}, 1, 0]}},
                "linkedin_count": {"$sum": {"$cond": [{"$gt": ["$linkedin", None]}, 1, 0]}},
                "leetcode_count": {"$sum": {"$cond": [{"$gt": ["$leetcode", None]}, 1, 0]}},
                "hackerrank_count": {"$sum": {"$cond": [{"$gt": ["$hackerrank", None]}, 1, 0]}}
            }}
        ]
        platform_res = list(search_collection.aggregate(platform_pipeline))
        platforms = platform_res[0] if platform_res else {
            "github_count": 0, "linkedin_count": 0, "leetcode_count": 0, "hackerrank_count": 0
        }
        if "_id" in platforms:
            del platforms["_id"]

        # Recent searches for dashboard preview
        recent = get_search_history(limit=5)

        return {
            "total_users": total_users,
            "total_searches": total_searches,
            "avg_confidence": avg_confidence,
            "platforms": platforms,
            "recent_searches": recent
        }
    except Exception as e:
        print(f"[X] Analytics Aggregation Error: {e}", file=sys.stderr)
        return {
            "total_users": 0,
            "total_searches": 0,
            "avg_confidence": 0.0,
            "platforms": {"github_count": 0, "linkedin_count": 0, "leetcode_count": 0, "hackerrank_count": 0},
            "recent_searches": []
        }