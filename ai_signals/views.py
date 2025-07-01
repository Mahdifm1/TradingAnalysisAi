from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Signal
from .serializers import SignalSerializer
from .redis_client import get_cached_latest_signal, cache_latest_signal
from market_data.models import Symbol
from accounts.permissions import IsUserVerified


class LatestSignalView(APIView):
    """
    Provides the latest AI-generated signal for a given symbol.
    Implements the Cache-Aside pattern for high performance.
    """
    permission_classes = [IsUserVerified]

    def get(self, request, symbol_name, format=None):
        print(Symbol.objects.values_list('name', flat=True))
        if symbol_name not in Symbol.objects.values_list('name', flat=True):
            Response({'error': 'No symbol found'}, status=status.HTTP_404_NOT_FOUND)

        # Step 1: Try to get the signal from the cache (Redis)
        cached_signal = get_cached_latest_signal(symbol_name)
        if cached_signal:
            return Response(cached_signal, status=status.HTTP_200_OK)

        # Step 2: If not in cache (Cache Miss), fetch from the database
        try:
            # Find the latest signal for the given symbol from PostgreSQL
            latest_signal = Signal.objects.filter(candle__symbol__name=symbol_name).latest('candle__timestamp')
        except Signal.DoesNotExist:
            return Response({'error': 'No signal found for this symbol.'}, status=status.HTTP_404_NOT_FOUND)

        # Step 3: Serialize the data and cache it for future requests
        serializer = SignalSerializer(instance=latest_signal)
        cache_latest_signal(symbol_name=symbol_name, signal_data=serializer.data)

        return Response(serializer.data, status=status.HTTP_200_OK)
