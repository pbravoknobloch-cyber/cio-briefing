"""Performance analysis module for P&L and benchmarks."""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple


class PerformanceAnalyzer:
    def __init__(self, portfolio_df: pd.DataFrame, current_prices: Dict[str, float]):
        self.portfolio = portfolio_df.copy()
        self.current_prices = current_prices

    def calculate_portfolio_returns(self, price_history: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """Calculate portfolio returns for different periods."""
        returns = {
            "today": 0.0,
            "wtd": 0.0,
            "mtd": 0.0,
            "ytd": 0.0,
        }

        # Prepare weighted prices
        total_current_value = (self.portfolio["shares"] * self.portfolio["current_price"]).sum()

        if total_current_value == 0:
            return returns

        for period_name, days in [
            ("today", 1),
            ("wtd", 5),
            ("mtd", 21),
            ("ytd", 252),
        ]:
            try:
                period_returns = []
                weights = []

                for _, row in self.portfolio.iterrows():
                    ticker = row["ticker"]

                    # Skip if no data
                    if ticker not in price_history or price_history[ticker] is None:
                        continue

                    hist = price_history[ticker]
                    if hist is None or len(hist) == 0:
                        continue

                    if len(hist) < days + 1:
                        continue

                    try:
                        close_prices = hist["Close"]

                        # Get scalar values
                        current_price = float(close_prices.iloc[-1].item() if hasattr(close_prices.iloc[-1], 'item') else close_prices.iloc[-1])
                        past_price = float(close_prices.iloc[-days - 1].item() if hasattr(close_prices.iloc[-days - 1], 'item') else close_prices.iloc[-days - 1])

                        # Calculate return
                        if past_price != 0:
                            period_return = (current_price - past_price) / past_price
                        else:
                            period_return = 0.0

                        # Calculate weight
                        weight = (row["shares"] * row["current_price"]) / total_current_value

                        period_returns.append(period_return)
                        weights.append(weight)
                    except Exception:
                        continue

                # Calculate weighted average return
                if period_returns and weights:
                    weights_sum = sum(weights)
                    if weights_sum > 0:
                        weighted_return = sum(r * w / weights_sum for r, w in zip(period_returns, weights)) * 100
                        returns[period_name] = float(weighted_return)
                    else:
                        returns[period_name] = 0.0
                else:
                    returns[period_name] = 0.0
            except Exception:
                returns[period_name] = 0.0

        return returns

    def calculate_benchmark_returns(self, price_history: Dict[str, pd.DataFrame]) -> Dict[str, Dict[str, float]]:
        """Calculate benchmark returns (SPY, QQQ)."""
        benchmark_returns = {}

        for benchmark in ["SPY", "QQQ"]:
            if benchmark not in price_history or price_history[benchmark] is None:
                continue

            try:
                hist = price_history[benchmark]
                if hist is None or len(hist) == 0:
                    continue

                close_prices = hist["Close"]
                returns = {
                    "today": 0.0,
                    "wtd": 0.0,
                    "mtd": 0.0,
                    "ytd": 0.0,
                }

                for period_name, days in [
                    ("today", 1),
                    ("wtd", 5),
                    ("mtd", 21),
                    ("ytd", 252),
                ]:
                    try:
                        if len(close_prices) < days + 1:
                            returns[period_name] = 0.0
                            continue

                        current = float(close_prices.iloc[-1].item() if hasattr(close_prices.iloc[-1], 'item') else close_prices.iloc[-1])
                        past = float(close_prices.iloc[-days - 1].item() if hasattr(close_prices.iloc[-days - 1], 'item') else close_prices.iloc[-days - 1])

                        if past != 0:
                            period_return = (current - past) / past * 100
                        else:
                            period_return = 0.0

                        returns[period_name] = float(period_return)
                    except Exception:
                        returns[period_name] = 0.0

                benchmark_returns[benchmark] = returns
            except Exception:
                continue

        return benchmark_returns

    def get_performance_comparison(
        self, portfolio_returns: Dict, benchmark_returns: Dict
    ) -> Dict[str, Dict[str, float]]:
        """Compare portfolio returns to benchmarks."""
        comparison = {
            "portfolio": portfolio_returns,
        }
        comparison.update(benchmark_returns)
        return comparison
