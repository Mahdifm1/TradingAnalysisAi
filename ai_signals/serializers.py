from rest_framework import serializers
from .models import Signal


class SignalSerializer(serializers.ModelSerializer):
    """
    Serializer for the Signal model to represent it in API responses
    and for caching in Redis.
    """
    # To show the candle's timestamp and symbol name in the response
    timestamp = serializers.DateTimeField(source='candle.timestamp', read_only=True)
    symbol = serializers.CharField(source='candle.symbol.name', read_only=True)

    class Meta:
        model = Signal
        fields = [
            'symbol', 'timestamp',
            'direction_next_candle', 'confidence_next_candle',
            'direction_3rd_candle', 'confidence_3rd_candle',
            'direction_5th_candle', 'confidence_5th_candle',
            'direction_10th_candle', 'confidence_10th_candle',
            'probability_text', 'risk_text',
        ]
