"""
Polymarket - Crypto Markets Tracker + Probabilidade Calculada
Busca mercados do Polymarket e adiciona coluna de probabilidade calculada via Monte Carlo
Logica de calculo EXATAMENTE igual ao codigo fornecido - sem nenhuma modificacao
"""

import requests
from datetime import datetime, timezone, timedelta
import json
import re
import numpy as np
import pandas as pd
from scipy import stats
import time
import warnings
warnings.filterwarnings('ignore')

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

COINS = [
    {"name": "BITCOIN", "emoji": "B", "symbol": "BTC", "slug_above": "bitcoin-above-on", "slug_price": "bitcoin-price-on", "pattern_above": "Bitcoin above", "pattern_price": "Bitcoin price on"},
    {"name": "ETHEREUM", "emoji": "E", "symbol": "ETH", "slug_above": "ethereum-above-on", "slug_price": "ethereum-price-on", "pattern_above": "Ethereum above", "pattern_price": "Ethereum price on"},
    {"name": "SOLANA", "emoji": "S", "symbol": "SOL", "slug_above": "solana-above-on", "slug_price": "solana-price-on", "pattern_above": "Solana above", "pattern_price": "Solana price on"},
    {"name": "XRP", "emoji": "X", "symbol": "XRP", "slug_above": "xrp-above-on", "slug_price": "xrp-price-on", "pattern_above": "XRP above", "pattern_price": "XRP price on"},
]

CACHE_DADOS = {}
CACHE_SIMULACOES = {}

# ============================================================================
# FUNCOES POLYMARKET
# ============================================================================

def generate_date_slugs(base_slug, days_ahead=14):
    months = {1: "january", 2: "february", 3: "march", 4: "april", 5: "may", 6: "june",
              7: "july", 8: "august", 9: "september", 10: "october", 11: "november", 12: "december"}
    slugs = []
    today = datetime.now(timezone.utc)
    for i in range(days_ahead):
        date = today + timedelta(days=i)
        slug = f"{base_slug}-{months[date.month]}-{date.day}"
        slugs.append(slug)
    return slugs


def fetch_event_by_slug(slug):
    try:
        response = requests.get(f"{GAMMA_API}/events", params={"slug": slug}, timeout=10)
        response.raise_for_status()
        events = response.json()
        return events[0] if events else None
    except:
        return None


def fetch_order_book_price(token_id, side):
    try:
        response = requests.get(f"{CLOB_API}/price", params={"token_id": token_id, "side": side}, timeout=5)
        response.raise_for_status()
        return float(response.json().get("price", 0))
    except:
        return None


def fetch_market_order_book(market):
    clob_tokens = market.get("clobTokenIds", "[]")
    try:
        token_ids = json.loads(clob_tokens) if isinstance(clob_tokens, str) else clob_tokens
    except:
        token_ids = []
    if len(token_ids) < 2:
        return None
    return {
        "yes": {"bid": fetch_order_book_price(token_ids[0], "BUY"), "ask": fetch_order_book_price(token_ids[0], "SELL")},
        "no": {"bid": fetch_order_book_price(token_ids[1], "BUY"), "ask": fetch_order_book_price(token_ids[1], "SELL")}
    }


def fetch_closest_event(base_slug, title_pattern):
    for slug in generate_date_slugs(base_slug, days_ahead=30):
        event = fetch_event_by_slug(slug)
        if event and not event.get("closed", True):
            if title_pattern in event.get("title", ""):
                end_date = event.get("endDate")
                if end_date:
                    seconds, time_str, hours_rounded = get_time_to_resolution(end_date)
                    if seconds and seconds > 0:
                        event["time_to_resolution"] = time_str
                        event["hours_rounded"] = hours_rounded
                        return event
    return None


def get_time_to_resolution(end_date_str):
    try:
        end_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        delta = end_date - now
        if delta.total_seconds() < 0:
            return None, "Resolvido", 0
        total_seconds = delta.total_seconds()
        total_hours = total_seconds / 3600
        days = int(total_seconds // 86400)
        hours = int((total_seconds % 86400) // 3600)
        minutes = int((total_seconds % 3600) // 60)

        # Arredondar: >=20min para cima, <20min para baixo
        if minutes >= 20:
            hours_rounded = int(total_hours) + 1
        else:
            hours_rounded = int(total_hours)
        hours_rounded = max(1, hours_rounded)

        if days > 0:
            time_str = f"{days}d {hours}h {minutes}min"
        else:
            time_str = f"{hours}h {minutes}min"
        return total_seconds, time_str, hours_rounded
    except:
        return None, "Erro", 0


def parse_outcomes_prices(outcomes_str, prices_str):
    try:
        outcomes = json.loads(outcomes_str) if isinstance(outcomes_str, str) else outcomes_str
        prices = json.loads(prices_str) if isinstance(prices_str, str) else prices_str
        return outcomes, prices
    except:
        return [], []


def extract_price_target(question):
    match = re.search(r'\$?([\d,]+(?:\.\d+)?)', question)
    return float(match.group(1).replace(",", "")) if match else 0


def extract_price_range(question):
    if "less than" in question.lower():
        match = re.search(r'\$?([\d,]+(?:\.\d+)?)', question)
        return (0, float(match.group(1).replace(",", ""))) if match else (0, 0)
    elif "between" in question.lower():
        matches = re.findall(r'\$?([\d,]+(?:\.\d+)?)', question)
        return (float(matches[0].replace(",", "")), float(matches[1].replace(",", ""))) if len(matches) >= 2 else (0, 0)
    elif "greater than" in question.lower():
        match = re.search(r'\$?([\d,]+(?:\.\d+)?)', question)
        return (float(match.group(1).replace(",", "")), 999999) if match else (0, 0)
    return (0, 0)


# ============================================================================
# FUNCOES DE CALCULO - EXATAMENTE IGUAL AO CODIGO ORIGINAL
# ============================================================================

def obter_config_janela(horizonte_horas):
    if horizonte_horas <= 6:
        return {
            'janela_momentum_min': 24,
            'n_bins': 15,
            'incluir_vizinhos': True,
            'n_sim': 50000,
            'half_life_dias': 7,
            'min_amostras': 20,
            'tipo': 'ULTRA-CURTA'
        }
    elif horizonte_horas <= 12:
        return {
            'janela_momentum_min': 48,
            'n_bins': 21,
            'incluir_vizinhos': True,
            'n_sim': 50000,
            'half_life_dias': 7,
            'min_amostras': 25,
            'tipo': 'CURTA'
        }
    else:
        return {
            'janela_momentum_min': 96,
            'n_bins': 47,
            'incluir_vizinhos': True,
            'n_sim': 100000,
            'half_life_dias': 30,
            'min_amostras': 50,
            'tipo': 'MEDIA/LONGA'
        }


def buscar_cryptocompare_horario(symbol, horas=35040):
    try:
        all_data = []
        for offset in range(0, horas, 2000):
            url = "https://min-api.cryptocompare.com/data/v2/histohour"
            params = {'fsym': symbol, 'tsym': 'USD', 'limit': min(2000, horas - offset)}
            if offset > 0:
                to_ts = int((datetime.now() - timedelta(hours=offset)).timestamp())
                params['toTs'] = to_ts
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data['Response'] == 'Success' and 'Data' in data:
                    all_data.extend(data['Data']['Data'])
            time.sleep(0.5)
        if len(all_data) == 0:
            return None
        df = pd.DataFrame(all_data)
        df['timestamp'] = pd.to_datetime(df['time'], unit='s')
        df = df.set_index('timestamp')
        df = df.rename(columns={'close': 'Close'})
        df = df[['Close']]
        df = df.sort_index()
        df = df[~df.index.duplicated(keep='last')]
        return df
    except:
        return None


def buscar_coingecko_horario(symbol, dias=365):
    coingecko_ids = {'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana', 'XRP': 'ripple'}
    coin_id = coingecko_ids.get(symbol)
    if not coin_id:
        return None
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {'vs_currency': 'usd', 'days': dias, 'interval': 'hourly'}
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if 'prices' not in data or len(data['prices']) == 0:
                return None
            df = pd.DataFrame(data['prices'], columns=['timestamp', 'Close'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df.set_index('timestamp')
            df = df.sort_index()
            df = df[~df.index.duplicated(keep='last')]
            return df
    except:
        return None
    return None


def buscar_dados_profissional(symbol):
    if symbol in CACHE_DADOS:
        return CACHE_DADOS[symbol], 'Cache'
    dados = buscar_cryptocompare_horario(symbol, horas=35040)
    if dados is not None and len(dados) > 1000:
        CACHE_DADOS[symbol] = dados
        return dados, 'CryptoCompare'
    time.sleep(1)
    dados = buscar_coingecko_horario(symbol, dias=365)
    if dados is not None and len(dados) > 1000:
        CACHE_DADOS[symbol] = dados
        return dados, 'CoinGecko'
    return None, None


def calcular_momentum(dados_historicos, janela_momentum):
    dados = dados_historicos.copy()
    dados = dados[~dados.index.duplicated(keep='last')].copy()
    dados['Retorno'] = dados['Close'].pct_change()
    dados = dados.dropna()
    momentums = []
    indices = []
    for i in range(janela_momentum, len(dados)):
        ret_momentum = np.prod(1 + dados['Retorno'].iloc[i-janela_momentum:i].values) - 1
        momentums.append(ret_momentum)
        indices.append(dados.index[i])
    df_momentum = pd.DataFrame({
        'Close': [dados['Close'].iloc[i] for i in range(janela_momentum, len(dados))],
        'Momentum': momentums
    }, index=indices)
    return df_momentum


def criar_bins_momentum(momentums, n_bins=47):
    min_mom = momentums.min()
    max_mom = momentums.max()
    bins_edges = np.linspace(min_mom, max_mom, n_bins + 1)
    bins_centers = (bins_edges[:-1] + bins_edges[1:]) / 2
    return bins_edges, bins_centers


def identificar_bin_atual(momentum_atual, bins_edges):
    for i in range(len(bins_edges) - 1):
        if bins_edges[i] <= momentum_atual < bins_edges[i + 1]:
            return i
    if momentum_atual >= bins_edges[-2]:
        return len(bins_edges) - 2
    return 0


def expandir_bins_dinamicamente(df_momentum, bins_edges, bin_atual, target_samples=50, max_expansao=10):
    bins_interesse = [bin_atual]
    distancia = 1
    n_bins_total = len(bins_edges) - 1
    while len(bins_interesse) < max_expansao and distancia < n_bins_total:
        if bin_atual - distancia >= 0:
            bins_interesse.append(bin_atual - distancia)
        if bin_atual + distancia < n_bins_total:
            bins_interesse.append(bin_atual + distancia)
        count = 0
        for idx in df_momentum.index:
            momentum = df_momentum.loc[idx, 'Momentum']
            bin_idx = identificar_bin_atual(momentum, bins_edges)
            if bin_idx in bins_interesse:
                count += 1
        if count >= target_samples:
            break
        distancia += 1
        if len(bins_interesse) > n_bins_total * 0.3:
            break
    bins_interesse.sort()
    return bins_interesse


def extrair_retornos_regime(dados_historicos, df_momentum, bins_edges, bin_atual, horizonte_horas,
                           incluir_vizinhos=True, usar_overlapping=True, overlap_step=None,
                           expansao_dinamica=False, target_samples=50):
    if expansao_dinamica:
        bins_interesse = expandir_bins_dinamicamente(df_momentum, bins_edges, bin_atual, target_samples, 10)
    elif incluir_vizinhos:
        bins_interesse = []
        if bin_atual > 0:
            bins_interesse.append(bin_atual - 1)
        bins_interesse.append(bin_atual)
        if bin_atual < len(bins_edges) - 2:
            bins_interesse.append(bin_atual + 1)
    else:
        bins_interesse = [bin_atual]

    dados = dados_historicos.copy()
    dados = dados[~dados.index.duplicated(keep='last')].copy()
    dados['Retorno'] = dados['Close'].pct_change()
    dados = dados.dropna()
    dados_reset = dados.reset_index(drop=True)
    timestamp_to_pos = {dados.index[i]: i for i in range(len(dados))}
    retornos_regime = []

    if usar_overlapping:
        step = max(1, horizonte_horas // 4) if overlap_step is None else overlap_step
    else:
        step = horizonte_horas

    for idx in df_momentum.index:
        momentum = df_momentum.loc[idx, 'Momentum']
        bin_idx = identificar_bin_atual(momentum, bins_edges)
        if bin_idx in bins_interesse:
            if idx in timestamp_to_pos:
                pos = timestamp_to_pos[idx]
                if pos + horizonte_horas < len(dados_reset):
                    rets = dados_reset['Retorno'].iloc[pos+1:pos+1+horizonte_horas].values
                    if len(rets) == horizonte_horas:
                        ret_acum = np.prod(1 + rets) - 1
                        retornos_regime.append(ret_acum)
                        if usar_overlapping and step < horizonte_horas:
                            pos_atual = pos + step
                            overlap_count = 0
                            while pos_atual + horizonte_horas < len(dados_reset) and overlap_count < 4:
                                rets_overlap = dados_reset['Retorno'].iloc[pos_atual+1:pos_atual+1+horizonte_horas].values
                                if len(rets_overlap) == horizonte_horas:
                                    ret_acum_overlap = np.prod(1 + rets_overlap) - 1
                                    retornos_regime.append(ret_acum_overlap)
                                pos_atual += step
                                overlap_count += 1
    return np.array(retornos_regime)


def extrair_retornos_regime_nonoverlap(dados_historicos, df_momentum, bins_edges, bin_atual,
                                       horizonte_horas, incluir_vizinhos=True):
    if incluir_vizinhos:
        bins_interesse = []
        if bin_atual > 0:
            bins_interesse.append(bin_atual - 1)
        bins_interesse.append(bin_atual)
        if bin_atual < len(bins_edges) - 2:
            bins_interesse.append(bin_atual + 1)
    else:
        bins_interesse = [bin_atual]

    dados = dados_historicos.copy()
    dados = dados[~dados.index.duplicated(keep='last')].copy()
    dados['Retorno'] = dados['Close'].pct_change()
    dados = dados.dropna()
    dados_reset = dados.reset_index(drop=True)
    timestamp_to_pos = {dados.index[i]: i for i in range(len(dados))}

    retornos_regime = []
    posicoes_usadas = set()

    for idx in df_momentum.index:
        momentum = df_momentum.loc[idx, 'Momentum']
        bin_idx = identificar_bin_atual(momentum, bins_edges)
        if bin_idx in bins_interesse:
            if idx in timestamp_to_pos:
                pos = timestamp_to_pos[idx]
                if pos not in posicoes_usadas:
                    if pos + horizonte_horas < len(dados_reset):
                        rets = dados_reset['Retorno'].iloc[pos+1:pos+1+horizonte_horas].values
                        if len(rets) == horizonte_horas:
                            ret_acum = np.prod(1 + rets) - 1
                            retornos_regime.append(ret_acum)
                            for p in range(pos, pos + horizonte_horas):
                                posicoes_usadas.add(p)

    return np.array(retornos_regime)


def calcular_tail_index_hill(retornos, percentile_threshold=10):
    n = len(retornos)
    if n < 20:
        return np.nan
    k = max(10, int(n * (percentile_threshold / 100)))
    abs_ret = np.abs(retornos)
    sorted_abs = np.sort(abs_ret)[::-1]
    if k < len(sorted_abs) and sorted_abs[k] > 0:
        hill_ratio = sorted_abs[:k] / sorted_abs[k]
        hill_ratio = hill_ratio[np.isfinite(hill_ratio) & (hill_ratio > 0)]
        if len(hill_ratio) > 0:
            log_ratios = np.log(hill_ratio)
            log_ratios = log_ratios[np.isfinite(log_ratios)]
            if len(log_ratios) > 0:
                alpha = 1.0 / np.mean(log_ratios)
                return alpha
    return np.nan


def calcular_max_to_sum(retornos):
    abs_ret = np.abs(retornos)
    if len(abs_ret) == 0 or np.sum(abs_ret) == 0:
        return np.nan
    max_to_sum = np.max(abs_ret) / np.sum(abs_ret)
    return max_to_sum


def monte_carlo_distribuicao_taleb(retornos_regime, n_sim=100000, alpha=None, max_to_sum=None):
    np.random.seed(42)
    ajustar_caudas = False
    tail_weight = 1.0
    if alpha is not None and not np.isnan(alpha):
        if alpha < 2:
            ajustar_caudas = True
            tail_weight = 3.0
        elif alpha < 3:
            ajustar_caudas = True
            tail_weight = 2.0
    if max_to_sum is not None and not np.isnan(max_to_sum):
        if max_to_sum > 0.05:
            ajustar_caudas = True
            tail_weight = max(tail_weight, 1.5)
    if not ajustar_caudas or len(retornos_regime) < 30:
        retornos_simulados = np.random.choice(retornos_regime, size=n_sim, replace=True)
        return retornos_simulados
    threshold_low = np.percentile(retornos_regime, 10)
    threshold_high = np.percentile(retornos_regime, 90)
    cauda_baixa = retornos_regime[retornos_regime < threshold_low]
    centro = retornos_regime[(retornos_regime >= threshold_low) & (retornos_regime <= threshold_high)]
    cauda_alta = retornos_regime[retornos_regime > threshold_high]
    p_cauda = 0.1 * tail_weight
    p_centro = 1.0 - (2 * p_cauda)
    if p_centro < 0.1:
        p_centro = 0.1
        p_cauda = (1.0 - p_centro) / 2
    retornos_simulados = []
    for _ in range(n_sim):
        u = np.random.random()
        if u < p_cauda and len(cauda_baixa) > 0:
            ret = np.random.choice(cauda_baixa)
        elif u > (1 - p_cauda) and len(cauda_alta) > 0:
            ret = np.random.choice(cauda_alta)
        else:
            if len(centro) > 0:
                ret = np.random.choice(centro)
            else:
                ret = np.random.choice(retornos_regime)
        retornos_simulados.append(ret)
    return np.array(retornos_simulados)


def obter_simulacao_cached(symbol, horizonte_horas):
    cache_key = f"{symbol}_{horizonte_horas}"
    if cache_key in CACHE_SIMULACOES:
        return CACHE_SIMULACOES[cache_key]

    config = obter_config_janela(horizonte_horas)
    janela_momentum = max(config['janela_momentum_min'], 3 * horizonte_horas)

    dados, fonte = buscar_dados_profissional(symbol)
    if dados is None:
        return None

    preco_atual = float(dados['Close'].iloc[-1])
    df_momentum = calcular_momentum(dados, janela_momentum)

    if len(df_momentum) < 100:
        return None

    bins_edges, bins_centers = criar_bins_momentum(df_momentum['Momentum'].values, n_bins=config['n_bins'])
    momentum_atual = df_momentum['Momentum'].iloc[-1]
    bin_atual = identificar_bin_atual(momentum_atual, bins_edges)

    retornos_regime = extrair_retornos_regime(
        dados, df_momentum, bins_edges, bin_atual, horizonte_horas,
        incluir_vizinhos=config['incluir_vizinhos'], usar_overlapping=True,
        overlap_step=max(1, horizonte_horas // 4)
    )

    if len(retornos_regime) < config['min_amostras']:
        retornos_regime = extrair_retornos_regime(
            dados, df_momentum, bins_edges, bin_atual, horizonte_horas,
            incluir_vizinhos=False, usar_overlapping=True,
            overlap_step=max(1, horizonte_horas // 4),
            expansao_dinamica=True, target_samples=config['min_amostras']
        )

    if len(retornos_regime) < config['min_amostras']:
        retornos_regime = extrair_retornos_regime(
            dados, df_momentum, bins_edges, bin_atual, horizonte_horas,
            incluir_vizinhos=False, usar_overlapping=True,
            overlap_step=max(1, horizonte_horas // 6),
            expansao_dinamica=True, target_samples=config['min_amostras'] * 2
        )

    if len(retornos_regime) < config['min_amostras']:
        return None

    alpha_regime = calcular_tail_index_hill(retornos_regime, percentile_threshold=10)
    retornos_regime_nonoverlap = extrair_retornos_regime_nonoverlap(
        dados, df_momentum, bins_edges, bin_atual, horizonte_horas,
        incluir_vizinhos=config['incluir_vizinhos']
    )
    max_to_sum_regime = calcular_max_to_sum(retornos_regime_nonoverlap)

    retornos_simulados = monte_carlo_distribuicao_taleb(
        retornos_regime, n_sim=config['n_sim'],
        alpha=alpha_regime, max_to_sum=max_to_sum_regime
    )

    resultado = {'preco_atual': preco_atual, 'simulados': retornos_simulados}
    CACHE_SIMULACOES[cache_key] = resultado
    return resultado


def calcular_prob_above(symbol, horizonte_horas, strike):
    sim = obter_simulacao_cached(symbol, horizonte_horas)
    if sim is None:
        return None
    precos_finais = sim['preco_atual'] * (1 + sim['simulados'])
    return (precos_finais >= strike).mean() * 100


def calcular_prob_range(symbol, horizonte_horas, low, high):
    sim = obter_simulacao_cached(symbol, horizonte_horas)
    if sim is None:
        return None
    precos_finais = sim['preco_atual'] * (1 + sim['simulados'])
    if high >= 999999:
        return (precos_finais > low).mean() * 100
    elif low == 0:
        return (precos_finais < high).mean() * 100
    return ((precos_finais >= low) & (precos_finais < high)).mean() * 100


# ============================================================================
# DISPLAY
# ============================================================================

def display_above_event(event, coin):
    horizonte = event.get("hours_rounded", 24)
    print("")
    print("=" * 85)
    print(f"{coin['emoji']} {coin['name']} ABOVE: {event.get('title')}")
    print(f"Resolucao: {event.get('time_to_resolution')} (calc: {horizonte}h) | https://polymarket.com/event/{event.get('slug')}")
    print("")

    markets = event.get("markets", [])
    if not markets:
        return

    markets_sorted = sorted(markets, key=lambda m: extract_price_target(m.get("question", "")))

    print(f"| {'STRIKE':<12} | {'CALC':<7} | {'YES BID':<9} | {'YES ASK':<9} | {'NO BID':<8} | {'NO ASK':<8} |")

    for market in markets_sorted:
        outcomes, prices = parse_outcomes_prices(market.get("outcomes", "[]"), market.get("outcomePrices", "[]"))
        strike = extract_price_target(market.get("question", ""))

        if outcomes and prices:
            prob_calc = calcular_prob_above(coin['symbol'], horizonte, strike)
            prob_str = f"{prob_calc:.1f}%" if prob_calc is not None else "N/A"

            if coin['name'] == "XRP":
                strike_str = f"${strike:.2f}"
            else:
                strike_str = f"${int(strike):,}"

            ob = fetch_market_order_book(market)
            if ob:
                yes_bid = f"{ob['yes']['bid']:.3f}" if ob['yes']['bid'] else "N/A"
                yes_ask = f"{ob['yes']['ask']:.3f}" if ob['yes']['ask'] else "N/A"
                no_bid = f"{ob['no']['bid']:.3f}" if ob['no']['bid'] else "N/A"
                no_ask = f"{ob['no']['ask']:.3f}" if ob['no']['ask'] else "N/A"
            else:
                yes_bid = yes_ask = no_bid = no_ask = "N/A"

            print(f"| {strike_str:<12} | {prob_str:>6} | {yes_bid:<9} | {yes_ask:<9} | {no_bid:<8} | {no_ask:<8} |")

    print("+" + "-" * 83 + "+")


def display_price_event(event, coin):
    horizonte = event.get("hours_rounded", 24)
    print("")
    print("=" * 85)
    print(f"{coin['emoji']} {coin['name']} PRICE: {event.get('title')}")
    print(f"Resolucao: {event.get('time_to_resolution')} (calc: {horizonte}h) | https://polymarket.com/event/{event.get('slug')}")
    print("")

    markets = event.get("markets", [])
    if not markets:
        return

    markets_sorted = sorted(markets, key=lambda m: extract_price_range(m.get("question", ""))[0])

    print(f"| {'RANGE':<15} | {'CALC':<7} | {'YES BID':<9} | {'YES ASK':<9} | {'NO BID':<8} | {'NO ASK':<8} |")

    for market in markets_sorted:
        outcomes, prices = parse_outcomes_prices(market.get("outcomes", "[]"), market.get("outcomePrices", "[]"))
        question = market.get("question", "")
        low, high = extract_price_range(question)

        if outcomes and prices:
            prob_calc = calcular_prob_range(coin['symbol'], horizonte, low, high)
            prob_str = f"{prob_calc:.1f}%" if prob_calc is not None else "N/A"

            if coin['name'] == "XRP":
                if "less than" in question.lower():
                    range_str = f"<${high:.2f}"
                elif "greater than" in question.lower():
                    range_str = f">${low:.2f}"
                else:
                    range_str = f"${low:.2f}-{high:.2f}"
            else:
                if "less than" in question.lower():
                    range_str = f"<${int(high):,}"
                elif "greater than" in question.lower():
                    range_str = f">${int(low):,}"
                else:
                    range_str = f"${int(low):,}-{int(high):,}"

            ob = fetch_market_order_book(market)
            if ob:
                yes_bid = f"{ob['yes']['bid']:.3f}" if ob['yes']['bid'] else "N/A"
                yes_ask = f"{ob['yes']['ask']:.3f}" if ob['yes']['ask'] else "N/A"
                no_bid = f"{ob['no']['bid']:.3f}" if ob['no']['bid'] else "N/A"
                no_ask = f"{ob['no']['ask']:.3f}" if ob['no']['ask'] else "N/A"
            else:
                yes_bid = yes_ask = no_bid = no_ask = "N/A"

            print(f"| {range_str:<15} | {prob_str:>6} | {yes_bid:<9} | {yes_ask:<9} | {no_bid:<8} | {no_ask:<8} |")

    print("+" + "-" * 83 + "+")


# ============================================================================
# DATA STORAGE FOR OPERATIONS ANALYSIS
# ============================================================================

DADOS_MERCADOS = {}


def salvar_dados_mercados():
    """Salva todos os dados dos mercados para uso na analise de operacoes"""
    global DADOS_MERCADOS

    for coin in COINS:
        coin_name = coin['name']
        DADOS_MERCADOS[coin_name] = {'above': [], 'price': []}

        # ABOVE
        above_event = fetch_closest_event(coin["slug_above"], coin["pattern_above"])
        if above_event:
            horizonte = above_event.get("hours_rounded", 24)
            for market in above_event.get("markets", []):
                strike = extract_price_target(market.get("question", ""))
                if strike == 0:
                    continue

                prob_calc = calcular_prob_above(coin['symbol'], horizonte, strike)
                ob = fetch_market_order_book(market)

                if coin_name == "XRP":
                    strike_str = f">${strike:.2f}"
                else:
                    strike_str = f">${int(strike):,}"

                DADOS_MERCADOS[coin_name]['above'].append({
                    'strike': strike_str,
                    'calc': prob_calc if prob_calc else 0,
                    'yes_bid': ob['yes']['bid'] if ob and ob['yes']['bid'] else 0,
                    'no_bid': ob['no']['bid'] if ob and ob['no']['bid'] else 0,
                })

        # PRICE (range)
        price_event = fetch_closest_event(coin["slug_price"], coin["pattern_price"])
        if price_event:
            horizonte = price_event.get("hours_rounded", 24)
            for market in price_event.get("markets", []):
                question = market.get("question", "")
                low, high = extract_price_range(question)
                if low == 0 and high == 0:
                    continue

                prob_calc = calcular_prob_range(coin['symbol'], horizonte, low, high)
                ob = fetch_market_order_book(market)

                if coin_name == "XRP":
                    if "less than" in question.lower():
                        strike_str = f"<${high:.2f}"
                    elif "greater than" in question.lower():
                        strike_str = f">${low:.2f}"
                    else:
                        strike_str = f"${low:.2f}-{high:.2f}"
                else:
                    if "less than" in question.lower():
                        strike_str = f"<${int(high):,}"
                    elif "greater than" in question.lower():
                        strike_str = f">${int(low):,}"
                    else:
                        strike_str = f"${int(low):,}-{int(high):,}"

                DADOS_MERCADOS[coin_name]['price'].append({
                    'strike': strike_str,
                    'calc': prob_calc if prob_calc else 0,
                    'yes_bid': ob['yes']['bid'] if ob and ob['yes']['bid'] else 0,
                    'no_bid': ob['no']['bid'] if ob and ob['no']['bid'] else 0,
                })


# ============================================================================
# OPERATIONS ANALYSIS
# ============================================================================

MAX_ENTRY_PRICE = 0.989  # 98.9c
MIN_SUCCESS_PROB = 0.015  # 1.5%
MIN_EDGE_RATIO = 1.5  # premio >= 1.5x prob_perda


def calcular_metricas_op(prob_calc_yes, bid_price, side):
    prob_yes = prob_calc_yes / 100 if prob_calc_yes > 1 else prob_calc_yes
    prob_no = 1 - prob_yes

    if side == "BUY_YES":
        prob_sucesso = prob_yes
        prob_perda = prob_no
    else:  # BUY_NO
        prob_sucesso = prob_no
        prob_perda = prob_yes

    premio = 1 - bid_price
    perda_max = bid_price

    edge_ratio = (premio / prob_perda) if prob_perda > 0 else float('inf')

    ev = (prob_sucesso * premio) - (prob_perda * perda_max)
    ev_pct = ev / bid_price if bid_price > 0 else 0

    return {
        'bid_price': bid_price,
        'premio': premio,
        'perda_max': perda_max,
        'prob_sucesso': prob_sucesso,
        'prob_perda': prob_perda,
        'edge_ratio': edge_ratio,
        'ev': ev,
        'ev_pct': ev_pct
    }


def verificar_qualif(metricas):
    motivos_rejeicao = []

    if metricas['bid_price'] > MAX_ENTRY_PRICE:
        motivos_rejeicao.append(f"BID>{MAX_ENTRY_PRICE*100:.1f}c")

    if metricas['prob_sucesso'] <= MIN_SUCCESS_PROB:
        motivos_rejeicao.append(f"P.SUC<={MIN_SUCCESS_PROB*100:.1f}%")

    if metricas['edge_ratio'] < MIN_EDGE_RATIO:
        motivos_rejeicao.append(f"EDGE={metricas['edge_ratio']:.2f}x<{MIN_EDGE_RATIO}x")

    if motivos_rejeicao:
        return False, "X " + " | ".join(motivos_rejeicao)

    return True, f"OK ACEITA (EV:{metricas['ev_pct']*100:.1f}%)"


def print_tabela_mercado(coin_name, operacoes):
    if not operacoes:
        return

    qualif = [op for op in operacoes if op['qualificada']]
    rejeit = [op for op in operacoes if not op['qualificada']]

    print(f"\n{'='*80}")
    print(f"  {coin_name}")
    print(f"{'='*80}")

    print(f"{'STRIKE':<15} | {'ACAO':<8} | {'BID':>6} | {'P.PERDA':>7} | STATUS")
    print(f"{'-'*15}-+-{'-'*8}-+-{'-'*6}-+-{'-'*7}-+-{'-'*35}")

    for op in qualif + rejeit:
        m = op['metricas']
        print(f"{op['strike']:<15} | {op['acao']:<8} | {m['bid_price']*100:>5.1f}c | {m['prob_perda']*100:>6.2f}% | {op['status']}")

    print(f"{'-'*80}")
    print(f"  OK Qualificadas: {len(qualif)} | X Rejeitadas: {len(rejeit)}")


def analisar_operacoes():
    """Analisa operacoes usando DADOS_MERCADOS"""

    todas_qualificadas = []
    todas_rejeitadas = []

    for coin_name, mercados in DADOS_MERCADOS.items():
        print(f"\nAnalisando {coin_name}...")

        operacoes_mercado = []

        # ABOVE
        for m in mercados.get('above', []):
            strike_str = m['strike']
            prob_calc = m['calc']
            yes_bid = m.get('yes_bid', 0)
            no_bid = m.get('no_bid', 0)

            if prob_calc is None or prob_calc == 0:
                continue

            # BUY YES
            if yes_bid and yes_bid > 0:
                metricas = calcular_metricas_op(prob_calc, yes_bid, "BUY_YES")
                qualificada, status = verificar_qualif(metricas)
                operacoes_mercado.append({
                    'strike': strike_str,
                    'acao': 'BUY YES',
                    'metricas': metricas,
                    'qualificada': qualificada,
                    'status': status
                })
                if qualificada:
                    todas_qualificadas.append((coin_name, operacoes_mercado[-1]))
                else:
                    todas_rejeitadas.append((coin_name, operacoes_mercado[-1]))

            # BUY NO
            if no_bid and no_bid > 0:
                metricas = calcular_metricas_op(prob_calc, no_bid, "BUY_NO")
                qualificada, status = verificar_qualif(metricas)
                operacoes_mercado.append({
                    'strike': strike_str,
                    'acao': 'BUY NO',
                    'metricas': metricas,
                    'qualificada': qualificada,
                    'status': status
                })
                if qualificada:
                    todas_qualificadas.append((coin_name, operacoes_mercado[-1]))
                else:
                    todas_rejeitadas.append((coin_name, operacoes_mercado[-1]))

        # PRICE (range)
        for m in mercados.get('price', []):
            strike_str = m['strike']
            prob_calc = m['calc']
            yes_bid = m.get('yes_bid', 0)
            no_bid = m.get('no_bid', 0)

            if prob_calc is None or prob_calc == 0:
                continue

            # BUY YES
            if yes_bid and yes_bid > 0:
                metricas = calcular_metricas_op(prob_calc, yes_bid, "BUY_YES")
                qualificada, status = verificar_qualif(metricas)
                operacoes_mercado.append({
                    'strike': strike_str,
                    'acao': 'BUY YES',
                    'metricas': metricas,
                    'qualificada': qualificada,
                    'status': status
                })
                if qualificada:
                    todas_qualificadas.append((coin_name, operacoes_mercado[-1]))
                else:
                    todas_rejeitadas.append((coin_name, operacoes_mercado[-1]))

            # BUY NO
            if no_bid and no_bid > 0:
                metricas = calcular_metricas_op(prob_calc, no_bid, "BUY_NO")
                qualificada, status = verificar_qualif(metricas)
                operacoes_mercado.append({
                    'strike': strike_str,
                    'acao': 'BUY NO',
                    'metricas': metricas,
                    'qualificada': qualificada,
                    'status': status
                })
                if qualificada:
                    todas_qualificadas.append((coin_name, operacoes_mercado[-1]))
                else:
                    todas_rejeitadas.append((coin_name, operacoes_mercado[-1]))

        print_tabela_mercado(coin_name, operacoes_mercado)

    # Resumo final
    print(f"\n{'='*80}")
    print(f"  RESUMO GERAL")
    print(f"{'='*80}")
    print(f"  Total analisadas: {len(todas_qualificadas) + len(todas_rejeitadas)}")
    print(f"  OK Qualificadas: {len(todas_qualificadas)}")
    print(f"  X Rejeitadas: {len(todas_rejeitadas)}")

    # Tabela final
    if todas_qualificadas or todas_rejeitadas:
        print(f"\n{'='*100}")
        print(f"  TODAS AS OPERACOES (ordenadas por EV%)")
        print(f"{'='*100}")
        print(f"{'COIN':<10} | {'STRIKE':<15} | {'ACAO':<8} | {'BID':>6} | {'P.PERDA':>7} | STATUS")
        print(f"{'-'*10}-+-{'-'*15}-+-{'-'*8}-+-{'-'*6}-+-{'-'*7}-+-{'-'*40}")

        todas = [(c, op, True) for c, op in todas_qualificadas] + [(c, op, False) for c, op in todas_rejeitadas]
        todas_sorted = sorted(todas, key=lambda x: (-x[2], -x[1]['metricas']['ev_pct']))

        for coin_name, op, _ in todas_sorted:
            m = op['metricas']
            print(f"{coin_name:<10} | {op['strike']:<15} | {op['acao']:<8} | {m['bid_price']*100:>5.1f}c | {m['prob_perda']*100:>6.2f}% | {op['status']}")

    return todas_qualificadas, todas_rejeitadas


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("POLYMARKET - CRYPTO TRACKER + PROB CALCULADA")
    print(f"Data: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("Carregando dados historicos...")

    # Pre-load data
    for coin in COINS:
        buscar_dados_profissional(coin['symbol'])

    for coin in COINS:
        print(f"\n{'='*85}")
        print(f"{coin['emoji']} {coin['name']}")
        print("="*85)

        above_event = fetch_closest_event(coin["slug_above"], coin["pattern_above"])
        if above_event:
            display_above_event(above_event, coin)
        else:
            print(f"\nX Nenhum evento '{coin['name']} above' encontrado")

        price_event = fetch_closest_event(coin["slug_price"], coin["pattern_price"])
        if price_event:
            display_price_event(price_event, coin)
        else:
            print(f"\nX Nenhum evento '{coin['name']} price on' encontrado")

    # Salva dados para analise de operacoes
    salvar_dados_mercados()

    # Analisa operacoes qualificadas
    print("\n\n" + "="*100)
    print("  ANALISE DE OPERACOES QUALIFICADAS")
    print("="*100)
    print("Criterios:")
    print("  1. Edge >= 1.5x (premio >= 1.5x prob_perda)")
    print("  2. Bid <= 98.9c (retorno minimo 1.1%)")
    print("  3. Prob sucesso > 1.5%")

    qualificadas, rejeitadas = analisar_operacoes()


if __name__ == "__main__":
    main()
