import re
import subprocess
import sys
import urllib.request
from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Safari/605.1.15"
)


# def open_fifa_index_page(league: str, version: str ) -> str:
#     """Open FIFA Index and navigate to the requested league/version page."""
#     version = "".join("FIFA 16".lower().split())
#     url = f"https://fifaindex.com/leagues/{league}/{version}"

#     try:
#         with sync_playwright() as playwright:
#             browser = playwright.chromium.launch(headless=False)
#             context = browser.new_context(locale="en-US", viewport={"width": 1440, "height": 900})
#             page = context.new_page()
#             page.goto(url, wait_until="domcontentloaded", timeout=60000)
#             page.wait_for_timeout(5000)
#             title = page.title()
#             browser.close()
#             return f"Opened in Playwright: {title}"
#     except Exception as exc:
#         if sys.platform == "darwin":
#             try:
#                 subprocess.Popen(["open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#                 return f"Opened in system browser: {url}"
#             except Exception:
#                 pass
#         return f"Could not open browser automatically: {exc}"


def extract_team_links_from_html(html: str, version: str) -> List[dict]:
    """Extract team names and FIFA Index URLs from the league page HTML."""
    soup = BeautifulSoup(html, "html.parser")
    teams: List[dict] = []
    seen = set()

    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        if "/teams/" not in href:
            continue

        text = re.sub(r"\s+", " ", link.get_text(" ", strip=True))
        if not text or text.lower() in {"home", "league", "teams", "players"}:
            continue

        absolute_url = urljoin("https://fifaindex.com", href)
        if absolute_url in seen:
            continue

        seen.add(absolute_url)
        teams.append({"name": text, "url": absolute_url})

    if not teams:
        return []

    if version:
        normalized_version = "".join(version.lower().split())
        for team in teams: 
            if f"/{normalized_version}" not in team["url"].lower():
                team["url"] = team["url"].rstrip("/") + f"/{normalized_version}"

    return teams


def get_league_teams(league: str, version: str) -> List[dict]:
    """Return the league teams listed on the FIFA Index league page as name/url pairs."""
    version = "".join(version.lower().split())
    url = f"https://fifaindex.com/leagues/{league}/{version}"

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context(locale="en-US", viewport={"width": 1440, "height": 900})
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)
            html = page.content()
            return extract_team_links_from_html(html, version)
    except Exception:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as response:
                html = response.read().decode("utf-8", errors="ignore")
                return extract_team_links_from_html(html, version)
        except Exception:
            return []


# def visit_team_urls_sequentially(team_urls: List[dict]) -> List[str]:
#     """Open each team URL one by one in a single Playwright session."""
#     visited_pages: List[str] = []
#
#     try:
#         with sync_playwright() as playwright:
#             browser = playwright.chromium.launch(headless=False)
#             context = browser.new_context(locale="en-US", viewport={"width": 1440, "height": 900})
#             page = context.new_page()

#             for team in team_urls:
#                 team_url = team.get("url")
#                 print(f"Visiting team: {team.get('name')} with URL: {team_url}")
#                 if not team_url:
#                     print(f"Skipping {team}: missing URL")
#                     continue
#                 # Goes into the team_url
#                 page.goto(team_url, wait_until="domcontentloaded", timeout=60000)
#                 # page.wait_for_timeout(2000)
#                 # print(f"Visited {team_url}")
#                 # Get code to extract player URLs from the team page if needed


#                 visited_pages.append(team_url)

#             browser.close()
#     except Exception:
#         return []

#     return visited_pages

def extract_player_links_from_html(html: str, version: str | None = None) -> List[dict]:
    """Extract player names and FIFA Index URLs from a team page HTML."""
    print(f"Extracting player links from HTML for version: {version}")
    soup = BeautifulSoup(html, "html.parser")
    players: List[dict] = []
    seen = set()

    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        print("Found link:", href)
        if "/players/" not in href and "/player/" not in href:
            print("Skipping link due to href check:", href)
            continue

        print("good 1: passed href check for link:", href)
        text = re.sub(r"\s+", " ", link.get_text(" ", strip=True))
        if not text or text.lower() in {"home", "league", "teams", "players", "player"}:
            print("Skipping link due to text check:", text)
            continue

        print("good 2: passed text check for link:", text)
        absolute_url = urljoin("https://fifaindex.com", href)
        if absolute_url in seen:
            print("Skipping link due to duplicate URL:", absolute_url)
            continue

        seen.add(absolute_url)
        print("Adding player:", text, "with URL:", absolute_url)
        players.append({"name": text, "url": absolute_url})

    if version:
        normalized_version = "".join(version.lower().split())
        for player in players:
            if f"/{normalized_version}" not in player["url"].lower():
                player["url"] = player["url"].rstrip("/") + f"/{normalized_version}"

    return players


def get_player_urls(team_url: str, version: str | None = None, page: object | None = None) -> List[str]:
    """Return player URLs discovered from a team page."""
    print(f"Extracting player URLs for team: {team.get('name')}")
    if not team_url:
        print(f"Missing team URL: {team_url}")
        return []
        
    players: List[dict] = []

    if page is not None:
        try:
            page.goto(team_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(3000)
            html = page.content()
   
            players.extend(extract_player_links_from_html(html, version))
            return players    
        except Exception:
            return []

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context(locale="en-US", viewport={"width": 1440, "height": 900})
            page = context.new_page()
            page.goto(team_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(3000)
            html = page.content()

            players.extend(extract_player_links_from_html(html, version))
            return players
    except Exception:
        try:
            req = urllib.request.Request(team_url, headers={"User-Agent": DEFAULT_USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as response:
                html = response.read().decode("utf-8", errors="ignore")

                players.extend(extract_player_links_from_html(html, version))
                return players
        except Exception:
            return []


def visit_team_and_player_urls(teams: List[dict], version: str, delay_seconds: float = 5.0) -> List[dict]:
    """Visit each team URL, then visit every player URL for that team before moving on."""
    collected: List[dict] = []
    version = "".join(version.lower().split())

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context(locale="en-US", viewport={"width": 1440, "height": 900})
            page = context.new_page()

            for team in teams:
                team_url = team.get("url")
                if not team_url:
                    print(f"Skipping {team['name']} with missing URL: {team_url}")
                    continue
                
                page.goto(team_url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(int(delay_seconds * 1000))
                print(f"Visiting team: {team.get('name')} with URL: {team_url}")

                player_urls = get_player_urls(team_url, version, page)
                collected.append({"team": team.get("name"), "players": list(player_urls.values())})

                for player_url in player_urls.values():
                    page.goto(player_url, wait_until="domcontentloaded", timeout=60000)
                    page.wait_for_timeout(int(delay_seconds * 1000))
    
            browser.close()
    except Exception:
        return collected

    return collected


if __name__ == "__main__":
    league = "13-england-premier-league-1"
    version = "FIFA 16"
    teams = get_league_teams(league, version) # returns a list of team dictionaries with "name" and "url" keys
    if teams:
        print("\nTeams in the league:")
        for index, team in enumerate(teams, 1):
            print(f"{index}. {team['name']} -> {team['url']}")
        print(f"\nTotal teams found: {len(teams)}")
        print("----------------------------------------------------------------------------------\n")

        # visited = visit_team_urls_sequentially(teams)
        # if visited:
        #     print("\nVisited team URLs sequentially:")
        #     for index, url in enumerate(visited, 1):
        #         print(f"{index}. {url}")
        # print(f"\nTotal team URLs visited: {len(visited)}")

        players_by_team = visit_team_and_player_urls(teams, version)
        print("\n----------------------------------------------------------------------------------\n")
        if players_by_team:
            print("\nPlayers discovered by team:")
            for team_data in players_by_team:
                print(f"- {team_data['team']}: {len(team_data['players'])} player URLs")
                for player_url in team_data["players"][:3]:
                    print(f"  • {player_url}")
    else:
        print("No team links were found on the page. FIFA Index may be blocking automated access from this environment.")
