from django.http import JsonResponse
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


_backend = JWTAuthentication()


class JwtAuthenticationMiddleware:
    """
    Similar to SessionMiddleware. Obtain a User object
    by info provided in Access token in header
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.exclusions = (
            reverse('account:google_login'),
            reverse('account:logout'),
            reverse('account:refresh'),
            reverse('account:session_login'),
            reverse('account:registration'),
        )

    def __call__(self, request):
        auth_result = None

        if request.path not in self.exclusions:
            try:
                auth_result = _backend.authenticate(request)

            except InvalidToken as exc:
                data = {'detail': 'Token is invalid or expired', 'code': 'token_not_valid'}
                return JsonResponse(data, status=status.HTTP_401_UNAUTHORIZED)

            except APIException as exc:
                detail, code = 'A server error occurred.', 'error'
                if det := getattr(exc, 'detail', {}) or getattr(exc, 'default_detail', {}):
                    detail, code = det.get('detail'), det.get('code')
                return JsonResponse({'detail': detail, 'code': code},
                                    status=status.HTTP_401_UNAUTHORIZED)

            if auth_result:
                request.user = request._cached_user = auth_result[0]

        response = self.get_response(request)
        return response
