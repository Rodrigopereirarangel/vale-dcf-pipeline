#!/usr/bin/env python3
"""
Exemplos práticos de uso do módulo de VaR do Bitcoin.
Este arquivo mostra diferentes formas de usar a calculadora de VaR.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def exemplo_1_basico():
    """Exemplo 1: Uso básico com dados simulados."""
    print("=" * 80)
    print("EXEMPLO 1: Uso Básico - Cálculo de VaR")
    print("=" * 80)

    # Simular retornos (1 ano de dados horários)
    np.random.seed(42)
    num_hours = 8760
    mean_return = 0.0001  # 0.01% por hora
    volatility = 0.015    # 1.5% volatilidade

    returns = np.random.normal(mean_return, volatility, num_hours)

    print(f"\n📊 Dados:")
    print(f"   Observações: {len(returns):,}")
    print(f"   Retorno médio: {returns.mean():.4%}")
    print(f"   Volatilidade: {returns.std():.4%}")

    # Simular VaR para 1 dia
    num_simulations = 10000
    horizon_hours = 24

    simulated_returns = []
    for _ in range(num_simulations):
        random_returns = np.random.normal(returns.mean(), returns.std(), horizon_hours)
        simulated_returns.append(random_returns.sum())

    simulated_returns = np.array(simulated_returns)

    var_95 = np.percentile(simulated_returns, 5)
    var_99 = np.percentile(simulated_returns, 1)

    print(f"\n💰 VaR para {horizon_hours} horas ({num_simulations:,} simulações):")
    print(f"   VaR 95%: {var_95:>8.2%}")
    print(f"   VaR 99%: {var_99:>8.2%}")

    # Converter para valores monetários
    investment = 10000
    print(f"\n💵 Com investimento de ${investment:,.2f}:")
    print(f"   Perda máxima (95%): ${abs(var_95 * investment):,.2f}")
    print(f"   Perda máxima (99%): ${abs(var_99 * investment):,.2f}")

    print("\n" + "=" * 80 + "\n")


def exemplo_2_multiplos_periodos():
    """Exemplo 2: Comparação entre múltiplos períodos."""
    print("=" * 80)
    print("EXEMPLO 2: VaR para Múltiplos Períodos")
    print("=" * 80)

    # Parâmetros
    np.random.seed(42)
    mean_return = 0.0001
    volatility = 0.015
    num_simulations = 10000

    periods = [
        ("6 horas", 6),
        ("12 horas", 12),
        ("1 dia", 24),
        ("2 dias", 48),
        ("3 dias", 72),
        ("1 semana", 168),
    ]

    print(f"\n{'Período':<15} {'Horas':<10} {'VaR 95%':<15} {'VaR 99%':<15}")
    print("-" * 80)

    for period_name, hours in periods:
        simulated_returns = []
        for _ in range(num_simulations):
            random_returns = np.random.normal(mean_return, volatility, hours)
            simulated_returns.append(random_returns.sum())

        simulated_returns = np.array(simulated_returns)
        var_95 = np.percentile(simulated_returns, 5)
        var_99 = np.percentile(simulated_returns, 1)

        print(f"{period_name:<15} {hours:<10} {var_95:<14.2%} {var_99:<14.2%}")

    print("-" * 80)
    print("\n💡 Observação: Quanto maior o período, maior o risco!")
    print("\n" + "=" * 80 + "\n")


def exemplo_3_diferentes_investimentos():
    """Exemplo 3: VaR para diferentes valores de investimento."""
    print("=" * 80)
    print("EXEMPLO 3: VaR Monetário para Diferentes Investimentos")
    print("=" * 80)

    # Calcular VaR uma vez
    np.random.seed(42)
    mean_return = 0.0001
    volatility = 0.015
    num_simulations = 10000
    horizon_hours = 24

    simulated_returns = []
    for _ in range(num_simulations):
        random_returns = np.random.normal(mean_return, volatility, horizon_hours)
        simulated_returns.append(random_returns.sum())

    simulated_returns = np.array(simulated_returns)
    var_95 = np.percentile(simulated_returns, 5)
    var_99 = np.percentile(simulated_returns, 1)

    print(f"\nVaR calculado para 1 dia (24 horas):")
    print(f"   VaR 95%: {var_95:.2%}")
    print(f"   VaR 99%: {var_99:.2%}")

    # Diferentes investimentos
    investments = [1000, 5000, 10000, 25000, 50000, 100000]

    print(f"\n{'Investimento':<20} {'Perda Máx 95%':<20} {'Perda Máx 99%':<20}")
    print("-" * 80)

    for investment in investments:
        loss_95 = abs(var_95 * investment)
        loss_99 = abs(var_99 * investment)

        print(
            f"${investment:>18,} "
            f"${loss_95:>18,.2f} "
            f"${loss_99:>18,.2f}"
        )

    print("-" * 80)
    print("\n" + "=" * 80 + "\n")


def exemplo_4_diferentes_volatilidades():
    """Exemplo 4: Impacto da volatilidade no VaR."""
    print("=" * 80)
    print("EXEMPLO 4: Impacto da Volatilidade no VaR")
    print("=" * 80)

    mean_return = 0.0001
    num_simulations = 10000
    horizon_hours = 24

    # Diferentes níveis de volatilidade
    volatilities = [
        ("Baixa (1%)", 0.01),
        ("Média (1.5%)", 0.015),
        ("Alta (2%)", 0.02),
        ("Muito Alta (3%)", 0.03),
        ("Extrema (5%)", 0.05),
    ]

    print(f"\n{'Volatilidade':<20} {'VaR 95%':<15} {'VaR 99%':<15}")
    print("-" * 80)

    for vol_name, volatility in volatilities:
        np.random.seed(42)
        simulated_returns = []

        for _ in range(num_simulations):
            random_returns = np.random.normal(mean_return, volatility, horizon_hours)
            simulated_returns.append(random_returns.sum())

        simulated_returns = np.array(simulated_returns)
        var_95 = np.percentile(simulated_returns, 5)
        var_99 = np.percentile(simulated_returns, 1)

        print(f"{vol_name:<20} {var_95:<14.2%} {var_99:<14.2%}")

    print("-" * 80)
    print("\n💡 Observação: Maior volatilidade = Maior risco!")
    print("   Bitcoin tipicamente tem volatilidade entre 2-5% (horária)")
    print("\n" + "=" * 80 + "\n")


def exemplo_5_interpretacao():
    """Exemplo 5: Como interpretar os resultados."""
    print("=" * 80)
    print("EXEMPLO 5: Como Interpretar VaR - Guia Prático")
    print("=" * 80)

    var_95 = -0.0523  # -5.23%
    var_99 = -0.0784  # -7.84%
    investment = 10000

    print(f"""
📊 CENÁRIO:
   • Investimento: ${investment:,.2f} em Bitcoin
   • Horizonte: 1 dia (24 horas)
   • VaR 95%: {var_95:.2%}
   • VaR 99%: {var_99:.2%}

📖 INTERPRETAÇÃO:

1. VaR 95% = {var_95:.2%}
   ✓ Em 95 de 100 dias, sua perda não excederá {abs(var_95):.2%}
   ✓ Perda máxima esperada: ${abs(var_95 * investment):,.2f}
   ✗ Ainda há 5% de chance de perder MAIS que isso

2. VaR 99% = {var_99:.2%}
   ✓ Em 99 de 100 dias, sua perda não excederá {abs(var_99):.2%}
   ✓ Perda máxima esperada: ${abs(var_99 * investment):,.2f}
   ✗ Ainda há 1% de chance de perder MAIS que isso

⚠️ IMPORTANTE:
   • VaR NÃO diz quanto você pode perder no pior cenário
   • VaR diz a perda máxima em X% dos cenários
   • Eventos extremos (tail risk) não são capturados
   • Use junto com outras métricas de risco

💡 DECISÃO:
   Se você NÃO pode perder mais que ${abs(var_99 * investment):,.2f}:
   → Considere reduzir o investimento
   → Ou escolher horizonte menor
   → Ou diversificar o portfólio

   Se você pode aceitar perda de até ${abs(var_99 * investment):,.2f}:
   → O risco está dentro da sua tolerância
   → Mas lembre-se: 1% de chance de perder mais!
""")

    print("=" * 80 + "\n")


def main():
    """Executa todos os exemplos."""
    print("\n")
    print("█" * 80)
    print("  EXEMPLOS PRÁTICOS - CÁLCULO DE VAR DO BITCOIN")
    print("█" * 80)
    print("\n")

    exemplo_1_basico()
    input("Pressione ENTER para continuar...")

    exemplo_2_multiplos_periodos()
    input("Pressione ENTER para continuar...")

    exemplo_3_diferentes_investimentos()
    input("Pressione ENTER para continuar...")

    exemplo_4_diferentes_volatilidades()
    input("Pressione ENTER para continuar...")

    exemplo_5_interpretacao()

    print("█" * 80)
    print("  EXEMPLOS CONCLUÍDOS!")
    print("█" * 80)
    print("\n💡 Próximos passos:")
    print("   1. Execute: python demo_btc_var.py")
    print("   2. Leia: BTC_VAR_README.md")
    print("   3. Com dados reais: python btc_var_cli.py --standard")
    print("   4. Interface visual: streamlit run btc_var_analysis.py")
    print("\n")


if __name__ == "__main__":
    main()
