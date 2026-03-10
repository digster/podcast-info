"""Environment setup — loads spotify-client .env and remaps SPOTIPY_* to SPOTIFY_* vars."""

import os
from pathlib import Path

from dotenv import dotenv_values


# Mapping from spotipy env var names to the ones spotify-client expects
_REMAP = {
    "SPOTIPY_CLIENT_ID": "SPOTIFY_CLIENT_ID",
    "SPOTIPY_CLIENT_SECRET": "SPOTIFY_CLIENT_SECRET",
    "SPOTIPY_REDIRECT_URI": "SPOTIFY_REDIRECT_URI",
}


def build_subprocess_env(spotify_client_path: Path) -> dict[str, str]:
    """Build an environment dict for running spotify-client subprocesses.

    1. Reads <spotify_client_path>/.env via python-dotenv
    2. Remaps SPOTIPY_* keys to SPOTIFY_* keys
    3. Merges with os.environ (caller's explicit SPOTIFY_* vars take precedence)
    4. Sets UV_CACHE_DIR to work around macOS SIP issue with uv cache
    """
    env_file = spotify_client_path / ".env"
    dotenv_vars = dotenv_values(env_file) if env_file.exists() else {}

    # Start with the current process environment
    env = dict(os.environ)

    # Remap SPOTIPY_* → SPOTIFY_* from the .env file (only if not already set)
    for old_key, new_key in _REMAP.items():
        if new_key not in env and old_key in dotenv_vars:
            env[new_key] = dotenv_vars[old_key]

    # macOS SIP workaround: uv cache dir gets a com.apple.provenance xattr
    # that prevents uv from functioning inside SIP-protected paths
    env.setdefault("UV_CACHE_DIR", "/tmp/uv-cache")

    return env
