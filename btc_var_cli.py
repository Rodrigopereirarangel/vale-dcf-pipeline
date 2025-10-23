#!/usr/bin/env python3
"""Script de linha de comando para calcular VaR do Bitcoin."""

import argparse
from src.btc_var_calculator import (
    fetch_btc_hourly_data,
    calculate_hourly_returns,
    monte_carlo_var,
    calculate_var_for_periods,
    get_var_statistics,
    calculate_var_monetary,
)


def main():
    """Função principal do CLI."""
    parser = argparse.ArgumentParser(
        description="Calcula VaR (Value at Risk) do Bitcoin usando Monte Carlo"
    )

    parser.add_argument(
        "--years",
        type=int,
        default=5,
        help="Número de anos de histórico (padrão: 5)"
    )

    parser.add_argument(
        "--simulations",
        type=int,
        default=10000,
        help="Número de simulações Monte Carlo (padrão: 10000)"
    )

    parser.add_argument(
        "--hours",
        type=int,
        help="Horizonte temporal em horas para cálculo customizado"
    )

    parser.add_argument(
        "--days",
        type=int,
        help="Horizonte temporal em dias para cálculo customizado (alternativo a --hours)"
    )

    parser.add_argument(
        "--investment",
        type=float,
        help="Valor do investimento para cálculo monetário (USD)"
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="Mostrar estatísticas descritivas dos retornos"
    )

    parser.add_argument(
        "--standard",
        action="store_true",
        help="Calcular VaR para períodos padrão (1 dia, 5 dias, 1 mês)"
    )

    args = parser.parse_args()

    # Validação
    if args.days and args.hours:
        print("Erro: Use --hours OU --days, não ambos")
        return

    # Calcular horizonte em horas
    if args.days:
        horizon_hours = args.days * 24
    elif args.hours:
        horizon_hours = args.hours
    else:
        horizon_hours = None

    print("=" * 80)
    print("ANÁLISE DE VAR - BITCOIN/USD")
    print("=" * 80)

    # Carregar dados
    print(f"\n[1/4] Carregando dados históricos ({args.years} anos)...")
    try:
        btc_prices = fetch_btc_hourly_data(years=args.years)
        print(f"✓ {len(btc_prices):,} observações horárias carregadas")
    except Exception as e:
        print(f"✗ Erro ao carregar dados: {e}")
        return

    # Calcular retornos
    print("\n[2/4] Calculando retornos...")
    returns = calculate_hourly_returns(btc_prices)
    print(f"✓ {len(returns):,} retornos calculados")

    # Estatísticas (se solicitado)
    if args.stats:
        print("\n[3/4] Estatísticas Descritivas dos Retornos:")
        print("-" * 80)
        stats = get_var_statistics(returns)
        for key, value in stats.items():
            print(f"  {key:.<30} {value}")
        print("-" * 80)
    else:
        print("\n[3/4] Pulando estatísticas descritivas (use --stats para ver)")

    # Calcular VaR
    print("\n[4/4] Calculando VaR...")

    if args.standard or horizon_hours is None:
        # Períodos padrão
        print("\nVaR para Períodos Padrão:")
        print("-" * 80)

        var_results = calculate_var_for_periods(
            returns,
            num_simulations=args.simulations
        )

        print(f"{'Período':<15} {'Horas':<10} {'VaR 95%':<15} {'VaR 99%':<15}")
        print("-" * 80)

        for _, row in var_results.iterrows():
            print(
                f"{row['Período']:<15} "
                f"{row['Horas']:<10} "
                f"{row['VaR 95%']:<15} "
                f"{row['VaR 99%']:<15}"
            )

        # Análise monetária
        if args.investment:
            print("\n" + "=" * 80)
            print(f"ANÁLISE MONETÁRIA (Investimento: ${args.investment:,.2f})")
            print("=" * 80)
            print(f"{'Período':<15} {'Perda Máx 95%':<20} {'Perda Máx 99%':<20}")
            print("-" * 80)

            for _, row in var_results.iterrows():
                var_95_money = calculate_var_monetary(
                    row['VaR 95% (valor)'],
                    args.investment
                )
                var_99_money = calculate_var_monetary(
                    row['VaR 99% (valor)'],
                    args.investment
                )

                print(
                    f"{row['Período']:<15} "
                    f"${var_95_money:>18,.2f} "
                    f"${var_99_money:>18,.2f}"
                )

    if horizon_hours:
        # Cálculo customizado
        print(f"\nVaR Customizado (Horizonte: {horizon_hours} horas):")
        print("-" * 80)

        var_result = monte_carlo_var(
            returns,
            horizon_hours=horizon_hours,
            num_simulations=args.simulations
        )

        print(f"  VaR 95% .................... {var_result.var_95:.4%}")
        print(f"  VaR 99% .................... {var_result.var_99:.4%}")
        print(f"  Retorno Médio Horário ...... {var_result.mean_return:.6%}")
        print(f"  Volatilidade Horária ....... {var_result.volatility:.6%}")
        print(f"  Simulações ................. {var_result.num_simulations:,}")

        if args.investment:
            var_95_money = calculate_var_monetary(var_result.var_95, args.investment)
            var_99_money = calculate_var_monetary(var_result.var_99, args.investment)

            print("\n  Análise Monetária:")
            print(f"    Investimento ............. ${args.investment:,.2f}")
            print(f"    Perda Máxima (VaR 95%) ... ${var_95_money:,.2f}")
            print(f"    Perda Máxima (VaR 99%) ... ${var_99_money:,.2f}")

    print("\n" + "=" * 80)
    print("ANÁLISE CONCLUÍDA")
    print("=" * 80)

    print("\n💡 Dica: Use 'streamlit run btc_var_analysis.py' para interface gráfica")


if __name__ == "__main__":
    main()
