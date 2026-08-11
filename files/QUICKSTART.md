# Quick Start Guide - SoFIFA Scraper

## 🚀 Get Running in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Download ChromeDriver (if needed)
```bash
pip install webdriver-manager
```

### Step 3: Run the Test Suite
```bash
python test_scrapers.py
```

That's it! The test suite will:
1. Run the Modified scraper
2. Run the Production scraper  
3. Compare results
4. Save data to CSV files

---

## 📊 What You Get

A pandas DataFrame with **English Premier League players** from **FIFA 16** containing:

### Player Info
- Player name
- Age
- Team
- Contract status

### Player Attributes
- ID
- Preferred foot
- Finishing
- Heading accuracy
- Volleys
- Shot power
- Long shots
- Attack position
- Penalties
- GK Diving
- GK Handling
- GK Positioning
- GK Reflexes

---

## 💻 Usage Examples

### Use the Production Version (Recommended)

```python
from sofifa_scraper_production import SoFIFAScraper

# Create scraper
scraper = SoFIFAScraper(headless=False)

# Scrape English Premier League for FIFA 16
df = scraper.scrape_league(
    league_name="English Premier League",
    fifa_version="FIFA 16"
)

# Close browser
scraper.close()

# View results
print(df.head())
print(f"Total players: {len(df)}")

# Save to file
df.to_csv("epl_players.csv", index=False)
```

### Change League or Version

```python
# La Liga
df = scraper.scrape_league(
    league_name="La Liga",
    fifa_version="FIFA 16"
)

# Bundesliga with FIFA 20
df = scraper.scrape_league(
    league_name="Bundesliga",
    fifa_version="FIFA 20"
)

# Serie A with FC 24
df = scraper.scrape_league(
    league_name="Serie A",
    fifa_version="FC 24"
)
```

### Run Headless (No Browser Window)

```python
# Faster, quieter execution
scraper = SoFIFAScraper(headless=True)
df = scraper.scrape_league()
scraper.close()
```

### Increase Timeout for Slow Connections

```python
# 20 seconds timeout instead of default 10
scraper = SoFIFAScraper(headless=False, timeout=20)
df = scraper.scrape_league()
scraper.close()
```

---

## 🔍 Comparing the Two Versions

| Aspect | Modified | Production |
|--------|----------|-----------|
| **Beginner-friendly** | ✓ | ✓✓ |
| **Error handling** | Basic | Advanced |
| **Logging/Progress** | Basic | Detailed |
| **Documentation** | Some | Extensive |
| **Type hints** | No | Yes |
| **Recommended for** | Learning | Production use |

**Recommendation:** Start with **Production version** - it has better error handling and won't crash as easily.

---

## 📁 Output Files

After running the test suite, you'll get:

```
~/epl_fifa16_modified_20240115_143022.csv    # Modified version results
~/epl_fifa16_production_20240115_143022.csv  # Production version results
```

Open these in Excel, Google Sheets, or analyze with pandas:

```python
import pandas as pd

df = pd.read_csv("epl_fifa16_production_20240115_143022.csv")

# Get best finishers
top_finishers = df.nlargest(10, 'finishing')[['name', 'team', 'finishing']]
print(top_finishers)

# Get average by team
team_avg = df.groupby('team')[['finishing', 'heading_accuracy', 'shot_power']].mean()
print(team_avg)

# Export specific columns
df[['name', 'team', 'finishing', 'shot_power']].to_csv("strikers.csv")
```

---

## ⚠️ Common Issues & Fixes

### "ChromeDriver not found"
Make sure you installed webdriver-manager:
```bash
pip install webdriver-manager
```

### "Timeout waiting for element"
Your internet might be slow. Increase timeout:
```python
scraper = SoFIFAScraper(timeout=30)
```

### "No data found for the given teams"
The league or FIFA version might not exist. Check the website to verify available options.

### "Getting blocked or CAPTCHA"
Set `headless=False` to see what's happening and add delays. You might need to use a proxy.

---

## 🎯 Next Steps

1. ✅ Install requirements
2. ✅ Run test suite
3. ✅ Review results
4. ✅ Customize for your needs
5. ✅ Integrate into your project

---

## 📚 More Information

See **SETUP_AND_TESTING.md** for:
- Detailed setup instructions
- Advanced customization
- Full troubleshooting guide
- Performance optimization tips

---

## 💡 Tips

- **Watch it work:** Set `headless=False` to see the browser automate
- **Speed it up:** Set `headless=True` for faster execution
- **Save your results:** Always save the CSV file before making changes
- **Test first:** Run on a small league before scraping large datasets
- **Be respectful:** Don't make too many requests in a short time

---

Ready? Start with:
```bash
python test_scrapers.py
```

Good luck! 🎉
