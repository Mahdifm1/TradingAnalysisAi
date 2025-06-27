from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny


class CustomVerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, key, *args, **kwargs):
        try:
            confirmation = EmailConfirmationHMAC.from_key(key)
            if confirmation:
                confirmation.confirm(self.request)
                return Response({'detail': 'Email confirmed successfully.'}, status=200)
            else:
                return Response({'detail': 'Error. Invalid or expired confirmation link.'}, status=404)
        except Exception as e:
            return Response({'detail': f'An error occurred, please try again'}, status=500)
