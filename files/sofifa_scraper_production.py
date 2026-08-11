"""
SoFIFA Player Data Scraper - Production Version
Extracts specific player attributes from sofifa.com for a given league and FIFA version.
"""

import re
from pathlib import Path
from typing import List, Dict, Optional
from lxml import html
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


# Configuration
SO_FIFA_API = "https://sofifa.com"
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
    """
    Web scraper for SoFIFA player data.
    
    Extracts player information and specific attributes from sofifa.com
    for a given league and FIFA/FC version.
    """
    
    def __init__(self, headless: bool = True, timeout: int = 10):
        """
        Initialize the scraper.
        
        Parameters
        ----------
        headless : bool, default True
            Run Chrome in headless mode
        timeout : int, default 10
            Timeout in seconds for WebDriverWait operations
        """
        self.timeout = timeout
        self.setup_driver(headless)
    
    def setup_driver(self, headless: bool = True):
        """Setup Chrome WebDriver with appropriate options."""
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("start-maximized")
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, self.timeout)
    
    def navigate_to_league_version(
        self, 
        league_name: str = "English Premier League", 
        fifa_version: str = "FIFA 16"
    ) -> bool:
        """
        Navigate to the specified league and FIFA version.
        
        Parameters
        ----------
        league_name : str
            Name of the league to select
        fifa_version : str
            FIFA/FC version to select
            
        Returns
        -------
        bool
            True if navigation was successful
        """
        try:
            print(f"Navigating to {league_name} - {fifa_version}...")
            self.driver.get(SO_FIFA_API)
            
            # Select FIFA version
            version_select = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//header/section/p/select[1]"))
            )
            version_dropdown = Select(version_select)
            version_dropdown.select_by_visible_text(fifa_version)
            print(f"✓ Selected {fifa_version}")
            
            # Wait for page update and select league
            self.wait.until(EC.staleness_of(version_select))
            
            league_select = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//header/section/p/select[2]"))
            )
            league_dropdown = Select(league_select)
            league_dropdown.select_by_visible_text(league_name)
            print(f"✓ Selected {league_name}")
            
            # Wait for teams page to load
            self.wait.until(EC.staleness_of(league_select))
            return True
            
        except TimeoutException as e:
            print(f"✗ Error: Timeout during navigation - {e}")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def get_team_links(self) -> List[Dict[str, str]]:
        """
        Extract all team links from the current league page.
        
        Returns
        -------
        List[Dict[str, str]]
            List of dicts with 'name' and 'url' keys
        """
        try:
            tree = html.fromstring(self.driver.page_source)
            teams = []
            
            for row in tree.xpath("//table/tbody/tr"):
                team_link = row.xpath(".//td[2]//a")
                if team_link:
                    team_name = team_link[0].text
                    team_href = team_link[0].get("href")
                    teams.append({
                        "name": team_name,
                        "url": SO_FIFA_API + team_href
                    })
            
            print(f"✓ Found {len(teams)} teams")
            return teams
        
        except Exception as e:
            print(f"✗ Error extracting team links: {e}")
            return []
    
    def get_player_links_from_team(self, team_url: str) -> List[Dict[str, Optional[str]]]:
        """
        Extract player information from a team page.
        
        Parameters
        ----------
        team_url : str
            URL of the team page
            
        Returns
        -------
        List[Dict[str, Optional[str]]]
            List of player dicts with 'name', 'age', 'contract', 'url' keys
        """
        try:
            self.driver.get(team_url)
            
            # Wait for table to load
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//article/table"))
            )
            
            tree = html.fromstring(self.driver.page_source)
            players = []
            
            for row in tree.xpath("//article/table//tbody/tr"):
                cells = row.xpath(".//td")
                player_link = row.xpath(".//td[2]/a[contains(@href,'/player/')]")
                
                if not player_link:
                    continue
                
                player_name = player_link[0].get("data-tippy-content")
                player_href = player_link[0].get("href")
                
                # Extract age and contract
                age = cells[2].text.strip() if len(cells) > 2 else None
                contract = cells[-1].text.strip() if len(cells) > 0 else None
                
                players.append({
                    "name": player_name,
                    "age": age,
                    "contract": contract,
                    "url": SO_FIFA_API + player_href
                })
            
            return players
        
        except TimeoutException:
            print(f"  ✗ Timeout loading team page")
            return []
        except Exception as e:
            print(f"  ✗ Error extracting players: {e}")
            return []
    
    def extract_player_attributes(self, player_url: str) -> Dict[str, Optional[str]]:
        """
        Extract specific attributes from a player's profile page.
        
        Parameters
        ----------
        player_url : str
            URL of the player profile
            
        Returns
        -------
        Dict[str, Optional[str]]
            Dictionary with attribute names as keys and values
        """
        try:
            self.driver.get(player_url)
            
            # Wait for profile to load
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'profile')]"))
            )
            
            tree = html.fromstring(self.driver.page_source)
            attributes = {}
            
            for attr_name in DESIRED_ATTRIBUTES:
                value = None
                
                # Try multiple XPath patterns
                xpaths = [
                    f"//p[.//text()[contains(.,'{attr_name}')]]/span/em",
                    f"//div[contains(.,'{attr_name}')]/em",
                    f"//li[not(self::script)][.//text()[contains(.,'{attr_name}')]]/em",
                ]
                
                for xpath in xpaths:
                    try:
                        nodes = tree.xpath(xpath)
                        if nodes:
                            value = nodes[0].text.strip()
                            break
                    except:
                        continue
                
                attributes[attr_name] = value
            
            return attributes
        
        except TimeoutException:
            print(f"    ✗ Timeout loading player profile")
            return {attr: None for attr in DESIRED_ATTRIBUTES}
        except Exception as e:
            print(f"    ✗ Error extracting attributes: {e}")
            return {attr: None for attr in DESIRED_ATTRIBUTES}
    
    def scrape_league(
        self, 
        league_name: str = "English Premier League", 
        fifa_version: str = "FIFA 16"
    ) -> pd.DataFrame:
        """
        Scrape all players from a league.
        
        Parameters
        ----------
        league_name : str
            Name of the league
        fifa_version : str
            FIFA/FC version
            
        Returns
        -------
        pd.DataFrame
            DataFrame with player data and attributes
        """
        # Navigate to league
        if not self.navigate_to_league_version(league_name, fifa_version):
            return pd.DataFrame()
        
        # Get teams
        teams = self.get_team_links()
        if not teams:
            return pd.DataFrame()
        
        all_players = []
        total_teams = len(teams)
        
        for i, team in enumerate(teams, 1):
            print(f"\n[{i}/{total_teams}] Scraping team: {team['name']}")
            
            # Get players from team
            players = self.get_player_links_from_team(team["url"])
            total_players = len(players)
            print(f"  Found {total_players} players")
            
            for j, player in enumerate(players, 1):
                # Extract attributes
                attributes = self.extract_player_attributes(player["url"])
                
                # Combine data
                player_data = {
                    "name": player["name"],
                    "age": player["age"],
                    "team": team["name"],
                    "contract": player["contract"],
                    **attributes
                }
                
                all_players.append(player_data)
                
                # Print progress
                if j % 5 == 0 or j == total_players:
                    print(f"    [{j}/{total_players}] Processed")
        
        # Create DataFrame
        df = pd.DataFrame(all_players)
        
        # Standardize column names
        df.columns = [col.lower().replace(" ", "_") for col in df.columns]
        
        print("\n" + "="*80)
        print("Scraping Complete!")
        print("="*80)
        print(f"DataFrame shape: {df.shape}")
        print(f"\nColumns:\n{list(df.columns)}")
        
        return df
    
    def close(self):
        """Close the browser."""
        if hasattr(self, 'driver'):
            self.driver.quit()
            print("\n✓ Browser closed")


def main():
    """Main execution function."""
    scraper = SoFIFAScraper(headless=False)  # Set to True for headless mode
    
    try:
        # Scrape data
        df = scraper.scrape_league(
            league_name="English Premier League",
            fifa_version="FIFA 16"
        )
        
        if not df.empty:
            print(f"\nFirst few rows:\n{df.head()}\n")
            
            # Save to CSV
            output_path = Path.home() / "epl_fifa16_players.csv"
            df.to_csv(output_path, index=False)
            print(f"✓ Saved to: {output_path}")
        else:
            print("✗ No data was scraped")
        
        return df
    
    finally:
        scraper.close()


if __name__ == "__main__":
    df = main()
