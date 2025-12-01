#!/usr/bin/env python3
"""
Stock price crawler that fetches daily prices and saves them in a GitHub Pages friendly format.
"""

import datetime
import requests
import time
import json
import re
from pathlib import Path
from lxml import html


def minify_html(html_content):
    """Minify HTML by removing unnecessary whitespace and newlines."""
    # Remove HTML comments
    html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
    
    # Remove whitespace between tags (but preserve space in text content)
    html_content = re.sub(r'>\s+<', '><', html_content)
    
    # Remove leading/trailing whitespace from lines
    lines = html_content.split('\n')
    minified_lines = [line.strip() for line in lines if line.strip()]
    html_content = ''.join(minified_lines)
    
    # Compress CSS (remove unnecessary whitespace in style tags)
    def compress_css(match):
        css = match.group(1)
        # Remove comments
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
        # Remove whitespace around colons, semicolons, braces
        css = re.sub(r'\s*([{}:;,])\s*', r'\1', css)
        # Remove whitespace at start/end
        css = css.strip()
        return f'<style>{css}</style>'
    
    html_content = re.sub(r'<style>(.*?)</style>', compress_css, html_content, flags=re.DOTALL)
    
    return html_content

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
                
                # Minify HTML to reduce file size
                html_content = minify_html(html_content)
                
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


def convert_turkish_to_us_number(turkish_number):
    """Convert Turkish number format to US format.
    
    Turkish format: 5.800,0980 (dot as thousands separator, comma as decimal)
    US format: 5800.0980 (dot as decimal separator, no thousands separator)
    """
    if not turkish_number:
        return ''
    
    # Remove all dots (thousands separators)
    # Replace comma with dot (decimal separator)
    us_number = turkish_number.replace('.', '').replace(',', '.')
    return us_number


def fetch_gold_prices_table():
    """Fetch the gold prices table from uzmanpara.milliyet.com.tr."""
    url = 'https://uzmanpara.milliyet.com.tr/gram-altin-fiyati/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        doc = html.fromstring(response.content)
        
        # Find the main table with all gold types (second table on the page)
        tables = doc.xpath('//table')
        if len(tables) < 2:
            print("Error: Could not find gold prices table")
            return None
        
        table = tables[1]  # Second table contains all gold types
        rows = table.xpath('.//tr')
        
        if len(rows) < 2:
            print("Error: Gold prices table has no data rows")
            return None
        
        gold_items = []
        
        # Skip header row (first row)
        for row in rows[1:]:
            cells = row.xpath('.//td')
            if len(cells) >= 7:
                name_cell = cells[1]
                name = name_cell.text_content().strip()
                
                # Skip if empty
                if not name:
                    continue
                
                # Get link if available
                link = name_cell.xpath('.//a/@href')
                link = link[0] if link else None
                
                # Extract prices and other data
                buy_price_raw = cells[2].text_content().strip() if len(cells) > 2 else ''
                sell_price_raw = cells[3].text_content().strip() if len(cells) > 3 else ''
                change_text = cells[4].text_content().strip() if len(cells) > 4 else ''
                time_str = cells[6].text_content().strip() if len(cells) > 6 else ''
                
                # Convert Turkish number format to US format
                buy_price = convert_turkish_to_us_number(buy_price_raw)
                sell_price = convert_turkish_to_us_number(sell_price_raw)
                
                # Parse change percentage (remove % and whitespace)
                change_match = re.search(r'([+-]?\d+[,.]?\d*)', change_text)
                change_value = change_match.group(1) if change_match else '0'
                # Convert Turkish number format to US format for change
                change_value = convert_turkish_to_us_number(change_value)
                try:
                    change_float = float(change_value)
                    change_class = 'change-positive' if change_float >= 0 else 'change-negative'
                except:
                    change_float = 0
                    change_class = 'change-positive'
                
                gold_items.append({
                    'name': name,
                    'link': link,
                    'buy_price': buy_price,
                    'sell_price': sell_price,
                    'change': change_text,
                    'change_value': change_value,
                    'change_class': change_class,
                    'time': time_str
                })
        
        print(f"Fetched {len(gold_items)} gold items from table")
        return gold_items
        
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching gold prices: {e}")
        return None
    except Exception as e:
        print(f"Error parsing gold prices table: {e}")
        return None


def save_gold_data(gold_items, date=None):
    """Save gold price data as individual HTML files."""
    if date is None:
        date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    market_dir = DATA_DIR / "gold"
    market_dir.mkdir(parents=True, exist_ok=True)
    
    # Load the HTML template
    template_path = Path("gold_template.html")
    if not template_path.exists():
        print("Error: gold_template.html not found")
        return
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    saved_count = 0
    
    if gold_items:
        for gold_item in gold_items:
            gold_name = gold_item['name']
            if not gold_name:
                continue
            
            # Create directory for this gold type (preserve spaces for URL accessibility)
            # Only remove truly problematic characters, keep spaces
            safe_name = re.sub(r'[<>:"|?*]', '', gold_name)  # Remove filesystem-invalid chars
            safe_name = safe_name.strip()  # Remove leading/trailing whitespace
            gold_dir = market_dir / safe_name
            gold_dir.mkdir(parents=True, exist_ok=True)
            
            # Format change percentage for display (separate number from % sign for easy selection)
            change_number = gold_item['change_value']
            
            # Prepare replacements
            replacements = {
                'GOLD_NAME': gold_name,
                'BUY_PRICE': gold_item['buy_price'],
                'SELL_PRICE': gold_item['sell_price'],
                'CHANGE_NUMBER': change_number,
                'CHANGE_CLASS': gold_item['change_class'],
                'DATE': date,
                'TIME': gold_item['time']
            }
            
            # Replace template placeholders
            html_content = template_content
            for placeholder, value in replacements.items():
                html_content = html_content.replace(f'{{{{{placeholder}}}}}', str(value))
            
            # Minify HTML to reduce file size
            html_content = minify_html(html_content)
            
            # Save HTML file for this date
            html_filename = f"{date}.html"
            html_path = gold_dir / html_filename
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Create/update latest.html symlink or copy
            latest_path = gold_dir / "latest.html"
            if latest_path.exists():
                latest_path.unlink()
            latest_path.symlink_to(html_filename)
            
            saved_count += 1
    
    print(f"Saved {saved_count} gold price HTML files for {date}")




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
            success_count += 1
        else:
            print("Failed to fetch TEFAS data")
            error_count += 1
            
    except Exception as e:
        error_message = f"Exception while processing TEFAS market: {str(e)}"
        print(error_message)
        error_count += 1
    
    # Fetch gold prices
    try:
        print("\nFetching gold prices from uzmanpara.milliyet.com.tr...")
        gold_items = fetch_gold_prices_table()
        
        if gold_items:
            # Save all the gold data as individual HTML files
            save_gold_data(gold_items)
            success_count += 1
        else:
            print("Failed to fetch gold prices")
            error_count += 1
            
    except Exception as e:
        error_message = f"Exception while processing gold prices: {str(e)}"
        print(error_message)
        error_count += 1

    
    # Update the index.html file with links to all tickers (TODO: Update for JSON approach)
    # update_index_html()
    
    print(f"\nCompleted at {datetime.datetime.now()}")
    print(f"Summary: {success_count} successful, {error_count} failed")

if __name__ == "__main__":
    main()