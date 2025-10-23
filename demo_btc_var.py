"""
Script de demonstração do cálculo de VaR do Bitcoin usando dados simulados.
Use este script para testar a funcionalidade sem precisar baixar dados reais.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def generate_synthetic_btc_returns(
    num_hours: int = 8760,  # 1 ano
    mean_hourly_return: float = 0.0001,  # ~0.01% por hora
    volatility: float = 0.015,  # ~1.5% de volatilidade horária
    seed: int = 42
) -> pd.Series:
    """
    Gera retornos sintéticos que simulam o comportamento do Bitcoin.

    Parameters
    ----------
    num_hours : int
        Número de horas de dados
    mean_hourly_return : float
        Retorno médio esperado por hora
    volatility : float
        Volatilidade (desvio padrão) dos retornos
    seed : int
        Seed para reprodutibilidade

    Returns
    -------
    pd.Series
        Série temporal de retornos sintéticos
    """
    np.random.seed(seed)

    # Gerar retornos com distribuição normal
    returns = np.random.normal(mean_hourly_return, volatility, num_hours)

    # Criar índice de datas
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=num_hours)
    dates = pd.date_range(start=start_date, periods=num_hours, freq='H')

    return pd.Series(returns, index=dates, name='Returns')


def monte_carlo_var_demo(
    returns: pd.Series,
    horizon_hours: int,
    confidence_levels: tuple = (0.95, 0.99),
    num_simulations: int = 10000,
    random_seed: int = 42,
) -> dict:
    """
    Versão simplificada do cálculo de VaR usando Monte Carlo.

    Parameters
    ----------
    returns : pd.Series
        Série de retornos históricos
    horizon_hours : int
        Horizonte temporal em horas
    confidence_levels : tuple
        Níveis de confiança para VaR
    num_simulations : int
        Número de simulações
    random_seed : int
        Seed para reprodutibilidade

    Returns
    -------
    dict
        Resultados do VaR
    """
    # Parâmetros históricos
    mean_return = returns.mean()
    std_return = returns.std()

    np.random.seed(random_seed)

    # Simulações
    simulated_returns = np.zeros(num_simulations)

    for i in range(num_simulations):
        # Gerar retornos aleatórios para o horizonte
        random_returns = np.random.normal(mean_return, std_return, horizon_hours)
        simulated_returns[i] = random_returns.sum()

    # Calcular VaR
    var_95 = np.percentile(simulated_returns, (1 - confidence_levels[0]) * 100)
    var_99 = np.percentile(simulated_returns, (1 - confidence_levels[1]) * 100)

    return {
        'var_95': var_95,
        'var_99': var_99,
        'mean_return': mean_return,
        'volatility': std_return,
        'simulated_returns': simulated_returns,
        'horizon_hours': horizon_hours,
        'num_simulations': num_simulations,
    }


def main():
    """Demonstração do cálculo de VaR."""
    print("=" * 80)
    print("DEMONSTRAÇÃO - CÁLCULO DE VAR DO BITCOIN (DADOS SIMULADOS)")
    print("=" * 80)

    # Gerar dados sintéticos
    print("\n[1/4] Gerando dados sintéticos (1 ano de dados horários)...")
    returns = generate_synthetic_btc_returns(num_hours=8760)
    print(f"✓ {len(returns):,} retornos gerados")
    print(f"  Retorno médio: {returns.mean():.4%}")
    print(f"  Volatilidade: {returns.std():.4%}")
    print(f"  Mínimo: {returns.min():.4%}")
    print(f"  Máximo: {returns.max():.4%}")

    # Estatísticas
    print("\n[2/4] Estatísticas descritivas:")
    print("-" * 80)
    print(f"  {'Métrica':<30} {'Valor':>15}")
    print("-" * 80)
    print(f"  {'Retorno Médio (horário)':<30} {returns.mean():>14.4%}")
    print(f"  {'Mediana':<30} {returns.median():>14.4%}")
    print(f"  {'Desvio Padrão':<30} {returns.std():>14.4%}")
    print(f"  {'Assimetria (Skewness)':<30} {returns.skew():>14.4f}")
    print(f"  {'Curtose (Kurtosis)':<30} {returns.kurtosis():>14.4f}")
    print("-" * 80)

    # VaR para diferentes períodos
    print("\n[3/4] Calculando VaR para diferentes períodos...")

    periods = {
        "1 dia (24h)": 24,
        "5 dias (120h)": 120,
        "1 mês (720h)": 720,
    }

    print("-" * 80)
    print(f"  {'Período':<20} {'VaR 95%':>15} {'VaR 99%':>15}")
    print("-" * 80)

    results = {}
    for period_name, hours in periods.items():
        var_result = monte_carlo_var_demo(
            returns,
            horizon_hours=hours,
            num_simulations=10000
        )
        results[period_name] = var_result

        print(
            f"  {period_name:<20} "
            f"{var_result['var_95']:>14.2%} "
            f"{var_result['var_99']:>14.2%}"
        )

    print("-" * 80)

    # Análise monetária
    print("\n[4/4] Análise Monetária (Investimento: $10,000)")
    print("-" * 80)
    print(f"  {'Período':<20} {'Perda Máx 95%':>18} {'Perda Máx 99%':>18}")
    print("-" * 80)

    investment = 10000

    for period_name, var_result in results.items():
        loss_95 = abs(var_result['var_95'] * investment)
        loss_99 = abs(var_result['var_99'] * investment)

        print(
            f"  {period_name:<20} "
            f"${loss_95:>17,.2f} "
            f"${loss_99:>17,.2f}"
        )

    print("-" * 80)

    # Interpretação
    print("\n" + "=" * 80)
    print("INTERPRETAÇÃO DOS RESULTADOS")
    print("=" * 80)

    # Usar resultado de 1 dia como exemplo
    var_1d = results["1 dia (24h)"]

    print(f"""
Com base nos dados simulados:

1. VaR para 1 dia:
   - VaR 95%: {var_1d['var_95']:.2%}
     → Em 95% dos cenários, a perda não excederá {abs(var_1d['var_95']):.2%}
     → Perda máxima esperada: ${abs(var_1d['var_95'] * investment):,.2f}

   - VaR 99%: {var_1d['var_99']:.2%}
     → Em 99% dos cenários, a perda não excederá {abs(var_1d['var_99']):.2%}
     → Perda máxima esperada: ${abs(var_1d['var_99'] * investment):,.2f}

2. Observações:
   - Quanto maior o período, maior o risco potencial
   - VaR 99% é sempre mais conservador que VaR 95%
   - Estes valores são baseados em {var_1d['num_simulations']:,} simulações Monte Carlo
   - Bitcoin real tem volatilidade muito maior que ações tradicionais

3. Próximos passos:
   - Use dados reais com: python btc_var_cli.py --standard
   - Interface visual: streamlit run btc_var_analysis.py
   - Leia BTC_VAR_README.md para documentação completa
""")

    print("=" * 80)
    print("DEMONSTRAÇÃO CONCLUÍDA")
    print("=" * 80)

    # Criar gráfico ASCII simples da distribuição
    print("\nDistribuição dos retornos simulados (1 dia):")
    print_ascii_histogram(var_1d['simulated_returns'], var_1d['var_95'], var_1d['var_99'])


def print_ascii_histogram(data: np.ndarray, var_95: float, var_99: float, bins: int = 50):
    """Imprime um histograma ASCII simples."""
    hist, bin_edges = np.histogram(data, bins=bins)
    max_count = hist.max()

    # Normalizar para 60 caracteres de largura
    width = 60

    print("\n" + "-" * 80)

    for i in range(len(hist)):
        bar_length = int((hist[i] / max_count) * width)
        bar = "█" * bar_length

        # Marcar onde estão os VaRs
        bin_center = (bin_edges[i] + bin_edges[i + 1]) / 2

        marker = ""
        if abs(bin_center - var_99) < 0.01:
            marker = " ← VaR 99%"
        elif abs(bin_center - var_95) < 0.01:
            marker = " ← VaR 95%"

        print(f"{bin_center:>7.2%} | {bar}{marker}")

    print("-" * 80)


if __name__ == "__main__":
    main()
