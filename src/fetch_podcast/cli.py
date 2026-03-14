"""Click entry point — orchestrates the full fetch-podcast pipeline."""

import logging
import sys
from pathlib import Path

import click

from fetch_podcast.csv_writer import write_episodes_csv
from fetch_podcast.env import build_subprocess_env
from fetch_podcast.spotify import SpotifyCliError, fetch_episodes, search_shows

logger = logging.getLogger("fetch_podcast")


def _configure_logging(verbose: bool) -> None:
    """Set up console logging with appropriate level."""
    level = logging.DEBUG if verbose else logging.INFO
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.setLevel(level)
    logger.addHandler(handler)


@click.command()
@click.argument("search_term")
@click.option(
    "--spotify-client-path", "-s",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    default=None,
    help="Path to spotify-client project. Defaults to ../../tools/spotify-client relative to this project.",
)
@click.option(
    "--output", "-o",
    type=click.Path(dir_okay=False),
    default=None,
    help="Output CSV path. Defaults to <show_id>_episodes.csv.",
)
@click.option(
    "--auto-select",
    is_flag=True,
    default=False,
    help="Automatically pick the first search result.",
)
@click.option(
    "--yes", "-y",
    is_flag=True,
    default=False,
    help="Skip confirmation prompt (for non-interactive/scripted usage).",
)
@click.option(
    "--limit", "-l",
    type=int,
    default=5000,
    help="Maximum number of episodes to fetch.",
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    default=False,
    help="Enable DEBUG logging.",
)
def cli(
    search_term: str,
    spotify_client_path: str | None,
    output: str | None,
    auto_select: bool,
    yes: bool,
    limit: int,
    verbose: bool,
) -> None:
    """Fetch all episodes of a podcast from Spotify and export to CSV.

    SEARCH_TERM is the podcast name to search for on Spotify.

    \b
    Examples:
      fetch-podcast "Theories of Everything with Curt Jaimungal" --auto-select
      fetch-podcast "Huberman Lab" -s /path/to/spotify-client -o huberman.csv
    """
    _configure_logging(verbose)

    # --- 1. Resolve and validate spotify-client path ---
    if spotify_client_path:
        sc_path = Path(spotify_client_path)
    else:
        # Default: ../../tools/spotify-client relative to this project
        sc_path = Path(__file__).resolve().parent.parent.parent / "../../tools/spotify-client"
        sc_path = sc_path.resolve()

    if not (sc_path / "pyproject.toml").exists():
        click.echo(f"Error: spotify-client not found at {sc_path}", err=True)
        click.echo("Use --spotify-client-path to specify the correct location.", err=True)
        sys.exit(1)

    logger.debug("Using spotify-client at: %s", sc_path)

    # --- 2. Build subprocess environment ---
    env = build_subprocess_env(sc_path)

    # --- 3. Search for shows ---
    click.echo(f'Searching for "{search_term}"...')
    try:
        shows = search_shows(sc_path, search_term, env)
    except SpotifyCliError as exc:
        click.echo(f"Error searching shows: {exc}", err=True)
        sys.exit(1)

    if not shows:
        click.echo("No shows found.", err=True)
        sys.exit(1)

    # --- 4. Display results and select ---
    if auto_select:
        selected = shows[0]
        click.echo(f"Auto-selected: {selected['name']}")
    else:
        click.echo(f"\nFound {len(shows)} show(s):\n")
        for i, show in enumerate(shows, 1):
            ep_count = show.get("total_episodes", "?")
            publisher = show.get("publisher", "Unknown")
            click.echo(f"  [{i}] {show['name']} — {publisher} ({ep_count} episodes)")

        click.echo()
        choice = click.prompt("Select a show", type=int, default=1)
        if choice < 1 or choice > len(shows):
            click.echo("Invalid selection.", err=True)
            sys.exit(1)
        selected = shows[choice - 1]

    # --- 5. Confirmation preview ---
    show_name = selected["name"]
    total_episodes = selected.get("total_episodes", "?")
    publisher = selected.get("publisher", "Unknown")
    show_url = selected.get("url", "")

    if not yes:
        click.echo(f"\n  Show:      {show_name}")
        click.echo(f"  Publisher: {publisher}")
        click.echo(f"  Episodes:  {total_episodes}")
        if show_url:
            click.echo(f"  URL:       {show_url}")
        click.echo()

        if not click.confirm("Proceed?", default=True):
            click.echo("Cancelled.")
            sys.exit(0)

    # --- 6. Fetch all episodes ---
    show_id = selected["id"]
    click.echo(f"\nFetching up to {limit} episodes for show {show_id}...")

    try:
        episodes = fetch_episodes(sc_path, show_id, env, limit=limit)
    except SpotifyCliError as exc:
        click.echo(f"Error fetching episodes: {exc}", err=True)
        sys.exit(1)

    if not episodes:
        click.echo("No episodes returned.", err=True)
        sys.exit(1)

    # --- 7. Warn on count mismatch ---
    exit_code = 0
    if isinstance(total_episodes, int) and len(episodes) != total_episodes:
        logger.warning(
            "Expected %d episodes but fetched %d (partial fetch)",
            total_episodes,
            len(episodes),
        )
        exit_code = 2

    # --- 8. Write CSV ---
    if output:
        output_path = Path(output)
    else:
        output_path = Path(f"{show_id}_episodes.csv")

    row_count = write_episodes_csv(episodes, output_path, show_name=show_name)

    # --- 9. Summary ---
    file_size = output_path.stat().st_size
    click.echo(f"\nDone! Wrote {row_count} episodes to {output_path} ({file_size:,} bytes)")
    sys.exit(exit_code)
