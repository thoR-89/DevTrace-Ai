from database.mongodb import get_search_history, delete_search_history_item, search_collection
from bson.objectid import ObjectId


def fetch_user_history(user_email, limit=50):
    """
    Fetch history items specific to a user.
    """
    return get_search_history(user_email=user_email, limit=limit)


def remove_history_entry(history_id, user_email):
    """
    Remove a history entry belonging to a specific user.
    """
    return delete_search_history_item(history_id, user_email)


def get_history_by_id(history_id, user_email=None):
    """
    Fetch a single search history record by ID.
    """
    try:
        query = {"_id": ObjectId(history_id)}
        if user_email:
            query["user_email"] = user_email
            
        doc = search_collection.find_one(query)
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc
    except Exception:
        return None
