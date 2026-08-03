from services.github_search import search_github

profiles = search_github("Sunny Yadav")

print("\n========== GitHub Profiles ==========\n")

for profile in profiles:

    print(profile)
    print("--------------------------------")