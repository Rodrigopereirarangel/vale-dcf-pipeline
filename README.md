# Comparador de Ativos da B3

Aplicação Streamlit para comparar o desempenho de ações e outros ativos listados na B3
utilizando dados históricos do Yahoo Finance.

## Funcionalidades

- Normalização dos preços para comparar a evolução relativa de cada ativo.
- Cálculo de retornos diários e estatísticas como retorno total, volatilidade e Sharpe.
- Heatmap de correlação entre os retornos dos ativos selecionados.
- Interface interativa para escolher tickers, intervalo e período de análise.

## Pré-requisitos

Instale as dependências em um ambiente virtual de sua preferência:

```bash
pip install -r requirements.txt
```

## Como executar

Inicie o dashboard com o Streamlit:

```bash
streamlit run app.py
```

A aplicação estará disponível em `http://localhost:8501`.

## Observações

- Informe os tickers no formato `TICKER` ou `TICKER.SA` (ex.: `PETR4` ou `VALE3.SA`).
- Os dados são obtidos via biblioteca `yfinance`, que utiliza a API pública do Yahoo Finance.
