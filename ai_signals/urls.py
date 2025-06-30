from django.urls import path
from .views import LatestSignalView

urlpatterns = [
    path('latest/<str:symbol_name>/', LatestSignalView.as_view(), name='latest-signal'),
]