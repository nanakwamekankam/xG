from sofifa_scraper_production import SoFIFAScraper

scraper = SoFIFAScraper(headless=False)
df = scraper.scrape_league(
    league_name="English Premier League",
    fifa_version="FIFA 16"
)
scraper.close()

# DataFrame will have columns like:
# name, age, team, contract, id, preferred_foot, finishing, etc.