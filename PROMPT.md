# Prompts

## 2026-03-09: Download Joe Rogan Podcast Episodes to CSV

Use the spotify-client CLI to fetch all JRE episode data from Spotify and convert to CSV. Steps: search for show ID, fetch all episodes with `-l 5000`, convert JSON to CSV with columns (id, name, description, duration_ms, duration_str, release_date, show_name, explicit, image_url, uri, url), and verify.

## 2026-03-10: Create a Single HTML Dashboard for the CSV

Create a single html file dashboard to explore the data from joe_rogan_episodes.csv.

## 2026-03-10: Implement the Dashboard Plan

Implement the approved plan for the single-file CSV dashboard, including the UI, browser verification, and the required repo documentation updates.

## 2026-03-10: Add Table Search and Pagination Options

Add pagination and search options for the table in the dashboard file.

## 2026-03-10: Implement the Table Search and Pagination Plan

Implement the approved plan.

## 2026-03-10: Download Curt Jaimungal Podcast Episodes to CSV

Fetch all episodes of "Theories of Everything with Curt Jaimungal" from Spotify and save as CSV. Same workflow as the Joe Rogan fetch: search for show ID, fetch all episodes with `-l 5000`, convert JSON to CSV with the same 11-column schema, and verify. Update documentation to reflect the new dataset.

## 2026-03-10: Implement fetch-podcast CLI Utility

Implement a Python CLI utility (`uv run fetch-podcast "Podcast Name"`) that automates the entire podcast data fetch pipeline into a single command. Uses Click, subprocess wrapper for spotify-client, env remapping, and CSV writer with show_name backfill. Includes full test suite.

## 2026-03-10: Add fetch-podcast Skill File

Create a Claude Code skill file at `.claude/skills/fetch-podcast/skill.md` so users can invoke `/fetch-podcast "Podcast Name"` and have Claude handle the entire workflow automatically — prerequisite validation, duplicate detection, CLI execution with proper flags, output verification, and next-step suggestions.

## 2026-03-13: Use Show ID in Default CSV Filename

Change the default CSV output filename from `{slugified_show_name}_episodes.csv` to `{show_id}_episodes.csv` for uniqueness and stability. Remove the `_slugify` helper and its tests.
