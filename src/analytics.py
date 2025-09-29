"""Analytics helpers for processing B3 market data."""

from __future__ import annotations

from typing import Tuple

import pandas as pd


def compute_normalised_prices(prices: pd.DataFrame) -> pd.DataFrame:
    """Scale prices so that every series starts at 100."""

    normalised = prices.div(prices.iloc[0]).mul(100)
    return normalised.dropna(how="all")


def compute_daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Compute percentage daily returns for the given price series."""

    returns = prices.pct_change().mul(100)
    return returns.dropna(how="all")


def summarise_performance(prices: pd.DataFrame) -> pd.DataFrame:
    """Generate summary statistics for each asset."""

    returns = compute_daily_returns(prices)
    cumulative = (1 + returns.div(100)).prod() - 1
    volatility = returns.std()
    sharpe = returns.mean() / returns.std()

    summary = pd.DataFrame(
        {
            "Total Return (%)": cumulative.mul(100),
            "Volatility (%)": volatility,
            "Sharpe (daily)": sharpe,
        }
    )
    return summary.sort_values(by="Total Return (%)", ascending=False)


def compute_correlation(prices: pd.DataFrame) -> pd.DataFrame:
    """Correlation matrix of daily returns."""

    returns = compute_daily_returns(prices)
    return returns.corr()


def split_index(prices: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    """Return the index as a tuple of date and time series for plotting convenience."""

    idx = prices.index
    return idx.date, idx.time
