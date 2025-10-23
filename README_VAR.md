# 📊 Análise de VaR (Value at Risk) - Bitcoin/USD

Sistema completo para cálculo de **Value at Risk (VaR)** do Bitcoin usando **simulação Monte Carlo**.

## 🚀 Como Usar AGORA

### Opção 1: Demo Rápida (Recomendado para começar)

```bash
python demo_btc_var.py
```

**Funciona imediatamente** sem instalar nada! Usa dados simulados.

### Opção 2: Exemplos Interativos

```bash
python exemplo_uso.py
```

5 exemplos práticos que explicam conceitos e cálculos.

### Opção 3: CLI com Dados REAIS

```bash
# Instalar dependências primeiro
pip install yfinance pandas numpy scipy

# Usar
python btc_var_cli.py --standard
python btc_var_cli.py --days 7 --investment 10000
```

### Opção 4: Dashboard Visual

```bash
# Instalar dependências primeiro
pip install -r requirements.txt

# Rodar
streamlit run btc_var_analysis.py
```

Abre interface gráfica completa no navegador!

---

## 📁 Estrutura de Arquivos

### Scripts Principais

| Arquivo | Descrição | Uso |
|---------|-----------|-----|
| `demo_btc_var.py` | Demo com dados simulados | `python demo_btc_var.py` |
| `btc_var_cli.py` | CLI para dados reais | `python btc_var_cli.py --standard` |
| `btc_var_analysis.py` | Dashboard Streamlit | `streamlit run btc_var_analysis.py` |
| `exemplo_uso.py` | 5 exemplos práticos | `python exemplo_uso.py` |

### Módulos

| Arquivo | Descrição |
|---------|-----------|
| `src/btc_var_calculator.py` | Módulo principal com funções de VaR |

### Documentação

| Arquivo | Descrição |
|---------|-----------|
| `COMO_USAR_AGORA.md` | **Guia rápido** - comece aqui! |
| `GUIA_USO.md` | Documentação completa |
| `BTC_VAR_README.md` | Teoria, metodologia e referências |
| `README_VAR.md` | Este arquivo |

### Testes

| Arquivo | Descrição |
|---------|-----------|
| `test_btc_var.py` | Testes automatizados |

---

## 🎯 O que é VaR?

**VaR (Value at Risk)** = Perda máxima esperada com um dado nível de confiança.

**Exemplo:**
- VaR 95% de -5% em 1 dia
- **Significa:** Em 95% dos cenários, você não perderá mais que 5% em 1 dia

---

## ⚡ Exemplos de Comandos

```bash
# Demo rápida (funciona agora!)
python demo_btc_var.py

# Exemplos educativos
python exemplo_uso.py

# VaR padrão (1 dia, 5 dias, 1 mês) - dados reais
python btc_var_cli.py --standard

# VaR para 48 horas
python btc_var_cli.py --hours 48

# VaR para 1 semana com $5,000 investidos
python btc_var_cli.py --days 7 --investment 5000

# Com estatísticas detalhadas
python btc_var_cli.py --standard --stats

# Dashboard visual
streamlit run btc_var_analysis.py
```

---

## 📊 Funcionalidades

### Cálculos
- ✅ VaR 95% e 99%
- ✅ Simulação Monte Carlo (10,000+ iterações)
- ✅ Períodos: customizável (qualquer qtd de horas/dias)
- ✅ Análise monetária (perda em dólares)

### Dados
- ✅ Dados horários do BTC/USD
- ✅ Histórico de até 5 anos
- ✅ Retornos logarítmicos

### Visualizações (Dashboard)
- ✅ Gráficos interativos
- ✅ Distribuição de retornos
- ✅ Q-Q plots para normalidade
- ✅ Volatilidade móvel
- ✅ Histórico de preços

---

## 📖 Interpretação

### VaR 95% = -5%
Em **95% dos cenários**, a perda não excederá **5%**.

**Com $10,000 investidos:**
- Perda máxima (95%): $500
- Mas há **5%** de chance de perder mais!

### VaR 99% = -8%
Em **99% dos cenários**, a perda não excederá **8%**.

**Com $10,000 investidos:**
- Perda máxima (99%): $800
- Mas há **1%** de chance de perder mais!

---

## 🔧 Instalação (para dados reais)

```bash
# Opção 1: Instalar tudo
pip install -r requirements.txt

# Opção 2: Apenas o essencial
pip install pandas numpy scipy yfinance plotly streamlit
```

---

## 💡 Recomendações

| Situação | Use |
|----------|-----|
| Primeira vez | `demo_btc_var.py` |
| Aprender conceitos | `exemplo_uso.py` |
| Análise rápida | `btc_var_cli.py` |
| Análise visual | `streamlit run btc_var_analysis.py` |
| Entender teoria | Leia `BTC_VAR_README.md` |

---

## ⚠️ Limitações

- VaR não captura eventos extremos (tail risk)
- Assume distribuição normal (Bitcoin tem fat tails)
- Baseado em dados históricos
- Use com outras métricas de risco (CVaR, etc.)

---

## 📚 Arquivos de Documentação

Leia nesta ordem:

1. **COMO_USAR_AGORA.md** - Guia rápido
2. **GUIA_USO.md** - Documentação completa
3. **BTC_VAR_README.md** - Teoria e metodologia

---

## 🤝 Contribuição

Código desenvolvido para análise de risco de criptomoedas usando técnicas quantitativas.

**Tecnologias:**
- Python 3.11+
- NumPy, Pandas, SciPy
- Plotly (visualizações)
- Streamlit (dashboard)
- yfinance (dados)

---

## 📞 Suporte

**Problemas comuns:**

1. **Erro: No module named 'yfinance'**
   ```bash
   pip install yfinance
   ```

2. **Erro ao baixar dados**
   - Verifique internet
   - Use: `--years 1` (menos dados)

3. **Quer apenas testar**
   ```bash
   python demo_btc_var.py
   ```

---

**Desenvolvido com Python | Última atualização: 2025**
