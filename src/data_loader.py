"""Utilities for downloading market data for B3 assets."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from typing import Iterable, List

import pandas as pd
import yfinance as yf


@dataclass(frozen=True)
class MarketDataRequest:
    """Request parameters for fetching historical price data."""

    tickers: Iterable[str]
    start: date
    end: date
    interval: str = "1d"

    def normalised_tickers(self) -> List[str]:
        """Return the list of tickers normalised for Yahoo Finance.

        Yahoo Finance expects B3 tickers in the format ``TICKER.SA`` (e.g. ``PETR4.SA``).
        This helper guarantees that every ticker contains the ``.SA`` suffix, making the
        rest of the code resilient to user input such as ``PETR4``.
        """

        normalised: List[str] = []
        for ticker in self.tickers:
            cleaned = ticker.strip().upper()
            if not cleaned:
                continue
            if cleaned.endswith(".SA"):
                normalised.append(cleaned)
            else:
                normalised.append(f"{cleaned}.SA")
        if not normalised:
            msg = "At least one ticker must be provided"
            raise ValueError(msg)
        return normalised


@lru_cache(maxsize=32)
def download_market_data(
    tickers: tuple[str, ...], start: date, end: date, interval: str = "1d"
) -> pd.DataFrame:
    """Download adjusted close price data for the given tickers.

    Parameters
    ----------
    tickers:
        Tuple of ticker symbols formatted for Yahoo Finance.
    start, end:
        Boundaries for the historical data.
    interval:
        Sampling interval compatible with ``yfinance.download``.
    """

    data = yf.download(
        tickers=list(tickers),
        start=start,
        end=end,
        interval=interval,
        auto_adjust=True,
        progress=False,
    )

    if data.empty:
        msg = "No data returned for the selected parameters"
        raise ValueError(msg)

    if isinstance(data.columns, pd.MultiIndex):
        # ``yfinance`` returns a multi-index when more than one ticker is requested.
        data = data["Close"]
    else:
        data = data.rename("Close")

    data.index = pd.to_datetime(data.index)
    return data.sort_index()


def load_prices(request: MarketDataRequest) -> pd.DataFrame:
    """Public helper that downloads data based on a :class:`MarketDataRequest`."""

    tickers = tuple(request.normalised_tickers())
    return download_market_data(
        tickers=tickers,
        start=request.start,
        end=request.end,
        interval=request.interval,
    )
