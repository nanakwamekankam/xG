"""
Test script to run both SoFIFA scraper versions and compare results.
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime


def test_modified_version():
    """Test the modified scraper version."""
    print("\n" + "="*80)
    print("TESTING: Modified Version (sofifa_scraper_modified.py)")
    print("="*80)
    
    try:
        from sofifa_scraper_modified import SoFIFAScraper
        
        scraper = SoFIFAScraper(headless=False)
        
        df = scraper.scrape_league(
            league_name="English Premier League",
            fifa_version="FIFA 16"
        )
        
        scraper.close()
        
        return {
            "version": "Modified",
            "success": True,
            "dataframe": df,
            "shape": df.shape,
            "columns": list(df.columns),
            "errors": None
        }
    
    except Exception as e:
        print(f"\n✗ Modified version failed: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "version": "Modified",
            "success": False,
            "dataframe": None,
            "shape": None,
            "columns": None,
            "errors": str(e)
        }


def test_production_version():
    """Test the production scraper version."""
    print("\n" + "="*80)
    print("TESTING: Production Version (sofifa_scraper_production.py)")
    print("="*80)
    
    try:
        from sofifa_scraper_production import SoFIFAScraper
        
        scraper = SoFIFAScraper(headless=False)
        
        df = scraper.scrape_league(
            league_name="English Premier League",
            fifa_version="FIFA 16"
        )
        
        scraper.close()
        
        return {
            "version": "Production",
            "success": True,
            "dataframe": df,
            "shape": df.shape,
            "columns": list(df.columns),
            "errors": None
        }
    
    except Exception as e:
        print(f"\n✗ Production version failed: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "version": "Production",
            "success": False,
            "dataframe": None,
            "shape": None,
            "columns": None,
            "errors": str(e)
        }


def print_results(results):
    """Print test results summary."""
    print("\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80)
    
    for result in results:
        version = result["version"]
        success = result["success"]
        
        print(f"\n{version} Version:")
        print("-" * 40)
        
        if success:
            print(f"  ✓ Success: YES")
            print(f"  ✓ Shape: {result['shape']} (rows, columns)")
            print(f"  ✓ Columns ({len(result['columns'])}):")
            for col in result['columns']:
                print(f"      - {col}")
            print(f"\n  Sample data (first 3 rows):")
            print(f"  {result['dataframe'].head(3).to_string()}")
        else:
            print(f"  ✗ Success: NO")
            print(f"  ✗ Error: {result['errors']}")


def compare_results(results):
    """Compare the two test results."""
    print("\n" + "="*80)
    print("COMPARISON")
    print("="*80)
    
    if all(r["success"] for r in results):
        df_mod = results[0]["dataframe"]
        df_prod = results[1]["dataframe"]
        
        print(f"\nModified Version Shape: {df_mod.shape}")
        print(f"Production Version Shape: {df_prod.shape}")
        
        if df_mod.shape == df_prod.shape:
            print("  ✓ Same number of rows and columns")
        else:
            print("  ✗ Different shapes!")
        
        # Check if columns are the same
        mod_cols = set(df_mod.columns)
        prod_cols = set(df_prod.columns)
        
        if mod_cols == prod_cols:
            print("  ✓ Same columns")
        else:
            print(f"  ✗ Different columns!")
            print(f"    Modified only: {mod_cols - prod_cols}")
            print(f"    Production only: {prod_cols - mod_cols}")
        
        # Save both to CSV for manual comparison
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        mod_path = Path.home() / f"epl_fifa16_modified_{timestamp}.csv"
        prod_path = Path.home() / f"epl_fifa16_production_{timestamp}.csv"
        
        df_mod.to_csv(mod_path, index=False)
        df_prod.to_csv(prod_path, index=False)
        
        print(f"\n✓ Results saved:")
        print(f"  Modified: {mod_path}")
        print(f"  Production: {prod_path}")
    
    else:
        print("\n✗ Cannot compare - one or both versions failed")
        for result in results:
            if not result["success"]:
                print(f"  {result['version']} failed: {result['errors']}")


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("SOFIFA SCRAPER TEST SUITE")
    print("="*80)
    print("Testing both Modified and Production versions")
    print("Starting tests...\n")
    
    results = []
    
    # Test modified version
    print("\n1/2 Testing Modified Version...")
    result_mod = test_modified_version()
    results.append(result_mod)
    
    input("\nPress Enter to start Production version test (or Ctrl+C to skip)...")
    
    # Test production version
    print("\n2/2 Testing Production Version...")
    result_prod = test_production_version()
    results.append(result_prod)
    
    # Print results
    print_results(results)
    
    # Compare results
    if any(r["success"] for r in results):
        compare_results(results)
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
