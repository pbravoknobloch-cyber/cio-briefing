"""Data fetching module for market data and technical indicators."""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import config


class DataFetcher:
    def __init__(self):
        self.cache = {}

    def fetch_ticker_data(self, tickers: List[str], period: str = "1y") -> Dict:
        """Fetch historical and current data for tickers."""
        data = {}
        for ticker in tickers:
            try:
                ticker_obj = yf.Ticker(ticker)
                hist = ticker_obj.history(period=period)
                hist.index = pd.to_datetime(hist.index)
                data[ticker] = {
                    "history": hist,
                    "info": ticker_obj.info,
                    "current_price": hist["Close"].iloc[-1],
                }
            except Exception as e:
                print(f"Warning: Could not fetch data for {ticker}: {e}")
                data[ticker] = None
        return data

    def fetch_current_prices(self, tickers: List[str]) -> Dict[str, float]:
        """Fetch current prices for tickers."""
        prices = {}
        for ticker in tickers:
            try:
                ticker_obj = yf.Ticker(ticker)
                hist = ticker_obj.history(period="1d")
                if not hist.empty:
                    prices[ticker] = hist["Close"].iloc[-1]
            except Exception as e:
                print(f"Warning: Could not fetch price for {ticker}: {e}")
        return prices

    def fetch_multi_day_prices(self, tickers: List[str], days: int = 252) -> Dict[str, pd.DataFrame]:
        """Fetch multi-day price history for performance calculations."""
        data = {}
        for ticker in tickers:
            try:
                hist = yf.download(ticker, period=f"{days}d", progress=False)
                data[ticker] = hist
            except Exception as e:
                print(f"Warning: Could not fetch history for {ticker}: {e}")
        return data

    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI(14) from price series."""
        if len(prices) < period + 1:
            return None
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1])

    def calculate_moving_averages(
        self, prices: pd.Series, short: int = 20, long: int = 50
    ) -> Tuple[float, float]:
        """Calculate moving averages."""
        ma_short = float(prices.rolling(window=short).mean().iloc[-1])
        ma_long = float(prices.rolling(window=long).mean().iloc[-1])
        return ma_short, ma_long

    def calculate_avg_volume(self, volume: pd.Series, period: int = 20) -> float:
        """Calculate average volume over period."""
        return float(volume.rolling(window=period).mean().iloc[-1])

    def fetch_macro_indicators(self) -> Dict:
        """Fetch macro indicators: VIX, 10Y yield, USD index."""
        macro = {}
        try:
            vix = yf.Ticker("^VIX").history(period="5d")
            macro["vix_current"] = vix["Close"].iloc[-1]
            macro["vix_prev"] = vix["Close"].iloc[-2]
            macro["vix_direction"] = "↑" if macro["vix_current"] > macro["vix_prev"] else "↓"
        except:
            macro["vix_current"] = None

        try:
            tnx = yf.Ticker("^TNX").history(period="5d")
            macro["yield_10y_current"] = tnx["Close"].iloc[-1]
            macro["yield_10y_prev"] = tnx["Close"].iloc[-2]
            macro["yield_10y_direction"] = "↑" if macro["yield_10y_current"] > macro["yield_10y_prev"] else "↓"
        except:
            macro["yield_10y_current"] = None

        try:
            dxy = yf.Ticker("^DXY").history(period="5d")
            macro["usd_index_current"] = dxy["Close"].iloc[-1]
            macro["usd_index_prev"] = dxy["Close"].iloc[-2]
            macro["usd_index_direction"] = "↑" if macro["usd_index_current"] > macro["usd_index_prev"] else "↓"
        except:
            macro["usd_index_current"] = None

        return macro
