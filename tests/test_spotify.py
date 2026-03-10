"""Tests for spotify.py — subprocess wrapper for spotify-client CLI."""

import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from fetch_podcast.spotify import SpotifyCliError, fetch_episodes, search_shows


@pytest.fixture
def mock_env():
    """Minimal env dict for subprocess calls."""
    return {"PATH": "/usr/bin", "SPOTIFY_CLIENT_ID": "test", "UV_CACHE_DIR": "/tmp/uv-cache"}


class TestSearchShows:
    def test_returns_parsed_json(self, tmp_path, mock_env):
        """Successful search returns a list of show dicts."""
        shows = [{"id": "abc", "name": "Test Show", "total_episodes": 10}]
        result = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps(shows), stderr=""
        )
        with patch("fetch_podcast.spotify.subprocess.run", return_value=result) as mock_run:
            data = search_shows(tmp_path, "Test Show", mock_env)

        assert data == shows
        # Verify the correct command was constructed
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert cmd == ["uv", "run", "spotify", "search", "shows", "Test Show"]
        assert call_args[1]["cwd"] == tmp_path

    def test_non_zero_exit_raises(self, tmp_path, mock_env):
        """Non-zero exit code raises SpotifyCliError with stderr."""
        result = subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr="Auth failed"
        )
        with patch("fetch_podcast.spotify.subprocess.run", return_value=result):
            with pytest.raises(SpotifyCliError, match="Auth failed"):
                search_shows(tmp_path, "query", mock_env)

    def test_invalid_json_raises(self, tmp_path, mock_env):
        """Invalid JSON output raises SpotifyCliError."""
        result = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="not json{", stderr=""
        )
        with patch("fetch_podcast.spotify.subprocess.run", return_value=result):
            with pytest.raises(SpotifyCliError, match="Invalid JSON"):
                search_shows(tmp_path, "query", mock_env)

    def test_timeout_raises(self, tmp_path, mock_env):
        """Command timeout raises SpotifyCliError."""
        with patch(
            "fetch_podcast.spotify.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="uv", timeout=300),
        ):
            with pytest.raises(SpotifyCliError, match="timed out"):
                search_shows(tmp_path, "query", mock_env)

    def test_single_object_wrapped_in_list(self, tmp_path, mock_env):
        """If the CLI returns a single object instead of a list, wrap it."""
        show = {"id": "abc", "name": "Single Show"}
        result = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps(show), stderr=""
        )
        with patch("fetch_podcast.spotify.subprocess.run", return_value=result):
            data = search_shows(tmp_path, "query", mock_env)

        assert data == [show]


class TestFetchEpisodes:
    def test_returns_episodes_with_correct_flags(self, tmp_path, mock_env):
        """Fetches episodes with compact mode and limit flags."""
        episodes = [{"id": "ep1", "name": "Ep 1"}]
        result = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps(episodes), stderr=""
        )
        with patch("fetch_podcast.spotify.subprocess.run", return_value=result) as mock_run:
            data = fetch_episodes(tmp_path, "show123", mock_env, limit=100)

        assert data == episodes
        cmd = mock_run.call_args[0][0]
        assert cmd == [
            "uv", "run", "spotify",
            "-c", "-l", "100",
            "show", "episodes", "show123",
        ]

    def test_default_limit_is_5000(self, tmp_path, mock_env):
        """Default limit parameter is 5000."""
        result = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="[]", stderr=""
        )
        with patch("fetch_podcast.spotify.subprocess.run", return_value=result) as mock_run:
            fetch_episodes(tmp_path, "show123", mock_env)

        cmd = mock_run.call_args[0][0]
        assert "-l" in cmd
        limit_idx = cmd.index("-l")
        assert cmd[limit_idx + 1] == "5000"
