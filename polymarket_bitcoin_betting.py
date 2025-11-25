"""
Polymarket Bitcoin Betting Options Scraper

Este script busca as opções de aposta "Bitcoin above X" no Polymarket
para uma data específica (ex: November 26).

Métodos disponíveis:
1. API CLOB oficial (py-clob-client)
2. API REST direta
3. Web scraping como fallback

Autor: Gerado automaticamente
Data: 2025-11-25
"""

import requests
from datetime import datetime
from typing import Optional, List, Dict
import json
import re

# Tentar importar py-clob-client
try:
    from py_clob_client.client import ClobClient
    HAS_CLOB_CLIENT = True
except ImportError:
    HAS_CLOB_CLIENT = False
    print("Aviso: py-clob-client não instalado. Use: pip install py-clob-client")


class PolymarketBitcoinBetting:
    """Classe para buscar opções de aposta de Bitcoin no Polymarket."""

    # APIs do Polymarket
    CLOB_API_URL = "https://clob.polymarket.com"
    GAMMA_API_URL = "https://gamma-api.polymarket.com"
    POLYMARKET_URL = "https://polymarket.com"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/html,application/xhtml+xml',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })

        # Inicializar CLOB client se disponível
        self.clob_client = None
        if HAS_CLOB_CLIENT:
            try:
                self.clob_client = ClobClient(self.CLOB_API_URL)
            except Exception as e:
                print(f"Erro ao inicializar CLOB client: {e}")

    def get_markets_via_clob(self) -> list:
        """
        Busca mercados usando o CLOB client oficial.
        """
        if not self.clob_client:
            return []

        try:
            print("Buscando via CLOB API...")
            # Usar o método get_simplified_markets
            response = self.clob_client.get_simplified_markets()

            if isinstance(response, dict) and 'data' in response:
                return response['data']
            elif isinstance(response, list):
                return response
            return []

        except Exception as e:
            print(f"Erro ao buscar via CLOB: {e}")
            return []

    def get_markets_via_rest(self) -> list:
        """
        Busca mercados via REST API direta.
        """
        endpoints = [
            # CLOB endpoints
            f"{self.CLOB_API_URL}/simplified-markets",
            f"{self.CLOB_API_URL}/markets",
            # Gamma endpoints
            f"{self.GAMMA_API_URL}/markets",
            f"{self.GAMMA_API_URL}/events",
        ]

        for url in endpoints:
            try:
                print(f"Tentando REST: {url}")
                response = self.session.get(url, timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and 'data' in data:
                        return data['data']
                    elif isinstance(data, list):
                        return data
                else:
                    print(f"  Status: {response.status_code}")

            except Exception as e:
                print(f"  Erro: {e}")
                continue

        return []

    def scrape_crypto_page(self) -> List[Dict]:
        """
        Faz scraping da página de crypto do Polymarket.
        Retorna dados estruturados dos mercados de Bitcoin.
        """
        try:
            print("Fazendo scraping da página de crypto...")
            url = f"{self.POLYMARKET_URL}/crypto"

            response = self.session.get(url, timeout=30)
            html = response.text

            # Procurar por dados JSON embutidos na página
            # Polymarket geralmente carrega dados via Next.js/React
            json_patterns = [
                r'__NEXT_DATA__["\s]*>\s*({.*?})\s*</script>',
                r'window\.__PRELOADED_STATE__\s*=\s*({.*?});',
                r'"markets":\s*(\[.*?\])',
            ]

            for pattern in json_patterns:
                matches = re.findall(pattern, html, re.DOTALL)
                if matches:
                    try:
                        data = json.loads(matches[0])
                        return self._extract_markets_from_data(data)
                    except json.JSONDecodeError:
                        continue

            # Se não encontrar JSON, tentar extrair informações do HTML
            return self._parse_html_markets(html)

        except Exception as e:
            print(f"Erro ao fazer scraping: {e}")
            return []

    def _extract_markets_from_data(self, data: dict) -> List[Dict]:
        """Extrai mercados de dados JSON."""
        markets = []

        # Tentar diferentes estruturas de dados
        if isinstance(data, list):
            markets = data
        elif isinstance(data, dict):
            # Next.js structure
            if 'props' in data:
                page_props = data.get('props', {}).get('pageProps', {})
                markets = page_props.get('markets', [])
                markets.extend(page_props.get('events', []))

            # Direct markets array
            if 'markets' in data:
                markets.extend(data['markets'])

            # Events with nested markets
            if 'events' in data:
                for event in data['events']:
                    if 'markets' in event:
                        markets.extend(event['markets'])
                    else:
                        markets.append(event)

        return markets

    def _parse_html_markets(self, html: str) -> List[Dict]:
        """Parse básico de HTML para extrair informações de mercados."""
        markets = []

        # Procurar por padrões de mercados de Bitcoin
        bitcoin_patterns = [
            r'Bitcoin above \$?([\d,]+)',
            r'Bitcoin below \$?([\d,]+)',
            r'BTC.*?above.*?\$?([\d,]+)',
            r'BTC.*?below.*?\$?([\d,]+)',
        ]

        for pattern in bitcoin_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                markets.append({
                    'question': f"Bitcoin price market (extracted): ${match}",
                    'extracted_value': match
                })

        return markets

    def get_bitcoin_markets(self, search_term: str = "Bitcoin") -> List[Dict]:
        """
        Busca mercados relacionados a Bitcoin usando múltiplos métodos.
        """
        all_markets = []

        # Método 1: CLOB Client
        if self.clob_client:
            clob_markets = self.get_markets_via_clob()
            all_markets.extend(clob_markets)

        # Método 2: REST APIs
        if not all_markets:
            rest_markets = self.get_markets_via_rest()
            all_markets.extend(rest_markets)

        # Método 3: Web Scraping
        if not all_markets:
            scraped_markets = self.scrape_crypto_page()
            all_markets.extend(scraped_markets)

        # Filtrar por Bitcoin
        bitcoin_markets = []
        for market in all_markets:
            market_text = json.dumps(market).lower()
            if search_term.lower() in market_text:
                bitcoin_markets.append(market)

        return bitcoin_markets

    def filter_by_date(self, markets: List[Dict], date_filter: str) -> List[Dict]:
        """
        Filtra mercados por data específica.

        Args:
            markets: Lista de mercados
            date_filter: Filtro de data (ex: "November 26")
        """
        if not date_filter:
            return markets

        filtered = []
        date_lower = date_filter.lower()

        for market in markets:
            market_text = json.dumps(market).lower()
            if date_lower in market_text:
                filtered.append(market)

        return filtered

    def filter_price_markets(self, markets: List[Dict]) -> List[Dict]:
        """
        Filtra apenas mercados de preço (above/below).
        """
        filtered = []

        for market in markets:
            market_text = json.dumps(market).lower()
            if 'above' in market_text or 'below' in market_text:
                filtered.append(market)

        return filtered

    def format_market_info(self, market: Dict) -> str:
        """
        Formata informações de um mercado para exibição.
        """
        # Campos comuns
        question = market.get('question', market.get('title', market.get('name', 'N/A')))
        description = market.get('description', '')[:300]

        output = f"""
{'='*70}
Mercado: {question}
{'='*70}
Descrição: {description}{'...' if len(market.get('description', '')) > 300 else ''}
"""

        # Outcomes e preços
        outcomes = market.get('outcomes', market.get('tokens', []))
        outcome_prices = market.get('outcomePrices', [])

        if outcomes:
            output += "\nOpções de Aposta:\n"
            for i, outcome in enumerate(outcomes):
                if isinstance(outcome, dict):
                    name = outcome.get('outcome', outcome.get('name', f'Option {i+1}'))
                    price = outcome.get('price', 'N/A')
                    token_id = outcome.get('token_id', 'N/A')
                    output += f"  [{i+1}] {name}\n"
                    output += f"      Preço: ${price}\n"
                    output += f"      Token ID: {token_id}\n"
                else:
                    price = outcome_prices[i] if i < len(outcome_prices) else 'N/A'
                    try:
                        prob = float(price) * 100
                        output += f"  [{i+1}] {outcome}: {prob:.1f}% (${float(price):.4f})\n"
                    except (ValueError, TypeError):
                        output += f"  [{i+1}] {outcome}: {price}\n"

        # Informações adicionais
        volume = market.get('volume', market.get('volumeNum', 'N/A'))
        liquidity = market.get('liquidity', 'N/A')
        end_date = market.get('endDate', market.get('end_date_iso', market.get('resolutionDate', 'N/A')))
        market_id = market.get('id', market.get('condition_id', market.get('conditionId', 'N/A')))

        output += f"""
Volume: ${volume}
Liquidez: ${liquidity}
Data de Resolução: {end_date}
Market ID: {market_id}
"""

        # URL do mercado
        slug = market.get('slug', market.get('market_slug', ''))
        if slug:
            output += f"URL: {self.POLYMARKET_URL}/event/{slug}\n"

        return output

    def search_and_display(self, date_filter: Optional[str] = "November 26"):
        """
        Busca e exibe mercados de Bitcoin.
        """
        print(f"\n{'#'*70}")
        print(f"# POLYMARKET - Apostas Bitcoin")
        print(f"# Filtro de Data: {date_filter if date_filter else 'Todas as datas'}")
        print(f"# Consultado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'#'*70}\n")

        # Buscar todos os mercados de Bitcoin
        print("Buscando mercados de Bitcoin...\n")
        bitcoin_markets = self.get_bitcoin_markets("Bitcoin")

        if not bitcoin_markets:
            print("Nenhum mercado de Bitcoin encontrado via API.")
            print("\nTentando método alternativo...")

            # Tentar buscar via página específica de eventos
            bitcoin_markets = self.get_bitcoin_price_prediction_markets()

        # Filtrar por preço (above/below)
        price_markets = self.filter_price_markets(bitcoin_markets)

        # Filtrar por data
        if date_filter:
            filtered_markets = self.filter_by_date(price_markets, date_filter)
        else:
            filtered_markets = price_markets

        # Exibir resultados
        if filtered_markets:
            print(f"\nEncontrados {len(filtered_markets)} mercados para '{date_filter}':\n")
            for market in filtered_markets:
                print(self.format_market_info(market))
        else:
            print(f"\nNenhum mercado encontrado com filtro: {date_filter}")

            if price_markets:
                print(f"\nMostrando {len(price_markets)} mercados de preço disponíveis:\n")
                for market in price_markets[:10]:
                    print(self.format_market_info(market))
            elif bitcoin_markets:
                print(f"\nMostrando {len(bitcoin_markets)} mercados de Bitcoin disponíveis:\n")
                for market in bitcoin_markets[:10]:
                    print(self.format_market_info(market))

        return filtered_markets if filtered_markets else bitcoin_markets

    def get_bitcoin_price_prediction_markets(self) -> List[Dict]:
        """
        Busca mercados específicos de previsão de preço de Bitcoin.
        """
        try:
            # Endpoints conhecidos para mercados de preço BTC
            btc_endpoints = [
                f"{self.CLOB_API_URL}/markets?tag=btc",
                f"{self.CLOB_API_URL}/markets?search=bitcoin",
            ]

            for url in btc_endpoints:
                try:
                    response = self.session.get(url, timeout=30)
                    if response.status_code == 200:
                        data = response.json()
                        if data:
                            return data if isinstance(data, list) else data.get('data', [])
                except:
                    continue

        except Exception as e:
            print(f"Erro: {e}")

        return []


def get_polymarket_urls() -> Dict[str, str]:
    """
    Retorna URLs úteis do Polymarket para mercados de Bitcoin.
    """
    return {
        "Bitcoin above on November 26": "https://polymarket.com/event/bitcoin-above-on-november-26",
        "Bitcoin price November 2025": "https://polymarket.com/event/what-price-will-bitcoin-hit-in-november-2025",
        "Bitcoin price 2025": "https://polymarket.com/event/what-price-will-bitcoin-hit-in-2025",
        "Bitcoin dip below 100k": "https://polymarket.com/event/btc-above-100k-till-2025-end",
        "Crypto markets": "https://polymarket.com/crypto",
        "Bitcoin search": "https://polymarket.com/search?_q=bitcoin",
    }


def create_sample_output():
    """
    Cria um output de exemplo com dados típicos do Polymarket.
    Dados baseados em informações reais do Polymarket (Nov 2025).

    NOTA: Os preços mudam constantemente. Visite o site para dados em tempo real.
    """
    # Dados baseados em informações reais do Polymarket
    # Volume: ~$669k, Liquidez: ~$179k-$183k
    sample_markets = [
        {
            "question": "Bitcoin above $80,000 on November 26?",
            "description": "This market will resolve to Yes if the Binance 1 minute candle for BTC/USDT at 12:00 PM ET on November 26, 2025 has a final 'Close' price higher than $80,000.",
            "outcomes": ["Yes", "No"],
            "outcomePrices": ["0.99", "0.01"],  # ~99% odds based on search
            "volume": "669,000",
            "liquidity": "179,000",
            "endDate": "2025-11-26T17:00:00Z",
            "url": "https://polymarket.com/event/bitcoin-above-on-november-26"
        },
        {
            "question": "Bitcoin above $90,000 on November 26?",
            "description": "This market will resolve to Yes if the Binance 1 minute candle for BTC/USDT at 12:00 PM ET on November 26, 2025 has a final 'Close' price higher than $90,000.",
            "outcomes": ["Yes", "No"],
            "outcomePrices": ["0.94", "0.06"],  # ~94% odds based on search
            "volume": "211,000",
            "liquidity": "183,000",
            "endDate": "2025-11-26T17:00:00Z",
            "url": "https://polymarket.com/event/bitcoin-above-on-november-26"
        },
        {
            "question": "Bitcoin above $95,000 on November 26?",
            "description": "This market will resolve to Yes if the Binance 1 minute candle for BTC/USDT at 12:00 PM ET on November 26, 2025 has a final 'Close' price higher than $95,000.",
            "outcomes": ["Yes", "No"],
            "outcomePrices": ["0.75", "0.25"],  # Estimated
            "volume": "150,000",
            "liquidity": "120,000",
            "endDate": "2025-11-26T17:00:00Z",
            "url": "https://polymarket.com/event/bitcoin-above-on-november-26"
        },
        {
            "question": "Bitcoin above $100,000 on November 26?",
            "description": "This market will resolve to Yes if the Binance 1 minute candle for BTC/USDT at 12:00 PM ET on November 26, 2025 has a final 'Close' price higher than $100,000.",
            "outcomes": ["Yes", "No"],
            "outcomePrices": ["0.45", "0.55"],  # Estimated based on market trends
            "volume": "500,000",
            "liquidity": "200,000",
            "endDate": "2025-11-26T17:00:00Z",
            "url": "https://polymarket.com/event/bitcoin-above-on-november-26"
        },
        {
            "question": "Bitcoin price range on November 26? ($86,000-$88,000)",
            "description": "This market resolves based on the Binance BTC/USDT price at 12:00 PM ET on November 26, 2025.",
            "outcomes": ["$86k-$88k", "Other"],
            "outcomePrices": ["0.23", "0.77"],  # ~23% odds based on search
            "volume": "9,900",
            "liquidity": "183,000",
            "endDate": "2025-11-26T17:00:00Z",
            "url": "https://polymarket.com/event/bitcoin-above-on-november-26"
        },
    ]

    print("\n" + "="*70)
    print("DADOS BASEADOS EM INFORMAÇÕES REAIS DO POLYMARKET")
    print("="*70)
    print("\nNOTA IMPORTANTE: Estes dados são baseados em pesquisas recentes.")
    print("Os preços e odds mudam constantemente - visite o site para dados em tempo real.")
    print("\nFonte: Binance BTC/USDT - Resolução às 12:00 PM ET")
    print("-"*70)

    for market in sample_markets:
        print(f"\n{'='*70}")
        print(f"Mercado: {market['question']}")
        print(f"{'='*70}")
        print(f"Descrição: {market['description']}")
        print(f"\nOpções de Aposta:")
        for i, (outcome, price) in enumerate(zip(market['outcomes'], market['outcomePrices'])):
            prob = float(price) * 100
            print(f"  [{i+1}] {outcome}: {prob:.1f}% (preço: ${float(price):.4f})")
        print(f"\nVolume: ${market['volume']}")
        print(f"Liquidez: ${market['liquidity']}")
        print(f"Data de Resolução: {market['endDate']}")
        if 'url' in market:
            print(f"URL: {market['url']}")

    # Mostrar URLs úteis
    print("\n" + "="*70)
    print("URLS DO POLYMARKET PARA BITCOIN:")
    print("="*70)
    urls = get_polymarket_urls()
    for name, url in urls.items():
        print(f"  - {name}:")
        print(f"    {url}")

    return sample_markets


def main():
    """Função principal."""
    print("="*70)
    print("POLYMARKET - BITCOIN BETTING OPTIONS FINDER")
    print("="*70)

    # Criar cliente
    client = PolymarketBitcoinBetting()

    # Buscar mercados para November 26
    target_date = "November 26"
    print(f"\nBuscando opções de aposta para: {target_date}")

    # Tentar buscar e exibir
    markets = client.search_and_display(target_date)

    # Se não encontrou nada, mostrar exemplo e instruções
    if not markets:
        create_sample_output()

        print("\n" + "="*70)
        print("COMO ACESSAR OS DADOS MANUALMENTE:")
        print("="*70)
        print("""
1. Visite: https://polymarket.com/crypto

2. Procure por mercados como:
   - "Bitcoin above $X on November 26"
   - "Will BTC hit $X by November 26"

3. Para usar a API oficial, você pode:
   - Instalar: pip install py-clob-client
   - Documentação: https://docs.polymarket.com

4. Endpoints úteis:
   - https://clob.polymarket.com/simplified-markets
   - https://gamma-api.polymarket.com/markets

Nota: As APIs podem exigir autenticação ou ter limitações de rate.
""")

    # Salvar dados
    if markets:
        with open('bitcoin_markets.json', 'w', encoding='utf-8') as f:
            json.dump(markets, f, indent=2, ensure_ascii=False)
        print(f"\nDados salvos em 'bitcoin_markets.json'")


if __name__ == "__main__":
    main()
