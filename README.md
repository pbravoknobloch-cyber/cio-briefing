# CIO Morning Briefing System

A professional quantitative briefing system for portfolio management and market analysis. Run once daily to get a comprehensive snapshot of your portfolio, rebalancing needs, and market context.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Update portfolio.csv with your holdings:**
   ```csv
   ticker,shares,avg_cost_basis,target_allocation_pct
   AAPL,100,175.50,25
   MSFT,50,350.00,25
   ```

3. **Run the briefing:**
   ```bash
   python cio_brief.py
   ```

## Usage

### Full Briefing (Default)
```bash
python cio_brief.py
```
Shows everything: portfolio snapshot, rebalancing alerts, performance vs benchmarks, technical analysis, and macro context.

### Quick Mode
```bash
python cio_brief.py --quick
```
Fast snapshot: just portfolio snapshot, P&L, and macro indicators. Perfect for 2-minute morning check.

### Rebalancing Report
```bash
python cio_brief.py --rebalance
```
Full briefing with detailed rebalancing calculations showing exact shares to buy/sell and dollar amounts.

## Output

### Terminal Display
- **Color-coded** P&L (green = positive, red = negative)
- **Real-time** current prices and weights
- **Drift flags** for positions off-target by >2%
- **Performance dashboard** comparing portfolio to SPY and QQQ
- **Technical summaries** (RSI, moving averages, volume)
- **Macro snapshot** (VIX, 10Y yield, USD)

### Markdown Export
Each run auto-saves a markdown briefing to `briefings/YYYY-MM-DD_CIO_brief.md` with:
- Full holdings table with P&L
- Rebalancing plan
- Performance comparison
- Technical context for all positions
- Manual section for IBKR top stories (you add manually)

## Portfolio Configuration

Edit `portfolio.csv` with your holdings:

| Column | Description |
|--------|-------------|
| `ticker` | Stock symbol (e.g., AAPL) |
| `shares` | Number of shares held |
| `avg_cost_basis` | Average purchase price |
| `target_allocation_pct` | Target portfolio weight |

**Requirements:**
- Target allocations should sum to 100%
- Tickers must be valid Yahoo Finance symbols
- Update after each trade

## Thresholds & Alerts

| Alert | Trigger |
|-------|---------|
| **Drift Flag** | Position weight deviates >2% from target |
| **Large Move Alert** | Single-day price move >3% |
| **Volume Spike** | Current volume >1.5x 20-day average |
| **RSI Overbought** | RSI(14) >70 |
| **RSI Oversold** | RSI(14) <30 |

All configurable in `config.py`

## Data Sources

- **Market Data:** Yahoo Finance (yfinance)
- **Technical Indicators:** Historical close/volume prices
- **Macro Indicators:** VIX, 10Y Treasury (^TNX), USD Index (DXY)

## Extending the System

The modular architecture makes it easy to add new data sources:

1. **Add TradingView data:** Extend `data_fetcher.py` with TradingView API calls
2. **Add IBKR API:** Create new module `ibkr_fetcher.py` and import in `cio_brief.py`
3. **Add custom indicators:** Extend `technical_analyzer.py` with new calculations
4. **Custom report format:** Modify `report_generator.py` templates

## Files Structure

```
cio-briefing/
├── cio_brief.py              # Main CLI entry point
├── config.py                 # Configuration & thresholds
├── data_fetcher.py           # Market data retrieval
├── portfolio_analyzer.py      # Portfolio calculations
├── performance_analyzer.py    # P&L & benchmark analysis
├── technical_analyzer.py      # RSI, MAs, volume
├── report_generator.py        # Markdown export
├── portfolio.csv             # Your holdings (edit this)
├── requirements.txt          # Python dependencies
├── briefings/                # Daily markdown briefings
└── data/                     # Cache directory for future use
```

## Requirements

- Python 3.7+
- pandas
- yfinance
- rich (terminal formatting)
- numpy

## Notes

- First run takes ~10-15 seconds to fetch all data
- Subsequent runs are faster with cached data
- All prices are in USD and use market close
- Performance returns calculated on close-to-close basis
- Add IBKR top stories manually to the markdown export each morning

## Author

Built for Paradym Private Capital CIO operations.
