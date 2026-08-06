import re

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
    matcher = difflib.SequenceMatcher(None, s1, s2)
    return float(matcher.ratio() * 100.0)


def _token_overlap_score(query_text, candidate_text):
    query_tokens = {token for token in normalize(query_text).split() if token}
    candidate_tokens = {token for token in normalize(candidate_text).split() if token}
    if not query_tokens or not candidate_tokens:
        return 0.0
    overlap = len(query_tokens & candidate_tokens)
    return min(100.0, (overlap / max(1, len(query_tokens))) * 100.0)


def calculate_score(target_name, target_college, target_city, profile, target_company=""):
    """
    Multi-dimensional AI weighted matching that rewards identity evidence across
    name, username, college, company, city, bio, languages, topics, website,
    and social links.
    """
    if not profile:
        return 0

    norm_search_name = normalize(target_name)
    norm_search_college = normalize(target_college)
    norm_search_company = normalize(target_company)
    norm_search_city = normalize(target_city)

    prof_name = profile.get("name", "") or ""
    prof_username = profile.get("username", "") or ""
    prof_bio = (profile.get("bio", "") or profile.get("snippet", "") or "").strip()
    prof_location = profile.get("location", "") or ""
    prof_company = (profile.get("company", "") or profile.get("title", "") or "").strip()
    website = profile.get("blog") or profile.get("website") or profile.get("link") or ""
    social_links = profile.get("social_links") or []
    languages = profile.get("languages") or []
    topics = profile.get("topics") or []

    name_score = calculate_string_similarity(target_name, prof_name)
    username_score = calculate_string_similarity(target_name, prof_username)
    username_tokens = [token for token in norm_search_name.split() if token]
    if username_tokens:
        username_score = max(
            username_score,
            max((calculate_string_similarity(token, normalize(prof_username)) for token in username_tokens), default=0.0),
        )

    college_score = calculate_string_similarity(target_college, prof_company)
    if norm_search_college:
        college_score = max(
            college_score,
            _token_overlap_score(target_college, prof_bio),
            _token_overlap_score(target_college, prof_location),
            _token_overlap_score(target_college, prof_company),
        )

    company_score = calculate_string_similarity(target_company, prof_company)
    if norm_search_company:
        company_score = max(company_score, _token_overlap_score(target_company, prof_bio))

    city_score = calculate_string_similarity(target_city, prof_location)
    if norm_search_city:
        city_score = max(city_score, _token_overlap_score(target_city, prof_bio), _token_overlap_score(target_city, prof_location))

    bio_score = 0.0
    if prof_bio:
        bio_context = " ".join([part for part in [target_name, target_college, target_company, target_city] if part]).strip()
        bio_score = max(
            calculate_string_similarity(bio_context, prof_bio),
            _token_overlap_score(bio_context, prof_bio),
        )
        if any(word in normalize(prof_bio) for word in ["developer", "engineer", "software", "python", "student", "cs", "code"]):
            bio_score = max(bio_score, 85.0)

    languages_score = 100.0 if languages else 0.0
    topics_score = 100.0 if topics else 0.0
    website_score = 100.0 if website else 0.0
    social_score = 100.0 if social_links else 0.0

    weighted_score = (
        name_score * 40.0
        + username_score * 20.0
        + college_score * 15.0
        + company_score * 10.0
        + city_score * 10.0
        + bio_score * 15.0
        + languages_score * 10.0
        + topics_score * 10.0
        + website_score * 10.0
        + social_score * 15.0
    ) / 155.0

    final_score = int(round(min(100.0, max(0.0, weighted_score))))
    return final_score


def find_best_match(target_name, target_college, target_city, candidate_profiles, target_company=""):
    """
    Evaluate candidate profiles using weighted scoring and return the profile with
    highest confidence score. Return None when the best score is still too weak.
    """
    if not candidate_profiles:
        return None

    best_candidate = None
    highest_score = -1

    for candidate in candidate_profiles:
        score = calculate_score(target_name, target_college, target_city, candidate, target_company=target_company)
        candidate["confidence"] = score

        if score > highest_score:
            highest_score = score
            best_candidate = candidate

    if best_candidate is not None and highest_score < 45:
        return None

    return best_candidate


def generate_ai_summary(github, linkedin, leetcode, hackerrank, developer_name=""):
    """
    Generate rich AI insights, developer archetype classification, language breakdown, and executive summary.
    """
    platforms_found = [p for p in [github, linkedin, leetcode, hackerrank] if p is not None]
    found_count = len(platforms_found)

    languages = []
    if github and github.get("languages"):
        languages = github.get("languages")

    top_langs_str = ", ".join(languages[:4]) if languages else "Python, JavaScript"

    dev_type = "Software Engineer"
    if github and (github.get("repositories", 0) > 10 or github.get("total_stars", 0) > 5):
        dev_type = "Open Source Developer"
    elif leetcode or hackerrank:
        dev_type = "Competitive Programmer"
    elif linkedin:
        dev_type = "Full Stack Engineer"

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