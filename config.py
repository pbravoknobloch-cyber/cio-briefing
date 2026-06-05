"""Configuration for CIO Briefing System."""
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
PORTFOLIO_FILE = PROJECT_ROOT / "portfolio.csv"
BRIEFINGS_DIR = PROJECT_ROOT / "briefings"
DATA_DIR = PROJECT_ROOT / "data"

# Ensure directories exist
BRIEFINGS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Portfolio thresholds
DRIFT_THRESHOLD_PCT = 2.0  # Flag positions that drift >2% from target
ALERT_MOVE_THRESHOLD_PCT = 3.0  # Alert on 1-day moves >3%
VOLUME_SPIKE_MULTIPLIER = 1.5  # Flag volume spikes >1.5x 20-day avg

# Benchmark tickers
BENCHMARK_TICKERS = ["SPY", "QQQ"]

# Technical indicators
RSI_PERIOD = 14
MA_SHORT = 20
MA_LONG = 50

# Date format for logging
DATE_FORMAT = "%Y-%m-%d"
BRIEF_FILENAME_FORMAT = f"{datetime.now().strftime(DATE_FORMAT)}_CIO_brief.md"
