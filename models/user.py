import re
import sys
import bcrypt
from datetime import datetime
from database.mongodb import users_collection


def is_valid_email(email):
    """
    Validate email address format using regular expressions.
    """
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, str(email).strip()))


def create_user(name, email, password):
    """
    Create a new user account with secure password hashing (stored as UTF-8 string).
    Returns (success: bool, message: str).
    """
    clean_name = str(name).strip()
    clean_email = str(email).strip().lower()

    if not clean_name:
        return False, "Full Name is required."

    if not is_valid_email(clean_email):
        return False, "Please enter a valid email address."

    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."

    # Check if user already exists
    existing_user = users_collection.find_one({"email": clean_email})
    if existing_user:
        return False, "An account with this email address already exists."

    # Generate salt and hash password
    hashed_bytes = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12))
    # CRITICAL FIX: Decode hashed_bytes to UTF-8 string to prevent PyMongo BSON binary type corruption
    hashed_password_str = hashed_bytes.decode("utf-8")

    user_document = {
        "name": clean_name,
        "email": clean_email,
        "password": hashed_password_str,
        "created_at": datetime.now(),
        "role": "user"
    }

    try:
        users_collection.insert_one(user_document)
        return True, "Account created successfully!"
    except Exception as e:
        print(f"[X] User Creation Error: {e}", file=sys.stderr)
        return False, "Database error creating user account."


def verify_user(email, password):
    """
    Verify user credentials against stored bcrypt password hash.
    Returns user document if valid, None if invalid.
    """
    clean_email = str(email).strip().lower()

    user = users_collection.find_one({"email": clean_email})
    if not user:
        return None

    stored_password = user.get("password")
    if not stored_password:
        return None

    # CRITICAL FIX: Handle stored_password if bytes or string safely
    if isinstance(stored_password, str):
        stored_bytes = stored_password.encode("utf-8")
    elif isinstance(stored_password, bytes):
        stored_bytes = stored_password
    else:
        stored_bytes = str(stored_password).encode("utf-8")

    try:
        if bcrypt.checkpw(password.encode("utf-8"), stored_bytes):
            return user
    except Exception as e:
        print(f"[X] Password Verification Error: {e}", file=sys.stderr)

    return None