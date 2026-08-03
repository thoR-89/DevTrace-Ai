import re


def normalize(text):
    if not text:
        return ""

    return re.sub(r"\s+", " ", str(text).lower()).strip()


def calculate_score(name, college, city, profile):

    score = 0

    search_name = normalize(name)
    search_college = normalize(college)
    search_city = normalize(city)

    profile_name = normalize(profile.get("name", ""))
    username = normalize(profile.get("username", ""))
    bio = normalize(profile.get("bio", ""))
    location = normalize(profile.get("location", ""))
    company = normalize(profile.get("company", ""))
    blog = normalize(profile.get("blog", ""))

    # -----------------------------
    # Name Match (40)
    # -----------------------------
    if search_name:

        if search_name == profile_name:
            score += 40

        elif search_name in profile_name or profile_name in search_name:
            score += 30

        else:
            search_parts = search_name.split()
            matched = 0

            for part in search_parts:
                if part in profile_name:
                    matched += 1

            if matched > 0:
                score += min(matched * 10, 20)

    # -----------------------------
    # Username Match (20)
    # -----------------------------
    if search_name:

        for part in search_name.split():

            if part in username:
                score += 10

    # -----------------------------
    # College / Company Match (20)
    # -----------------------------
    if search_college:

        if (
            search_college in company
            or search_college in bio
        ):
            score += 20

    # -----------------------------
    # City Match (15)
    # -----------------------------
    if search_city:

        if (
            search_city in location
            or search_city in bio
        ):
            score += 15

    # -----------------------------
    # Bio Available (5)
    # -----------------------------
    if bio:
        score += 5

    # -----------------------------
    # Website Available (5)
    # -----------------------------
    if blog:
        score += 5

    # -----------------------------
    # Popular Account Bonus (5)
    # -----------------------------
    if profile.get("followers", 0) >= 10:
        score += 5

    return min(score, 100)


def find_best_match(name, college, city, profiles):

    if not profiles:
        return None

    best_profile = None
    highest_score = -1

    for profile in profiles:

        score = calculate_score(
            name,
            college,
            city,
            profile
        )

        profile["confidence"] = score

        if score > highest_score:
            highest_score = score
            best_profile = profile

    return best_profile