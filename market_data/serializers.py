from rest_framework import serializers
from .models import Symbol, Candle


class SymbolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symbol
        fields = ['name', 'is_active']


class CandleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candle
        fields = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
