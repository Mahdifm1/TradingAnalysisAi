from django.urls import path
from .views import CustomVerifyEmailView

urlpatterns = [
    path('registration/account-confirm-email/<str:key>', CustomVerifyEmailView.as_view(), name='account_confirm_email'),
]