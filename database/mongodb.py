"""
DevTrace AI — TinyDB Database Layer
Replaces MongoDB with a local file-based JSON database (TinyDB).
No server installation required. Data stored in db/devtrace.json
"""

import sys
import os
from datetime import datetime
from tinydb import TinyDB, Query, where
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

# ── Database file path ────────────────────────────────────────────────────────
DB_DIR  = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db")
DB_FILE = os.path.join(DB_DIR, "devtrace.json")

# Create db/ directory if it doesn't exist
os.makedirs(DB_DIR, exist_ok=True)

# ── Open TinyDB with caching middleware for performance ────────────────────────
try:
    _db = TinyDB(DB_FILE, storage=CachingMiddleware(JSONStorage), indent=2)
    users_table   = _db.table("users")
    history_table = _db.table("search_history")
    print("[+] TinyDB connected — local file database active.", file=sys.stderr)
except Exception as e:
    print(f"[X] TinyDB init error: {e}", file=sys.stderr)
    _db = None
    users_table   = None
    history_table = None


# ── Compatibility shims so existing code keeps working ────────────────────────
class _FakeCollection:
    """Minimal pymongo-compatible shim over TinyDB table."""

    def __init__(self, table):
        self._table = table

    def find_one(self, query_dict):
        if self._table is None:
            return None
        Q = Query()
        results = self._table.search(self._build_query(query_dict))
        return results[0] if results else None

    def insert_one(self, doc):
        if self._table is None:
            raise RuntimeError("Database not available")
        doc_id = self._table.insert(doc)

        class _InsertResult:
            inserted_id = str(doc_id)
        return _InsertResult()

    def delete_one(self, query_dict):
        if self._table is None:
            return _DeleteResult(0)
        Q = Query()
        ids = [item.doc_id for item in self._table.search(self._build_query(query_dict))]
        if ids:
            self._table.remove(doc_ids=[ids[0]])
            return _DeleteResult(1)
        return _DeleteResult(0)

    def count_documents(self, query_dict=None):
        if self._table is None:
            return 0
        if not query_dict:
            return len(self._table)
        return len(self._table.search(self._build_query(query_dict)))

    def find(self, query_dict=None):
        if self._table is None:
            return _Cursor([])
        if not query_dict:
            docs = self._table.all()
        else:
            docs = self._table.search(self._build_query(query_dict))
        # Attach doc_id as string "_id"
        for d in docs:
            d["_id"] = str(d.doc_id)
        return _Cursor(docs)

    def create_index(self, *args, **kwargs):
        pass  # Not needed for TinyDB

    def aggregate(self, pipeline):
        """Minimal aggregation support for analytics."""
        if self._table is None:
            return iter([])
        docs = self._table.all()
        # Supports only the simple group-by-None patterns used in get_analytics_stats
        result = {}
        for stage in pipeline:
            if "$group" in stage:
                group_spec = stage["$group"]
                out = {}
                for field, expr in group_spec.items():
                    if field == "_id":
                        continue
                    if isinstance(expr, dict):
                        op = list(expr.keys())[0]
                        val_spec = expr[op]
                        if op == "$avg" and isinstance(val_spec, str):
                            key = val_spec.lstrip("$")
                            vals = [d[key] for d in docs if key in d and d[key] is not None]
                            out[field] = sum(vals) / len(vals) if vals else None
                        elif op == "$sum" and isinstance(val_spec, dict):
                            # $cond-based sum
                            cond_args = val_spec.get("$cond", [])
                            count = 0
                            if isinstance(cond_args, list) and len(cond_args) == 3:
                                cond, if_true, if_false = cond_args
                                if isinstance(cond, dict) and "$gt" in cond:
                                    gt_args = cond["$gt"]
                                    if isinstance(gt_args, list) and len(gt_args) == 2:
                                        field_ref, threshold = gt_args
                                        if isinstance(field_ref, str) and field_ref.startswith("$"):
                                            fkey = field_ref.lstrip("$")
                                            count = sum(1 for d in docs if d.get(fkey) is not None)
                            out[field] = count
                result = out
        return iter([result]) if result else iter([])

    def _build_query(self, query_dict):
        """Convert a simple {key: value} dict to a TinyDB Query."""
        Q = Query()
        if not query_dict:
            return Q._id.exists()  # match all — unused path
        conditions = []
        for k, v in query_dict.items():
            conditions.append(Q[k] == v)
        if len(conditions) == 1:
            return conditions[0]
        result = conditions[0]
        for c in conditions[1:]:
            result = result & c
        return result


class _DeleteResult:
    def __init__(self, count):
        self.deleted_count = count


class _Cursor(list):
    """A list with .sort() and .limit() that return self (fluent API)."""

    def sort(self, key, direction=-1):
        try:
            self.sort_by = key
            reverse = direction == -1
            list.sort(self, key=lambda x: x.get(key) or "", reverse=reverse)
        except Exception:
            pass
        return self

    def limit(self, n):
        del self[n:]
        return self


# Expose as module-level vars so imports in models/ still work
users_collection  = _FakeCollection(users_table)
search_collection = _FakeCollection(history_table)


# ── Public API (same signatures as original mongodb.py) ──────────────────────

def check_connection():
    """Return True if the TinyDB file is accessible."""
    try:
        _ = len(users_table)
        return True
    except Exception as e:
        print(f"[X] TinyDB check failed: {e}", file=sys.stderr)
        return False


def get_database():
    return _db


def save_search_history(data):
    """Insert a search history document. Returns inserted id string or None."""
    try:
        data["created_at"] = datetime.now().isoformat()
        doc_id = history_table.insert(data)
        _db.storage.flush()
        return str(doc_id)
    except Exception as e:
        print(f"[X] Search History Save Error: {e}", file=sys.stderr)
        return None


def get_search_history(user_email=None, limit=50):
    """Fetch history entries for a user (or all if user_email is None)."""
    try:
        if user_email:
            Q = Query()
            docs = history_table.search(Q.user_email == user_email)
        else:
            docs = history_table.all()

        # Attach string _id and format date
        for d in docs:
            d["_id"] = str(d.doc_id)
            raw_date = d.get("created_at")
            if isinstance(raw_date, str):
                try:
                    dt = datetime.fromisoformat(raw_date)
                    d["formatted_date"] = dt.strftime("%b %d, %Y %I:%M %p")
                except Exception:
                    d["formatted_date"] = raw_date
            elif isinstance(raw_date, datetime):
                d["formatted_date"] = raw_date.strftime("%b %d, %Y %I:%M %p")
            else:
                d["formatted_date"] = "N/A"

        # Sort newest first
        docs.sort(key=lambda x: x.get("created_at") or "", reverse=True)
        return docs[:limit]
    except Exception as e:
        print(f"[X] Search History Fetch Error: {e}", file=sys.stderr)
        return []


def delete_search_history_item(history_id, user_email):
    """Delete a history item by its TinyDB doc_id."""
    try:
        doc_id = int(history_id)
        Q = Query()
        doc = history_table.get(doc_id=doc_id)
        if doc and doc.get("user_email") == user_email:
            history_table.remove(doc_ids=[doc_id])
            _db.storage.flush()
            return True
        return False
    except Exception as e:
        print(f"[X] Search History Delete Error: {e}", file=sys.stderr)
        return False


def get_analytics_stats():
    """Compute aggregated dashboard metrics from local TinyDB."""
    try:
        total_users   = len(users_table)
        total_searches = len(history_table)

        all_searches = history_table.all()
        confidences = [d["overall_confidence"] for d in all_searches
                       if "overall_confidence" in d and d["overall_confidence"] is not None]
        avg_confidence = round(sum(confidences) / len(confidences), 1) if confidences else 0.0

        github_count    = sum(1 for d in all_searches if d.get("github") is not None)
        linkedin_count  = sum(1 for d in all_searches if d.get("linkedin") is not None)
        leetcode_count  = sum(1 for d in all_searches if d.get("leetcode") is not None)
        hackerrank_count = sum(1 for d in all_searches if d.get("hackerrank") is not None)

        recent = get_search_history(limit=5)

        return {
            "total_users":    total_users,
            "total_searches": total_searches,
            "avg_confidence": avg_confidence,
            "platforms": {
                "github_count":    github_count,
                "linkedin_count":  linkedin_count,
                "leetcode_count":  leetcode_count,
                "hackerrank_count": hackerrank_count
            },
            "recent_searches": recent
        }
    except Exception as e:
        print(f"[X] Analytics Error: {e}", file=sys.stderr)
        return {
            "total_users": 0, "total_searches": 0, "avg_confidence": 0.0,
            "platforms": {"github_count": 0, "linkedin_count": 0,
                          "leetcode_count": 0, "hackerrank_count": 0},
            "recent_searches": []
        }


def setup_indexes():
    """No-op — TinyDB doesn't need indexes."""
    pass