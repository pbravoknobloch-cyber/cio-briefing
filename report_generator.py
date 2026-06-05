"""Report generation module for markdown export."""
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import config


class ReportGenerator:
    def __init__(self):
        self.timestamp = datetime.now()

    def generate_markdown_brief(
        self,
        portfolio_df: pd.DataFrame,
        portfolio_totals: Dict,
        alerts: List[str],
        performance: Dict,
        technical_data: Dict,
        macro_data: Dict,
        rebalance_df: Optional[pd.DataFrame] = None,
    ) -> str:
        """Generate complete markdown briefing."""
        md = []
        md.append(f"# CIO Morning Briefing")
        md.append(f"**{self.timestamp.strftime('%A, %B %d, %Y at %H:%M %Z')}**\n")

        # Alerts section
        if alerts:
            md.append("## 🔴 ALERTS\n")
            for alert in alerts:
                md.append(f"- **{alert}** has moved more than 3% today")
            md.append("")

        # Portfolio Snapshot
        md.append("## 📊 PORTFOLIO SNAPSHOT\n")
        md.append(
            f"| Metric | Value |\n"
            f"|--------|-------|\n"
            f"| Total Portfolio Value | ${portfolio_totals['total_value']:,.2f} |\n"
            f"| Total P&L | ${portfolio_totals['total_gain_loss']:,.2f} ({portfolio_totals['total_gain_loss_pct']:.2f}%) |\n"
        )
        md.append("")

        # Holdings Table
        md.append("### Holdings\n")
        holdings_display = portfolio_df[[
            "ticker", "shares", "current_price", "current_value",
            "gain_loss_dollar", "gain_loss_pct", "current_weight_pct",
            "target_allocation_pct", "drift_status"
        ]].copy()
        holdings_display.columns = [
            "Ticker", "Shares", "Price", "Value", "P&L ($)", "P&L (%)",
            "Weight %", "Target %", "Status"
        ]
        holdings_display["P&L ($)"] = holdings_display["P&L ($)"].apply(lambda x: f"${x:,.2f}")
        holdings_display["P&L (%)"] = holdings_display["P&L (%)"].apply(lambda x: f"{x:.2f}%")
        holdings_display["Price"] = holdings_display["Price"].apply(lambda x: f"${x:.2f}")
        holdings_display["Value"] = holdings_display["Value"].apply(lambda x: f"${x:,.2f}")
        holdings_display["Weight %"] = holdings_display["Weight %"].apply(lambda x: f"{x:.2f}%")
        holdings_display["Target %"] = holdings_display["Target %"].apply(lambda x: f"{x:.2f}%")

        md.append(holdings_display.to_markdown(index=False))
        md.append("")

        # Rebalancing Section
        if rebalance_df is not None and not rebalance_df.empty:
            md.append("## 🔄 REBALANCING ALERTS\n")
            rebalance_display = rebalance_df[[
                "ticker", "current_weight_pct", "target_allocation_pct",
                "weight_drift_pct", "shares_to_trade", "rebalance_amount", "priority"
            ]].copy()
            rebalance_display.columns = [
                "Ticker", "Current %", "Target %", "Drift %", "Shares to Trade", "Amount ($)", "Priority"
            ]
            rebalance_display["Current %"] = rebalance_display["Current %"].apply(lambda x: f"{x:.2f}%")
            rebalance_display["Target %"] = rebalance_display["Target %"].apply(lambda x: f"{x:.2f}%")
            rebalance_display["Drift %"] = rebalance_display["Drift %"].apply(lambda x: f"{x:.2f}%")
            rebalance_display["Amount ($)"] = rebalance_display["Amount ($)"].apply(lambda x: f"${x:,.2f}")

            md.append(rebalance_display.to_markdown(index=False))
            md.append("")

        # Performance Dashboard
        md.append("## 📈 PERFORMANCE DASHBOARD\n")
        perf_table = "| Period | Portfolio | SPY | QQQ |\n"
        perf_table += "|--------|-----------|-----|-----|\n"
        for period in ["today", "wtd", "mtd", "ytd"]:
            port_return = performance.get("portfolio", {}).get(period, 0)
            spy_return = performance.get("SPY", {}).get(period, 0)
            qqq_return = performance.get("QQQ", {}).get(period, 0)
            perf_table += f"| {period.upper()} | {port_return:+.2f}% | {spy_return:+.2f}% | {qqq_return:+.2f}% |\n"
        md.append(perf_table)
        md.append("")

        # Technical Analysis
        md.append("## 🔬 HOLDINGS TECHNICAL CONTEXT\n")
        tech_data = []
        for ticker in portfolio_df["ticker"]:
            if ticker in technical_data and "error" not in technical_data[ticker]:
                tech = technical_data[ticker]
                data_row = {
                    "Ticker": ticker,
                    "Price": f"${tech.get('current_price', 0):.2f}",
                    "RSI": f"{tech.get('rsi', 'N/A'):.1f}" if tech.get('rsi') else "N/A",
                    "20/50 MA": f"{tech.get('price_vs_ma20', 'N/A')}",
                    "Volume": tech.get('volume_flag', '✓'),
                    "Technical": tech.get('summary', 'N/A')
                }
                tech_data.append(data_row)

        if tech_data:
            tech_df = pd.DataFrame(tech_data)
            md.append(tech_df.to_markdown(index=False))
        md.append("")

        # Macro Snapshot
        md.append("## 🌍 MACRO SNAPSHOT\n")
        macro_lines = []
        if macro_data.get("vix_current"):
            vix_dir = macro_data["vix_direction"]
            macro_lines.append(
                f"**VIX:** {macro_data['vix_current']:.2f} {vix_dir}"
            )
        if macro_data.get("yield_10y_current"):
            yld_dir = macro_data["yield_10y_direction"]
            macro_lines.append(
                f"**10Y Yield:** {macro_data['yield_10y_current']:.2f}% {yld_dir}"
            )
        if macro_data.get("usd_index_current"):
            usd_dir = macro_data["usd_index_direction"]
            macro_lines.append(
                f"**USD Index:** {macro_data['usd_index_current']:.2f} {usd_dir}"
            )
        md.append(" | ".join(macro_lines))
        md.append("\n")

        # Manual Section
        md.append("## 📰 IBKR TOP STORIES — ADD MANUALLY\n")
        md.append("1. \n2. \n3. \n4. \n5. \n6. \n7. \n8. \n9. \n10. \n")

        return "\n".join(md)

    def save_brief(self, content: str) -> str:
        """Save markdown brief to file."""
        filename = self.timestamp.strftime("%Y-%m-%d") + "_CIO_brief.md"
        filepath = config.BRIEFINGS_DIR / filename
        with open(filepath, "w") as f:
            f.write(content)
        return str(filepath)
