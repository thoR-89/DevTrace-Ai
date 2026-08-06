import importlib
from types import SimpleNamespace

import pytest


@pytest.fixture
def client():
    app_module = importlib.import_module("app")
    app_module.app.config.update(TESTING=True)
    with app_module.app.test_client() as client:
        yield client


def test_get_github_profile_falls_back_when_api_is_blocked(monkeypatch):
    import services.github_utils as github_utils

    class FakeResponse:
        def __init__(self, status_code=403, text="", json_data=None):
            self.status_code = status_code
            self._text = text
            self._json_data = json_data or {}

        def json(self):
            return self._json_data

        def text(self):
            return self._text

    def fake_get(url, headers=None, timeout=12, params=None):
        if url.endswith("/users/thoR-89"):
            return FakeResponse(status_code=403, text="")
        if url == "https://github.com/thoR-89":
            return FakeResponse(
                status_code=200,
                text="<html><head><meta property='og:title' content='thoR-89' /><meta property='og:description' content='Python developer' /></head><body></body></html>",
            )
        return FakeResponse(status_code=404, text="")

    monkeypatch.setattr(github_utils.requests, "get", fake_get)

    profile = github_utils.get_github_profile("thoR-89")

    assert profile is not None
    assert profile["username"] == "thoR-89"
    assert profile["profile"] == "https://github.com/thoR-89"
    assert profile["bio"] == "Python developer"


def test_route_keeps_discovered_github_profile_visible(client, monkeypatch):
    search_module = importlib.import_module("routes.search")

    monkeypatch.setattr(search_module, "search_by_username", lambda username: None)
    monkeypatch.setattr(
        search_module,
        "discover_profiles",
        lambda *args, **kwargs: {
            "github": [
                {
                    "platform": "GitHub",
                    "username": "octocat",
                    "name": "The Octocat",
                    "profile": "https://github.com/octocat",
                }
            ],
            "linkedin": [],
            "leetcode": [],
            "hackerrank": [],
        },
    )
    monkeypatch.setattr(search_module, "find_best_match", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        search_module,
        "generate_ai_summary",
        lambda *args, **kwargs: {"summary_text": "ok", "dev_type": "Developer", "top_languages": [], "confidence_level": "High", "platforms_count": 1},
    )
    monkeypatch.setattr(search_module, "save_search_history", lambda record: None)

    with client.session_transaction() as session:
        session["user"] = "tester@example.com"

    response = client.post(
        "/search",
        data={"name": "Alex Developer", "college": "", "company": "", "city": "", "github_username": ""},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"octocat" in response.data
    assert b"The Octocat" in response.data
