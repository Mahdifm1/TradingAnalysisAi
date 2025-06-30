import requests
from datetime import datetime
from decimal import Decimal


class KucoinClient:
    """
    A client to interact with the public KuCoin API for market data.
    """
    BASE_URL = "https://api.kucoin.com"

    def get_kline_data(self, symbol: str, interval: str = '15min'):
        """
        Fetches K-line (candle) data for a given symbol.
        Docs: https://docs.kucoin.com/#get-klines
        """
        endpoint = f"/api/v1/market/candles?type={interval}min&symbol={symbol}"

        try:
            response = requests.get(f"{self.BASE_URL}{endpoint}")
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            data = response.json().get('data', [])

            parsed_data = []
            for item in data:
                parsed_data.append({
                    'timestamp': datetime.fromtimestamp(int(item[0])),
                    'open': Decimal(item[1]),
                    'close': Decimal(item[2]),
                    'high': Decimal(item[3]),
                    'low': Decimal(item[4]),
                    'volume': Decimal(item[5]),
                })
            return parsed_data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
