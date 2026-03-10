"""Tests for csv_writer.py — JSON episodes to CSV conversion."""

import csv
from pathlib import Path

from fetch_podcast.csv_writer import COLUMNS, write_episodes_csv


def test_writes_correct_headers(tmp_path, sample_episodes):
    """CSV header row matches the 11-column schema."""
    out = tmp_path / "test.csv"
    write_episodes_csv(sample_episodes, out)

    with open(out) as f:
        reader = csv.reader(f)
        headers = next(reader)

    assert headers == COLUMNS


def test_returns_row_count(tmp_path, sample_episodes):
    """Return value is the number of data rows written."""
    out = tmp_path / "test.csv"
    count = write_episodes_csv(sample_episodes, out)
    assert count == 3


def test_backfills_empty_show_name(tmp_path, sample_episodes):
    """Episodes with empty show_name get it backfilled from the show_name arg."""
    out = tmp_path / "test.csv"
    write_episodes_csv(sample_episodes, out, show_name="My Podcast")

    with open(out) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # ep001 and ep002 had empty show_name — should be backfilled
    assert rows[0]["show_name"] == "My Podcast"
    assert rows[1]["show_name"] == "My Podcast"
    # ep003 already had "Already Set" — should be preserved
    assert rows[2]["show_name"] == "Already Set"


def test_handles_quotes_and_commas(tmp_path, sample_episodes):
    """Episodes with quotes and commas in fields are properly escaped."""
    out = tmp_path / "test.csv"
    write_episodes_csv(sample_episodes, out)

    with open(out) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # ep002 has quotes and commas in name/description
    assert rows[1]["name"] == 'Episode "Two"'
    assert "commas" in rows[1]["description"]
    assert "quotes" in rows[1]["description"]


def test_handles_newlines_in_description(tmp_path, sample_episodes):
    """Descriptions with embedded newlines are handled by csv module."""
    out = tmp_path / "test.csv"
    write_episodes_csv(sample_episodes, out)

    with open(out) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert "newlines" in rows[2]["description"]


def test_extra_keys_ignored(tmp_path):
    """Episode dicts with extra keys beyond the 11 columns are silently ignored."""
    episodes = [
        {
            "id": "ep1",
            "name": "Test",
            "description": "",
            "duration_ms": 1000,
            "duration_str": "0:01",
            "release_date": "2024-01-01",
            "show_name": "",
            "explicit": False,
            "image_url": "",
            "uri": "spotify:episode:ep1",
            "url": "https://open.spotify.com/episode/ep1",
            "extra_field": "should be ignored",
            "another_extra": 42,
        }
    ]
    out = tmp_path / "test.csv"
    count = write_episodes_csv(episodes, out)

    assert count == 1
    with open(out) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert "extra_field" not in rows[0]


def test_empty_episodes_list(tmp_path):
    """Writing an empty list produces a CSV with only the header."""
    out = tmp_path / "test.csv"
    count = write_episodes_csv([], out)

    assert count == 0
    with open(out) as f:
        content = f.read()
    # Should have exactly the header line
    lines = content.strip().split("\n")
    assert len(lines) == 1
    assert lines[0] == ",".join(COLUMNS)
