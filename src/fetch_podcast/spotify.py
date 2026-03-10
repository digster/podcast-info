"""Subprocess wrapper for spotify-client CLI commands."""

import json
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

# Timeout for subprocess calls (5 minutes — large podcasts can take a while)
_TIMEOUT = 300


class SpotifyCliError(Exception):
    """Raised when a spotify-client subprocess fails."""


def search_shows(
    path: Path, query: str, env: dict[str, str]
) -> list[dict]:
    """Run `uv run spotify search shows "<query>"` and return parsed JSON.

    Args:
        path: Path to the spotify-client project root.
        query: Search query string (e.g. podcast name).
        env: Environment variables for the subprocess.

    Returns:
        List of show dicts from the spotify-client output.
    """
    cmd = ["uv", "run", "spotify", "search", "shows", query]
    return _run_json(cmd, cwd=path, env=env)


def fetch_episodes(
    path: Path, show_id: str, env: dict[str, str], limit: int = 5000
) -> list[dict]:
    """Run `uv run spotify -c -l <limit> show episodes <id>` and return parsed JSON.

    Uses compact mode (-c) for smaller output and a high limit to fetch all episodes.

    Args:
        path: Path to the spotify-client project root.
        show_id: Spotify show ID.
        env: Environment variables for the subprocess.
        limit: Maximum number of episodes to fetch.

    Returns:
        List of episode dicts from the spotify-client output.
    """
    cmd = [
        "uv", "run", "spotify",
        "-c", "-l", str(limit),
        "show", "episodes", show_id,
    ]
    return _run_json(cmd, cwd=path, env=env)


def _run_json(
    cmd: list[str], *, cwd: Path, env: dict[str, str]
) -> list[dict]:
    """Execute a command, parse stdout as JSON, and return the result.

    Raises SpotifyCliError on non-zero exit code or invalid JSON.
    """
    logger.debug("Running: %s (cwd=%s)", " ".join(cmd), cwd)
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            timeout=_TIMEOUT,
        )
    except subprocess.TimeoutExpired as exc:
        raise SpotifyCliError(f"Command timed out after {_TIMEOUT}s: {' '.join(cmd)}") from exc

    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise SpotifyCliError(
            f"spotify-client exited with code {result.returncode}: {stderr}"
        )

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise SpotifyCliError(f"Invalid JSON from spotify-client: {exc}") from exc

    # The CLI returns either a list directly or sometimes a single object
    if isinstance(data, list):
        return data
    return [data]
