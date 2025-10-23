# Análise de VaR (Value at Risk) - Bitcoin/USD

Este projeto implementa cálculo de **VaR (Value at Risk)** para Bitcoin usando **simulação Monte Carlo** com dados históricos de preços horários.

## O que é VaR?

**Value at Risk (VaR)** é uma métrica de risco que estima a **perda máxima esperada** em um investimento durante um determinado período de tempo com um dado nível de confiança.

Por exemplo:
- **VaR 95% de -5%** em 1 dia significa: *"Em 95% dos cenários, a perda não excederá 5% em 1 dia"*
- **VaR 99% de -8%** em 1 semana significa: *"Em 99% dos cenários, a perda não excederá 8% em 1 semana"*

## Funcionalidades

- Coleta dados horários do BTC/USD dos últimos ~5 anos
- Calcula retornos logarítmicos horários
- Implementa simulação **Monte Carlo** para projetar retornos futuros
- Calcula **VaR 95%** e **VaR 99%** para:
  - Períodos padrão: 1 dia, 5 dias, 1 mês
  - Períodos customizados: qualquer quantidade de horas ou dias
- Análise monetária: converte VaR percentual em perda máxima em dólares
- Interface gráfica interativa com **Streamlit**
- CLI (linha de comando) para uso em scripts

## Instalação

```bash
# Clonar o repositório
git clone <seu-repositorio>
cd Main

# Instalar dependências
pip install -r requirements.txt
```

## Uso

### 1. Interface Gráfica (Streamlit) - RECOMENDADO

A forma mais fácil e visual de usar:

```bash
streamlit run btc_var_analysis.py
```

Isso abrirá um dashboard interativo no navegador com:
- 📊 VaR para períodos padrão (1 dia, 5 dias, 1 mês)
- 🎯 Calculadora de VaR customizado (escolha horas ou dias)
- 📈 Análise de distribuição de retornos históricos
- 💰 Análise monetária (quanto você pode perder em $)
- 📉 Visualizações de dados históricos e volatilidade

### 2. Linha de Comando (CLI)

Para uso em scripts ou terminal:

```bash
# VaR para períodos padrão
python btc_var_cli.py --standard

# VaR customizado para 48 horas
python btc_var_cli.py --hours 48

# VaR customizado para 7 dias
python btc_var_cli.py --days 7

# Com análise monetária (investimento de $10,000)
python btc_var_cli.py --days 30 --investment 10000

# Com estatísticas descritivas
python btc_var_cli.py --standard --stats

# Personalizar número de simulações e anos de histórico
python btc_var_cli.py --hours 72 --simulations 50000 --years 3
```

#### Opções do CLI:

```
--years N           Número de anos de histórico (padrão: 5)
--simulations N     Número de simulações Monte Carlo (padrão: 10000)
--hours N           Horizonte em horas
--days N            Horizonte em dias (alternativo a --hours)
--investment X      Valor do investimento em USD
--stats             Mostrar estatísticas descritivas
--standard          Calcular para períodos padrão
```

### 3. Uso Programático

Você pode importar e usar as funções em seu próprio código:

```python
from src.btc_var_calculator import (
    fetch_btc_hourly_data,
    calculate_hourly_returns,
    monte_carlo_var,
)

# Carregar dados
btc_prices = fetch_btc_hourly_data(years=5)

# Calcular retornos
returns = calculate_hourly_returns(btc_prices)

# Calcular VaR para 24 horas (1 dia)
var_result = monte_carlo_var(
    returns,
    horizon_hours=24,
    num_simulations=10000
)

print(f"VaR 95%: {var_result.var_95:.2%}")
print(f"VaR 99%: {var_result.var_99:.2%}")
```

## Estrutura do Projeto

```
Main/
├── src/
│   ├── btc_var_calculator.py    # Módulo principal com funções de VaR
│   ├── analytics.py              # Análises para ativos B3
│   └── data_loader.py            # Carregamento de dados B3
├── btc_var_analysis.py           # Dashboard Streamlit para Bitcoin VaR
├── btc_var_cli.py                # Script CLI para Bitcoin VaR
├── app.py                        # Dashboard para ativos B3
├── requirements.txt              # Dependências
└── BTC_VAR_README.md            # Esta documentação
```

## Metodologia

### 1. Coleta de Dados
- Fonte: Yahoo Finance via biblioteca `yfinance`
- Ticker: BTC-USD
- Intervalo: Horário (1h)
- Período: Até 5 anos de histórico

### 2. Cálculo de Retornos
- Retornos logarítmicos: `ln(Pt / Pt-1)`
- Vantagem: propriedades aditivas para múltiplos períodos

### 3. Simulação Monte Carlo
Para cada simulação:
1. Calcula média (μ) e desvio padrão (σ) dos retornos históricos
2. Gera N retornos aleatórios seguindo distribuição normal: `N(μ, σ)`
3. Soma os retornos para obter retorno total do período
4. Repete 10,000+ vezes

### 4. Cálculo do VaR
- **VaR 95%**: Percentil 5% das simulações (5% piores cenários)
- **VaR 99%**: Percentil 1% das simulações (1% piores cenários)

## Interpretação dos Resultados

### Exemplo Prático

```
VaR 95% = -5.2% para 1 dia
VaR 99% = -7.8% para 1 dia
```

**Significado:**
- Em **95%** dos cenários, você não perderá mais que **5.2%** em 1 dia
- Em **99%** dos cenários, você não perderá mais que **7.8%** em 1 dia
- Ainda há **1%** de chance de perder **mais que 7.8%**

### Conversão Monetária

Se você investiu **$10,000**:
- VaR 95%: Perda máxima de $520 (em 95% dos casos)
- VaR 99%: Perda máxima de $780 (em 99% dos casos)

## Limitações e Considerações

⚠️ **Importante entender:**

1. **VaR não captura "tail risk"**: Perdas extremas além dos percentis calculados não são capturadas
2. **Assume normalidade**: Retornos de cripto têm "fat tails" (caudas pesadas)
3. **Baseado em dados históricos**: Performance passada não garante resultados futuros
4. **Não captura eventos extremos**: Crashes, regulamentações, hacks, etc.
5. **Volatilidade varia**: Bitcoin tem períodos de alta e baixa volatilidade

### Recomendações

- Use em conjunto com outras métricas (CVaR, Expected Shortfall)
- Monitore o Q-Q Plot para avaliar normalidade
- Considere stress testing e análise de cenários
- Revise periodicamente com dados atualizados
- Ajuste o número de simulações para maior precisão

## Exemplo de Saída

### CLI:
```
================================================================================
ANÁLISE DE VAR - BITCOIN/USD
================================================================================

[1/4] Carregando dados históricos (5 anos)...
✓ 43,824 observações horárias carregadas

[2/4] Calculando retornos...
✓ 43,823 retornos calculados

[3/4] Estatísticas Descritivas dos Retornos:
--------------------------------------------------------------------------------
  Retorno Médio (horário)...... 0.0123%
  Desvio Padrão................ 1.2456%
  Assimetria (Skewness)........ 0.2345
  Curtose (Kurtosis)........... 5.6789
--------------------------------------------------------------------------------

[4/4] Calculando VaR...

VaR para Períodos Padrão:
--------------------------------------------------------------------------------
Período         Horas      VaR 95%         VaR 99%
--------------------------------------------------------------------------------
1 dia           24         -5.23%          -7.84%
5 dias          120        -11.67%         -17.52%
1 mês           720        -28.45%         -42.68%

================================================================================
ANÁLISE CONCLUÍDA
================================================================================
```

## Recursos Adicionais

### Referências
- [Investopedia - Value at Risk (VaR)](https://www.investopedia.com/terms/v/var.asp)
- [Monte Carlo Simulation](https://en.wikipedia.org/wiki/Monte_Carlo_method)
- [Risk Management in Trading](https://www.investopedia.com/trading/risk-management/)

### Extensões Futuras
- [ ] Implementar CVaR (Conditional VaR) / Expected Shortfall
- [ ] Adicionar backtesting do VaR
- [ ] Modelos GARCH para volatilidade
- [ ] Análise multi-ativo (portfólio)
- [ ] Exportar relatórios em PDF

## Suporte

Para questões ou problemas:
1. Verifique se todas as dependências estão instaladas
2. Certifique-se de ter conexão com internet (para baixar dados)
3. Tente reduzir o número de anos se houver erro de dados

## Licença

Este projeto é fornecido "como está" para fins educacionais e de pesquisa.

---

**Desenvolvido com**: Python, Streamlit, Pandas, NumPy, Plotly, yfinance

**Última atualização**: 2025
