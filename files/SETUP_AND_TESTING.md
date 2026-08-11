# SoFIFA Scraper - Setup & Testing Guide

## Files Overview

You now have three Python files:

1. **`sofifa_scraper_modified.py`** - Initial version with core functionality
2. **`sofifa_scraper_production.py`** - Production version with better error handling and documentation
3. **`test_scrapers.py`** - Test suite to run and compare both versions

## Prerequisites

### 1. Install Required Packages

```bash
pip install selenium pandas lxml
```

### 2. Install ChromeDriver

The scrapers use Selenium with Chrome. You need ChromeDriver:

**Option A: Using WebDriver Manager (Automatic)**
```bash
pip install webdriver-manager
```

Then modify the driver initialization in both scrapers to:
```python
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

service = Service(ChromeDriverManager().install())
self.driver = webdriver.Chrome(service=service, options=options)
```

**Option B: Manual**
1. Download ChromeDriver from: https://chromedriver.chromium.org/
2. Place it in your PATH or specify the path when creating the driver:
```python
self.driver = webdriver.Chrome('/path/to/chromedriver', options=options)
```

## Running Tests

### Method 1: Run Full Test Suite (Recommended)

```bash
cd /home/claude
python test_scrapers.py
```

This will:
- Test the Modified version
- Pause for you to review the browser automation
- Test the Production version
- Compare results side-by-side
- Save both results to CSV with timestamps

### Method 2: Run Individual Scrapers

**Modified Version:**
```bash
python sofifa_scraper_modified.py
```

**Production Version:**
```bash
python sofifa_scraper_production.py
```

### Method 3: Interactive Testing in Python

```python
from sofifa_scraper_production import SoFIFAScraper

# Create scraper instance
scraper = SoFIFAScraper(headless=False)  # headless=True for no browser window

# Scrape data
df = scraper.scrape_league(
    league_name="English Premier League",
    fifa_version="FIFA 16"
)

# Close browser
scraper.close()

# Inspect data
print(df.head())
print(df.info())
print(df.describe())

# Save to CSV
df.to_csv("my_players.csv", index=False)
```

## Expected Output

Both scrapers should return a DataFrame with these columns:

- **name** - Player name
- **age** - Player age
- **team** - Team name
- **contract** - Contract status
- **id** - Player ID
- **preferred_foot** - Left/Right foot
- **finishing** - Finishing rating
- **heading_accuracy** - Heading accuracy rating
- **volleys** - Volleys rating
- **shot_power** - Shot power rating
- **long_shots** - Long shots rating
- **attack_position** - Attack positioning rating
- **penalties** - Penalties rating
- **gk_diving** - Goalkeeper diving rating
- **gk_handling** - Goalkeeper handling rating
- **gk_positioning** - Goalkeeper positioning rating
- **gk_reflexes** - Goalkeeper reflexes rating

## Troubleshooting

### Issue: "ChromeDriver not found"
**Solution:** Install webdriver-manager or download ChromeDriver manually (see Prerequisites)

### Issue: "TimeoutException" when loading pages
**Solution:** 
- Increase the timeout value in the scraper initialization:
  ```python
  scraper = SoFIFAScraper(headless=False, timeout=20)
  ```
- Check your internet connection
- SoFIFA might be rate-limiting - add delays between requests

### Issue: "No such element" or missing attributes
**Solution:**
- The website structure may have changed
- Check the XPath selectors in the `extract_player_attributes()` method
- You may need to inspect the HTML and update the XPath patterns

### Issue: "CAPTCHA detected" or getting blocked
**Solution:**
- Set `headless=False` to see what's happening
- Add delays between requests
- Consider using a proxy (modify the scraper to add proxy support)

## Key Differences Between Versions

| Feature | Modified | Production |
|---------|----------|-----------|
| Error Handling | Basic | Comprehensive try-except blocks |
| Logging | Print statements | Detailed progress tracking |
| Documentation | Basic | Full docstrings & type hints |
| Timeout Handling | Simple | Advanced with fallbacks |
| Code Comments | Minimal | Extensive |
| Return Values | DataFrame | DataFrame + metadata |

## Performance Tips

1. **Use headless mode** for faster execution (set `headless=True`)
2. **Adjust timeout** based on your connection speed
3. **Test with a smaller league first** before running on large leagues
4. **Save results** periodically in case of crashes

## Customization Examples

### Change League
```python
df = scraper.scrape_league(
    league_name="La Liga",  # or "Serie A", "Bundesliga", etc.
    fifa_version="FIFA 16"
)
```

### Change FIFA Version
```python
df = scraper.scrape_league(
    league_name="English Premier League",
    fifa_version="FIFA 17"  # or "FIFA 20", "FC 24", etc.
)
```

### Change Desired Attributes
Edit the `DESIRED_ATTRIBUTES` list in the scraper file:
```python
DESIRED_ATTRIBUTES = [
    "ID",
    "Preferred foot",
    "Pace",  # Add new attributes
    "Dribbling",
    # ... etc
]
```

## Output Files

After running the scrapers, you'll find:

- `epl_fifa16_players.csv` - Single test result
- `epl_fifa16_modified_YYYYMMDD_HHMMSS.csv` - From test suite
- `epl_fifa16_production_YYYYMMDD_HHMMSS.csv` - From test suite

## Next Steps

1. Run the test suite to compare both versions
2. Choose which version works best for you
3. Customize attributes or league as needed
4. Integrate into your project or analysis pipeline

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the console output for specific error messages
3. Try running with `headless=False` to watch the browser automation
4. Inspect the website HTML to verify element locations haven't changed
