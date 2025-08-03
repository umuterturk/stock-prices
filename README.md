# Stock Price API

A simple, no-cost stock price API that serves daily stock prices via GitHub Pages.

## How to Use

Access stock prices using these URL patterns:

- Latest price: `https://[your-username].github.io/prices-to-github/[market]/[ticker]/latest`
- Specific date: `https://[your-username].github.io/prices-to-github/[market]/[ticker]/YYYY-MM-DD`

Examples:
```
# Plain text format
https://[your-username].github.io/prices-to-github/us/AAPL/latest.txt
https://[your-username].github.io/prices-to-github/uk/BP.L/2023-12-31.txt

# HTML format with styled display
https://[your-username].github.io/prices-to-github/us/AAPL/latest.html
https://[your-username].github.io/prices-to-github/tr-tefas/HFA/latest.html
```

Each endpoint is available in two formats:
- Plain text (.txt): Returns only the price value
- HTML (.html): Returns a styled page with ticker name, currency symbol, and price

### HTML Price Display

The HTML format provides a clean, stylish display with the following elements:
- Ticker symbol (large, bold)
- Currency symbol and price (centered, prominent)
- Date of the price
- Market identifier

Each element has its own distinct HTML element with an ID for easy access:
- `<div id="ticker">` - The ticker symbol
- `<div id="currency">` - The currency symbol
- `<div id="price">` - The price value
- `<div id="date">` - The date of the price
- `<div id="market">` - The market identifier

#### Customizing the Display

To customize the appearance of the price display:

1. Edit the `sample-price-display.html` file
2. Modify the CSS styles or HTML structure as needed
3. Keep the ID attributes and placeholder content intact
4. The crawler will use this template to generate all price pages

This approach allows you to change the design in one place and have it applied to all generated price pages.

#### Error Handling

The system includes robust error handling to ensure reliability:

1. **Continuous Operation**: If fetching one ticker fails, the system continues with others
2. **Error Pages**: Failed fetches generate error pages with descriptive messages
3. **Latest Price Preservation**: The `/latest.html` endpoint always shows the most recent successful price
4. **Error Indicators**:
   - Visual warning when showing a previous price due to fetch failure
   - Clear error messages explaining what went wrong
   - Error information in text files for API consumers (`ERROR: message`)
5. **Summary Reports**: After each run, a summary shows success and failure counts

## Supported Markets and Tickers

### US Market (`/us/`)
- AAPL (Apple)
- MSFT (Microsoft)
- GOOGL (Alphabet)
- AMZN (Amazon)
- META (Meta Platforms)
- TSLA (Tesla)
- NVDA (NVIDIA)
- JPM (JPMorgan Chase)
- V (Visa)
- WMT (Walmart)

### UK Market (`/uk/`)
- BARC.L (Barclays)
- HSBA.L (HSBC)
- BP.L (BP)
- SHEL.L (Shell)
- ULVR.L (Unilever)

### European Market (`/eu/`)
- AIR.PA (Airbus)
- ASML.AS (ASML Holding)
- SAP.DE (SAP)
- SAN.MC (Banco Santander)
- ENEL.MI (Enel)

### Turkish TEFAS Funds (`/tr-tefas/`)
- HFA (HSBC PORTFÖY ALLİANZ SERBEST ÖZEL FON)
- YAY (YAPI KREDİ PORTFÖY YENİLENEBİLİR ENERJİ DEĞİŞKEN FON)
- TTE (TEB PORTFÖY EUROBOND (DÖVİZ) BORÇLANMA ARAÇLARI FONU)
- TI2 (TEB PORTFÖY İKİNCİ HİSSE SENEDİ FONU)
- AFT (AK PORTFÖY PETROL YABANCI BYF FON SEPETİ FONU)

## Data Update Frequency

Prices are updated once daily after market close.