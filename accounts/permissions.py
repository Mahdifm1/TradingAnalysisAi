from rest_framework.permissions import BasePermission


class IsUserVerified(BasePermission):
    """
    Custom permission to only allow access to users who have verified their email.
    In our setup, 'dj-rest-auth' sets a user to 'is_active=True' upon email verification.
    """

    message = "Your account is not active. Please verify your email address to proceed."

    def has_permission(self, request, view):
        # Must be authenticated AND have an active account.
        return request.user and request.user.is_authenticated and request.user.is_active
