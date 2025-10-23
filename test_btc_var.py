"""Script de teste rápido para validar o módulo de VaR do Bitcoin."""

import sys
from src.btc_var_calculator import (
    fetch_btc_hourly_data,
    calculate_hourly_returns,
    monte_carlo_var,
    calculate_var_for_periods,
    get_var_statistics,
)

def test_basic_functionality():
    """Testa funcionalidade básica do módulo."""
    print("=" * 80)
    print("TESTE DO MÓDULO BTC VAR CALCULATOR")
    print("=" * 80)

    try:
        # Teste 1: Carregar dados (apenas 1 ano para teste rápido)
        print("\n[Teste 1] Carregando dados do Bitcoin (1 ano)...")
        btc_prices = fetch_btc_hourly_data(years=1)
        print(f"✓ Sucesso! {len(btc_prices):,} observações carregadas")
        print(f"  Período: {btc_prices.index[0]} até {btc_prices.index[-1]}")
        print(f"  Preço inicial: ${btc_prices['Close'].iloc[0]:,.2f}")
        print(f"  Preço final: ${btc_prices['Close'].iloc[-1]:,.2f}")

    except Exception as e:
        print(f"✗ Erro ao carregar dados: {e}")
        return False

    try:
        # Teste 2: Calcular retornos
        print("\n[Teste 2] Calculando retornos...")
        returns = calculate_hourly_returns(btc_prices)
        print(f"✓ Sucesso! {len(returns):,} retornos calculados")
        print(f"  Retorno médio: {returns.mean():.6%}")
        print(f"  Desvio padrão: {returns.std():.6%}")

    except Exception as e:
        print(f"✗ Erro ao calcular retornos: {e}")
        return False

    try:
        # Teste 3: Estatísticas
        print("\n[Teste 3] Estatísticas descritivas...")
        stats = get_var_statistics(returns)
        print("✓ Sucesso!")
        for key, value in list(stats.items())[:4]:  # Mostrar apenas 4 primeiras
            print(f"  {key}: {value}")

    except Exception as e:
        print(f"✗ Erro ao calcular estatísticas: {e}")
        return False

    try:
        # Teste 4: VaR para 1 dia
        print("\n[Teste 4] Calculando VaR para 1 dia (1000 simulações)...")
        var_1d = monte_carlo_var(returns, horizon_hours=24, num_simulations=1000)
        print("✓ Sucesso!")
        print(f"  VaR 95%: {var_1d.var_95:.2%}")
        print(f"  VaR 99%: {var_1d.var_99:.2%}")
        print(f"  Volatilidade: {var_1d.volatility:.4%}")

    except Exception as e:
        print(f"✗ Erro ao calcular VaR: {e}")
        return False

    try:
        # Teste 5: VaR para múltiplos períodos
        print("\n[Teste 5] Calculando VaR para períodos padrão (1000 simulações)...")
        var_periods = calculate_var_for_periods(returns, num_simulations=1000)
        print("✓ Sucesso!")
        print(var_periods[["Período", "VaR 95%", "VaR 99%"]].to_string(index=False))

    except Exception as e:
        print(f"✗ Erro ao calcular VaR para períodos: {e}")
        return False

    print("\n" + "=" * 80)
    print("TODOS OS TESTES PASSARAM! ✓")
    print("=" * 80)

    print("\n💡 Próximos passos:")
    print("  1. Execute: python btc_var_cli.py --standard")
    print("  2. Execute: streamlit run btc_var_analysis.py")

    return True


if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)
