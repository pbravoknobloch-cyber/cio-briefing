"""Portfolio analysis module."""
import pandas as pd
from typing import Dict, List, Tuple
import config


class PortfolioAnalyzer:
    def __init__(self, portfolio_df: pd.DataFrame, current_prices: Dict[str, float]):
        self.portfolio = portfolio_df.copy()
        self.current_prices = current_prices
        self.analyze()

    def analyze(self):
        """Calculate portfolio metrics."""
        self.portfolio["current_price"] = self.portfolio["ticker"].map(self.current_prices)
        self.portfolio["current_value"] = self.portfolio["shares"] * self.portfolio["current_price"]
        self.portfolio["cost_basis_total"] = self.portfolio["shares"] * self.portfolio["avg_cost_basis"]
        self.portfolio["gain_loss_dollar"] = self.portfolio["current_value"] - self.portfolio["cost_basis_total"]
        self.portfolio["gain_loss_pct"] = (
            (self.portfolio["current_price"] - self.portfolio["avg_cost_basis"]) / self.portfolio["avg_cost_basis"] * 100
        )

    def get_portfolio_totals(self) -> Dict:
        """Get total portfolio metrics."""
        total_value = self.portfolio["current_value"].sum()
        total_cost_basis = self.portfolio["cost_basis_total"].sum()
        total_gain_loss = self.portfolio["gain_loss_dollar"].sum()
        total_gain_loss_pct = (
            (total_gain_loss / total_cost_basis * 100) if total_cost_basis > 0 else 0
        )
        return {
            "total_value": total_value,
            "total_cost_basis": total_cost_basis,
            "total_gain_loss": total_gain_loss,
            "total_gain_loss_pct": total_gain_loss_pct,
        }

    def calculate_weights(self) -> pd.DataFrame:
        """Calculate current weights vs target weights."""
        total_value = self.portfolio["current_value"].sum()
        self.portfolio["current_weight_pct"] = (self.portfolio["current_value"] / total_value) * 100
        self.portfolio["weight_drift_pct"] = (
            self.portfolio["current_weight_pct"] - self.portfolio["target_allocation_pct"]
        )
        self.portfolio["is_drifted"] = (
            abs(self.portfolio["weight_drift_pct"]) > config.DRIFT_THRESHOLD_PCT
        )
        self.portfolio["drift_status"] = self.portfolio.apply(
            lambda row: "OVERWEIGHT" if row["weight_drift_pct"] > 0 else "UNDERWEIGHT"
            if row["is_drifted"] else "ON_TARGET",
            axis=1,
        )
        return self.portfolio

    def get_rebalancing_plan(self) -> pd.DataFrame:
        """Calculate rebalancing needed to return to targets."""
        total_value = self.portfolio["current_value"].sum()
        self.portfolio["target_value"] = total_value * (self.portfolio["target_allocation_pct"] / 100)
        self.portfolio["rebalance_amount"] = self.portfolio["target_value"] - self.portfolio["current_value"]
        self.portfolio["shares_to_trade"] = self.portfolio["rebalance_amount"] / self.portfolio["current_price"]
        self.portfolio["shares_to_trade"] = self.portfolio["shares_to_trade"].round(2)

        # Only show positions that need rebalancing
        rebalance_df = self.portfolio[self.portfolio["is_drifted"]].copy()
        rebalance_df = rebalance_df.sort_values("weight_drift_pct", key=abs, ascending=False)
        rebalance_df["priority"] = range(1, len(rebalance_df) + 1)

        return rebalance_df[
            ["ticker", "current_weight_pct", "target_allocation_pct", "weight_drift_pct",
             "shares_to_trade", "rebalance_amount", "priority"]
        ]

    def get_sorted_positions(self, sort_by: str = "current_value", ascending: bool = False) -> pd.DataFrame:
        """Get portfolio sorted by specified column."""
        return self.portfolio.sort_values(sort_by, ascending=ascending)

    def get_positions_by_performance(self) -> Tuple[pd.Series, pd.Series]:
        """Get best and worst performers today."""
        best = self.portfolio.loc[self.portfolio["gain_loss_pct"].idxmax()]
        worst = self.portfolio.loc[self.portfolio["gain_loss_pct"].idxmin()]
        return best, worst

    def check_large_moves(self, threshold_pct: float = 3.0) -> List[str]:
        """Check for positions with large 1-day moves."""
        alerted = self.portfolio[abs(self.portfolio["gain_loss_pct"]) > threshold_pct]["ticker"].tolist()
        return alerted
