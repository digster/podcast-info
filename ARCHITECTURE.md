# Architecture

This repo has three layers: a Python CLI that automates the podcast data fetch pipeline, CSV episode datasets, and a zero-build browser dashboard for exploring them.

## Big Picture

```text
User runs: uv run fetch-podcast "Podcast Name"
  -> cli.py orchestrates the pipeline
  -> env.py loads spotify-client .env, remaps SPOTIPY_* → SPOTIFY_*
  -> spotify.py runs subprocess: uv run spotify search shows "..."
  -> User selects a show (or --auto-select picks first)
  -> spotify.py runs subprocess: uv run spotify -c -l 5000 show episodes <id>
  -> csv_writer.py converts JSON episodes to CSV (backfills show_name)
  -> *.csv output file

dashboard.html upload flow
  -> client-side parsing, derivation, filtering, charts, table, detail panel
```

## Main Components

### Python CLI (`src/fetch_podcast/`)

- **`cli.py`** — Click entry point. Orchestrates: validate path → build env → search shows → user selection → fetch episodes → write CSV. Exit codes: 0 = success, 1 = error, 2 = partial fetch.
- **`env.py`** — Reads `<spotify_client_path>/.env` via python-dotenv, remaps `SPOTIPY_*` → `SPOTIFY_*`, sets `UV_CACHE_DIR=/tmp/uv-cache` for macOS SIP workaround. Caller's explicit `SPOTIFY_*` vars take precedence.
- **`spotify.py`** — Subprocess wrapper with two functions: `search_shows()` and `fetch_episodes()`. Both parse stdout as JSON and raise `SpotifyCliError` on failure. 300s timeout.
- **`csv_writer.py`** — Writes episodes to CSV with the 11-column schema. Backfills `show_name` from the search result since the `show episodes` endpoint doesn't include the parent show in each episode.
- **`__init__.py`** — Package marker with version.

### CSV Datasets

- `joe_rogan_episodes.csv` — The Joe Rogan Experience (Show ID: `4rOoJ6Egrf8K2IrywzwOMk`)
- `curt_jaimungal_episodes.csv` — Theories of Everything with Curt Jaimungal (Show ID: `4gL14b92xAErofYQA7bU4e`)

### Dashboard

- **`dashboard.html`** — Fully self-contained UI with inline CSS and JavaScript. Parses uploaded CSV files in-browser, derives presentation fields client-side, provides filters/charts/search/pagination.

### Tests

- `tests/test_env.py` — Env remapping, precedence, SIP workaround
- `tests/test_spotify.py` — Subprocess mocking, error handling, JSON parsing
- `tests/test_csv_writer.py` — CSV output format, backfill, edge cases
- `tests/test_cli.py` — CliRunner integration tests for the full pipeline
- `tests/conftest.py` — Shared fixtures (sample show, episodes)
- `tests/dashboard.spec.js` — Playwright browser smoke test

## Key Decisions

- **Subprocess over library import**: spotify-client is treated as an external CLI tool. This avoids coupling to its internals and means fetch-podcast only needs `click` and `python-dotenv` as dependencies.
- **show_name backfill**: The Spotify API's `show episodes` endpoint doesn't include the parent show object in each episode, so `clean_episode()` returns `""` for `show_name`. The CSV writer injects it from the search result.
- **UV_CACHE_DIR workaround**: Baked into `env.py` so users don't need to remember to set it manually on macOS.
- **Runtime CSV upload for dashboard**: Local `file://` pages cannot reliably fetch sibling files across browsers.

## Developer Workflows

- **Fetch a podcast**: `UV_CACHE_DIR=/tmp/uv-cache uv run fetch-podcast "Podcast Name" --auto-select`
- **Run Python tests**: `UV_CACHE_DIR=/tmp/uv-cache uv run pytest`
- **Run dashboard smoke test**: `npx --yes @playwright/test test tests/dashboard.spec.js --workers=1 --reporter=line`
- **Open the dashboard**: Double-click `dashboard.html` or open directly in browser

## Integration Notes

- **External dependency**: spotify-client at `/Users/ishan/lab/tools/spotify-client` (or specify with `--spotify-client-path`)
- **Env var mapping**: spotify-client `.env` uses `SPOTIPY_*` prefixes; `env.py` remaps them to `SPOTIFY_*`
- **Pagination**: Spotify API returns max 50 episodes per request; the CLI uses `-l 5000` to paginate automatically
