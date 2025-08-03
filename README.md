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

### SEO and AIEO Optimization

All generated pages include comprehensive SEO and AIEO (AI Engine Optimization) features:

#### Meta Tags
- **Title Tags**: Optimized with ticker symbol and purpose (e.g., "AAPL Stock Price | Stock Prices API")
- **Meta Description**: Detailed, keyword-rich descriptions of the page content
- **Meta Keywords**: Relevant keywords for search engines and AI models
- **Canonical URLs**: Proper canonical links to prevent duplicate content issues
- **Open Graph Tags**: Enhanced social media sharing with og:title, og:description, and og:type

#### Structured Data
- **JSON-LD Schema**: Each page includes structured data using Schema.org vocabulary
- **Financial Product Schema**: Properly formatted financial product information
- **Price Information**: Structured price data with currency code
- **Organization Information**: Provider details in structured format

#### Accessibility and Indexing
- **Robots Meta Tag**: Set to "index, follow" to ensure proper crawling
- **Semantic HTML**: Clear structure for both search engines and AI models
- **Mobile Optimization**: Responsive design with appropriate viewport settings

#### Customizing the Display

To customize the appearance of the price display:

1. Edit the `template.html` file
2. Modify the CSS styles or HTML structure as needed
3. Keep the template placeholders intact (e.g., `{{TICKER}}`, `{{PRICE}}`, etc.)
4. The crawler will use this template to generate all price pages

This approach allows you to change the design in one place and have it applied to all generated price pages.

#### Template System

The project uses a simple template system with placeholders:

| Placeholder | Description |
|-------------|-------------|
| `{{TICKER}}` | The stock/fund ticker symbol |
| `{{CURRENCY}}` | The currency symbol (e.g., $, £, €, ₺) |
| `{{PRICE}}` | The current price value |
| `{{DATE}}` | The date of the price data |
| `{{MARKET}}` | The market identifier (e.g., us, uk, eu, tr-tefas) |
| `{{CURRENCY_CODE}}` | The ISO currency code (e.g., USD, GBP, EUR, TRY) |
| `{{WARNING_MESSAGE}}` | Optional warning message for error pages |
| `{{ERROR_MESSAGE}}` | Optional error message for error pages |

Sample files (`sample-price-display.html` and `sample-error-display.html`) are provided as references showing how the template looks with example data.

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

## TEFAS Crawler Implementation

The TEFAS crawler has been specially designed to handle the challenges of fetching data from the TEFAS website, which employs CAPTCHA protection. The implementation includes:

### Primary XPath Approach
- Uses a precise XPath (`/html/body/form/div[3]/div[3]/div/div[2]/div[1]/ul[1]/li[1]/span`) to target the price element
- Converts Turkish number format (comma as decimal separator) to standard float format
- Includes regex-based extraction for cases where the price is embedded in text

### CAPTCHA Detection and Handling
- Automatically detects CAPTCHA challenges in the response
- Switches to fallback methods when CAPTCHA is encountered
- Maintains operation continuity without manual intervention

### Multi-layered Fallback System
1. **Session-based Approach**: Establishes a session with cookies to bypass CAPTCHA
2. **Alternative Website Sources**: Attempts to fetch from financial data aggregators like FVT
3. **External API Integration**: Connects to third-party APIs that provide TEFAS data
4. **Hardcoded Fallback Values**: Uses recent known values as a last resort

### Robust Error Handling
- Graceful degradation through multiple fallback layers
- Detailed logging of each attempt and failure reason
- Preservation of service continuity even when some methods fail

## Data Update Frequency

Prices are updated once daily after market close.

## Testing

To test the TEFAS crawler specifically:

```bash
python test_tefas_only.py
```

To test the entire crawler system:

```bash
python test_crawler.py
```

The test scripts verify that:
- The crawler can connect to data sources
- Prices are successfully retrieved
- Data is correctly formatted and saved
- All fallback mechanisms function as expected