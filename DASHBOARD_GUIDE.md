# 📊 Streamlit Dashboard Guide

## What You Now Have

A **beautiful, interactive web dashboard** that shows:

✅ **Portfolio Summary** — Real-time value, P&L, returns  
✅ **Holdings Table** — All positions with color-coded gains  
✅ **Portfolio Pie Chart** — Visual allocation breakdown  
✅ **Performance Charts** — Portfolio vs SPY vs QQQ  
✅ **Technical Analysis** — RSI, volume, status for each holding  
✅ **Rebalancing Recommendations** — Exact trades needed  
✅ **Macro Snapshot** — VIX, 10Y yield, USD index  
✅ **Responsive Design** — Works on desktop, tablet, phone  

---

## How to Run

### Step 1: Install Dependencies (one time)
Dependencies are installing now. Once done, you're ready!

### Step 2: Open the Dashboard
```bash
cd /Users/patriciobravoknobloch/cio-briefing
streamlit run dashboard.py
```

### What Happens
1. Your browser automatically opens
2. Beautiful dashboard appears
3. Data auto-updates every 5 minutes
4. You can interact with charts and tables

---

## Dashboard Sections

### 📊 Top Metrics
- Portfolio Value (total)
- Total Return ($ and %)
- Number of Holdings
- Today's Return

### 🔴 Alerts Section
Shows any positions that moved >3% today

### 📈 Holdings Table
- Ticker, Shares, Current Price
- Current Value, P&L ($), P&L (%)
- Weight vs Target
- Status (ON_TARGET / OVERWEIGHT / UNDERWEIGHT)

### 🥧 Allocation Pie Chart
Interactive pie showing your portfolio breakdown

### 📊 Performance Chart
Bar chart comparing:
- Your Portfolio
- SPY benchmark
- QQQ benchmark

By period: Today, WTD, MTD, YTD

### 🔬 Technical Analysis
For each holding shows:
- Current Price
- RSI(14) with overbought/oversold indicator
- Volume status
- Technical summary

### 🔄 Rebalancing Recommendations
If any position drifts >2%:
- Shows priority ranked list
- Current vs Target weight
- Shares to buy/sell
- Dollar amount

### 🌍 Macro Snapshot
- VIX (with up/down arrow)
- 10Y Treasury Yield
- USD Index

---

## How to Use

### Daily Check-In
```bash
streamlit run dashboard.py
```
Opens in browser → Review all metrics in 2 minutes

### Interactive Features
- **Click charts** — Zoom, pan, hover for details
- **Sort tables** — Click column headers to sort
- **Responsive** — Resizes for any screen size

### Data Refresh
- Auto-refreshes every 5 minutes
- Click "Rerun" button to refresh immediately
- Shows "Last Updated" timestamp

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `R` | Rerun the app |
| `C` | Clear cache (forces fresh data) |
| `Ctrl+C` | Stop the server |

---

## Stopping the Dashboard

In your terminal:
```bash
Ctrl+C
```

---

## Customizing the Dashboard

To modify colors, layout, or add new sections, edit `dashboard.py`:

```bash
nano dashboard.py
```

Then restart:
```bash
streamlit run dashboard.py
```

---

## Troubleshooting

### Dashboard won't open in browser
Try opening manually:
```
http://localhost:8501
```

### Data looks stale
Press `R` to rerun
Or click "Rerun" button in top right

### Charts not showing
Make sure `plotly` is installed:
```bash
pip install plotly
```

### Port already in use
Use different port:
```bash
streamlit run dashboard.py --server.port 8502
```

---

## Mobile View

The dashboard works great on mobile:
1. Run on your Mac
2. Find your Mac's IP: `ipconfig getifaddr en0`
3. Open on phone/tablet: `http://[your-ip]:8501`

---

## Next Steps

1. ✅ Run the dashboard: `streamlit run dashboard.py`
2. ✅ Review your portfolio visually
3. ✅ Check rebalancing recommendations
4. ✅ Monitor technical health
5. ✅ Make trading decisions

---

## You Now Have Two Ways to Check Your Portfolio

### Option 1: Terminal (Fast, Simple)
```bash
python3 cio_brief.py
```
Text output in your terminal

### Option 2: Dashboard (Visual, Interactive)
```bash
streamlit run dashboard.py
```
Beautiful web dashboard in your browser

**Use whichever you prefer!** 🎨
