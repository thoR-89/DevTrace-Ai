from database.mongodb import get_search_history, delete_search_history_item, history_table
from tinydb import Query


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
    Fetch a single search history record by TinyDB doc_id (integer).
    """
    try:
        doc_id = int(history_id)
        doc = history_table.get(doc_id=doc_id)
        if doc:
            if user_email and doc.get("user_email") != user_email:
                return None
            doc["_id"] = str(doc.doc_id)
            return doc
        return None
    except Exception:
        return None
