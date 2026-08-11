"""Modified Scraper for sofifa.com - English Premier League FIFA 16."""

import re
from lxml import html
import pandas as pd
from pathlib import Path

# Configuration
SO_FIFA_API = "https://sofifa.com"
DATA_DIR = Path.home() / "soccerdata" / "data" / "SoFIFA"

# Desired attributes to extract from player pages
DESIRED_ATTRIBUTES = [
    "ID",
    "Preferred foot",
    "Finishing",
    "Heading accuracy",
    "Volleys",
    "Shot power",
    "Long shots",
    "Attack position",
    "Penalties",
    "GK Diving",
    "GK Handling",
    "GK Positioning",
    "GK Reflexes",
]


class SoFIFAScraper:
    """Scraper for SoFIFA data with Selenium support."""
    
    def __init__(self, headless=True):
        """Initialize the scraper with Selenium."""
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import Select
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        self.By = By
        self.Select = Select
        self.WebDriverWait = WebDriverWait
        self.EC = EC
        
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(options=options)
    
    def navigate_to_league_version(self, league_name="English Premier League", fifa_version="FIFA 16"):
        """Navigate to the specific league and FIFA version."""
        print(f"Navigating to {league_name} - {fifa_version}...")
        
        # Start at the main SoFIFA page
        self.driver.get(SO_FIFA_API)
        
        # Wait for the page to load and find the version dropdown
        version_select = self.WebDriverWait(self.driver, 10).until(
            self.EC.presence_of_element_located((self.By.XPATH, "//header/section/p/select[1]"))
        )
        
        # Select the FIFA version
        version_dropdown = self.Select(version_select)
        version_dropdown.select_by_visible_text(fifa_version)
        
        # Wait for the page to update after version selection
        self.WebDriverWait(self.driver, 10).until(
            self.EC.staleness_of(version_select)
        )
        
        print(f"✓ Selected {fifa_version}")
        
        # Now find and select the league
        # This might require waiting for the page to fully load
        league_select = self.WebDriverWait(self.driver, 10).until(
            self.EC.presence_of_element_located((self.By.XPATH, "//header/section/p/select[2]"))
        )
        
        league_dropdown = self.Select(league_select)
        league_dropdown.select_by_visible_text(league_name)
        
        print(f"✓ Selected {league_name}")
        
        # Wait for the teams page to load
        self.WebDriverWait(self.driver, 10).until(
            self.EC.staleness_of(league_select)
        )
    
    def get_team_links(self):
        """Extract all team links from the league page."""
        tree = html.fromstring(self.driver.page_source)
        teams = []
        
        # Extract team links from the table
        for row in tree.xpath("//table/tbody/tr"):
            team_link = row.xpath(".//td[2]//a")
            if team_link:
                team_name = team_link[0].text
                team_href = team_link[0].get("href")
                teams.append({"name": team_name, "url": SO_FIFA_API + team_href})
        
        print(f"✓ Found {len(teams)} teams")
        return teams
    
    def get_player_links_from_team(self, team_url):
        """Extract all player links from a team page."""
        self.driver.get(team_url)
        
        # Wait for the player table to load
        self.WebDriverWait(self.driver, 10).until(
            self.EC.presence_of_element_located((self.By.XPATH, "//article/table"))
        )
        
        tree = html.fromstring(self.driver.page_source)
        players = []
        
        # Extract player links and basic info
        for row in tree.xpath("//article/table//tbody/tr"):
            cells = row.xpath(".//td")
            
            # Get player link
            player_link = row.xpath(".//td[2]/a[contains(@href,'/player/')]")
            if not player_link:
                continue
            
            player_name = player_link[0].get("data-tippy-content")
            player_href = player_link[0].get("href")
            
            # Extract age (usually in 3rd column)
            age = cells[2].text.strip() if len(cells) > 2 else None
            
            # Extract contract info (usually last column)
            contract = cells[-1].text.strip() if len(cells) > 0 else None
            
            players.append({
                "name": player_name,
                "age": age,
                "contract": contract,
                "url": SO_FIFA_API + player_href
            })
        
        return players
    
    def extract_player_attributes(self, player_url):
        """Extract specific attributes from a player's profile page."""
        self.driver.get(player_url)
        
        # Wait for the profile to load
        self.WebDriverWait(self.driver, 10).until(
            self.EC.presence_of_element_located((self.By.XPATH, "//div[contains(@class, 'profile')]"))
        )
        
        tree = html.fromstring(self.driver.page_source)
        attributes = {}
        
        # Extract attributes using multiple XPath strategies
        for attr_name in DESIRED_ATTRIBUTES:
            value = None
            
            # Try different XPath patterns to find the attribute
            xpaths = [
                f"//p[.//text()[contains(.,'{attr_name}')]]/span/em",
                f"//div[contains(.,'{attr_name}')]/em",
                f"//li[not(self::script)][.//text()[contains(.,'{attr_name}')]]/em",
            ]
            
            for xpath in xpaths:
                nodes = tree.xpath(xpath)
                if nodes:
                    value = nodes[0].text.strip()
                    break
            
            attributes[attr_name] = value
        
        return attributes
    
    def scrape_league(self, league_name="English Premier League", fifa_version="FIFA 16"):
        """Scrape all players and their attributes from a league."""
        
        # Navigate to the league and version
        self.navigate_to_league_version(league_name, fifa_version)
        
        # Get all teams
        teams = self.get_team_links()
        
        all_players = []
        
        for i, team in enumerate(teams):
            print(f"\n[{i+1}/{len(teams)}] Scraping team: {team['name']}")
            
            # Get players from this team
            players = self.get_player_links_from_team(team["url"])
            print(f"  Found {len(players)} players")
            
            for j, player in enumerate(players):
                print(f"    [{j+1}/{len(players)}] Scraping: {player['name']}")
                
                # Extract attributes from player profile
                attributes = self.extract_player_attributes(player["url"])
                
                # Combine player info with attributes
                player_data = {
                    "name": player["name"],
                    "age": player["age"],
                    "team": team["name"],
                    "contract": player["contract"],
                    **attributes
                }
                
                all_players.append(player_data)
        
        # Create DataFrame
        df = pd.DataFrame(all_players)
        
        # Standardize column names (convert to lowercase, replace spaces with underscores)
        df.columns = [col.lower().replace(" ", "_") for col in df.columns]
        
        return df
    
    def close(self):
        """Close the browser."""
        self.driver.quit()


def main():
    """Main execution function."""
    scraper = SoFIFAScraper(headless=False)  # Set to True for headless mode
    
    try:
        # Scrape English Premier League for FIFA 16
        df = scraper.scrape_league(
            league_name="English Premier League",
            fifa_version="FIFA 16"
        )
        
        print("\n" + "="*80)
        print("Scraping Complete!")
        print("="*80)
        print(f"\nDataFrame shape: {df.shape}")
        print(f"\nColumns: {list(df.columns)}")
        print(f"\nFirst few rows:\n{df.head()}")
        
        # Save to CSV
        output_path = Path.home() / "epl_fifa16_players.csv"
        df.to_csv(output_path, index=False)
        print(f"\n✓ Saved to: {output_path}")
        
        return df
    
    finally:
        scraper.close()


if __name__ == "__main__":
    df = main()
