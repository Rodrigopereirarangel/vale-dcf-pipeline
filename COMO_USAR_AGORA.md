# 🚀 Como Usar AGORA - Análise de VaR Bitcoin

## ✅ O que funciona AGORA (sem instalar nada):

### 1. Demonstração Completa com Dados Simulados

```bash
python demo_btc_var.py
```

**O que faz:**
- ✅ Gera 1 ano de dados sintéticos de Bitcoin
- ✅ Calcula VaR 95% e 99% para:
  - 1 dia (24 horas)
  - 5 dias (120 horas)
  - 1 mês (720 horas)
- ✅ Mostra análise monetária (perda máxima em dólares)
- ✅ Exibe histograma ASCII da distribuição
- ✅ Mostra estatísticas descritivas

**Resultado:**
```
VaR para 1 dia:
- VaR 95%: -11.93% → Perda máxima: $1,192.63
- VaR 99%: -17.24% → Perda máxima: $1,724.15

(Com investimento de $10,000)
```

---

## 📦 Para usar com DADOS REAIS do Bitcoin:

### Passo 1: Instalar dependências

Em seu ambiente (fora do container, se aplicável):

```bash
# Método 1: Instalar todas as dependências
pip install -r requirements.txt

# Método 2: Instalar apenas o necessário
pip install pandas numpy scipy yfinance plotly streamlit
```

### Passo 2: Usar o CLI

Depois de instalar, você pode:

```bash
# VaR para 1 dia, 5 dias e 1 mês
python btc_var_cli.py --standard

# VaR customizado para 48 horas
python btc_var_cli.py --hours 48

# VaR para 1 semana com valor investido
python btc_var_cli.py --days 7 --investment 5000

# Com estatísticas detalhadas
python btc_var_cli.py --standard --stats
```

### Passo 3: Dashboard Visual (Melhor opção!)

```bash
streamlit run btc_var_analysis.py
```

Abre no navegador com interface completa:
- Gráficos interativos
- Calculadora de VaR customizada
- Análise visual de distribuições
- Q-Q plots para normalidade
- Histórico completo de preços

---

## 🎯 Casos de Uso Práticos

### Caso 1: "Quero testar rapidinho como funciona"
```bash
python demo_btc_var.py
```

### Caso 2: "Preciso saber o risco real do Bitcoin para próxima semana"
```bash
# Instale as dependências primeiro
pip install yfinance pandas numpy

# Execute
python btc_var_cli.py --days 7 --investment 10000 --stats
```

### Caso 3: "Quero análise visual completa"
```bash
# Instale as dependências primeiro
pip install -r requirements.txt

# Execute
streamlit run btc_var_analysis.py
```

### Caso 4: "Preciso calcular VaR para 72 horas"
```bash
python btc_var_cli.py --hours 72 --simulations 20000
```

---

## 📊 Entendendo os Resultados

### O que significa VaR 95% = -5%?

Em **95% dos cenários**, sua perda não excederá **5%**.

**Exemplo:**
- Você investe $10,000
- VaR 95% de 1 dia = -5%
- **Significa:** Em 95 de 100 dias, você não perderá mais que $500

### O que significa VaR 99% = -8%?

Em **99% dos cenários**, sua perda não excederá **8%**.

**Exemplo:**
- Você investe $10,000
- VaR 99% de 1 dia = -8%
- **Significa:** Em 99 de 100 dias, você não perderá mais que $800

⚠️ **ATENÇÃO:** Ainda existe **1%** de chance de perder MAIS que 8%!

---

## 🔧 Comandos Disponíveis (CLI)

| Comando | Descrição |
|---------|-----------|
| `--standard` | Calcula VaR para 1 dia, 5 dias e 1 mês |
| `--hours N` | Horizonte em horas (ex: `--hours 48`) |
| `--days N` | Horizonte em dias (ex: `--days 7`) |
| `--investment X` | Valor investido em USD (ex: `--investment 5000`) |
| `--simulations N` | Número de simulações MC (padrão: 10000) |
| `--years N` | Anos de histórico (padrão: 5, máx: 5) |
| `--stats` | Mostra estatísticas descritivas |

---

## 💡 Dicas

1. **Primeira vez?** → Use `demo_btc_var.py`
2. **Precisa de velocidade?** → Use CLI: `btc_var_cli.py`
3. **Quer gráficos bonitos?** → Use Streamlit: `streamlit run btc_var_analysis.py`
4. **Quer entender a teoria?** → Leia `BTC_VAR_README.md`

---

## ⚡ Teste AGORA

Execute este comando para ver a demo funcionando:

```bash
python demo_btc_var.py
```

Tempo de execução: ~5 segundos
Saída: Análise completa com VaR para múltiplos períodos!
