import csv
import sys
from pathlib import Path
from typing import List, Dict

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scapper import fifaindexscrape


DEFAULT_LEAGUE_SLUG = "13-england-premier-league-1"


def scrape_league(
    version: str,
    league_name: str,
    output_path: str = "players.csv",
    headless: bool = True,
    timeout: int = 120,
    delay: float = 2.0,
    continue_on_error: bool = True,
) -> List[Dict[str, object]]:
    """Run the restored team-to-player scrape flow and optionally write a CSV export."""
    league_slug = DEFAULT_LEAGUE_SLUG if league_name.lower() == "english premier league" else league_name.lower().replace(" ", "-")
    results = fifaindexscrape.scrape_team_player_pipeline(league_slug, version, delay_seconds=delay)

    if output_path:
        with open(output_path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["team", "team_url", "player_name", "player_url"])
            writer.writeheader()
            for team_data in results:
                for player in team_data.get("players", []):
                    writer.writerow(
                        {
                            "team": team_data.get("team", ""),
                            "team_url": team_data.get("team_url", ""),
                            "player_name": player.get("name", ""),
                            "player_url": player.get("url", ""),
                        }
                    )

    return results


def main() -> None:
    scrape_league("FIFA 16", "English Premier League", "players.csv", headless=True, timeout=120, delay=2.0, continue_on_error=True)


if __name__ == "__main__":
    main()
