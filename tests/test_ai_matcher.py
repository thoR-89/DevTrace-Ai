from services.ai_matcher import calculate_score, find_best_match


def test_calculate_score_rewards_identity_metadata():
    profile = {
        "name": "Sunny Yadav",
        "username": "sunnyyadav",
        "bio": "Software engineer and Python developer from Nashik, studying at KK Wagh Institute",
        "location": "Nashik, India",
        "company": "KK Wagh Institute",
        "blog": "https://sunny.dev",
        "languages": ["Python", "JavaScript"],
        "topics": ["flask", "ai", "django"],
        "social_links": ["https://github.com/sunnyyadav", "https://linkedin.com/in/sunnyyadav"],
        "followers": 12,
        "repositories": 8,
    }

    score = calculate_score("Sunny Yadav", "KK Wagh Institute", "Nashik", profile)

    assert score >= 85


def test_find_best_match_prefers_profile_with_stronger_identity_evidence():
    profiles = [
        {
            "name": "Sunny Yadav",
            "username": "sunny_yadav",
            "bio": "Generic developer profile",
            "location": "Mumbai",
            "company": "",
            "blog": "",
            "languages": [],
            "topics": [],
            "social_links": [],
            "followers": 200,
            "repositories": 40,
        },
        {
            "name": "Sunny Yadav",
            "username": "sunnyyadav",
            "bio": "Python developer from Nashik, student at KK Wagh Institute",
            "location": "Nashik",
            "company": "KK Wagh Institute",
            "blog": "https://sunny.dev",
            "languages": ["Python"],
            "topics": ["flask", "ai"],
            "social_links": ["https://github.com/sunnyyadav"],
            "followers": 5,
            "repositories": 3,
        },
    ]

    best = find_best_match("Sunny Yadav", "KK Wagh Institute", "Nashik", profiles)

    assert best is not None
    assert best["username"] == "sunnyyadav"


def test_find_best_match_rejects_low_confidence_profiles():
    profiles = [
        {
            "name": "Alex Johnson",
            "username": "alexj",
            "bio": "Another developer",
            "location": "London",
            "company": "",
            "blog": "",
            "languages": [],
            "topics": [],
            "social_links": [],
            "followers": 2,
            "repositories": 1,
        }
    ]

    best = find_best_match("Sunny Yadav", "KK Wagh Institute", "Nashik", profiles, target_company="Microsoft")

    assert best is None
