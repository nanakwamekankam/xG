import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location("scratchwork", ROOT / "scratchwork.py")
scratchwork = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scratchwork)

sys.path.insert(0, str(ROOT / ".."))
from scapper.fifascrapper import _challenge_state, _league_team_urls, _team_player_rows, _try_auto_challenge_click
from scapper import fifaindexscrape


class ScratchworkTests(unittest.TestCase):
    def test_main_uses_visible_browser_and_longer_timeout(self):
        with patch.object(scratchwork, "scrape_league", return_value=None) as mock_scrape:
            scratchwork.main()

        mock_scrape.assert_called_once_with(
            "FIFA 16",
            "English Premier League",
            "players.csv",
            headless=True,
            timeout=120,
            delay=2.0,
            continue_on_error=True,
        )

    def test_challenge_state_detects_security_verification_pages(self):
        self.assertEqual(
            _challenge_state(
                "Performing security verification",
                "This website uses a security service to protect against malicious bots.",
                ("performing security verification", "verify you are human"),
            ),
            "challenge",
        )
        self.assertEqual(
            _challenge_state(
                "FIFA Index",
                "FIFA Index - English Premier League",
                ("performing security verification", "verify you are human"),
            ),
            "ready",
        )

    def test_team_player_rows_extracts_player_records_from_team_tables(self):
        html = """
        <html><body>
        <table>
            <tr><th>Num</th><th>Name</th><th>Pos</th><th>Age</th><th>OVR</th><th>POT</th><th>Value</th><th>Wage</th></tr>
            <tr><td>11</td><td>Mesut Özil</td><td>CAM</td><td>26</td><td>88</td><td>89</td><td>€61M</td><td>€3.2M</td></tr>
        </table>
        </body></html>
        """
        soup = __import__("bs4").BeautifulSoup(html, "html.parser")
        records = _team_player_rows(soup)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["player_name"], "Mesut Özil")
        self.assertEqual(records[0]["position"], "CAM")
        self.assertEqual(records[0]["ovr"], 88)

    def test_league_team_urls_extracts_team_links_from_league_pages(self):
        html = """
        <html><body>
        <a href='/teams/1-arsenal/fifa16'>Arsenal</a>
        <a href='/teams/2-chelsea/fifa16'>Chelsea</a>
        </body></html>
        """
        soup = __import__("bs4").BeautifulSoup(html, "html.parser")
        urls = _league_team_urls(soup, "fifa16")
        self.assertEqual(urls[0], "https://fifaindex.com/teams/1-arsenal/fifa16")
        self.assertEqual(urls[1], "https://fifaindex.com/teams/2-chelsea/fifa16")

    def test_try_auto_challenge_click_returns_false_when_no_control_exists(self):
        class FakePage:
            def locator(self, *_args, **_kwargs):
                return self

            def filter(self, *_args, **_kwargs):
                return self

            def count(self):
                return 0

        self.assertFalse(_try_auto_challenge_click(FakePage()))

    def test_extract_team_names_and_urls_from_html(self):
        html = """
        <html><body>
        <a href='/teams/1-arsenal/fifa16'>Arsenal</a>
        <a href='/teams/2-chelsea/fifa16'>Chelsea</a>
        <a href='/leagues/13-england-premier-league-1/fifa16'>League</a>
        </body></html>
        """
        teams = fifaindexscrape.extract_team_links_from_html(html, version="fifa16")
        self.assertEqual(teams[0]["name"], "Arsenal")
        self.assertEqual(teams[0]["url"], "https://fifaindex.com/teams/1-arsenal/fifa16")
        self.assertEqual(teams[1]["name"], "Chelsea")

    def test_get_player_urls_uses_existing_page_object(self):
        class FakePage:
            def goto(self, *_args, **_kwargs):
                return None

            def wait_for_timeout(self, *_args, **_kwargs):
                return None

            def content(self):
                return """
                <html><body>
                <a href='/players/1-mesut-ozil/fifa16'>Mesut Özil</a>
                <a href='/players/2-eden-hazard/fifa16'>Eden Hazard</a>
                </body></html>
                """

        urls = fifaindexscrape.get_player_urls(
            "https://fifaindex.com/teams/1-arsenal/fifa16",
            version="fifa16",
            page=FakePage(),
        )
        self.assertEqual(
            urls,
            [
                "https://fifaindex.com/players/1-mesut-ozil/fifa16",
                "https://fifaindex.com/players/2-eden-hazard/fifa16",
            ],
        )


if __name__ == "__main__":
    unittest.main()
