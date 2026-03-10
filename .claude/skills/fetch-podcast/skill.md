---
name: fetch-podcast
description: Fetch podcast episode data from Spotify and export to CSV. Trigger when the user wants to download podcast data, fetch episodes, or export a podcast to CSV.
allowed-tools: Bash, Read, Glob
---

# Fetch Podcast Episodes from Spotify

Automates the `fetch-podcast` CLI to search Spotify for a podcast and export all episodes to CSV.

## Step 1 — Parse Podcast Name

Extract the podcast name from `$ARGUMENTS`. If no name was provided, ask the user what podcast they want to fetch.

## Step 2 — Validate Prerequisites

Check that the spotify-client project exists and is properly set up:

```
# Both of these must exist
/Users/ishan/lab/tools/spotify-client/pyproject.toml
/Users/ishan/lab/tools/spotify-client/.env
```

If either is missing, stop and tell the user what's wrong. The `.env` file must contain Spotify API credentials (`SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET`).

## Step 3 — Check for Existing Data

Before running a multi-minute fetch, check if a CSV already exists for this podcast:

```bash
ls /Users/ishan/lab/experiments/podcast-info/*episodes*.csv
```

If a matching CSV exists, tell the user and ask whether they want to re-fetch (overwrites the file) or skip. Show the file size and row count of the existing file so they can make an informed decision.

## Step 4 — Run the CLI

Build and execute the command. **Always** use `--auto-select` and `--yes` because Claude cannot interact with Click's interactive prompts in a subprocess.

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run fetch-podcast "<PODCAST_NAME>" \
  --spotify-client-path /Users/ishan/lab/tools/spotify-client \
  --auto-select \
  --yes
```

Use a **10-minute timeout** (`timeout: 600000`) on the Bash call — large podcasts (2000+ episodes) take several minutes due to Spotify API pagination.

If the user specified a custom output path or episode limit, add `--output <path>` or `--limit <n>` accordingly.

## Step 5 — Interpret the Result

| Exit Code | Meaning | Action |
|-----------|---------|--------|
| 0 | Success | Proceed to verification |
| 1 | Error | Show the error output. Suggest re-running with `--verbose` for more detail. Check that the spotify-client venv is healthy (`uv sync` inside spotify-client dir). |
| 2 | Partial fetch | Warn the user that fewer episodes were returned than expected. The CSV is still valid — it just may be incomplete. |

## Step 6 — Verify the Output

After a successful fetch:

1. Find the output CSV (default name is `<slugified_show_name>_episodes.csv` in the project root).
2. Read the first 5 rows to preview the data.
3. Report:
   - Total episode count (number of data rows)
   - File size
   - Date range (earliest to latest `release_date`)
   - Show name from the CSV

## Step 7 — Offer Next Steps

Suggest what the user can do next:

- **Explore in the dashboard** — open `dashboard.html` in a browser and upload the CSV
- **Preview more data** — read additional rows or search for specific episodes
- **Fetch another podcast** — run `/fetch-podcast "Another Podcast Name"`

## Error Recovery

If the fetch fails:

1. Re-run with `--verbose` to get DEBUG-level output:
   ```bash
   UV_CACHE_DIR=/tmp/uv-cache uv run fetch-podcast "<PODCAST_NAME>" \
     --spotify-client-path /Users/ishan/lab/tools/spotify-client \
     --auto-select --yes --verbose
   ```
2. If the error mentions missing modules or broken venv, suggest running `uv sync` inside the spotify-client directory.
3. If the error mentions authentication, remind the user to check their `.env` credentials at `/Users/ishan/lab/tools/spotify-client/.env`.
