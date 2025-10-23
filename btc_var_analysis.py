"""Dashboard Streamlit para análise de VaR do Bitcoin usando Monte Carlo."""

from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

from src.btc_var_calculator import (
    fetch_btc_hourly_data,
    calculate_hourly_returns,
    monte_carlo_var,
    calculate_var_for_periods,
    calculate_var_monetary,
    get_var_statistics,
)

st.set_page_config(
    page_title="Análise de VaR - Bitcoin",
    page_icon="₿",
    layout="wide"
)

st.title("₿ Análise de VaR (Value at Risk) - Bitcoin/USD")

st.markdown("""
Esta aplicação calcula o **VaR (Value at Risk)** do Bitcoin usando **simulação Monte Carlo**.
O VaR estima a perda máxima esperada em um investimento durante um período com um dado nível de confiança.

**Dados**: Preços horários do BTC/USD dos últimos ~5 anos
""")

# Sidebar com configurações
with st.sidebar:
    st.header("⚙️ Configurações")

    st.subheader("Simulação Monte Carlo")
    num_simulations = st.number_input(
        "Número de Simulações",
        min_value=1000,
        max_value=100000,
        value=10000,
        step=1000,
        help="Maior número = resultados mais precisos, mas demora mais"
    )

    random_seed = st.number_input(
        "Seed Aleatória",
        min_value=1,
        max_value=9999,
        value=42,
        help="Para reprodutibilidade dos resultados"
    )

    st.subheader("Análise Monetária")
    investment_value = st.number_input(
        "Valor do Investimento (USD)",
        min_value=0.0,
        value=10000.0,
        step=1000.0,
        help="Valor investido em Bitcoin"
    )

    years_history = st.slider(
        "Anos de Histórico",
        min_value=1,
        max_value=5,
        value=5,
        help="Quantidade de anos de dados históricos (limitado pela API)"
    )


# Cache para dados
@st.cache_data(show_spinner=False)
def load_btc_data(years: int):
    """Carrega dados do Bitcoin."""
    return fetch_btc_hourly_data(years=years)


@st.cache_data(show_spinner=False)
def compute_returns(prices: pd.DataFrame):
    """Calcula retornos."""
    return calculate_hourly_returns(prices)


# Carregar dados
with st.spinner("🔄 Carregando dados do Bitcoin..."):
    try:
        btc_prices = load_btc_data(years_history)
        returns = compute_returns(btc_prices)
        st.success(f"✅ Dados carregados: {len(btc_prices)} observações horárias")
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        st.stop()

# Tabs para organizar conteúdo
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 VaR - Períodos Padrão",
    "🎯 VaR - Período Customizado",
    "📈 Distribuição de Retornos",
    "💰 Análise Monetária",
    "📉 Dados Históricos"
])

# Tab 1: VaR para períodos padrão
with tab1:
    st.header("VaR para Períodos Padrão")

    with st.spinner("🔄 Calculando VaR para períodos padrão..."):
        var_results_df = calculate_var_for_periods(
            returns,
            num_simulations=num_simulations
        )

    st.dataframe(
        var_results_df[["Período", "Horas", "VaR 95%", "VaR 99%"]],
        use_container_width=True,
        hide_index=True
    )

    # Gráfico comparativo
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='VaR 95%',
        x=var_results_df['Período'],
        y=var_results_df['VaR 95% (valor)'] * 100,
        marker_color='orange'
    ))

    fig.add_trace(go.Bar(
        name='VaR 99%',
        x=var_results_df['Período'],
        y=var_results_df['VaR 99% (valor)'] * 100,
        marker_color='red'
    ))

    fig.update_layout(
        title='Comparação de VaR por Período',
        xaxis_title='Período',
        yaxis_title='VaR (%)',
        barmode='group',
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    st.info("""
    **Interpretação**:
    - **VaR 95%**: Em 95% dos casos, a perda não excederá este valor
    - **VaR 99%**: Em 99% dos casos, a perda não excederá este valor
    - Valores negativos indicam perdas potenciais
    """)

# Tab 2: VaR customizado
with tab2:
    st.header("VaR para Período Customizado")

    col1, col2 = st.columns(2)

    with col1:
        time_unit = st.radio(
            "Unidade de Tempo",
            options=["Horas", "Dias"],
            horizontal=True
        )

    with col2:
        if time_unit == "Horas":
            time_value = st.number_input(
                "Quantidade de Horas",
                min_value=1,
                max_value=24 * 365,
                value=24,
                step=1
            )
            horizon_hours = time_value
        else:
            time_value = st.number_input(
                "Quantidade de Dias",
                min_value=1,
                max_value=365,
                value=1,
                step=1
            )
            horizon_hours = time_value * 24

    if st.button("🎲 Calcular VaR", type="primary"):
        with st.spinner(f"🔄 Calculando VaR para {horizon_hours} horas..."):
            custom_var = monte_carlo_var(
                returns,
                horizon_hours=horizon_hours,
                num_simulations=num_simulations,
                random_seed=random_seed
            )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "VaR 95%",
                f"{custom_var.var_95:.2%}",
                help="Perda máxima em 95% dos cenários"
            )

        with col2:
            st.metric(
                "VaR 99%",
                f"{custom_var.var_99:.2%}",
                help="Perda máxima em 99% dos cenários"
            )

        with col3:
            st.metric(
                "Volatilidade Horária",
                f"{custom_var.volatility:.4%}"
            )

        # Histograma das simulações
        st.subheader("Distribuição dos Retornos Simulados")

        fig = go.Figure()

        fig.add_trace(go.Histogram(
            x=custom_var.simulated_returns * 100,
            nbinsx=100,
            name='Retornos Simulados',
            marker_color='lightblue'
        ))

        # Linhas de VaR
        fig.add_vline(
            x=custom_var.var_95 * 100,
            line_dash="dash",
            line_color="orange",
            annotation_text=f"VaR 95%: {custom_var.var_95:.2%}"
        )

        fig.add_vline(
            x=custom_var.var_99 * 100,
            line_dash="dash",
            line_color="red",
            annotation_text=f"VaR 99%: {custom_var.var_99:.2%}"
        )

        fig.update_layout(
            title=f'Distribuição de {num_simulations:,} Simulações Monte Carlo',
            xaxis_title='Retorno (%)',
            yaxis_title='Frequência',
            height=500,
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)

        # Estatísticas das simulações
        st.subheader("Estatísticas das Simulações")

        sim_stats = pd.DataFrame({
            "Métrica": [
                "Média",
                "Mediana",
                "Desvio Padrão",
                "Mínimo",
                "Máximo",
                "Percentil 5%",
                "Percentil 1%"
            ],
            "Valor": [
                f"{custom_var.simulated_returns.mean():.2%}",
                f"{np.median(custom_var.simulated_returns):.2%}",
                f"{custom_var.simulated_returns.std():.2%}",
                f"{custom_var.simulated_returns.min():.2%}",
                f"{custom_var.simulated_returns.max():.2%}",
                f"{custom_var.var_95:.2%}",
                f"{custom_var.var_99:.2%}",
            ]
        })

        st.dataframe(sim_stats, use_container_width=True, hide_index=True)

# Tab 3: Distribuição de retornos históricos
with tab3:
    st.header("Distribuição de Retornos Históricos")

    # Estatísticas descritivas
    stats = get_var_statistics(returns)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Retorno Médio", stats["Retorno Médio (horário)"])
        st.metric("Desvio Padrão", stats["Desvio Padrão"])

    with col2:
        st.metric("Assimetria", stats["Assimetria (Skewness)"])
        st.metric("Curtose", stats["Curtose (Kurtosis)"])

    with col3:
        st.metric("Mínimo", stats["Mínimo"])
        st.metric("Máximo", stats["Máximo"])

    with col4:
        st.metric("Observações", f"{stats['Observações']:,}")
        st.metric("Mediana", stats["Retorno Mediano"])

    # Histograma de retornos
    fig = px.histogram(
        returns * 100,
        nbins=100,
        title="Distribuição de Retornos Horários",
        labels={"value": "Retorno (%)", "count": "Frequência"}
    )

    fig.update_layout(
        showlegend=False,
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    # QQ Plot (para verificar normalidade)
    st.subheader("Q-Q Plot (Teste de Normalidade)")

    from scipy import stats as scipy_stats

    qq_data = scipy_stats.probplot(returns.dropna(), dist="norm")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=qq_data[0][0],
        y=qq_data[0][1],
        mode='markers',
        name='Dados',
        marker=dict(color='blue', size=3)
    ))

    fig.add_trace(go.Scatter(
        x=qq_data[0][0],
        y=qq_data[0][0] * qq_data[1][0] + qq_data[1][1],
        mode='lines',
        name='Normal Teórica',
        line=dict(color='red', dash='dash')
    ))

    fig.update_layout(
        title='Q-Q Plot - Comparação com Distribuição Normal',
        xaxis_title='Quantis Teóricos',
        yaxis_title='Quantis Amostrais',
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    st.info("""
    **Interpretação do Q-Q Plot**:
    - Se os pontos seguem a linha vermelha, os dados são aproximadamente normais
    - Desvios nas extremidades indicam caudas mais pesadas (fat tails)
    - Retornos de criptomoedas tipicamente têm caudas pesadas
    """)

# Tab 4: Análise monetária
with tab4:
    st.header("Análise Monetária do VaR")

    st.info(f"💰 Valor do Investimento: **${investment_value:,.2f}**")

    # Calcular VaR monetário para períodos padrão
    monetary_results = []

    for _, row in var_results_df.iterrows():
        var_95_monetary = calculate_var_monetary(row['VaR 95% (valor)'], investment_value)
        var_99_monetary = calculate_var_monetary(row['VaR 99% (valor)'], investment_value)

        monetary_results.append({
            "Período": row['Período'],
            "Perda Máxima (VaR 95%)": f"${var_95_monetary:,.2f}",
            "Perda Máxima (VaR 99%)": f"${var_99_monetary:,.2f}",
            "VaR 95% valor": var_95_monetary,
            "VaR 99% valor": var_99_monetary,
        })

    monetary_df = pd.DataFrame(monetary_results)

    st.dataframe(
        monetary_df[["Período", "Perda Máxima (VaR 95%)", "Perda Máxima (VaR 99%)"]],
        use_container_width=True,
        hide_index=True
    )

    # Gráfico de barras
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='Perda Máxima VaR 95%',
        x=monetary_df['Período'],
        y=monetary_df['VaR 95% valor'],
        marker_color='orange',
        text=monetary_df['Perda Máxima (VaR 95%)'],
        textposition='outside'
    ))

    fig.add_trace(go.Bar(
        name='Perda Máxima VaR 99%',
        x=monetary_df['Período'],
        y=monetary_df['VaR 99% valor'],
        marker_color='red',
        text=monetary_df['Perda Máxima (VaR 99%)'],
        textposition='outside'
    ))

    fig.update_layout(
        title=f'Perda Máxima Esperada (Investimento: ${investment_value:,.2f})',
        xaxis_title='Período',
        yaxis_title='Perda Máxima (USD)',
        barmode='group',
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    st.warning("""
    **Importante**:
    - Estes valores representam a perda máxima esperada com os níveis de confiança especificados
    - VaR não captura perdas extremas (tail risk) além dos percentis calculados
    - Considere também o CVaR (Conditional VaR) para cenários extremos
    - Criptomoedas têm alta volatilidade - use estes valores como referência de risco
    """)

# Tab 5: Dados históricos
with tab5:
    st.header("Dados Históricos do Bitcoin")

    st.subheader("Evolução do Preço")

    fig = px.line(
        btc_prices,
        y='Close',
        title='Preço do Bitcoin/USD (Horário)',
        labels={'Close': 'Preço (USD)', 'index': 'Data'}
    )

    fig.update_layout(height=400)

    st.plotly_chart(fig, use_container_width=True)

    # Série de retornos
    st.subheader("Série Temporal de Retornos")

    fig = px.line(
        returns * 100,
        title='Retornos Horários do Bitcoin (%)',
        labels={'value': 'Retorno (%)', 'index': 'Data'}
    )

    fig.update_layout(height=400, showlegend=False)

    st.plotly_chart(fig, use_container_width=True)

    # Rolling volatility
    st.subheader("Volatilidade Móvel (30 dias)")

    rolling_vol = returns.rolling(window=24*30).std() * np.sqrt(24) * 100  # Volatilidade diária

    fig = px.line(
        rolling_vol,
        title='Volatilidade Diária Móvel (janela de 30 dias)',
        labels={'value': 'Volatilidade Diária (%)', 'index': 'Data'}
    )

    fig.update_layout(height=400, showlegend=False)

    st.plotly_chart(fig, use_container_width=True)

    # Tabela com amostra dos dados
    st.subheader("Amostra dos Dados")

    sample_data = btc_prices[['Close']].copy()
    sample_data['Retorno (%)'] = returns * 100

    st.dataframe(
        sample_data.tail(100),
        use_container_width=True
    )

# Footer
st.divider()

st.markdown("""
**Notas**:
- VaR calculado usando simulação Monte Carlo com retornos logarítmicos
- Assume distribuição normal dos retornos (validar com Q-Q Plot)
- Dados obtidos via yfinance (Yahoo Finance)
- Para análise profissional, considere também CVaR, Expected Shortfall e stress testing

**Desenvolvido com**: Python, Streamlit, Pandas, NumPy, Plotly
""")
