"""Tests for env.py — .env loading and SPOTIPY_* → SPOTIFY_* remapping."""

from pathlib import Path

from fetch_podcast.env import build_subprocess_env


def test_remaps_spotipy_vars(tmp_path, monkeypatch):
    """SPOTIPY_* vars in .env file are remapped to SPOTIFY_* in the output."""
    env_file = tmp_path / ".env"
    env_file.write_text(
        "SPOTIPY_CLIENT_ID=test_id\n"
        "SPOTIPY_CLIENT_SECRET=test_secret\n"
        "SPOTIPY_REDIRECT_URI=http://localhost:8888/callback\n"
    )
    # Clear any existing SPOTIFY_* vars from the test environment
    monkeypatch.delenv("SPOTIFY_CLIENT_ID", raising=False)
    monkeypatch.delenv("SPOTIFY_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("SPOTIFY_REDIRECT_URI", raising=False)

    env = build_subprocess_env(tmp_path)

    assert env["SPOTIFY_CLIENT_ID"] == "test_id"
    assert env["SPOTIFY_CLIENT_SECRET"] == "test_secret"
    assert env["SPOTIFY_REDIRECT_URI"] == "http://localhost:8888/callback"


def test_caller_env_takes_precedence(tmp_path, monkeypatch):
    """Explicit SPOTIFY_* vars in caller's env override .env file values."""
    env_file = tmp_path / ".env"
    env_file.write_text("SPOTIPY_CLIENT_ID=from_dotenv\n")
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "from_caller")

    env = build_subprocess_env(tmp_path)

    assert env["SPOTIFY_CLIENT_ID"] == "from_caller"


def test_sets_uv_cache_dir(tmp_path, monkeypatch):
    """UV_CACHE_DIR is set to /tmp/uv-cache by default."""
    monkeypatch.delenv("UV_CACHE_DIR", raising=False)
    (tmp_path / ".env").write_text("")

    env = build_subprocess_env(tmp_path)

    assert env["UV_CACHE_DIR"] == "/tmp/uv-cache"


def test_preserves_existing_uv_cache_dir(tmp_path, monkeypatch):
    """If UV_CACHE_DIR is already set, it is not overridden."""
    monkeypatch.setenv("UV_CACHE_DIR", "/custom/cache")
    (tmp_path / ".env").write_text("")

    env = build_subprocess_env(tmp_path)

    assert env["UV_CACHE_DIR"] == "/custom/cache"


def test_missing_env_file(tmp_path, monkeypatch):
    """Works gracefully when .env file doesn't exist."""
    monkeypatch.delenv("SPOTIFY_CLIENT_ID", raising=False)

    env = build_subprocess_env(tmp_path)

    # Should not crash — SPOTIFY_CLIENT_ID just won't be set (unless from os.environ)
    assert "UV_CACHE_DIR" in env


def test_includes_os_environ(tmp_path, monkeypatch):
    """The output env includes all of os.environ plus the remapped vars."""
    (tmp_path / ".env").write_text("")
    monkeypatch.setenv("MY_CUSTOM_VAR", "hello")

    env = build_subprocess_env(tmp_path)

    assert env["MY_CUSTOM_VAR"] == "hello"
