from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- API Documentation ---
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI:
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Redoc UI:
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # --- Authentication & User Management ---
    path('accounts/', include('accounts.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('auth/', include('dj_rest_auth.urls')),

    # --- Market Data Management ---
    path('market/', include('market_data.urls')),

    # --- AI Signals ---
    path('signals/', include('ai_signals.urls')),


]
