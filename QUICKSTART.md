# Quick Start Guide — CIO Morning Briefing

## 30-Second Setup

1. **Install dependencies** (one time):
   ```bash
   pip install -r requirements.txt
   ```

2. **Update your portfolio** (after each trade):
   Edit `portfolio.csv` with your holdings:
   ```csv
   ticker,shares,avg_cost_basis,target_allocation_pct
   AAPL,100,175.50,25
   MSFT,50,350.00,25
   NVDA,40,875.00,20
   ```

3. **Run your briefing** (every morning):
   ```bash
   python3 cio_brief.py
   ```

---

## Three Usage Modes

### Full Briefing (3 minutes)
```bash
python3 cio_brief.py
```
**Shows:** Portfolio snapshot + Performance + Technical + Macro + Rebalancing status  
**Use when:** Daily deep review, before making decisions

### Quick Snapshot (1 minute)
```bash
python3 cio_brief.py --quick
```
**Shows:** Portfolio snapshot + Macro only  
**Use when:** Quick morning check, fast decision-making

### Detailed Rebalancing (3 minutes)
```bash
python3 cio_brief.py --rebalance
```
**Shows:** Everything + Exact rebalancing calculations (shares to trade, $ amounts)  
**Use when:** Time to rebalance your portfolio

---

## What You'll See

### Terminal Output (Color-Coded)
- ✅ **Green** = Positive returns
- ❌ **Red** = Negative returns
- 🟡 **Yellow** = Drift alerts, rebalancing needed

### Key Metrics
- **Portfolio value** & total P&L
- **Position-by-position** P&L ($ and %)
- **Weight vs target** allocation
- **Rebalancing** what to buy/sell
- **Performance** vs SPY & QQQ
- **Technical health** (RSI, moving averages)
- **VIX, 10Y yield, USD index**

### Daily Log (Auto-saved)
Every run saves a markdown file to:
```
briefings/2026-06-04_CIO_brief.md
```
Perfect for record-keeping and audits.

---

## Daily Workflow Example

### 6:00 AM — Run Briefing
```bash
python3 cio_brief.py
```

### Review Output
- Any alerts for moves >3%?
- Is portfolio drifting from targets?
- How am I performing vs benchmarks?
- Any technical warnings (overbought/oversold)?

### Manual Entry (1 minute)
Open the markdown file and paste your **top 10 IBKR stories** from IBKR into the manual section.

### Decision Time
- **No rebalancing needed?** → Monitor and move on
- **Drift detected?** → Run `python3 cio_brief.py --rebalance` to see exact trades
- **Large moves?** → Check technical summary for context
- **Underperforming?** → Compare to benchmarks, review holdings

---

## Editing Your Portfolio

### When to Update `portfolio.csv`
After each trade, update:
- **ticker** — Stock symbol (e.g., AAPL)
- **shares** — Current holdings
- **avg_cost_basis** — Average purchase price
- **target_allocation_pct** — Target weight (sum = 100%)

### Example
```csv
ticker,shares,avg_cost_basis,target_allocation_pct
AAPL,150,175.50,30
MSFT,50,350.00,20
NVDA,40,875.00,25
SPY,75,450.00,15
QQQ,30,380.00,10
```

---

## Customization (if needed)

### Change Alert Thresholds
Edit `config.py`:
```python
DRIFT_THRESHOLD_PCT = 2.0        # Flag when weight drifts >2%
ALERT_MOVE_THRESHOLD_PCT = 3.0   # Alert on 1-day moves >3%
VOLUME_SPIKE_MULTIPLIER = 1.5    # Flag volume >1.5x average
```

### Change Technical Periods
```python
RSI_PERIOD = 14          # Relative Strength Index period
MA_SHORT = 20            # Short moving average
MA_LONG = 50             # Long moving average
```

---

## Troubleshooting

### "Command not found: python3"
Use the full path or alias:
```bash
/usr/bin/python3 cio_brief.py
```

### "No module named 'yfinance'"
Reinstall dependencies:
```bash
pip install -r requirements.txt
```

### "Missing optional dependency 'tabulate'"
Install tabulate:
```bash
pip install tabulate
```

### Data looks wrong
Check your `portfolio.csv`:
- Are tickers valid Yahoo Finance symbols?
- Are shares and cost basis correct?
- Do target allocations sum to 100%?

---

## FAQ

**Q: How often should I run the briefing?**  
A: Daily, ideally before market open or at your preferred review time.

**Q: Can I automate it?**  
A: Yes! Use cron:
```bash
0 6 * * * cd /Users/patriciobravoknobloch/cio-briefing && python3 cio_brief.py
```

**Q: What if a ticker is delisted?**  
A: Remove it from portfolio.csv and re-run.

**Q: Can I add more indicators?**  
A: Yes! Extend `technical_analyzer.py` with MACD, Bollinger Bands, etc.

**Q: How do I add TradingView data?**  
A: Create a new module `tradingview_fetcher.py` and import it in `cio_brief.py`.

**Q: Can I export to CSV instead of markdown?**  
A: Modify `report_generator.py` to generate CSV output.

---

## Files at a Glance

| File | Purpose |
|------|---------|
| `cio_brief.py` | **Main script** — run this daily |
| `portfolio.csv` | **Your holdings** — edit after trades |
| `config.py` | Thresholds & settings |
| `data_fetcher.py` | Market data module |
| `portfolio_analyzer.py` | Portfolio calculations |
| `performance_analyzer.py` | P&L & benchmarks |
| `technical_analyzer.py` | RSI, MAs, volume |
| `report_generator.py` | Markdown export |
| `briefings/` | Daily markdown logs |
| `README.md` | Full documentation |
| `SYSTEM_SUMMARY.md` | Complete feature list |

---

## Next Steps

1. ✅ **Today:** Run `python3 cio_brief.py` and review output
2. ✅ **Tomorrow:** Run again, add to your morning routine
3. ✅ **Weekly:** Check rebalancing with `--rebalance` flag
4. 🔄 **Optional:** Set up cron job for automatic daily runs
5. 🔄 **Optional:** Add TradingView or IBKR API integration

---

**Questions?** See `README.md` for detailed documentation.  
**Ready?** Run: `python3 cio_brief.py`
