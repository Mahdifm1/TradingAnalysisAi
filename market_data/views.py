from rest_framework import generics
from .models import Symbol, Candle
from .serializers import SymbolSerializer, CandleSerializer
from accounts.permissions import IsUserVerified


class SymbolListView(generics.ListAPIView):
    """
    API view to list all active symbols.
    """
    queryset = Symbol.objects.filter(is_active=True)
    serializer_class = SymbolSerializer
    permission_classes = [IsUserVerified]


class CandleListView(generics.ListAPIView):
    """
    API view to list the last 1000 candles for a given symbol.
    """
    serializer_class = CandleSerializer
    permission_classes = [IsUserVerified]

    def get_queryset(self):
        symbol_name = self.kwargs['symbol_name']
        # Fetch the last 1000 candles for the given symbol, ordered by timestamp descending
        return Candle.objects.filter(symbol__name=symbol_name).order_by('-timestamp')[:1000]
