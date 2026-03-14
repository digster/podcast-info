"""Tests for cli.py — Click CLI integration tests using CliRunner."""

import json
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from fetch_podcast.cli import cli


class TestCli:
    """Integration tests using Click's CliRunner."""

    def _mock_shows(self):
        """Sample search result."""
        return [
            {
                "id": "show1",
                "name": "Test Podcast",
                "publisher": "Test Publisher",
                "total_episodes": 2,
                "url": "https://open.spotify.com/show/show1",
            }
        ]

    def _mock_episodes(self):
        """Sample episodes matching the show."""
        return [
            {
                "id": "ep1",
                "name": "Episode 1",
                "description": "First",
                "duration_ms": 3600000,
                "duration_str": "60:00",
                "release_date": "2024-01-01",
                "show_name": "",
                "explicit": False,
                "image_url": "https://example.com/img1",
                "uri": "spotify:episode:ep1",
                "url": "https://open.spotify.com/episode/ep1",
            },
            {
                "id": "ep2",
                "name": "Episode 2",
                "description": "Second",
                "duration_ms": 7200000,
                "duration_str": "120:00",
                "release_date": "2024-01-08",
                "show_name": "",
                "explicit": False,
                "image_url": "https://example.com/img2",
                "uri": "spotify:episode:ep2",
                "url": "https://open.spotify.com/episode/ep2",
            },
        ]

    def test_auto_select_with_yes(self, tmp_path):
        """--auto-select --yes runs the full pipeline non-interactively."""
        # Create a fake spotify-client dir with pyproject.toml
        sc_path = tmp_path / "spotify-client"
        sc_path.mkdir()
        (sc_path / "pyproject.toml").write_text("[project]\nname = 'fake'\n")
        (sc_path / ".env").write_text("SPOTIPY_CLIENT_ID=test\nSPOTIPY_CLIENT_SECRET=secret\n")

        output_csv = tmp_path / "output.csv"

        with (
            patch("fetch_podcast.cli.search_shows", return_value=self._mock_shows()),
            patch("fetch_podcast.cli.fetch_episodes", return_value=self._mock_episodes()),
        ):
            runner = CliRunner()
            result = runner.invoke(cli, [
                "Test Podcast",
                "-s", str(sc_path),
                "-o", str(output_csv),
                "--auto-select",
                "--yes",
            ])

        assert result.exit_code == 0, result.output
        assert output_csv.exists()
        assert "2 episodes" in result.output

        # Verify CSV content
        content = output_csv.read_text()
        lines = content.strip().split("\n")
        assert len(lines) == 3  # header + 2 episodes
        assert lines[0].startswith("id,name,")

    def test_missing_spotify_client_path(self, tmp_path):
        """Error when spotify-client path doesn't have pyproject.toml."""
        sc_path = tmp_path / "nonexistent"
        sc_path.mkdir()  # exists but no pyproject.toml

        runner = CliRunner()
        result = runner.invoke(cli, [
            "query",
            "-s", str(sc_path),
        ])

        assert result.exit_code == 1
        assert "spotify-client not found" in result.output

    def test_no_shows_found(self, tmp_path):
        """Exits with error when search returns empty."""
        sc_path = tmp_path / "spotify-client"
        sc_path.mkdir()
        (sc_path / "pyproject.toml").write_text("[project]\nname = 'fake'\n")
        (sc_path / ".env").write_text("")

        with patch("fetch_podcast.cli.search_shows", return_value=[]):
            runner = CliRunner()
            result = runner.invoke(cli, [
                "NonexistentPodcast",
                "-s", str(sc_path),
                "--auto-select",
                "--yes",
            ])

        assert result.exit_code == 1
        assert "No shows found" in result.output

    def test_default_output_filename(self, tmp_path):
        """Without -o, the output file is named using the Spotify show ID."""
        sc_path = tmp_path / "spotify-client"
        sc_path.mkdir()
        (sc_path / "pyproject.toml").write_text("[project]\nname = 'fake'\n")
        (sc_path / ".env").write_text("")

        with (
            patch("fetch_podcast.cli.search_shows", return_value=self._mock_shows()),
            patch("fetch_podcast.cli.fetch_episodes", return_value=self._mock_episodes()),
        ):
            runner = CliRunner()
            # Run in a temp dir so the default output goes there
            with runner.isolated_filesystem(temp_dir=tmp_path):
                result = runner.invoke(cli, [
                    "Test Podcast",
                    "-s", str(sc_path),
                    "--auto-select",
                    "--yes",
                ])

                assert result.exit_code == 0
                assert Path("show1_episodes.csv").exists()

    def test_partial_fetch_exit_code_2(self, tmp_path):
        """Exit code 2 when fetched count doesn't match total_episodes."""
        sc_path = tmp_path / "spotify-client"
        sc_path.mkdir()
        (sc_path / "pyproject.toml").write_text("[project]\nname = 'fake'\n")
        (sc_path / ".env").write_text("")

        # Show says 5 episodes but we only get 2
        shows = self._mock_shows()
        shows[0]["total_episodes"] = 5

        with (
            patch("fetch_podcast.cli.search_shows", return_value=shows),
            patch("fetch_podcast.cli.fetch_episodes", return_value=self._mock_episodes()),
        ):
            runner = CliRunner()
            result = runner.invoke(cli, [
                "Test Podcast",
                "-s", str(sc_path),
                "-o", str(tmp_path / "out.csv"),
                "--auto-select",
                "--yes",
            ])

        assert result.exit_code == 2

    def test_show_name_backfilled_in_csv(self, tmp_path):
        """The show_name column is backfilled from the search result."""
        sc_path = tmp_path / "spotify-client"
        sc_path.mkdir()
        (sc_path / "pyproject.toml").write_text("[project]\nname = 'fake'\n")
        (sc_path / ".env").write_text("")

        output_csv = tmp_path / "output.csv"

        with (
            patch("fetch_podcast.cli.search_shows", return_value=self._mock_shows()),
            patch("fetch_podcast.cli.fetch_episodes", return_value=self._mock_episodes()),
        ):
            runner = CliRunner()
            result = runner.invoke(cli, [
                "Test Podcast",
                "-s", str(sc_path),
                "-o", str(output_csv),
                "--auto-select",
                "--yes",
            ])

        assert result.exit_code == 0
        import csv
        with open(output_csv) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Episodes had empty show_name — should be backfilled
        assert all(row["show_name"] == "Test Podcast" for row in rows)

    def test_interactive_selection(self, tmp_path):
        """Interactive mode prompts for show selection and confirmation."""
        sc_path = tmp_path / "spotify-client"
        sc_path.mkdir()
        (sc_path / "pyproject.toml").write_text("[project]\nname = 'fake'\n")
        (sc_path / ".env").write_text("")

        output_csv = tmp_path / "output.csv"

        with (
            patch("fetch_podcast.cli.search_shows", return_value=self._mock_shows()),
            patch("fetch_podcast.cli.fetch_episodes", return_value=self._mock_episodes()),
        ):
            runner = CliRunner()
            # Simulate: select show 1, then confirm "y"
            result = runner.invoke(
                cli,
                ["Test Podcast", "-s", str(sc_path), "-o", str(output_csv)],
                input="1\ny\n",
            )

        assert result.exit_code == 0
        assert output_csv.exists()
