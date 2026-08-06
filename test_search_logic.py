from services.discovery_engine import discover_profiles


def test_discovery_engine_passes_github_username_to_github_search(monkeypatch):
    captured = {}

    def fake_search_github(name, college="", city="", company="", github_username=""):
        captured['name'] = name
        captured['college'] = college
        captured['city'] = city
        captured['company'] = company
        captured['github_username'] = github_username
        return [{"platform": "GitHub", "username": github_username}]

    monkeypatch.setattr("services.discovery_engine.search_github", fake_search_github)
    monkeypatch.setattr("services.discovery_engine.search_linkedin", lambda *args, **kwargs: [])
    monkeypatch.setattr("services.discovery_engine.search_leetcode", lambda *args, **kwargs: [])
    monkeypatch.setattr("services.discovery_engine.search_hackerrank", lambda *args, **kwargs: [])

    profiles = discover_profiles(
        "Ada Lovelace",
        college="King's College",
        city="London",
        company="Babbage Ltd",
        github_username="ada",
    )

    assert profiles["github"][0]["username"] == "ada"
    assert captured["github_username"] == "ada"
    assert captured["name"] == "Ada Lovelace"
    assert captured["college"] == "King's College"
    assert captured["city"] == "London"
    assert captured["company"] == "Babbage Ltd"
