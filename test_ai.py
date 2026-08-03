from services.github_search import search_github
from services.ai_matcher import find_best_match

name = "Sunny Yadav"
college = "Your College"
city = "Your City"

profiles = search_github(name)

best = find_best_match(
    name,
    college,
    city,
    profiles
)

print(best)