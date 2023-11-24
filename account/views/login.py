import logging
from datetime import timedelta
from django.core.cache import cache
from django.conf import settings
from django.contrib import auth, messages
from django.utils import timezone
from rest_framework import status, exceptions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.settings import api_settings as jwt_settings
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from account.authentication import get_jwtokens, set_jwt_cookies, model_backend_login
from account.serializers import JwtLoginSerializer, JwtRefreshSerializer, LoginSerializer
from common.utils import get_msg_json


logger = logging.getLogger(__name__)


class SessionLoginView(APIView):
    """
    Login a user by setting Session ID to cookies
    """
    serializer_class = LoginSerializer
    queryset = ''

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, 'Already authenticated')
            data = {'server_messages': get_msg_json(request)}
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            messages.error(request, 'Incorrent login data')
            data = {'errors': serializer.errors, 'server_messages': get_msg_json(request)}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if user := auth.authenticate(request, email=serializer.data['email'],
                                              password=serializer.data['password']):
            model_backend_login(request, user)
            messages.success(request, 'You are successfully logged in')
            data = {'server_messages': get_msg_json(request)}
            return Response(data, status=status.HTTP_200_OK)

        messages.error(request, 'Incorrent email or password')
        data = {'server_messages': get_msg_json(request)}
        return Response(data, status=status.HTTP_401_UNAUTHORIZED)


class JwtLoginView(TokenObtainPairView):
    """
    Login a user by setting Refresh JWT token to cookie,
    and returning an Access JWT token
    """
    serializer_class = JwtLoginSerializer

    def post(self, request, *args, **kwargs):
        try:
            tokens = super().post(request, *args, **kwargs).data
        except exceptions.AuthenticationFailed:
            messages.error(request, 'Incorrent email or password')
            data = {'server_messages': get_msg_json(request)}
            return Response(data, status.HTTP_401_UNAUTHORIZED)

        access, refresh = tokens['access'], tokens['refresh']
        response = Response({'access': access}, status=status.HTTP_200_OK)
        set_jwt_cookies(response, access, refresh)
        cache.set("access", access, timeout=None)

        return response


class JwtRefreshView(TokenRefreshView):
    """
    Read Refresh token from cookie,
    return Access token in response data
    """
    serializer_class = JwtRefreshSerializer

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data['refresh'] = request.COOKIES.get('refresh')
        serializer = self.get_serializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exc:
            raise InvalidToken(exc.args[0])

        access = serializer.validated_data['access']
        response = Response({'access': access}, status=status.HTTP_200_OK)
        set_jwt_cookies(response, access)
        return response
