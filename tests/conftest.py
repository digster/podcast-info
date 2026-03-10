"""Shared fixtures for fetch-podcast tests."""

import pytest


@pytest.fixture
def sample_show():
    """A single cleaned show dict matching spotify-client's clean_show() output."""
    return {
        "id": "4gL14b92xAErofYQA7bU4e",
        "name": "Theories of Everything with Curt Jaimungal",
        "publisher": "Curt Jaimungal",
        "description": "A podcast about physics and consciousness.",
        "total_episodes": 347,
        "languages": ["en"],
        "explicit": False,
        "image_url": "https://i.scdn.co/image/example",
        "uri": "spotify:show:4gL14b92xAErofYQA7bU4e",
        "url": "https://open.spotify.com/show/4gL14b92xAErofYQA7bU4e",
    }


@pytest.fixture
def sample_episodes():
    """A small list of cleaned episode dicts matching clean_episode() output."""
    return [
        {
            "id": "ep001",
            "name": "Episode One",
            "description": "The first episode.",
            "duration_ms": 3600000,
            "duration_str": "60:00",
            "release_date": "2024-01-01",
            "show_name": "",
            "explicit": False,
            "image_url": "https://i.scdn.co/image/ep1",
            "uri": "spotify:episode:ep001",
            "url": "https://open.spotify.com/episode/ep001",
        },
        {
            "id": "ep002",
            "name": 'Episode "Two"',
            "description": "Has commas, and \"quotes\" in it.",
            "duration_ms": 7200000,
            "duration_str": "120:00",
            "release_date": "2024-01-08",
            "show_name": "",
            "explicit": True,
            "image_url": "https://i.scdn.co/image/ep2",
            "uri": "spotify:episode:ep002",
            "url": "https://open.spotify.com/episode/ep002",
        },
        {
            "id": "ep003",
            "name": "Episode Three",
            "description": "Third episode\nwith newlines.",
            "duration_ms": 1800000,
            "duration_str": "30:00",
            "release_date": "2024-01-15",
            "show_name": "Already Set",
            "explicit": False,
            "image_url": "https://i.scdn.co/image/ep3",
            "uri": "spotify:episode:ep003",
            "url": "https://open.spotify.com/episode/ep003",
        },
    ]
