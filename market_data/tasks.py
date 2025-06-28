from celery import shared_task
from .models import Symbol, Candle
from .services import KucoinClient
from datetime import datetime, timezone

# Define the number of candles to keep per symbol as a constant
CANDLES_TO_KEEP_PER_SYMBOL = 100


@shared_task
def fetch_and_store_candles(symbol_name: str):
    """
    Fetches latest candles, stores new ones, and prunes old ones to a fixed limit.
    """
    client = KucoinClient()
    candles_data = client.get_kline_data(symbol_name, interval='15min')

    if not candles_data:
        return f"No data received from API for {symbol_name}"

    try:
        symbol = Symbol.objects.get(name=symbol_name)
    except Symbol.DoesNotExist:
        return f"Symbol {symbol_name} not found in the database."

    # Bulk insert new candles, ignoring duplicates
    candles_to_create = [
        Candle(
            symbol=symbol,
            timestamp=data['timestamp'].replace(tzinfo=timezone.utc),
            open=data['open'],
            close=data['close'],
            high=data['high'],
            low=data['low'],
            volume=data['volume']
        ) for data in candles_data
    ]
    created_candles = Candle.objects.bulk_create(candles_to_create, ignore_conflicts=True)

    # Prune old candles
    # Get the primary keys of the newest N candles for this symbol
    latest_candle_ids = Candle.objects.filter(symbol=symbol).order_by('-timestamp')[
                        :CANDLES_TO_KEEP_PER_SYMBOL].values_list('id', flat=True)

    # Delete all candles for this symbol that are NOT in the list of the newest ones
    # This is a highly efficient way to prune the dataset.
    Candle.objects.filter(symbol=symbol).exclude(id__in=list(latest_candle_ids)).delete()

    # todo: This logic will be activated when the 'ai_signals' app is ready.
    # if created_candles:
    #     for candle in created_candles:
    #         generate_signal_for_candle.delay(candle.id)

    return f"Processed {symbol_name}. Added {len(created_candles)} new candles. Total candles kept at/below {CANDLES_TO_KEEP_PER_SYMBOL}."


@shared_task
def schedule_all_active_symbols_fetching():
    """
    A periodic task that finds all active symbols and triggers individual fetching tasks
    with a small delay between each to avoid API rate limiting.
    """
    active_symbols = Symbol.objects.filter(is_active=True)
    # Stagger the tasks to prevent a "thundering herd" problem
    for i, symbol in enumerate(active_symbols):
        # The 'countdown' argument adds a delay in seconds before the task executes.
        fetch_and_store_candles.apply_async(args=[symbol.name], countdown=i * 2)  # 2-second delay between each task

    return f"Triggered fetching for {active_symbols.count()} active symbols with staggering."