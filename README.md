# Podcast Episode Data

Datasets of podcast episodes fetched from Spotify, plus a standalone browser dashboard for exploring the exports locally.

## Quick Start — Fetch a Podcast

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run fetch-podcast "Theories of Everything with Curt Jaimungal" \
  --spotify-client-path /Users/ishan/lab/tools/spotify-client \
  --auto-select
```

### CLI Options

| Flag | Default | Description |
| --- | --- | --- |
| `SEARCH_TERM` (positional) | — | Podcast name to search |
| `--spotify-client-path` / `-s` | `../../tools/spotify-client` | Path to spotify-client project |
| `--output` / `-o` | `<show_id>_episodes.csv` | Output CSV path |
| `--auto-select` | `False` | Auto-pick first search result |
| `--yes` / `-y` | `False` | Skip confirmation prompt |
| `--limit` / `-l` | `5000` | Max episodes to fetch |
| `--verbose` / `-v` | `False` | DEBUG logging |

### Running Tests

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run pytest
```

## Files

- `src/fetch_podcast/` — Python CLI package (Click entry point, subprocess wrapper, CSV writer, env setup)
- `joe_rogan_episodes.csv` — Full episode listing for The Joe Rogan Experience (2,651 episodes as of 2026-03-09)
- `curt_jaimungal_episodes.csv` — Full episode listing for Theories of Everything with Curt Jaimungal (347 episodes as of 2026-03-10)
- `dashboard.html` — Single-file dashboard that parses any CSV in-browser
- `tests/` — Pytest unit/integration tests + Playwright dashboard smoke test

## Dashboard Usage

1. Open `dashboard.html` directly in a browser.
2. Upload a CSV with the file picker or drag-and-drop area.
3. Explore the dataset with:
   - summary cards for volume, date span, average duration, and longest episode
   - dashboard filters for year range, series type, explicit flag, and duration bucket
   - charts for yearly output, series mix, and duration spread
   - a sortable table toolbar with full-row search, rows-per-page options, direct page navigation, and a linked detail panel

The dashboard runs locally with no backend and no build step.

## Running the Browser Smoke Test

```bash
npx --yes @playwright/test test tests/dashboard.spec.js --workers=1 --reporter=line
```

## CSV Columns

| Column | Description |
| --- | --- |
| `id` | Spotify episode ID |
| `name` | Episode title |
| `description` | Episode description |
| `duration_ms` | Duration in milliseconds |
| `duration_str` | Human-readable duration (e.g. `2h 45m`) |
| `release_date` | Release date (`YYYY-MM-DD`) |
| `show_name` | Show name |
| `explicit` | Whether the episode is marked explicit |
| `image_url` | Episode cover image URL |
| `uri` | Spotify URI |
| `url` | Spotify web URL |

## Data Source

Fetched via [spotify-client](../../../tools/spotify-client) CLI using the Spotify Web API.
