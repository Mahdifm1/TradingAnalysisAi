from django.urls import path
from .views import SymbolListView, CandleListView

urlpatterns = [
    path('symbols/', SymbolListView.as_view(), name='symbol-list'),
    path('candles/<str:symbol_name>/', CandleListView.as_view(), name='candle-list'),
]
