from celery import shared_task
from market_data.models import Candle
from .models import Signal
from .services import LiaraAIService
from .serializers import SignalSerializer
from .redis_client import cache_latest_signal
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_signal_for_candle(self, candle_id: int):
    """
    A robust task that calls the AI, parses the new multi-timeframe response,
    and saves it to the updated Signal model.
    """
    try:
        candle = Candle.objects.select_related('symbol').get(id=candle_id)
        if Signal.objects.filter(candle=candle).exists():
            return f"Signal already exists for {candle}. Skipping."

        # Fetching data logic remains the same
        candles_for_ai = Candle.objects.filter(
            symbol=candle.symbol, timestamp__lte=candle.timestamp
        ).order_by('-timestamp')[:100]
        if len(candles_for_ai) < 100:
            return f"Not enough historical data for {candle.symbol.name}."
        candle_data_list = list(candles_for_ai.values('open', 'high', 'low', 'close', 'volume', 'timestamp'))

        ai_service = LiaraAIService()
        signal_data = ai_service.generate_signal_from_candles(candle_data_list)

        if not signal_data:
            logger.error(f"AI service failed to generate a signal for {candle}.")
            raise self.retry()

        # --- This is the new, robust parsing logic ---
        # It safely extracts data from the nested JSON response.
        next_candle_data = signal_data.get('next_candle', {})
        third_candle_data = signal_data.get('third_candle', {})
        fifth_candle_data = signal_data.get('fifth_candle', {})
        tenth_candle_data = signal_data.get('tenth_candle', {})

        final_signal_data = {
            'direction_next_candle': next_candle_data.get('direction'),
            'confidence_next_candle': next_candle_data.get('confidence'),

            'direction_3rd_candle': third_candle_data.get('direction'),
            'confidence_3rd_candle': third_candle_data.get('confidence'),

            'direction_5th_candle': fifth_candle_data.get('direction'),
            'confidence_5th_candle': fifth_candle_data.get('confidence'),

            'direction_10th_candle': tenth_candle_data.get('direction'),
            'confidence_10th_candle': tenth_candle_data.get('confidence'),

            'probability_text': signal_data.get('probability_text'),
            'risk_text': signal_data.get('risk_text'),
        }

        # Validate that we have all the necessary data before creating the object
        if not all(final_signal_data.values()):
            logger.error(f"Incomplete data received from AI for {candle}: {signal_data}")
            return f"Incomplete data from AI for {candle}."

        new_signal = Signal.objects.create(candle=candle, **final_signal_data)

        # Caching logic remains the same
        serializer = SignalSerializer(instance=new_signal)
        cache_latest_signal(symbol_name=candle.symbol.name, signal_data=serializer.data)

        logger.info(f"Successfully generated multi-timeframe signal for {candle}.")
        return f"Successfully generated multi-timeframe signal for {candle}."

    except Candle.DoesNotExist:
        logger.error(f"Candle with id={candle_id} not found.")
    except Exception as exc:
        logger.error(f"An unexpected error occurred for candle_id {candle_id}: {exc}")
        raise self.retry(exc=exc)
