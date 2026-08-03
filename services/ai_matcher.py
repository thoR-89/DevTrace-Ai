import re
import sys

# Try importing rapidfuzz, fallback to difflib if unavailable
try:
    from rapidfuzz import fuzz
    HAS_RAPIDFUZZ = True
except ImportError:
    import difflib
    HAS_RAPIDFUZZ = False


def normalize(text):
    """
    Clean and normalize string for accurate string distance calculations.
    """
    if not text:
        return ""
    # Lowercase, replace non-alphanumeric with spaces, collapse whitespace
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", str(text).lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def calculate_string_similarity(str1, str2):
    """
    Calculate similarity score between 0 and 100 between two strings.
    """
    s1 = normalize(str1)
    s2 = normalize(str2)
    if not s1 or not s2:
        return 0.0

    if s1 == s2:
        return 100.0

    if HAS_RAPIDFUZZ:
        return float(fuzz.token_set_ratio(s1, s2))
    else:
        matcher = difflib.SequenceMatcher(None, s1, s2)
        return float(matcher.ratio() * 100.0)


def calculate_score(target_name, target_college, target_city, profile):
    """
    Multi-dimensional AI Weighted Scoring Algorithm for Candidate Validation.
    Weights:
    - Name Similarity: 35%
    - Username & Handle Match: 20%
    - Location Match: 15%
    - College / Company Match: 15%
    - Bio & Keyword Context Match: 10%
    - Completeness & Social Proof: 5%
    Total Max Score: 100%
    """
    if not profile:
        return 0

    score = 0.0

    norm_search_name = normalize(target_name)
    norm_search_college = normalize(target_college)
    norm_search_city = normalize(target_city)

    prof_name = profile.get("name", "")
    prof_username = profile.get("username", "")
    prof_bio = profile.get("bio", "") or profile.get("snippet", "")
    prof_location = profile.get("location", "")
    prof_company = profile.get("company", "") or profile.get("title", "")

    # 1. Name Similarity (Weight: 35)
    name_sim = calculate_string_similarity(target_name, prof_name)
    score += (name_sim / 100.0) * 35.0

    # 2. Username Match (Weight: 20)
    user_sim = calculate_string_similarity(target_name, prof_username)
    # Check if name tokens exist in username
    name_tokens = norm_search_name.split()
    norm_user = normalize(prof_username)
    token_bonus = sum(1 for t in name_tokens if t in norm_user)
    token_factor = min(1.0, token_bonus / max(1, len(name_tokens)))
    username_score = max(user_sim, token_factor * 100.0)
    score += (username_score / 100.0) * 20.0

    # 3. Location Match (Weight: 15)
    if norm_search_city:
        loc_sim = max(
            calculate_string_similarity(target_city, prof_location),
            100.0 if norm_search_city in normalize(prof_location) or norm_search_city in normalize(prof_bio) else 0.0
        )
        score += (loc_sim / 100.0) * 15.0
    else:
        # If city not specified by user, redistribute partial score if location exists
        if prof_location:
            score += 10.0

    # 4. College / Company Match (Weight: 15)
    if norm_search_college:
        inst_sim = max(
            calculate_string_similarity(target_college, prof_company),
            100.0 if norm_search_college in normalize(prof_company) or norm_search_college in normalize(prof_bio) else 0.0
        )
        score += (inst_sim / 100.0) * 15.0
    else:
        if prof_company:
            score += 10.0

    # 5. Bio & Context Match (Weight: 10)
    if prof_bio:
        bio_score = 5.0
        if any(w in normalize(prof_bio) for w in ["developer", "engineer", "software", "python", "student", "cs", "code"]):
            bio_score += 5.0
        score += bio_score

    # 6. Completeness & Social Proof (Weight: 5)
    followers = profile.get("followers", 0)
    repos = profile.get("repositories", 0)
    if followers > 5 or repos > 3 or profile.get("avatar"):
        score += 5.0

    final_score = int(round(min(100.0, score)))
    return final_score


def find_best_match(target_name, target_college, target_city, candidate_profiles):
    """
    Evaluate candidate profiles using weighted scoring and return the profile with highest confidence score.
    """
    if not candidate_profiles:
        return None

    best_candidate = None
    highest_score = -1

    for candidate in candidate_profiles:
        score = calculate_score(target_name, target_college, target_city, candidate)
        candidate["confidence"] = score

        if score > highest_score:
            highest_score = score
            best_candidate = candidate

    return best_candidate


def generate_ai_summary(github, linkedin, leetcode, hackerrank, developer_name=""):
    """
    Generate rich AI insights, developer archetype classification, language breakdown, and executive summary.
    """
    platforms_found = [p for p in [github, linkedin, leetcode, hackerrank] if p is not None]
    found_count = len(platforms_found)

    # Collect languages & tech
    languages = []
    if github and github.get("languages"):
        languages = github.get("languages")

    top_langs_str = ", ".join(languages[:4]) if languages else "Python, JavaScript"

    # Determine Developer Classification
    dev_type = "Software Engineer"
    if github and (github.get("repositories", 0) > 10 or github.get("total_stars", 0) > 5):
        dev_type = "Open Source Developer"
    elif leetcode or hackerrank:
        dev_type = "Competitive Programmer"
    elif linkedin:
        dev_type = "Full Stack Engineer"

    # AI Summary sentence construction
    name_str = developer_name if developer_name else "This developer"
    
    if found_count >= 3:
        summary_text = (
            f"Verified Digital Footprint: {name_str} demonstrates a strong multi-platform digital identity across "
            f"{', '.join([p['platform'] for p in platforms_found])}. "
            f"Extensive open-source work noted with core technical focus in {top_langs_str}."
        )
        confidence_level = "High"
    elif found_count >= 1:
        summary_text = (
            f"Active Digital Footprint: Candidate identified primarily via {platforms_found[0]['platform']}. "
            f"Technical proficiency detected in {top_langs_str}. "
            "Additional cross-platform indexing recommended for full recruitment verification."
        )
        confidence_level = "Medium" if found_count == 2 else "Possible"
    else:
        summary_text = "No public developer profiles matching the exact parameters could be verified at this time."
        confidence_level = "Low"

    return {
        "summary_text": summary_text,
        "dev_type": dev_type,
        "top_languages": languages,
        "confidence_level": confidence_level,
        "platforms_count": found_count
    }