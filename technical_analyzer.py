"""Technical analysis module for RSI, moving averages, and volume."""
import pandas as pd
from typing import Dict, Optional, Tuple
import config
from data_fetcher import DataFetcher


class TechnicalAnalyzer:
    def __init__(self, price_history: Dict[str, pd.DataFrame]):
        self.price_history = price_history
        self.data_fetcher = DataFetcher()

    def analyze_ticker(self, ticker: str) -> Dict:
        """Analyze a ticker for technical indicators."""
        if ticker not in self.price_history or self.price_history[ticker] is None:
            return {"error": f"No data for {ticker}"}

        hist = self.price_history[ticker]
        if hist.empty:
            return {"error": f"Empty data for {ticker}"}

        close_prices = hist["Close"]
        volumes = hist["Volume"]

        result = {
            "ticker": ticker,
            "current_price": float(close_prices.iloc[-1]),
        }

        # RSI
        try:
            result["rsi"] = self.data_fetcher.calculate_rsi(close_prices, config.RSI_PERIOD)
        except:
            result["rsi"] = None

        # Moving Averages
        try:
            ma_20, ma_50 = self.data_fetcher.calculate_moving_averages(
                close_prices, config.MA_SHORT, config.MA_LONG
            )
            result["ma_20"] = ma_20
            result["ma_50"] = ma_50
            result["price_vs_ma20"] = "Above" if close_prices.iloc[-1] > ma_20 else "Below"
            result["price_vs_ma50"] = "Above" if close_prices.iloc[-1] > ma_50 else "Below"
        except:
            result["ma_20"] = None
            result["ma_50"] = None
            result["price_vs_ma20"] = None
            result["price_vs_ma50"] = None

        # Volume
        try:
            avg_volume = self.data_fetcher.calculate_avg_volume(volumes, 20)
            current_volume = volumes.iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            result["volume_ratio"] = volume_ratio
            result["volume_flag"] = "🔴 SPIKE" if volume_ratio > config.VOLUME_SPIKE_MULTIPLIER else "✓"
        except:
            result["volume_ratio"] = 1.0
            result["volume_flag"] = "✓"

        # Technical Summary
        result["summary"] = self._get_technical_summary(result)

        return result

    def _get_technical_summary(self, analysis: Dict) -> str:
        """Generate 1-line technical summary."""
        summary_parts = []

        rsi = analysis.get("rsi")
        if rsi is not None and not pd.isna(rsi):
            rsi = float(rsi)
            if rsi > 70:
                summary_parts.append("Overbought (RSI>70)")
            elif rsi < 30:
                summary_parts.append("Oversold (RSI<30)")
            else:
                summary_parts.append(f"RSI {rsi:.0f}")

        ma_20 = analysis.get("ma_20")
        ma_50 = analysis.get("ma_50")
        if ma_20 is not None and ma_50 is not None and not pd.isna(ma_20) and not pd.isna(ma_50):
            ma_20 = float(ma_20)
            ma_50 = float(ma_50)
            if ma_20 > ma_50:
                summary_parts.append("20>50 (bullish)")
            else:
                summary_parts.append("20<50 (bearish)")

        if analysis.get("volume_flag") == "🔴 SPIKE":
            summary_parts.append(f"Vol spike ({float(analysis['volume_ratio']):.1f}x)")

        if not summary_parts:
            summary_parts.append("Neutral")

        return " | ".join(summary_parts[:2])  # Max 2 summary items for brevity

    def analyze_all(self, tickers: list) -> Dict[str, Dict]:
        """Analyze all tickers."""
        results = {}
        for ticker in tickers:
            results[ticker] = self.analyze_ticker(ticker)
        return results
