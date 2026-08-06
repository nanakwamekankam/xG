"""Scrape every player in a FIFA Index league.

Example
-------
pip install -r requirements.txt
playwright install chromium
python fifascrapper.py "FIFA 16" "English Premier League" players.csv

FIFA Index is an external site.  Please use a sensible delay and comply with its
terms of service and robots.txt when running this program.
"""

from __future__ import annotations

import argparse
import logging
import re
import unicodedata
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlparse

import pandas as pd
from bs4 import BeautifulSoup, Tag
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, sync_playwright


BASE_URL = "https://fifaindex.com"
CARD_NAMES = (
    "Profile",
    "Pace",
    "Shooting",
    "Passing",
    "Dribbling",
    "Defending",
    "Physical",
    "Goal Keeping",
)
MAIN_COLUMNS = [
    "player_name", "position", "ovr", "pot", "age", "height_cm",
    "weight_kg", "value", "wage",
]
LOGGER = logging.getLogger("fifascrapper")


def normalize_version(version: str) -> str:
    """Turn strings such as ``' FC 25 '`` into FIFA Index's ``'fc25'``."""
    normalized = re.sub(r"[^a-z0-9]", "", version.strip().lower())
    if not re.fullmatch(r"(?:fc|fifa)\d{2}", normalized):
        raise ValueError(
            "Version must look like 'FC 24', 'FC25', 'FIFA 16', or 'fifa24'."
        )
    return normalized


def _plain_key(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _league_key(value: str) -> str:
    key = re.sub(r"\b\d+\s+teams?\b", "", _plain_key(value))
    words = ["england" if word == "english" else word for word in key.split()]
    return " ".join(word for word in words if not word.isdigit())


def _column_part(value: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", unicodedata.normalize("NFKD", value))
    return "_".join(word.capitalize() for word in words)


def _versioned_url(href: str, version: str) -> str:
    """Return an absolute URL with exactly one version suffix."""
    path = urlparse(urljoin(BASE_URL, href)).path.rstrip("/")
    path = re.sub(r"/(?:fc|fifa)\d{2}$", "", path, flags=re.I)
    return f"{BASE_URL}{path}/{version}"


def _get_soup(page: Page, url: str, timeout: float) -> BeautifulSoup:
    """Navigate a real browser page and return its rendered DOM."""
    timeout_ms = max(1, int(timeout * 1000))
    try:
        response = page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        # Give JavaScript challenges and client-side rendering a chance to finish.
        page.locator("h1").first.wait_for(state="visible", timeout=timeout_ms)
    except PlaywrightTimeoutError as exc:
        raise RuntimeError(f"Timed out loading {url} in Chromium") from exc

    challenge_markers = (
        "just a moment", "verify you are human", "attention required",
        "access denied", "enable javascript and cookies",
    )
    title = page.title().lower()
    body_text = page.locator("body").inner_text(timeout=timeout_ms).lower()
    challenged = any(
        marker in title or marker in body_text[:2000]
        for marker in challenge_markers
    )
    if challenged:
        LOGGER.info("Waiting for the browser challenge to be completed...")
        try:
            page.wait_for_function(
                """markers => {
                    const text = `${document.title} ${document.body?.innerText || ''}`
                        .slice(0, 2500).toLowerCase();
                    return document.querySelector('h1') &&
                        !markers.some(marker => text.includes(marker));
                }""",
                arg=list(challenge_markers),
                timeout=timeout_ms,
            )
        except PlaywrightTimeoutError as exc:
            raise RuntimeError(
                f"The FIFA Index browser challenge at {url} was not completed. "
                "Leave headless=False and complete the challenge in the window."
            ) from exc
        title = page.title().lower()
        body_text = page.locator("body").inner_text(timeout=timeout_ms).lower()

    valid_site_page = "fifa index" in title and "fifa index" in body_text[:2000]
    if response is not None and response.status >= 400 and not valid_site_page:
        raise RuntimeError(f"HTTP {response.status} while loading {url} in Chromium")
    return BeautifulSoup(page.content(), "html.parser")


def find_league_url(
    page: Page, version: str, league_name: str, timeout: float = 30
) -> str:
    """Resolve a human-readable league name to its FIFA Index league URL."""
    target = _league_key(league_name)
    candidates: dict[str, tuple[str, str]] = {}
    next_url: str | None = f"{BASE_URL}/leagues/{version}"
    visited: set[str] = set()

    while next_url and next_url not in visited:
        visited.add(next_url)
        soup = _get_soup(page, next_url, timeout)
        for link in soup.select('a[href*="/leagues/"]'):
            href = link.get("href", "")
            if not re.search(r"/leagues/\d+-", href):
                continue
            name = link.get_text(" ", strip=True)
            candidates[_league_key(name)] = (name, _versioned_url(href, version))

        page_link = soup.select_one('a[rel="next"], .pagination .next a')
        next_url = urljoin(BASE_URL, page_link["href"]) if page_link else None

    if target in candidates:
        return candidates[target][1]

    # Accommodate inputs such as "English Premier League" versus the site's
    # "England Premier League (1)" without silently selecting an unrelated league.
    target_words = set(target.split()) - {"english", "england", "the", "league"}
    ranked = sorted(
        (
            len(target_words & (set(key.split()) - {"english", "england", "the", "league"})),
            name,
            url,
        )
        for key, (name, url) in candidates.items()
    )
    if ranked and ranked[-1][0] >= max(1, len(target_words)):
        return ranked[-1][2]
    available = ", ".join(name for name, _ in list(candidates.values())[:15])
    raise ValueError(f"League {league_name!r} was not found. Examples: {available}")


def _links(soup: BeautifulSoup, kind: str, version: str) -> list[str]:
    pattern = re.compile(rf"/{re.escape(kind)}/\d+-", re.I)
    found: list[str] = []
    seen: set[str] = set()
    for link in soup.find_all("a", href=pattern):
        url = _versioned_url(link["href"], version)
        if url not in seen:
            seen.add(url)
            found.append(url)
    return found


def _star_count(node: Tag) -> int | None:
    stars = node.select(
        ".fa-star, .icon-star, [class*='star-full'], [class*='star-filled'], "
        "[data-icon='star']"
    )
    if not stars:
        return None
    shaded = 0
    for star in stars:
        classes = {str(c).lower() for c in star.get("class", [])}
        class_text = " ".join(classes)
        unfilled = any(x in class_text for x in ("far", "regular", "empty", "muted", "outline"))
        if not unfilled:
            shaded += 1
    return shaded


def _value_from_node(node: Tag) -> str | int:
    stars = _star_count(node)
    if stars is not None:
        return stars
    return node.get_text(" ", strip=True)


def _row_pair(row: Tag) -> tuple[str, str | int] | None:
    """Extract a label/value pair from a FIFA Index card row."""
    value_node = row.select_one(
        ".float-right, .float-end, [class*='text-right'], [class*='text-end'], "
        ".badge, dd, .value"
    )
    if value_node is not None:
        value = _value_from_node(value_node)
        clone = BeautifulSoup(str(row), "html.parser")
        clone_value = clone.select_one(
            ".float-right, .float-end, [class*='text-right'], [class*='text-end'], "
            ".badge, dd, .value"
        )
        if clone_value:
            clone_value.decompose()
        label = clone.get_text(" ", strip=True)
        if label and str(value).strip():
            return label, value

    cells = row.find_all(["th", "td", "dt", "dd"], recursive=False)
    if len(cells) >= 2:
        return cells[0].get_text(" ", strip=True), _value_from_node(cells[-1])
    return None


def _card_container(heading: Tag) -> Tag:
    card = heading.find_parent(class_=re.compile(r"(?:^|\s)card(?:\s|$)"))
    if card:
        return card
    return heading.parent if isinstance(heading.parent, Tag) else heading


def _extract_card(soup: BeautifulSoup, card_name: str) -> dict[str, object]:
    heading = next(
        (h for h in soup.find_all(re.compile(r"^h[2-6]$"))
         if _plain_key(h.get_text(" ", strip=True)).replace(" ", "")
         == _plain_key(card_name).replace(" ", "")),
        None,
    )
    if heading is None:
        return {}
    container = _card_container(heading)
    result: dict[str, object] = {}
    if card_name != "Profile":
        for element in container.find_all(["p", "span", "div"], recursive=True):
            if element.find(True, recursive=False):
                continue
            score = element.get_text(" ", strip=True)
            if re.fullmatch(r"\d{1,3}", score):
                result[f"{_column_part(card_name)}_Overall"] = int(score)
                break
    rows: Iterable[Tag] = container.select("p, tr, dl, li")
    for row in rows:
        pair = _row_pair(row)
        if not pair:
            continue
        label, value = pair
        label = re.sub(r"\s+", " ", label).strip(" :-")
        if not label or _plain_key(label) == _plain_key(card_name):
            continue
        column = f"{_column_part(card_name)}_{_column_part(label)}"
        result[column] = _coerce_number(value)
    return result


def _coerce_number(value: object) -> object:
    if isinstance(value, (int, float)):
        return value
    text = str(value).strip()
    return int(text) if re.fullmatch(r"-?\d+", text) else text


def _nearby_value(soup: BeautifulSoup, label: str) -> object:
    label_node = soup.find(string=lambda s: bool(s and s.strip().lower() == label.lower()))
    if label_node is None:
        return 0
    node = label_node.parent
    for candidate in (node.find_next_sibling(), node.parent.find_next_sibling() if node.parent else None):
        if isinstance(candidate, Tag):
            match = re.search(r"(?:€|£|\$)?[\d,.]+(?:[KMB])?(?:/wk)?", candidate.get_text(" ", strip=True), re.I)
            if match:
                return _coerce_number(match.group(0))
    # Common layout: the label and value are separate descendants of one tile.
    parent = node.parent
    if isinstance(parent, Tag):
        text = parent.get_text(" ", strip=True)
        match = re.search(rf"{re.escape(label)}\s*((?:€|£|\$)?[\d,.]+(?:[KMB])?(?:/wk)?)", text, re.I)
        if match:
            return _coerce_number(match.group(1))
    return 0


def parse_player(soup: BeautifulSoup) -> dict[str, object]:
    """Parse one player page into a flat record."""
    heading = soup.find("h1")
    if heading is None:
        raise ValueError("Player page has no h1 heading (site layout may have changed).")
    top_text = " ".join(soup.get_text(" ", strip=True).split())
    physical = re.search(r"(\d{1,2})\s*y\.o\.\s*(\d{3})\s*cm\s*(\d{2,3})\s*kg", top_text, re.I)

    # The position is the first football-position token following the player h1.
    after_heading = " ".join(
        str(x) for x in list(heading.parent.stripped_strings)[1:12]
    ) if heading.parent else ""
    pos = re.search(r"\b(GK|R?WB|L?WB|CB|LB|RB|CDM|CM|CAM|LM|RM|LW|RW|CF|ST)\b", after_heading)

    record: dict[str, object] = {
        "player_name": heading.get_text(" ", strip=True),
        "position": pos.group(1) if pos else "",
        "ovr": _nearby_value(soup, "OVR"),
        "pot": _nearby_value(soup, "POT"),
        "age": int(physical.group(1)) if physical else 0,
        "height_cm": int(physical.group(2)) if physical else 0,
        "weight_kg": int(physical.group(3)) if physical else 0,
        "value": _nearby_value(soup, "Value"),
        "wage": _nearby_value(soup, "Wage"),
    }
    for card_name in CARD_NAMES:
        record.update(_extract_card(soup, card_name))
    return record


def _save_frame(frame: pd.DataFrame, output_path: str | Path) -> None:
    path = Path(output_path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        frame.to_csv(path, index=False)
    elif suffix in {".xlsx", ".xls"}:
        frame.to_excel(path, index=False)
    elif suffix == ".parquet":
        frame.to_parquet(path, index=False)
    elif suffix == ".json":
        frame.to_json(path, orient="records", force_ascii=False, indent=2)
    elif suffix in {".pkl", ".pickle"}:
        frame.to_pickle(path)
    else:
        raise ValueError("Output extension must be csv, xlsx, parquet, json, or pickle.")


def scrape_league(
    fifa_version: str,
    league_name: str,
    output_path: str | Path,
    *,
    delay: float = 1.0,
    timeout: float = 30,
    continue_on_error: bool = True,
    headless: bool = False,
    page: Page | None = None,
) -> pd.DataFrame:
    """Scrape all teams and players in a league, save, and return a DataFrame.

    By default a visible Chromium window is used because it is less likely to be
    rejected than a raw HTTP client.  Pass an existing Playwright ``page`` to
    reuse a browser managed by the caller; otherwise this function owns and
    closes the browser it launches.
    """
    version = normalize_version(fifa_version)
    if page is None:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=headless)
            context = browser.new_context(locale="en-US")
            owned_page = context.new_page()
            try:
                return _scrape_league_with_page(
                    owned_page, version, league_name, output_path,
                    delay, timeout, continue_on_error,
                )
            finally:
                context.close()
                browser.close()
    return _scrape_league_with_page(
        page, version, league_name, output_path, delay, timeout, continue_on_error
    )


def _scrape_league_with_page(
    page: Page,
    version: str,
    league_name: str,
    output_path: str | Path,
    delay: float,
    timeout: float,
    continue_on_error: bool,
) -> pd.DataFrame:
    league_url = find_league_url(page, version, league_name, timeout)
    LOGGER.info("League: %s", league_url)
    league_soup = _get_soup(page, league_url, timeout)
    team_urls = _links(league_soup, "teams", version)
    if not team_urls:
        raise RuntimeError(f"No team links found at {league_url}")

    player_urls: list[str] = []
    seen_players: set[str] = set()
    for number, team_url in enumerate(team_urls, 1):
        LOGGER.info("Team %d/%d: %s", number, len(team_urls), team_url)
        team_soup = _get_soup(page, team_url, timeout)
        for player_url in _links(team_soup, "players", version):
            if player_url not in seen_players:
                seen_players.add(player_url)
                player_urls.append(player_url)
        page.wait_for_timeout(max(0, delay) * 1000)

    records: list[dict[str, object]] = []
    for number, player_url in enumerate(player_urls, 1):
        LOGGER.info("Player %d/%d: %s", number, len(player_urls), player_url)
        try:
            record = parse_player(_get_soup(page, player_url, timeout))
            record["source_url"] = player_url
            records.append(record)
        except Exception as exc:
            if not continue_on_error:
                raise
            LOGGER.warning("Skipping %s: %s", player_url, exc)
        page.wait_for_timeout(max(0, delay) * 1000)

    frame = pd.DataFrame.from_records(records)
    if frame.empty:
        raise RuntimeError("No player records were scraped; no output was written.")

    # A non-goalkeeper has no Goal Keeping card; a goalkeeper may lack outfield
    # cards.  Missing numeric card attributes are explicitly represented as zero.
    attribute_columns = [
        column for column in frame.columns
        if any(column.startswith(f"{_column_part(card)}_") for card in CARD_NAMES[1:])
    ]
    frame[attribute_columns] = frame[attribute_columns].fillna(0)
    ordered = MAIN_COLUMNS + sorted(c for c in frame.columns if c not in MAIN_COLUMNS)
    frame = frame.reindex(columns=ordered)
    _save_frame(frame, output_path)
    return frame


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fifa_version", help="For example: 'FC 25' or 'FIFA 16'")
    parser.add_argument("league_name", help="For example: 'English Premier League'")
    parser.add_argument("output_path", help="CSV, XLSX, Parquet, JSON, or pickle path")
    parser.add_argument("--delay", type=float, default=1.0, help="Seconds between requests")
    parser.add_argument("--timeout", type=float, default=30.0, help="Request timeout in seconds")
    parser.add_argument("--headless", action="store_true", help="Run Chromium without a window")
    parser.add_argument("--fail-fast", action="store_true", help="Stop on the first player error")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    frame = scrape_league(
        args.fifa_version,
        args.league_name,
        args.output_path,
        delay=args.delay,
        timeout=args.timeout,
        continue_on_error=not args.fail_fast,
        headless=args.headless,
    )
    LOGGER.info("Saved %d players to %s", len(frame), args.output_path)


if __name__ == "__main__":
    main()
