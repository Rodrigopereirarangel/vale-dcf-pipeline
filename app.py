"""Streamlit dashboard for comparing B3 assets."""

from __future__ import annotations

from datetime import date, timedelta
from typing import List

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics import (
    compute_correlation,
    compute_daily_returns,
    compute_normalised_prices,
    summarise_performance,
)
from src.data_loader import MarketDataRequest, load_prices

st.set_page_config(page_title="Comparador de Ativos B3", layout="wide")

st.title("📈 Comparador de Ativos da B3")

st.write(
    """
    Compare ações e outros ativos listados na B3 utilizando dados históricos do Yahoo
    Finance. Informe os tickers no formato `TICKER` ou `TICKER.SA` (ex.: `PETR4` ou
    `VALE3.SA`).
    """
)

with st.sidebar:
    st.header("Configurações")
    default_tickers = "PETR4, VALE3, ITUB4"
    tickers_input = st.text_input(
        "Tickers", value=default_tickers, help="Separe vários tickers por vírgula."
    )

    col_start, col_end = st.columns(2)
    with col_start:
        start_date = st.date_input(
            "Data inicial",
            value=date.today() - timedelta(days=365),
            max_value=date.today(),
        )
    with col_end:
        end_date = st.date_input(
            "Data final", value=date.today(), min_value=start_date, max_value=date.today()
        )

    interval = st.selectbox(
        "Intervalo",
        options=["1d", "1wk", "1mo"],
        index=0,
        help="Periodicidade das observações retornadas pelo Yahoo Finance.",
    )

    st.caption(
        "Os dados são obtidos através da API gratuita do Yahoo Finance via biblioteca"
        " `yfinance`."
    )

@st.cache_data(show_spinner=False)
def _load_data(tickers: List[str], start: date, end: date, interval: str) -> pd.DataFrame:
    request = MarketDataRequest(tickers=tickers, start=start, end=end, interval=interval)
    return load_prices(request)


def parse_tickers(raw: str) -> List[str]:
    return [ticker.strip() for ticker in raw.split(",") if ticker.strip()]


def main() -> None:
    tickers = parse_tickers(tickers_input)

    if not tickers:
        st.info("Informe pelo menos um ticker para visualizar os dados.")
        return

    try:
        prices = _load_data(tickers, start_date, end_date + timedelta(days=1), interval)
    except ValueError as exc:  # includes missing data and validation errors
        st.error(str(exc))
        return

    st.subheader("Evolução Normalizada")
    normalised = compute_normalised_prices(prices)
    fig_prices = px.line(normalised, labels={"value": "Preço normalizado", "index": "Data"})
    st.plotly_chart(fig_prices, use_container_width=True)

    st.subheader("Retornos Diários (%)")
    returns = compute_daily_returns(prices)
    fig_returns = px.line(returns, labels={"value": "Retorno (%)", "index": "Data"})
    st.plotly_chart(fig_returns, use_container_width=True)

    st.subheader("Estatísticas")
    summary = summarise_performance(prices)
    st.dataframe(summary.style.format({"Total Return (%)": "{:.2f}", "Volatility (%)": "{:.2f}", "Sharpe (daily)": "{:.2f}"}))

    st.subheader("Correlação dos Retornos")
    corr = compute_correlation(prices)
    fig_corr = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="RdBu",
        zmin=-1,
        zmax=1,
        labels=dict(color="Correlação"),
    )
    st.plotly_chart(fig_corr, use_container_width=True)


if __name__ == "__main__":
    main()
