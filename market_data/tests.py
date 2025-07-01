from dj_rest_auth.tests.mixins import APIClient
from django.test import TestCase
from unittest.mock import patch, MagicMock

from rest_framework import status

from .models import Symbol, Candle
from .tasks import fetch_and_store_candles, schedule_all_active_symbols_fetching, CANDLES_TO_KEEP_PER_SYMBOL
from .services import KucoinClient
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import requests

# This is sample data that our Mock API will return
MOCK_API_RESPONSE = [
    {'timestamp': datetime(2025, 1, 1, 10, 15, 0), 'open': '100', 'close': '105', 'high': '110', 'low': '95',
     'volume': '1000'},
    {'timestamp': datetime(2025, 1, 1, 10, 0, 0), 'open': '90', 'close': '100', 'high': '102', 'low': '88',
     'volume': '800'},
]


class ComprehensiveMarketDataTests(TestCase):

    def setUp(self):
        self.symbol_active = Symbol.objects.create(name='BTC-USDT', is_active=True)
        self.symbol_inactive = Symbol.objects.create(name='ETH-USDT', is_active=False)
        self.client = APIClient()

    # --- Service Layer Tests (KucoinClient) ---

    @patch('market_data.services.requests.get')
    def test_kucoin_client_success(self, mock_get):
        """Test the KucoinClient handles a successful API response."""
        # Configure the mock to return a successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [["1529596800", "9710", "9700.9", "9719.9", "9700", "2.422", "23507.491"]]
        }
        mock_get.return_value = mock_response

        client = KucoinClient()
        data = client.get_kline_data('BTC-USDT')
        self.assertIsNotNone(data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['open'], Decimal('9710'))

    @patch('market_data.services.requests.get')
    def test_kucoin_client_api_error(self, mock_get):
        """Test the KucoinClient handles an API error (e.g., 404)."""
        mock_get.side_effect = requests.exceptions.HTTPError("404 Not Found")
        client = KucoinClient()
        data = client.get_kline_data('INVALID-SYMBOL')
        self.assertIsNone(data)

    # --- Task Logic Tests (Celery Tasks) ---

    @patch('market_data.tasks.KucoinClient')
    def test_task_full_logic_with_pruning(self, MockKucoinClient):
        """A comprehensive test for the main task's logic: fetch, store, and prune."""
        # Configure the mock client instance
        mock_client_instance = MockKucoinClient.return_value
        mock_client_instance.get_kline_data.return_value = MOCK_API_RESPONSE

        # --- Part 1: Initial fetch ---
        fetch_and_store_candles(self.symbol_active.name)
        self.assertEqual(Candle.objects.count(), 2)

        # --- Part 2: Running again should not create duplicates ---
        fetch_and_store_candles(self.symbol_active.name)
        self.assertEqual(Candle.objects.count(), 2)  # Count should remain the same

        # --- Part 3: Test pruning logic ---
        # Create more candles than the limit
        for i in range(CANDLES_TO_KEEP_PER_SYMBOL):
            Candle.objects.create(
                symbol=self.symbol_active,
                timestamp=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc).replace(microsecond=i),
                open=1, high=1, low=1, close=1, volume=1
            )
        # Total candles = 2 + 300 = 302
        self.assertEqual(Candle.objects.count(), CANDLES_TO_KEEP_PER_SYMBOL + 2)

        # Run the task again. It should add no new candles but prune 2 old ones.
        fetch_and_store_candles(self.symbol_active.name)
        self.assertEqual(Candle.objects.filter(symbol=self.symbol_active).count(), CANDLES_TO_KEEP_PER_SYMBOL)

    @patch('market_data.tasks.fetch_and_store_candles.apply_async')
    def test_scheduler_task(self, mock_apply_async):
        """Test that the scheduler task correctly triggers jobs for active symbols only."""
        schedule_all_active_symbols_fetching()

        # Assert that the task was called only once (for the active symbol)
        mock_apply_async.assert_called_once()
        # Assert it was called with the correct symbol name
        self.assertEqual(mock_apply_async.call_args.kwargs['args'][0], self.symbol_active.name)

    # --- API View Tests ---

    def test_candle_list_view(self):
        """Test the API endpoint for retrieving candle data."""
        # Create some data for the API to return
        start_time = datetime(2025, 6, 26, 10, 0, 0, tzinfo=timezone.utc)
        for i in range(5):
            # FIX: Use timedelta to correctly increment the time.
            candle_time = start_time + timedelta(minutes=i * 15)
            Candle.objects.create(
                symbol=self.symbol_active,
                timestamp=candle_time,
                open=100 + i, high=110 + i, low=95 + i, close=105 + i, volume=1000
            )

        url = f'/market/candles/{self.symbol_active.name}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
        # Check that the data is ordered by most recent first
        self.assertEqual(Decimal(response.data[0]['open']), Decimal('104'))
        self.assertEqual(Decimal(response.data[4]['open']), Decimal('100'))

    def test_candle_list_view_for_nonexistent_symbol(self):
        """Test the candle list view for a symbol that does not exist."""
        url = '/market/candles/NON-EXISTENT/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # Should return an empty list
