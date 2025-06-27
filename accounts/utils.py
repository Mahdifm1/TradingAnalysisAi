from django.utils.http import urlencode


def custom_password_reset_url_generator(request, user, temp_key):
    """
    Generates a password reset URL pointing back to the backend.
    This version manually constructs the URL to avoid NoReverseMatch errors.
    """
    # Manually define the path to the password reset confirm view
    # This path corresponds to what's defined in dj_rest_auth.urls
    path = "/auth/password/reset/confirm/"

    # Create the query string with uid and token
    # dj-rest-auth automatically handles the base64 encoding for user.pk
    query_params = urlencode({'uid': user.pk, 'token': temp_key})

    # Build the full, absolute URL using the request's domain
    # e.g., http://127.0.0.1:8000/api/auth/password/reset/confirm/?uid=...&token=...
    reset_url = f'{request.build_absolute_uri(path)}?{query_params}'

    return reset_url
