#!/usr/bin/env python3
"""
CIO Morning Briefing System
Main CLI entry point with rich terminal output.
"""
import argparse
import sys
from pathlib import Path

import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from datetime import datetime

import config
from data_fetcher import DataFetcher
from portfolio_analyzer import PortfolioAnalyzer
from performance_analyzer import PerformanceAnalyzer
from technical_analyzer import TechnicalAnalyzer
from report_generator import ReportGenerator


console = Console()


def load_portfolio() -> pd.DataFrame:
    """Load portfolio from CSV."""
    try:
        portfolio = pd.read_csv(config.PORTFOLIO_FILE)
        return portfolio
    except FileNotFoundError:
        console.print(
            f"[red]Error: portfolio.csv not found at {config.PORTFOLIO_FILE}[/red]"
        )
        sys.exit(1)


def print_header():
    """Print briefing header."""
    timestamp = datetime.now().strftime("%A, %B %d, %Y at %H:%M")
    header = f"CIO MORNING BRIEFING — {timestamp}"
    console.print(Panel(header, style="bold blue"))


def print_alerts(alerts: list):
    """Print alert section."""
    if not alerts:
        return

    console.print("\n[bold red]🔴 ALERTS[/bold red]")
    for ticker in alerts:
        console.print(f"  • {ticker} moved >3% today")


def print_portfolio_snapshot(portfolio_df: pd.DataFrame, portfolio_totals: dict):
    """Print portfolio snapshot."""
    console.print("\n[bold green]📊 PORTFOLIO SNAPSHOT[/bold green]")

    snapshot_table = Table(show_header=False, box=None)
    snapshot_table.add_row("Total Value", f"${portfolio_totals['total_value']:,.2f}")

    gain_loss = portfolio_totals["total_gain_loss"]
    gain_loss_pct = portfolio_totals["total_gain_loss_pct"]
    color = "green" if gain_loss >= 0 else "red"
    snapshot_table.add_row(
        "Total P&L",
        f"[{color}]${gain_loss:,.2f} ({gain_loss_pct:+.2f}%)[/{color}]",
    )

    console.print(snapshot_table)
    console.print()

    # Holdings table
    holdings_table = Table(title="Holdings", show_header=True, header_style="bold")
    holdings_table.add_column("Ticker", style="bold")
    holdings_table.add_column("Shares", justify="right")
    holdings_table.add_column("Price", justify="right")
    holdings_table.add_column("Value", justify="right")
    holdings_table.add_column("P&L ($)", justify="right")
    holdings_table.add_column("P&L (%)", justify="right")
    holdings_table.add_column("Weight", justify="right")
    holdings_table.add_column("Target", justify="right")
    holdings_table.add_column("Status", style="bold")

    for _, row in portfolio_df.iterrows():
        pl_color = "green" if row["gain_loss_dollar"] >= 0 else "red"
        status_color = "yellow" if row["drift_status"] != "ON_TARGET" else "white"

        holdings_table.add_row(
            row["ticker"],
            f"{row['shares']:.0f}",
            f"${row['current_price']:.2f}",
            f"${row['current_value']:,.2f}",
            f"[{pl_color}]${row['gain_loss_dollar']:,.2f}[/{pl_color}]",
            f"[{pl_color}]{row['gain_loss_pct']:+.2f}%[/{pl_color}]",
            f"{row['current_weight_pct']:.2f}%",
            f"{row['target_allocation_pct']:.2f}%",
            f"[{status_color}]{row['drift_status']}[/{status_color}]",
        )

    console.print(holdings_table)


def print_rebalancing(rebalance_df: pd.DataFrame):
    """Print rebalancing section."""
    if rebalance_df.empty:
        console.print("\n[green]✓ Portfolio on target—no rebalancing needed[/green]")
        return

    console.print("\n[bold yellow]🔄 REBALANCING ALERTS[/bold yellow]")
    rebalance_table = Table(show_header=True, header_style="bold")
    rebalance_table.add_column("Priority", justify="right")
    rebalance_table.add_column("Ticker", style="bold")
    rebalance_table.add_column("Drift %", justify="right")
    rebalance_table.add_column("Action", style="bold")
    rebalance_table.add_column("Shares", justify="right")
    rebalance_table.add_column("Amount", justify="right")

    for _, row in rebalance_df.iterrows():
        action_color = "red" if row["shares_to_trade"] < 0 else "green"
        action_text = "SELL" if row["shares_to_trade"] < 0 else "BUY"
        shares_abs = abs(row["shares_to_trade"])
        amount_abs = abs(row["rebalance_amount"])

        rebalance_table.add_row(
            f"{int(row['priority'])}",
            row["ticker"],
            f"{row['weight_drift_pct']:+.2f}%",
            f"[{action_color}]{action_text}[/{action_color}]",
            f"{shares_abs:.2f}",
            f"${amount_abs:,.2f}",
        )

    console.print(rebalance_table)


def print_performance(performance: dict):
    """Print performance dashboard."""
    console.print("\n[bold cyan]📈 PERFORMANCE DASHBOARD[/bold cyan]")

    perf_table = Table(show_header=True, header_style="bold")
    perf_table.add_column("Period", style="bold")
    perf_table.add_column("Portfolio", justify="right")
    perf_table.add_column("SPY", justify="right")
    perf_table.add_column("QQQ", justify="right")

    for period in ["today", "wtd", "mtd", "ytd"]:
        port = performance.get("portfolio", {}).get(period, 0)
        spy = performance.get("SPY", {}).get(period, 0)
        qqq = performance.get("QQQ", {}).get(period, 0)

        port_color = "green" if port >= 0 else "red"
        spy_color = "green" if spy >= 0 else "red"
        qqq_color = "green" if qqq >= 0 else "red"

        perf_table.add_row(
            period.upper(),
            f"[{port_color}]{port:+.2f}%[/{port_color}]",
            f"[{spy_color}]{spy:+.2f}%[/{spy_color}]",
            f"[{qqq_color}]{qqq:+.2f}%[/{qqq_color}]",
        )

    console.print(perf_table)


def print_technical(portfolio_df: pd.DataFrame, technical_data: dict):
    """Print technical analysis."""
    console.print("\n[bold magenta]🔬 HOLDINGS TECHNICAL CONTEXT[/bold magenta]")

    tech_table = Table(show_header=True, header_style="bold")
    tech_table.add_column("Ticker", style="bold")
    tech_table.add_column("Price", justify="right")
    tech_table.add_column("RSI(14)", justify="right")
    tech_table.add_column("MA(20/50)", justify="center")
    tech_table.add_column("Volume", justify="center")
    tech_table.add_column("Technical", style="dim")

    for _, row in portfolio_df.iterrows():
        ticker = row["ticker"]
        if ticker not in technical_data or "error" in technical_data[ticker]:
            continue

        tech = technical_data[ticker]
        rsi = f"{tech['rsi']:.1f}" if tech.get("rsi") else "N/A"
        ma_pos = tech.get("price_vs_ma20", "N/A")
        volume_flag = tech.get("volume_flag", "✓")
        summary = tech.get("summary", "N/A")

        tech_table.add_row(
            ticker,
            f"${tech['current_price']:.2f}",
            rsi,
            ma_pos,
            volume_flag,
            summary,
        )

    console.print(tech_table)


def print_macro(macro_data: dict):
    """Print macro snapshot."""
    console.print("\n[bold]🌍 MACRO SNAPSHOT[/bold]")

    macro_table = Table(show_header=False, box=None)

    if macro_data.get("vix_current"):
        vix_color = "red" if macro_data["vix_current"] > 20 else "green"
        vix_dir = macro_data["vix_direction"]
        macro_table.add_row(
            "VIX",
            f"[{vix_color}]{macro_data['vix_current']:.2f}[/{vix_color}] {vix_dir}",
        )

    if macro_data.get("yield_10y_current"):
        yld_dir = macro_data["yield_10y_direction"]
        macro_table.add_row(
            "10Y Yield", f"{macro_data['yield_10y_current']:.2f}% {yld_dir}"
        )

    if macro_data.get("usd_index_current"):
        usd_dir = macro_data["usd_index_direction"]
        macro_table.add_row(
            "USD Index", f"{macro_data['usd_index_current']:.2f} {usd_dir}"
        )

    console.print(macro_table)


def print_manual_section():
    """Print manual entry section."""
    console.print("\n[bold]📰 IBKR TOP STORIES — ADD MANUALLY[/bold]")
    console.print("[dim]Paste your top 10 from IBKR here[/dim]\n")


def run_briefing(quick: bool = False, rebalance: bool = False):
    """Run the complete briefing."""
    print_header()

    # Load portfolio
    portfolio_df = load_portfolio()
    tickers = portfolio_df["ticker"].tolist()

    # Fetch data
    console.print("\n[dim]Fetching market data...[/dim]")
    fetcher = DataFetcher()

    # Current prices and multi-day history
    current_prices = fetcher.fetch_current_prices(tickers)
    price_history = fetcher.fetch_multi_day_prices(tickers)

    # Macro data
    macro_data = fetcher.fetch_macro_indicators()

    # Analyze portfolio
    analyzer = PortfolioAnalyzer(portfolio_df, current_prices)
    portfolio_df = analyzer.calculate_weights()
    portfolio_totals = analyzer.get_portfolio_totals()

    # Check for alerts
    alerts = analyzer.check_large_moves(config.ALERT_MOVE_THRESHOLD_PCT)

    # Quick mode: just snapshot
    if quick:
        print_alerts(alerts)
        print_portfolio_snapshot(portfolio_df, portfolio_totals)
        print_macro(macro_data)
        console.print("\n[dim]Full briefing saved to briefings folder[/dim]\n")
        return

    # Full briefing mode
    print_alerts(alerts)
    print_portfolio_snapshot(portfolio_df, portfolio_totals)

    # Rebalancing section
    rebalance_df = analyzer.get_rebalancing_plan()
    if rebalance:
        print_rebalancing(rebalance_df)
    else:
        # Show brief status
        if not rebalance_df.empty:
            console.print(f"\n[yellow]⚠ {len(rebalance_df)} position(s) need rebalancing (use --rebalance for details)[/yellow]")
        else:
            console.print("\n[green]✓ Portfolio on target[/green]")

    # Performance
    perf_analyzer = PerformanceAnalyzer(portfolio_df, current_prices)
    portfolio_returns = perf_analyzer.calculate_portfolio_returns(price_history)
    benchmark_returns = perf_analyzer.calculate_benchmark_returns(price_history)
    performance = perf_analyzer.get_performance_comparison(portfolio_returns, benchmark_returns)
    print_performance(performance)

    # Technical analysis
    tech_analyzer = TechnicalAnalyzer(price_history)
    technical_data = tech_analyzer.analyze_all(tickers)
    print_technical(portfolio_df, technical_data)

    # Macro
    print_macro(macro_data)

    # Manual section
    print_manual_section()

    # Generate and save markdown report
    report_gen = ReportGenerator()
    markdown_content = report_gen.generate_markdown_brief(
        portfolio_df,
        portfolio_totals,
        alerts,
        performance,
        technical_data,
        macro_data,
        rebalance_df if not rebalance_df.empty else None,
    )
    filepath = report_gen.save_brief(markdown_content)
    console.print(f"[dim]📄 Briefing saved: {filepath}[/dim]\n")


def main():
    parser = argparse.ArgumentParser(
        description="CIO Morning Briefing System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cio_brief.py              # Full briefing
  python cio_brief.py --quick      # Snapshot only
  python cio_brief.py --rebalance  # Full briefing with rebalancing details
        """,
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick mode: portfolio snapshot and macro only",
    )
    parser.add_argument(
        "--rebalance",
        action="store_true",
        help="Show detailed rebalancing report",
    )

    args = parser.parse_args()

    try:
        run_briefing(quick=args.quick, rebalance=args.rebalance)
    except KeyboardInterrupt:
        console.print("\n[yellow]Briefing interrupted[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
