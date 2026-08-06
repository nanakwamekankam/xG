from fifascrapper import scrape_league

df = scrape_league(
    "FIFA 16",
    "English Premier League",
    "players.csv",
    headless=True,
)