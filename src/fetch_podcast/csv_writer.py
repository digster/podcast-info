"""JSON episode list → CSV writer with the standard 11-column schema."""

import csv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Canonical column order — matches the schema produced by spotify-client's clean_episode()
COLUMNS = [
    "id",
    "name",
    "description",
    "duration_ms",
    "duration_str",
    "release_date",
    "show_name",
    "explicit",
    "image_url",
    "uri",
    "url",
]


def write_episodes_csv(
    episodes: list[dict],
    output_path: Path,
    show_name: str = "",
) -> int:
    """Write a list of episode dicts to a CSV file.

    Backfills the `show_name` column from the search result, since the
    `show episodes` endpoint doesn't nest the parent show in each episode
    (clean_episode returns "" for show_name in that case).

    Args:
        episodes: List of episode dicts (from spotify-client JSON output).
        output_path: Path for the output CSV file.
        show_name: Show name to backfill into episodes missing it.

    Returns:
        Number of rows written (excluding header).
    """
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=COLUMNS,
            extrasaction="ignore",
            quoting=csv.QUOTE_MINIMAL,
        )
        writer.writeheader()

        for ep in episodes:
            # Backfill show_name if missing or empty
            if not ep.get("show_name") and show_name:
                ep["show_name"] = show_name
            writer.writerow(ep)

    row_count = len(episodes)
    file_size = output_path.stat().st_size
    logger.info(
        "Wrote %d episodes to %s (%s)",
        row_count,
        output_path,
        _human_size(file_size),
    )
    return row_count


def _human_size(size_bytes: int) -> str:
    """Convert bytes to a human-readable string."""
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
