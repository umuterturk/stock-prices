#!/usr/bin/env python3
"""
Stock price crawler that fetches daily prices and saves them in a GitHub Pages friendly format.
"""

import datetime
import requests
import time
from pathlib import Path
from bs4 import BeautifulSoup

# Market configuration with tickers and crawler functions
MARKETS = {
    "us": {
        "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "JPM", "V", "WMT"],
        "crawler": "yahoo",
        "currency": "$"
    },
    "uk": {
        "tickers": ["BARC.L", "HSBA.L", "BP.L", "SHEL.L", "ULVR.L"],
        "crawler": "yahoo",
        "currency": "£"
    },
    "eu": {
        "tickers": ["AIR.PA", "ASML.AS", "SAP.DE", "SAN.MC", "ENEL.MI"],
        "crawler": "yahoo",
        "currency": "€"
    },
    "tr-tefas": {
        "tickers": ["HFA", "YAY", "TTE", "TI2", "AFT"],
        "crawler": "tefas",
        "currency": "₺"
    }
}

# Base directory for storing price data
DATA_DIR = Path("data")

def ensure_directories():
    """Create the necessary directory structure if it doesn't exist."""
    for market, config in MARKETS.items():
        for ticker in config["tickers"]:
            ticker_dir = DATA_DIR / market / ticker
            ticker_dir.mkdir(parents=True, exist_ok=True)

def fetch_price(ticker, market):
    """Fetch the latest price for a given ticker using the appropriate crawler."""
    crawler_type = MARKETS[market]["crawler"]
    
    if crawler_type == "tefas":
        return fetch_tefas_price(ticker)
    elif crawler_type == "yahoo":
        return fetch_yahoo_price(ticker)
    else:
        print(f"Unknown crawler type: {crawler_type}")
        return None

def fetch_yahoo_price(ticker):
    """Fetch the latest price for a given ticker using Yahoo Finance API."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Extract the latest price
        price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
        return round(float(price), 2)
    except Exception as e:
        print(f"Error fetching price for {ticker} from Yahoo Finance: {e}")
        return None

def fetch_tefas_price(fund_code):
    """Fetch the latest price for a Turkish fund from TEFAS."""
    url = f"https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod={fund_code}"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Approach 1: Look for the element that contains "Son Fiyat (TL)" and get the next element
        price_label = soup.find(string=lambda text: text and "Son Fiyat (TL)" in text)
        if price_label:
            price_container = price_label.find_parent().find_next_sibling()
            if price_container:
                price_text = price_container.get_text().strip()
                # Convert from Turkish format (comma as decimal separator) to float
                price = float(price_text.replace('.', '').replace(',', '.'))
                return round(price, 6)  # TEFAS prices typically have 6 decimal places
        
        # Approach 2: Fallback to searching by specific class or structure
        price_elements = soup.select("div.field-value, span.price-value, td.price-cell")
        for element in price_elements:
            text = element.get_text().strip()
            try:
                price = float(text.replace('.', '').replace(',', '.'))
                return round(price, 6)
            except ValueError:
                continue
        
        print(f"Could not find price for {fund_code} on TEFAS")
        return None
    except Exception as e:
        print(f"Error fetching price for {fund_code} from TEFAS: {e}")
        return None

def save_price(market, ticker, price, date=None):
    """Save the price to a file as a styled HTML page using the template."""
    if date is None:
        date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    ticker_dir = DATA_DIR / market / ticker
    currency = MARKETS[market]["currency"]
    
    # Load the HTML template
    try:
        template_path = Path("sample-price-display.html")
        with open(template_path, "r") as template_file:
            html_template = template_file.read()
        
        # Replace placeholders with actual values
        html_content = (html_template
            .replace('id="ticker">AAPL', f'id="ticker">{ticker}')
            .replace('id="currency">$', f'id="currency">{currency}')
            .replace('id="price">182.63', f'id="price">{price}')
            .replace('id="date">2023-05-15', f'id="date">{date}')
            .replace('id="market">us', f'id="market">{market}')
            .replace('<title>AAPL Price - Sample</title>', f'<title>{ticker} Price - {date}</title>')
        )
    except FileNotFoundError:
        print(f"Warning: Template file {template_path} not found. Using fallback template.")
        # Fallback to a minimal template if the file is not found
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{ticker} Price - {date}</title>
    <style>
        body {{ font-family: sans-serif; text-align: center; padding: 20px; }}
        .ticker {{ font-size: 24px; font-weight: bold; }}
        .price-wrapper {{ margin: 20px 0; }}
        .currency {{ display: inline; font-size: 20px; }}
        .price {{ display: inline; font-size: 32px; font-weight: bold; }}
        .date, .market {{ color: #666; }}
    </style>
</head>
<body>
    <div class="ticker" id="ticker">{ticker}</div>
    <div class="price-wrapper">
        <div class="currency" id="currency">{currency}</div>
        <div class="price" id="price">{price}</div>
    </div>
    <div class="date" id="date">{date}</div>
    <div class="market" id="market">{market}</div>
</body>
</html>"""
    
    # Save to date-specific file
    with open(ticker_dir / f"{date}.html", "w") as f:
        f.write(html_content)
    
    # Save to latest.html
    with open(ticker_dir / "latest.html", "w") as f:
        f.write(html_content)
    
    # Also save plain text versions for backward compatibility
    with open(ticker_dir / f"{date}.txt", "w") as f:
        f.write(str(price))
    
    with open(ticker_dir / "latest.txt", "w") as f:
        f.write(str(price))

def save_error_page(market, ticker, error_message, date=None):
    """Save an error page when price fetching fails."""
    if date is None:
        date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    ticker_dir = DATA_DIR / market / ticker
    currency = MARKETS[market]["currency"]
    
    # Check if there's a latest successful price we can show
    latest_txt_path = ticker_dir / "latest.txt"
    latest_price = None
    last_success_date = None
    
    if latest_txt_path.exists():
        try:
            with open(latest_txt_path, "r") as f:
                latest_price = f.read().strip()
            
            # Find the date of the last successful fetch
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            html_files = list(ticker_dir.glob("*.html"))
            date_files = [f for f in html_files if f.stem != "latest" and f.stem != today]
            
            if date_files:
                # Sort by modification time, newest first
                date_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                last_success_date = date_files[0].stem
        except Exception as e:
            print(f"Error reading latest price for {ticker}: {e}")
    
    # Load the HTML template
    try:
        template_path = Path("sample-price-display.html")
        with open(template_path, "r") as template_file:
            html_template = template_file.read()
        
        # Add error styling to the template
        error_style = """
        .error-message {
            background-color: #f8d7da;
            color: #721c24;
            padding: 10px;
            border-radius: 4px;
            margin-top: 1rem;
            font-size: 0.9rem;
            text-align: left;
        }
        .warning-message {
            background-color: #fff3cd;
            color: #856404;
            padding: 10px;
            border-radius: 4px;
            margin-top: 0.5rem;
            font-size: 0.8rem;
        }
        """
        html_template = html_template.replace("</style>", f"{error_style}</style>")
        
        # Create error content
        error_content = f'<div class="error-message" id="error">{error_message}</div>'
        
        if latest_price:
            # Show the latest price with a warning
            html_content = (html_template
                .replace('id="ticker">AAPL', f'id="ticker">{ticker}')
                .replace('id="currency">$', f'id="currency">{currency}')
                .replace('id="price">182.63', f'id="price">{latest_price}')
                .replace('id="date">2023-05-15', f'id="date">{last_success_date or "Unknown"}')
                .replace('id="market">us', f'id="market">{market}')
                .replace('<title>AAPL Price - Sample</title>', f'<title>{ticker} Price - Error</title>')
            )
            
            # Add warning after the price
            warning = f'<div class="warning-message" id="warning">This is the last known price from {last_success_date or "a previous fetch"}. Current price fetch failed.</div>'
            html_content = html_content.replace('</div>\n    <div class="date"', f'</div>\n    {warning}\n    <div class="date"')
            
            # Add error message at the bottom
            html_content = html_content.replace('</div>\n</body>', f'</div>\n    {error_content}\n</body>')
        else:
            # No previous price available, show a minimal error page
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{ticker} Price - Error</title>
    <style>
        body {{ font-family: sans-serif; text-align: center; padding: 20px; }}
        .ticker {{ font-size: 24px; font-weight: bold; }}
        .error-message {{
            background-color: #f8d7da;
            color: #721c24;
            padding: 20px;
            border-radius: 4px;
            margin-top: 2rem;
            text-align: left;
        }}
    </style>
</head>
<body>
    <div class="ticker" id="ticker">{ticker}</div>
    <div class="error-message" id="error">
        <strong>Error fetching price:</strong><br>
        {error_message}
    </div>
    <div id="date" style="display:none">{date}</div>
    <div id="market" style="display:none">{market}</div>
</body>
</html>"""
        
        # Save to date-specific file
        with open(ticker_dir / f"{date}.html", "w") as f:
            f.write(html_content)
        
        # Save error to text file for API consumers
        with open(ticker_dir / f"{date}.txt", "w") as f:
            f.write(f"ERROR: {error_message}")
            
    except Exception as e:
        print(f"Error creating error page for {ticker}: {e}")

def main():
    """Main function to fetch and save prices for all tickers."""
    print(f"Starting price crawler at {datetime.datetime.now()}")
    
    ensure_directories()
    success_count = 0
    error_count = 0
    
    for market, config in MARKETS.items():
        print(f"\nProcessing {market.upper()} market:")
        for ticker in config["tickers"]:
            try:
                print(f"Fetching price for {ticker}...")
                price = fetch_price(ticker, market)
                
                if price is not None:
                    print(f"{ticker}: {config['currency']}{price}")
                    save_price(market, ticker, price)
                    success_count += 1
                else:
                    error_message = "Failed to fetch price (unknown error)"
                    print(f"Error for {ticker}: {error_message}")
                    save_error_page(market, ticker, error_message)
                    error_count += 1
                
                # Add a delay between requests to avoid rate limiting
                time.sleep(2)
            except Exception as e:
                error_message = f"Exception while processing {ticker}: {str(e)}"
                print(error_message)
                try:
                    save_error_page(market, ticker, error_message)
                except Exception as inner_e:
                    print(f"Critical error saving error page for {ticker}: {inner_e}")
                error_count += 1
                
                # Add a delay after errors too
                time.sleep(2)
    
    print(f"\nCompleted at {datetime.datetime.now()}")
    print(f"Summary: {success_count} successful, {error_count} failed")

if __name__ == "__main__":
    main()