#!/usr/bin/env python3
"""
Streamlit Dashboard for CIO Morning Briefing
Interactive web dashboard for portfolio management
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# Import our modules
from data_fetcher import DataFetcher
from portfolio_analyzer import PortfolioAnalyzer
from performance_analyzer import PerformanceAnalyzer
from technical_analyzer import TechnicalAnalyzer
import config

# Page config
st.set_page_config(
    page_title="Paradym CIO Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
    }
    .metric-label {
        font-size: 14px;
        opacity: 0.9;
    }
    .alert-box {
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .alert-danger {
        background-color: #fee;
        border-left: 4px solid #f44;
    }
    .alert-warning {
        background-color: #fef3cd;
        border-left: 4px solid #ffc107;
    }
    .alert-success {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_portfolio_data():
    """Load and process portfolio data"""
    portfolio_df = pd.read_csv(config.PORTFOLIO_FILE)
    return portfolio_df

@st.cache_data(ttl=300)
def fetch_market_data(tickers):
    """Fetch all market data"""
    fetcher = DataFetcher()
    current_prices = fetcher.fetch_current_prices(tickers)
    price_history = fetcher.fetch_multi_day_prices(tickers)
    macro_data = fetcher.fetch_macro_indicators()
    return current_prices, price_history, macro_data

def main():
    # Title
    st.markdown("# 📊 Paradym Private Capital — CIO Dashboard")
    st.markdown(f"**{datetime.now().strftime('%A, %B %d, %Y at %H:%M')}**")
    st.divider()

    # Load portfolio
    portfolio_df = load_portfolio_data()
    tickers = portfolio_df["ticker"].tolist()

    # Fetch data
    with st.spinner("Fetching market data..."):
        current_prices, price_history, macro_data = fetch_market_data(tickers)

    # Analyze portfolio
    analyzer = PortfolioAnalyzer(portfolio_df, current_prices)
    portfolio_df = analyzer.calculate_weights()
    portfolio_totals = analyzer.get_portfolio_totals()
    rebalance_df = analyzer.get_rebalancing_plan()

    # Analyze performance
    perf_analyzer = PerformanceAnalyzer(portfolio_df, current_prices)
    portfolio_returns = perf_analyzer.calculate_portfolio_returns(price_history)
    benchmark_returns = perf_analyzer.calculate_benchmark_returns(price_history)
    performance = perf_analyzer.get_performance_comparison(portfolio_returns, benchmark_returns)

    # Technical analysis
    tech_analyzer = TechnicalAnalyzer(price_history)
    technical_data = tech_analyzer.analyze_all(tickers)

    # Check for alerts
    alerts = analyzer.check_large_moves(config.ALERT_MOVE_THRESHOLD_PCT)

    # ============================================================================
    # TOP METRICS ROW
    # ============================================================================
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Portfolio Value",
            f"${portfolio_totals['total_value']:,.0f}",
            f"${portfolio_totals['total_gain_loss']:,.0f}"
        )

    with col2:
        pl_pct = portfolio_totals['total_gain_loss_pct']
        st.metric(
            "Total Return",
            f"{pl_pct:+.2f}%",
            f"${portfolio_totals['total_gain_loss']:,.0f}"
        )

    with col3:
        st.metric(
            "Holdings",
            f"{len(portfolio_df)}",
            "positions"
        )

    with col4:
        st.metric(
            "Today's Return",
            f"{portfolio_returns.get('today', 0):+.2f}%",
            help="Portfolio return for today"
        )

    st.divider()

    # ============================================================================
    # ALERTS SECTION
    # ============================================================================
    if alerts:
        st.markdown("### 🔴 ALERTS")
        for ticker in alerts:
            position = portfolio_df[portfolio_df['ticker'] == ticker].iloc[0]
            st.warning(
                f"**{ticker}** moved {position['gain_loss_pct']:+.2f}% today (threshold: ±3%)"
            )
        st.divider()

    # ============================================================================
    # MAIN CONTENT - TWO COLUMNS
    # ============================================================================
    col_left, col_right = st.columns(2)

    # ========== LEFT COLUMN: HOLDINGS TABLE ==========
    with col_left:
        st.markdown("### 📈 HOLDINGS")

        # Format holdings table
        holdings_display = portfolio_df[[
            "ticker", "shares", "current_price", "current_value",
            "gain_loss_dollar", "gain_loss_pct", "current_weight_pct",
            "target_allocation_pct", "drift_status"
        ]].copy()

        holdings_display = holdings_display.rename(columns={
            "ticker": "Ticker",
            "shares": "Shares",
            "current_price": "Price",
            "current_value": "Value",
            "gain_loss_dollar": "P&L ($)",
            "gain_loss_pct": "P&L (%)",
            "current_weight_pct": "Weight %",
            "target_allocation_pct": "Target %",
            "drift_status": "Status"
        })

        # Format display columns
        display_cols = holdings_display.copy()
        display_cols["Price"] = display_cols["Price"].apply(lambda x: f"${x:,.2f}")
        display_cols["Value"] = display_cols["Value"].apply(lambda x: f"${x:,.0f}")
        display_cols["P&L ($)"] = display_cols["P&L ($)"].apply(lambda x: f"${x:,.0f}")
        display_cols["P&L (%)"] = display_cols["P&L (%)"].apply(lambda x: f"{x:+.2f}%")
        display_cols["Shares"] = display_cols["Shares"].apply(lambda x: f"{x:.0f}")
        display_cols["Weight %"] = display_cols["Weight %"].apply(lambda x: f"{x:.2f}%")
        display_cols["Target %"] = display_cols["Target %"].apply(lambda x: f"{x:.2f}%")

        st.dataframe(
            display_cols,
            use_container_width=True,
            hide_index=True,
            column_config={
                "P&L (%)": st.column_config.TextColumn(),
                "Status": st.column_config.TextColumn()
            }
        )

    # ========== RIGHT COLUMN: PORTFOLIO PIE CHART ==========
    with col_right:
        st.markdown("### 🥧 PORTFOLIO ALLOCATION")

        pie_data = portfolio_df[["ticker", "current_value"]].copy()
        pie_data = pie_data.rename(columns={"ticker": "Ticker", "current_value": "Value"})

        fig_pie = px.pie(
            pie_data,
            values="Value",
            names="Ticker",
            hole=0.4,
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    st.divider()

    # ============================================================================
    # PERFORMANCE DASHBOARD
    # ============================================================================
    st.markdown("### 📊 PERFORMANCE vs BENCHMARKS")

    perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)

    periods = ["today", "wtd", "mtd", "ytd"]
    period_names = ["Today", "Week-to-Date", "Month-to-Date", "Year-to-Date"]
    cols = [perf_col1, perf_col2, perf_col3, perf_col4]

    for col, period, period_name in zip(cols, periods, period_names):
        with col:
            port_ret = performance.get("portfolio", {}).get(period, 0)
            spy_ret = performance.get("SPY", {}).get(period, 0)
            qqq_ret = performance.get("QQQ", {}).get(period, 0)

            st.metric(
                period_name,
                f"{port_ret:+.2f}%",
                help=f"SPY: {spy_ret:+.2f}% | QQQ: {qqq_ret:+.2f}%"
            )

    # Performance chart
    perf_data = {
        "Period": ["Today", "WTD", "MTD", "YTD"],
        "Portfolio": [
            performance.get("portfolio", {}).get("today", 0),
            performance.get("portfolio", {}).get("wtd", 0),
            performance.get("portfolio", {}).get("mtd", 0),
            performance.get("portfolio", {}).get("ytd", 0),
        ],
        "SPY": [
            performance.get("SPY", {}).get("today", 0),
            performance.get("SPY", {}).get("wtd", 0),
            performance.get("SPY", {}).get("mtd", 0),
            performance.get("SPY", {}).get("ytd", 0),
        ],
        "QQQ": [
            performance.get("QQQ", {}).get("today", 0),
            performance.get("QQQ", {}).get("wtd", 0),
            performance.get("QQQ", {}).get("mtd", 0),
            performance.get("QQQ", {}).get("ytd", 0),
        ]
    }
    perf_df = pd.DataFrame(perf_data)

    fig_perf = px.bar(
        perf_df,
        x="Period",
        y=["Portfolio", "SPY", "QQQ"],
        barmode="group",
        color_discrete_map={"Portfolio": "#667eea", "SPY": "#764ba2", "QQQ": "#f093fb"}
    )
    fig_perf.update_layout(height=400, yaxis_title="Return (%)", xaxis_title="")
    st.plotly_chart(fig_perf, use_container_width=True)

    st.divider()

    # ============================================================================
    # TECHNICAL ANALYSIS
    # ============================================================================
    st.markdown("### 🔬 TECHNICAL ANALYSIS")

    tech_cols = st.columns(3)
    col_idx = 0

    for ticker in portfolio_df["ticker"]:
        if ticker not in technical_data or "error" in technical_data[ticker]:
            continue

        tech = technical_data[ticker]
        rsi = tech.get("rsi")
        vol_flag = tech.get("volume_flag", "✓")
        summary = tech.get("summary", "N/A")

        with tech_cols[col_idx % 3]:
            st.markdown(f"#### {ticker}")

            # Price
            st.write(f"**Price:** ${tech['current_price']:.2f}")

            # RSI gauge
            if rsi:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("RSI(14)", f"{rsi:.1f}")
                with col2:
                    if rsi > 70:
                        st.warning("Overbought", icon="⚠️")
                    elif rsi < 30:
                        st.info("Oversold", icon="ℹ️")
                    else:
                        st.success("Neutral", icon="✓")

            # Volume
            st.write(f"**Volume:** {vol_flag}")

            # Summary
            st.write(f"**Status:** {summary}")

        col_idx += 1

    st.divider()

    # ============================================================================
    # REBALANCING RECOMMENDATIONS
    # ============================================================================
    st.markdown("### 🔄 REBALANCING RECOMMENDATIONS")

    if rebalance_df.empty:
        st.success("✓ Portfolio is on target — no rebalancing needed")
    else:
        st.warning(f"⚠️ {len(rebalance_df)} position(s) need rebalancing")

        rebal_display = rebalance_df[[
            "ticker", "current_weight_pct", "target_allocation_pct",
            "weight_drift_pct", "shares_to_trade", "rebalance_amount", "priority"
        ]].copy()

        rebal_display = rebal_display.rename(columns={
            "ticker": "Ticker",
            "current_weight_pct": "Current %",
            "target_allocation_pct": "Target %",
            "weight_drift_pct": "Drift %",
            "shares_to_trade": "Shares to Trade",
            "rebalance_amount": "Amount ($)",
            "priority": "Priority"
        })

        # Format for display
        display_rebal = rebal_display.copy()
        display_rebal["Current %"] = display_rebal["Current %"].apply(lambda x: f"{x:.2f}%")
        display_rebal["Target %"] = display_rebal["Target %"].apply(lambda x: f"{x:.2f}%")
        display_rebal["Drift %"] = display_rebal["Drift %"].apply(lambda x: f"{x:+.2f}%")
        display_rebal["Amount ($)"] = display_rebal["Amount ($)"].apply(lambda x: f"${x:,.0f}")
        display_rebal["Shares to Trade"] = display_rebal["Shares to Trade"].apply(lambda x: f"{x:+.2f}")

        st.dataframe(
            display_rebal,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    # ============================================================================
    # MACRO SNAPSHOT
    # ============================================================================
    st.markdown("### 🌍 MACRO SNAPSHOT")

    macro_col1, macro_col2, macro_col3 = st.columns(3)

    with macro_col1:
        if macro_data.get("vix_current"):
            vix_dir = "↑" if macro_data["vix_direction"] == "↑" else "↓"
            st.metric(
                "VIX",
                f"{macro_data['vix_current']:.2f}",
                f"{vix_dir}",
                delta_color="normal" if macro_data["vix_direction"] == "↑" else "inverse"
            )

    with macro_col2:
        if macro_data.get("yield_10y_current"):
            yld_dir = "↑" if macro_data["yield_10y_direction"] == "↑" else "↓"
            st.metric(
                "10Y Yield",
                f"{macro_data['yield_10y_current']:.2f}%",
                f"{yld_dir}",
                delta_color="off"
            )

    with macro_col3:
        if macro_data.get("usd_index_current"):
            usd_dir = "↑" if macro_data["usd_index_direction"] == "↑" else "↓"
            st.metric(
                "USD Index",
                f"{macro_data['usd_index_current']:.2f}",
                f"{usd_dir}",
                delta_color="off"
            )

    st.divider()

    # ============================================================================
    # FOOTER
    # ============================================================================
    st.markdown("---")
    st.markdown(
        f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"**Data Source:** Yahoo Finance | "
        f"**Dashboard:** Streamlit"
    )

if __name__ == "__main__":
    main()
