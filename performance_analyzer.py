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
        returns = {}

        # Prepare weighted prices
        total_current_value = (self.portfolio["shares"] * self.portfolio["current_price"]).sum()

        for period_name, days in [
            ("today", 1),
            ("wtd", 5),
            ("mtd", 21),
            ("ytd", 252),
        ]:
            period_returns = []
            weights = []

            for _, row in self.portfolio.iterrows():
                ticker = row["ticker"]
                if ticker not in price_history or price_history[ticker] is None:
                    continue

                hist = price_history[ticker]
                if hist is None or len(hist) < days + 1:
                    continue

                close_prices = hist["Close"]
                if days == 1:
                    period_return = float((close_prices.iloc[-1] - close_prices.iloc[-2]) / close_prices.iloc[-2])
                else:
                    period_return = float((close_prices.iloc[-1] - close_prices.iloc[-days - 1]) / close_prices.iloc[-days - 1])

                weight = float((row["shares"] * row["current_price"]) / total_current_value)
                period_returns.append(period_return)
                weights.append(weight)

            if period_returns and weights:
                # Normalize weights to sum to 1.0 (in case some positions were excluded)
                weights_sum = sum(weights)
                weighted_return = float(sum(r * w / weights_sum for r, w in zip(period_returns, weights)) * 100)
                returns[period_name] = weighted_return
            else:
                returns[period_name] = 0.0

        return {k: float(v) for k, v in returns.items()}

    def calculate_benchmark_returns(self, price_history: Dict[str, pd.DataFrame]) -> Dict[str, Dict[str, float]]:
        """Calculate benchmark returns (SPY, QQQ)."""
        benchmark_returns = {}

        for benchmark in ["SPY", "QQQ"]:
            if benchmark not in price_history or price_history[benchmark] is None:
                continue

            hist = price_history[benchmark]
            close_prices = hist["Close"]
            returns = {}

            for period_name, days in [
                ("today", 1),
                ("wtd", 5),
                ("mtd", 21),
                ("ytd", 252),
            ]:
                if len(close_prices) < days + 1:
                    returns[period_name] = 0.0
                    continue

                if days == 1:
                    period_return = float((close_prices.iloc[-1] - close_prices.iloc[-2]) / close_prices.iloc[-2] * 100)
                else:
                    period_return = float(
                        (close_prices.iloc[-1] - close_prices.iloc[-days - 1]) / close_prices.iloc[-days - 1] * 100
                    )

                returns[period_name] = period_return

            benchmark_returns[benchmark] = returns

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
