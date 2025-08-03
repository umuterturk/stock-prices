#!/usr/bin/env python3
"""
Test script to verify the TEFAS crawler functionality.
"""

from crawler import fetch_tefas_price, MARKETS

def test_tefas_crawler():
    """Test the TEFAS crawler with the configured fund codes."""
    fund_codes = MARKETS["tr-tefas"]["tickers"]
    currency = MARKETS["tr-tefas"]["currency"]
    
    print("Testing TEFAS crawler...")
    for fund_code in fund_codes:
        print(f"Fetching price for {fund_code}...")
        price = fetch_tefas_price(fund_code)
        if price is not None:
            print(f"{fund_code}: {currency}{price}")
        else:
            print(f"Failed to fetch price for {fund_code}")
    
    print("TEFAS crawler test completed.")

if __name__ == "__main__":
    test_tefas_crawler()