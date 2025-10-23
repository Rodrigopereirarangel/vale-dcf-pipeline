# Guia Rápido de Uso - Análise de VaR do Bitcoin

## Opção 1: Demonstração com Dados Simulados (RÁPIDO)

**Não precisa instalar nada extra, funciona agora:**

```bash
python demo_btc_var.py
```

Mostra:
- VaR 95% e 99% para 1 dia, 5 dias, 1 mês
- Análise monetária (investimento de $10,000)
- Histograma ASCII da distribuição

---

## Opção 2: CLI com Dados REAIS do Bitcoin

### Instalação (fazer uma vez):
```bash
pip install yfinance
```

### Exemplos de Uso:

**a) VaR para períodos padrão (1 dia, 5 dias, 1 mês):**
```bash
python btc_var_cli.py --standard
```

**b) VaR para 1 dia (24 horas):**
```bash
python btc_var_cli.py --days 1
```

**c) VaR para 48 horas:**
```bash
python btc_var_cli.py --hours 48
```

**d) VaR para 7 dias com análise monetária ($10,000 investidos):**
```bash
python btc_var_cli.py --days 7 --investment 10000
```

**e) VaR com estatísticas completas:**
```bash
python btc_var_cli.py --standard --stats
```

**f) VaR com mais simulações (mais preciso):**
```bash
python btc_var_cli.py --days 30 --simulations 50000
```

**g) Usar menos anos de histórico (mais rápido):**
```bash
python btc_var_cli.py --standard --years 1
```

---

## Opção 3: Dashboard Visual com Streamlit (MELHOR!)

### Instalação (fazer uma vez):
```bash
pip install streamlit yfinance
```

### Rodar o Dashboard:
```bash
streamlit run btc_var_analysis.py
```

Isso abrirá automaticamente no navegador com:
- ✅ Interface visual completa
- ✅ Gráficos interativos
- ✅ Calculadora de VaR customizado
- ✅ Análise de distribuição
- ✅ Q-Q plots
- ✅ Histórico de preços e volatilidade

---

## Tabela Comparativa

| Opção | Velocidade | Dados | Visualização | Uso |
|-------|-----------|-------|--------------|-----|
| demo_btc_var.py | ⚡⚡⚡ Muito rápido | Simulados | Texto | Teste rápido |
| btc_var_cli.py | ⚡⚡ Rápido | REAIS | Texto | Scripts/Terminal |
| btc_var_analysis.py | ⚡ Normal | REAIS | Gráficos | Análise completa |

---

## Resolução de Problemas

### Erro: "No module named 'yfinance'"
```bash
pip install yfinance
```

### Erro ao baixar dados do Bitcoin
- Verifique sua conexão com internet
- Tente reduzir anos: `--years 1`

### Erro: "No module named 'streamlit'"
```bash
pip install streamlit
```

---

## Exemplos Práticos

### Cenário 1: "Quero saber o risco de investir $5000 por 1 semana"
```bash
python btc_var_cli.py --days 7 --investment 5000
```

### Cenário 2: "Preciso de análise visual completa"
```bash
streamlit run btc_var_analysis.py
# Depois configure no sidebar
```

### Cenário 3: "Teste rápido sem internet"
```bash
python demo_btc_var.py
```

### Cenário 4: "Análise de risco para próximas 72 horas"
```bash
python btc_var_cli.py --hours 72 --investment 10000 --stats
```

---

## Dicas

1. **Primeira vez**: Use `demo_btc_var.py` para entender o conceito
2. **Análise rápida**: Use `btc_var_cli.py`
3. **Análise profunda**: Use `streamlit run btc_var_analysis.py`
4. **Scripts automatizados**: Use `btc_var_cli.py` em cron jobs ou scripts
