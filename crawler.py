#!/usr/bin/env python3
"""
Stock price crawler that fetches daily prices and saves them in a GitHub Pages friendly format.
"""

import datetime
import requests
import time
import json
from pathlib import Path
# Removed BeautifulSoup and lxml imports - no longer needed with API approach

# Market configuration with tickers and crawler functions

# Base directory for storing price data
DATA_DIR = Path("data")

def fetch_all_tefas_data(date=None):
    """Fetch all fund data from TEFAS API for a specific date."""
    if date is None:
        date = datetime.datetime.now()
    
    date_str = date.strftime("%d.%m.%Y")
    print(f"Fetching all TEFAS data for {date_str}...")
    
    try:
        # First, get cookies by visiting the main page
        session = requests.Session()
        
        # Headers for initial request to get cookies
        initial_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Priority': 'u=1'
        }
        
        # Visit the main page to get session cookies
        main_page = session.get('https://www.tefas.gov.tr/TarihselVeriler.aspx', headers=initial_headers, timeout=10)
        print(f"Main page response status: {main_page.status_code}")
        
        if main_page.status_code != 200:
            print(f"Failed to access main page. Status code: {main_page.status_code}")
            return None
        
        # Now make the API request with the session cookies
        api_url = 'https://www.tefas.gov.tr/api/DB/BindHistoryInfo'
        
        # Headers for API request
        api_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://www.tefas.gov.tr',
            'Connection': 'keep-alive',
            'Referer': 'https://www.tefas.gov.tr/TarihselVeriler.aspx',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Priority': 'u=0',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        }
        
        # Request data for ALL funds (empty fonkod)
        data = {
            'fontip': 'YAT',  # Fund type
            'sfontur': '',
            'fonkod': '',     # Empty to get all funds
            'fongrup': '',
            'bastarih': date_str,    # Start date
            'bittarih': date_str,    # End date (same as start for single day)
            'fonturkod': '',
            'fonunvantip': '',
            'kurucukod': ''
        }
        
        # Make the API request
        response = session.post(api_url, headers=api_headers, data=data, timeout=30)
        response.raise_for_status()
        
        # Parse JSON response
        result = response.json()
        print(f"API returned {result.get('recordsTotal', 0)} total funds")
        
        # Return the full API response
        if 'data' in result and len(result['data']) > 0:
            return result
        else:
            print(f"No data found in API response for {date_str}")
            return None
        
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching TEFAS data: {e}")
        return None
    except (ValueError, KeyError) as e:
        print(f"Error parsing API response: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error fetching TEFAS data: {e}")
        return None


# Fallback method removed - API approach is reliable and efficient

def get_currency_code(currency_symbol):
    """Convert currency symbol to ISO currency code."""
    currency_map = {
        "$": "USD",
        "£": "GBP",
        "€": "EUR",
        "₺": "TRY"
    }
    return currency_map.get(currency_symbol, "USD")

def render_template(template_content, replacements):
    """Render a template by replacing placeholders with actual values."""
    result = template_content
    for placeholder, value in replacements.items():
        result = result.replace(f'{{{{{placeholder}}}}}', str(value))
    return result

def save_daily_data(market, all_funds_data, date=None):
    """Save daily fund data as individual HTML files."""
    if date is None:
        date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    market_dir = DATA_DIR / market
    market_dir.mkdir(parents=True, exist_ok=True)
    
    # Load the HTML template
    template_path = Path("fund_template.html")
    if not template_path.exists():
        print("Error: fund_template.html not found")
        return
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    currency = "₺"  # Turkish Lira for TEFAS funds
    saved_count = 0
    
    if all_funds_data and 'data' in all_funds_data:
        for fund in all_funds_data['data']:
            fund_code = fund.get('FONKODU', '')
            if fund_code:
                # Create directory for this fund code
                fund_dir = market_dir / fund_code
                fund_dir.mkdir(parents=True, exist_ok=True)
                
                # Prepare fund data
                fund_data = {
                    'code': fund_code,
                    'name': fund.get('FONUNVAN', ''),
                    'price': fund.get('FIYAT', 0),
                    'shares': fund.get('TEDPAYSAYISI', 0),
                    'investors': fund.get('KISISAYISI', 0),
                    'portfolio_size': fund.get('PORTFOYBUYUKLUK', 0),
                    'currency': currency,
                    'date': date,
                    'timestamp': fund.get('TARIH', '')
                }
                
                # Format numbers for display
                price_str = f"{fund_data['price']:.6f}".rstrip('0').rstrip('.')
                shares_str = f"{fund_data['shares']:,.0f}" if fund_data['shares'] else "0"
                investors_str = f"{fund_data['investors']:,.0f}" if fund_data['investors'] else "0"
                portfolio_str = f"{fund_data['portfolio_size']:,.2f}".rstrip('0').rstrip('.') if fund_data['portfolio_size'] else "0"
                avg_portfolio_per_investor_str = f"{fund_data['portfolio_size'] / fund_data['investors']:.2f}".rstrip('0').rstrip('.') if fund_data['portfolio_size'] and fund_data['investors'] else "0"
                # Replace template placeholders
                html_content = template_content
                replacements = {
                    'FUND_CODE': fund_data['code'],
                    'FUND_NAME': fund_data['name'],
                    'CURRENCY': fund_data['currency'],
                    'PRICE': price_str,
                    'SHARES': shares_str,
                    'INVESTORS': investors_str,
                    'PORTFOLIO_SIZE': portfolio_str,
                    'DATE': fund_data['date'],
                    'TIMESTAMP': fund_data['timestamp'],
                    'AVG_PORTFOLIO_PER_INVESTOR': avg_portfolio_per_investor_str
                }
                
                for placeholder, value in replacements.items():
                    html_content = html_content.replace(f'{{{{{placeholder}}}}}', str(value))
                
                # Save HTML file for this date
                html_filename = f"{date}.html"
                html_path = fund_dir / html_filename
                
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                # Create/update latest.html symlink or copy
                latest_path = fund_dir / "latest.html"
                if latest_path.exists():
                    latest_path.unlink()
                latest_path.symlink_to(html_filename)
                
                saved_count += 1
    
    print(f"Saved {saved_count} fund HTML files for {date}")





def main():
    """Main function to fetch and save prices for all tickers."""
    print(f"Starting price crawler at {datetime.datetime.now()}")
    
    success_count = 0
    error_count = 0
    
    try:
        print("Fetching all TEFAS funds data in one request...")
        all_funds_data = fetch_all_tefas_data()
        
        if all_funds_data:
            # Save all the data as individual HTML files
            save_daily_data("tr-tefas", all_funds_data)
            
        else:
            print("Failed to fetch TEFAS data")
            error_count += 1
            
    except Exception as e:
        error_message = f"Exception while processing TEFAS market: {str(e)}"
        print(error_message)
        error_count += 1

    
    # Update the index.html file with links to all tickers (TODO: Update for JSON approach)
    # update_index_html()
    
    print(f"\nCompleted at {datetime.datetime.now()}")
    print(f"Summary: {success_count} successful, {error_count} failed")

if __name__ == "__main__":
    main()