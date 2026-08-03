import re
import html


def sanitize_input(text):
    """
    Sanitize HTML input text to prevent Cross-Site Scripting (XSS).
    Escapes special HTML tags and strips dangerous characters.
    """
    if not text:
        return ""
    clean = str(text).strip()
    return html.escape(clean)


def check_password_strength(password):
    """
    Check strength of a password string.
    Returns dict with score (0-100), label ('Weak', 'Medium', 'Strong'), and requirements list.
    """
    if not password:
        return {"score": 0, "label": "Weak", "message": "Password cannot be empty"}

    score = 0
    feedback = []

    if len(password) >= 8:
        score += 30
    else:
        feedback.append("At least 8 characters long")

    if re.search(r"[A-Z]", password):
        score += 20
    else:
        feedback.append("Include uppercase letter")

    if re.search(r"[a-z]", password):
        score += 20
    else:
        feedback.append("Include lowercase letter")

    if re.search(r"[0-9]", password):
        score += 15
    else:
        feedback.append("Include at least one number")

    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        score += 15
    else:
        feedback.append("Include at least one special character")

    label = "Weak"
    if score >= 80:
        label = "Strong"
    elif score >= 50:
        label = "Medium"

    return {
        "score": score,
        "label": label,
        "feedback": feedback
    }


def format_platform_name(name):
    """
    Return clean capitalized platform name.
    """
    mapping = {
        "github": "GitHub",
        "linkedin": "LinkedIn",
        "leetcode": "LeetCode",
        "hackerrank": "HackerRank"
    }
    return mapping.get(str(name).lower(), str(name).capitalize())
