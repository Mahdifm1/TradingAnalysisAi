from django.test import TestCase
from django.core.cache import cache  # 1. Import Django's cache framework
from unittest.mock import patch, MagicMock
from rest_framework.test import APIClient
from rest_framework import status
from market_data.models import Symbol, Candle
from .models import Signal
from .tasks import generate_signal_for_candle
from datetime import datetime, timezone, timedelta
import json

# Sample response simulating a successful AI API call
MOCK_AI_RESPONSE = {
    "direction_next": "BULLISH", "confidence_next": 75.5,
    "direction_medium": "BEARISH", "confidence_medium": 60.0,
    "probability_text": "Mock probability text.",
    "risk_text": "Mock risk text."
}


class ComprehensiveAISignalsTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.symbol = Symbol.objects.create(name='TEST-USDT', is_active=True)
        self.candle = Candle.objects.create(
            symbol=self.symbol,
            timestamp=datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
            open=100, high=110, low=95, close=105, volume=1000
        )
        # 2. Clear the entire cache before each test to ensure isolation
        cache.clear()

    @patch('ai_signals.services.LiaraAIService.generate_signal_from_candles')
    def test_generate_signal_task_success(self, mock_generate_signal):
        """Test the successful execution of the signal generation task."""
        mock_generate_signal.return_value = MOCK_AI_RESPONSE

        # Create 99 older candles to meet the 100-candle requirement
        for i in range(1, 100):
            Candle.objects.create(
                symbol=self.symbol,
                timestamp=self.candle.timestamp - timedelta(minutes=i * 15),
                open=1, high=1, low=1, close=1, volume=1
            )

        # Execute the task directly
        generate_signal_for_candle(self.candle.id)

        # 1. Assert Signal was created in PostgreSQL
        self.assertEqual(Signal.objects.count(), 1)
        signal = Signal.objects.first()
        self.assertEqual(signal.candle, self.candle)
        self.assertEqual(signal.risk_text, "Mock risk text.")

        # 2. Assert Signal was cached in Redis using Django's cache
        cache_key = f"signal:{self.symbol.name}"
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data['risk_text'], "Mock risk text.")

    @patch('ai_signals.tasks.generate_signal_for_candle.retry')
    @patch('ai_signals.services.LiaraAIService.generate_signal_from_candles')
    def test_task_failure_and_retry(self, mock_generate_signal, mock_retry):
        """Test that the task retries if the AI service fails."""
        mock_generate_signal.return_value = None
        mock_retry.side_effect = Exception("Celery Retry")

        with self.assertRaises(Exception, msg="Celery Retry"):
            generate_signal_for_candle(self.candle.id)

        mock_retry.assert_called_once()

    def test_latest_signal_api_cache_miss_and_hit(self):
        """Test the cache-aside logic of the LatestSignalView."""
        url = f'/api/signals/latest/{self.symbol.name}/'

        # --- Cache Miss ---
        response_miss = self.client.get(url)
        self.assertEqual(response_miss.status_code, status.HTTP_404_NOT_FOUND)

        # Create a signal in the database
        Signal.objects.create(
            candle=self.candle,
            direction_next_candle='BULLISH', confidence_next_candle=80,
            direction_3rd_candle='BULLISH', confidence_3rd_candle=80,
            direction_5th_candle='BULLISH', confidence_5th_candle=80,
            direction_10th_candle='BULLISH', confidence_10th_candle=80,
            probability_text='Test', risk_text='Test'
        )

        # First request should be a cache miss, but it should populate the cache
        response_first = self.client.get(url)
        self.assertEqual(response_first.status_code, status.HTTP_200_OK)

        # Verify that the cache is now populated
        self.assertIsNotNone(cache.get(f"signal:{self.symbol.name}"))

        # --- Cache Hit ---
        # Modify the DB object to ensure the next response comes from the cache
        Signal.objects.update(probability_text="CHANGED IN DB")

        response_hit = self.client.get(url)
        self.assertEqual(response_hit.status_code, status.HTTP_200_OK)
        # The text should be the OLD text from the cache
        self.assertEqual(response_hit.data['probability_text'], 'Test')
