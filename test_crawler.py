#!/usr/bin/env python3
"""
Test script to run the crawler locally and verify it works.
"""

import os
import json
from pathlib import Path
from crawler import main, DATA_DIR, MARKETS

def test_crawler():
    """Run the crawler and verify the output files."""
    # Run the crawler
    main()
    
    # Check if the data directory was created
    assert DATA_DIR.exists(), f"Data directory {DATA_DIR} was not created"
    
    # Only check the TR-TEFAS market
    market = "tr-tefas"
    market_info = MARKETS.get(market, {})
    tickers = market_info.get("tickers", [])
    
    if tickers:
        market_dir = DATA_DIR / market
        assert market_dir.exists(), f"Market directory {market_dir} was not created"
        
        for ticker in tickers:
            ticker_dir = market_dir / ticker
            assert ticker_dir.exists(), f"Ticker directory {ticker_dir} was not created"
            
            # Check if latest.txt was created
            latest_file = ticker_dir / "latest.txt"
            assert latest_file.exists(), f"Latest file {latest_file} was not created"
            
            # Check if the price is a valid number
            with open(latest_file, "r") as f:
                price = f.read().strip()
                try:
                    price = float(price)
                    currency = market_info.get("currency", "₺")
                    print(f"{market}/{ticker}: {currency}{price}")
                except ValueError:
                    assert False, f"Price for {market}/{ticker} is not a valid number: {price}"
    else:
        print(f"No tickers defined for {market} market")

if __name__ == "__main__":
    test_crawler()
    print("All tests passed!")