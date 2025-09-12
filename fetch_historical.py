#!/usr/bin/env python3
"""
Historical data fetcher for TEFAS funds.
Fetches the last 30 days of data and saves as JSON files.
"""

import datetime
import sys
import time
from pathlib import Path
from crawler import fetch_all_tefas_data, save_daily_data, MARKETS

def fetch_historical_data(days_back=30):
    """Fetch historical data for the specified number of days."""
    print(f"Starting historical data fetch for the last {days_back} days...")
    
    # Get date range
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=days_back)
    
    success_count = 0
    error_count = 0
    current_date = start_date
    
    print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print("=" * 60)
    
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        
        # Check if we already have this data
        market_dir = Path("data/tr-tefas")
        json_file = market_dir / f"{date_str}.json"
        
        if json_file.exists():
            print(f"📁 {date_str}: File already exists, skipping...")
            current_date += datetime.timedelta(days=1)
            continue
        
        print(f"🔄 {date_str}: Fetching data...")
        
        try:
            # Fetch data for this specific date
            all_funds_data = fetch_all_tefas_data(current_date)
            
            if all_funds_data and 'data' in all_funds_data and len(all_funds_data['data']) > 0:
                # Save the data
                funds_by_code = save_daily_data("tr-tefas", all_funds_data, date_str)
                
                fund_count = len(funds_by_code)
                print(f"✅ {date_str}: Successfully saved {fund_count} funds")
                success_count += 1
                
                # Check if our target funds are included
                target_funds = MARKETS["tr-tefas"]["tickers"]
                found_targets = [code for code in target_funds if code in funds_by_code]
                if found_targets:
                    print(f"   📊 Found target funds: {', '.join(found_targets)}")
                else:
                    print(f"   ⚠️  No target funds found (might be weekend/holiday)")
                    
            else:
                print(f"❌ {date_str}: No data available (likely weekend/holiday)")
                error_count += 1
                
        except Exception as e:
            print(f"❌ {date_str}: Error - {str(e)}")
            error_count += 1
        
        # Add delay to be respectful to the API
        time.sleep(2)
        current_date += datetime.timedelta(days=1)
    
    print("\n" + "=" * 60)
    print(f"Historical data fetch completed!")
    print(f"✅ Successful: {success_count} days")
    print(f"❌ Failed/Skipped: {error_count} days")
    print(f"📁 Total files in data/tr-tefas: {len(list(Path('data/tr-tefas').glob('*.json')))}")

def main():
    """Main function to run historical data fetch."""
    if len(sys.argv) > 1:
        try:
            days_back = int(sys.argv[1])
        except ValueError:
            print("Error: Please provide a valid number of days")
            print("Usage: python fetch_historical.py [days_back]")
            sys.exit(1)
    else:
        days_back = 30  # Default to 30 days
    
    print(f"TEFAS Historical Data Fetcher")
    print(f"Fetching last {days_back} days of data...")
    print("-" * 40)
    
    # Ensure directory exists
    Path("data/tr-tefas").mkdir(parents=True, exist_ok=True)
    
    fetch_historical_data(days_back)

if __name__ == "__main__":
    main()
