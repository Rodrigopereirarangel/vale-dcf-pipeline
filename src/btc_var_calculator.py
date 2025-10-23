"""Módulo para cálculo de VaR (Value at Risk) do Bitcoin usando simulação Monte Carlo."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Tuple

import numpy as np
import pandas as pd
import yfinance as yf


@dataclass
class VaRResult:
    """Resultado do cálculo de VaR."""

    var_95: float
    var_99: float
    horizon_hours: int
    num_simulations: int
    mean_return: float
    volatility: float
    simulated_returns: np.ndarray

    def to_dict(self) -> dict:
        """Converte o resultado para dicionário."""
        return {
            "VaR 95%": f"{self.var_95:.2%}",
            "VaR 99%": f"{self.var_99:.2%}",
            "Horizonte (horas)": self.horizon_hours,
            "Simulações": self.num_simulations,
            "Retorno Médio": f"{self.mean_return:.4%}",
            "Volatilidade": f"{self.volatility:.4%}",
        }


def fetch_btc_hourly_data(years: int = 5) -> pd.DataFrame:
    """
    Busca dados horários do Bitcoin/USD.

    Parameters
    ----------
    years : int
        Número de anos de histórico a buscar.

    Returns
    -------
    pd.DataFrame
        DataFrame com preços horários do BTC/USD.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years * 365)

    # Baixar dados horários (1h interval)
    # Nota: yfinance limita dados horários a ~730 dias
    # Então vamos baixar em chunks e combinar

    all_data = []
    current_end = end_date

    # yfinance permite ~730 dias de dados horários por vez
    chunk_days = 729

    while current_end > start_date:
        current_start = max(current_end - timedelta(days=chunk_days), start_date)

        print(f"Baixando dados de {current_start.date()} até {current_end.date()}...")

        data = yf.download(
            tickers="BTC-USD",
            start=current_start,
            end=current_end,
            interval="1h",
            auto_adjust=True,
            progress=False,
        )

        if not data.empty:
            all_data.append(data)

        current_end = current_start - timedelta(hours=1)

        if current_start <= start_date:
            break

    if not all_data:
        raise ValueError("Não foi possível obter dados do Bitcoin")

    # Combinar todos os chunks
    combined_data = pd.concat(all_data)
    combined_data = combined_data.sort_index()

    # Remover duplicatas se houver
    combined_data = combined_data[~combined_data.index.duplicated(keep='first')]

    return combined_data


def calculate_hourly_returns(prices: pd.DataFrame) -> pd.Series:
    """
    Calcula retornos logarítmicos horários.

    Parameters
    ----------
    prices : pd.DataFrame
        DataFrame com coluna 'Close' contendo preços.

    Returns
    -------
    pd.Series
        Série com retornos logarítmicos.
    """
    if 'Close' in prices.columns:
        close_prices = prices['Close']
    else:
        close_prices = prices

    returns = np.log(close_prices / close_prices.shift(1))
    return returns.dropna()


def monte_carlo_var(
    returns: pd.Series,
    horizon_hours: int,
    confidence_levels: Tuple[float, float] = (0.95, 0.99),
    num_simulations: int = 10000,
    random_seed: int = 42,
) -> VaRResult:
    """
    Calcula VaR usando simulação Monte Carlo.

    Parameters
    ----------
    returns : pd.Series
        Série de retornos históricos (logarítmicos).
    horizon_hours : int
        Horizonte temporal em horas.
    confidence_levels : Tuple[float, float]
        Níveis de confiança para VaR (padrão: 95% e 99%).
    num_simulations : int
        Número de simulações Monte Carlo.
    random_seed : int
        Semente para reprodutibilidade.

    Returns
    -------
    VaRResult
        Objeto com resultados do VaR.
    """
    # Parâmetros da distribuição histórica
    mean_return = returns.mean()
    std_return = returns.std()

    # Configurar seed para reprodutibilidade
    np.random.seed(random_seed)

    # Simular retornos futuros
    # Para cada simulação, geramos 'horizon_hours' retornos aleatórios
    # e somamos para obter o retorno total do período
    simulated_returns = np.zeros(num_simulations)

    for i in range(num_simulations):
        # Gerar 'horizon_hours' retornos horários aleatórios
        random_returns = np.random.normal(mean_return, std_return, horizon_hours)
        # Retorno acumulado do período
        simulated_returns[i] = random_returns.sum()

    # Calcular VaR nos níveis de confiança especificados
    # VaR é o percentil negativo (perda)
    var_95 = np.percentile(simulated_returns, (1 - confidence_levels[0]) * 100)
    var_99 = np.percentile(simulated_returns, (1 - confidence_levels[1]) * 100)

    return VaRResult(
        var_95=var_95,
        var_99=var_99,
        horizon_hours=horizon_hours,
        num_simulations=num_simulations,
        mean_return=mean_return,
        volatility=std_return,
        simulated_returns=simulated_returns,
    )


def calculate_var_for_periods(
    returns: pd.Series,
    periods: dict[str, int] = None,
    num_simulations: int = 10000,
) -> pd.DataFrame:
    """
    Calcula VaR para múltiplos períodos.

    Parameters
    ----------
    returns : pd.Series
        Série de retornos históricos.
    periods : dict[str, int]
        Dicionário com nome do período e horas correspondentes.
    num_simulations : int
        Número de simulações Monte Carlo.

    Returns
    -------
    pd.DataFrame
        DataFrame com resultados de VaR para cada período.
    """
    if periods is None:
        periods = {
            "1 dia": 24,
            "5 dias": 24 * 5,
            "1 mês": 24 * 30,
        }

    results = []

    for period_name, hours in periods.items():
        var_result = monte_carlo_var(returns, hours, num_simulations=num_simulations)

        results.append({
            "Período": period_name,
            "Horas": hours,
            "VaR 95%": f"{var_result.var_95:.2%}",
            "VaR 99%": f"{var_result.var_99:.2%}",
            "VaR 95% (valor)": var_result.var_95,
            "VaR 99% (valor)": var_result.var_99,
        })

    return pd.DataFrame(results)


def calculate_var_monetary(
    var_percentage: float,
    investment_value: float,
) -> float:
    """
    Converte VaR percentual para valor monetário.

    Parameters
    ----------
    var_percentage : float
        VaR em formato decimal (ex: -0.05 para -5%).
    investment_value : float
        Valor do investimento.

    Returns
    -------
    float
        Perda máxima esperada em valor monetário.
    """
    return abs(var_percentage * investment_value)


def get_var_statistics(returns: pd.Series) -> dict:
    """
    Calcula estatísticas descritivas dos retornos.

    Parameters
    ----------
    returns : pd.Series
        Série de retornos.

    Returns
    -------
    dict
        Dicionário com estatísticas.
    """
    return {
        "Retorno Médio (horário)": f"{returns.mean():.4%}",
        "Retorno Mediano": f"{returns.median():.4%}",
        "Desvio Padrão": f"{returns.std():.4%}",
        "Assimetria (Skewness)": f"{returns.skew():.4f}",
        "Curtose (Kurtosis)": f"{returns.kurtosis():.4f}",
        "Mínimo": f"{returns.min():.4%}",
        "Máximo": f"{returns.max():.4%}",
        "Observações": len(returns),
    }
