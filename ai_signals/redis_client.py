from django.core.cache import cache
import json


def cache_latest_signal(symbol_name: str, signal_data: dict):
    key = f"signal:{symbol_name}"
    # Use Django's cache.set with a timeout of 1 day
    cache.set(key, signal_data, timeout=86400)


def get_cached_latest_signal(symbol_name: str):
    key = f"signal:{symbol_name}"
    # Use Django's cache.get
    return cache.get(key)
