import logging

import facebook
from django.conf import settings
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import update_last_login
from django.utils import timezone
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework.authentication import SessionAuthentication as DrfSessionAuthentication
from rest_framework.exceptions import NotAuthenticated
from rest_framework_simplejwt.settings import api_settings as jwt_settings

import common.tasks as tasks
from common.utils import encrypt


User = get_user_model()
logger = logging.getLogger(__name__)


class SessionAuthentication(DrfSessionAuthentication):

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.

        We use 401 as a marker of not-authenticated request.
        'Basic' or 'Digest' will trigger auth pop-up, so we return 'BasicCustom'
        """
        return 'BasicCustom'


class SocialJwtBackend(ModelBackend):
    """
    Base class for a social login provider
    """
    def authenticate(self, request, token=None, **kwargs):
        if token is None:
            return

        info = self._verify_token(token)
        created = False
        user = User.objects.filter(email=info['email']).first()
        if not user:
            user = User.objects.create_user(email=info['email'])
            created = True

        if self.user_can_authenticate(user):
            became_verified = not user.verified
            self._fill_user_fields(user, info, created)
            if became_verified:
                tasks.track_user_status_changed.delay(user.pk)
            return user

        else:
            raise NotAuthenticated


class GoogleJwtBackend(SocialJwtBackend):

    def _fill_user_fields(self, user, info, created):
        user.verified = True
        user.google_user_id = info.get('sub', '')

        if created:
            user.first_name = info.get('given_name', '')
            user.last_name = info.get('family_name', '')
            user.accepted_terms_of_use = False

        user.save()

    def _verify_token(self, token):
        """
        Verify Google ID token and return its payload if it's valid. Details:
        https://developers.google.com/identity/gsi/web/guides/verify-google-id-token
        """
        client_id = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
        try:
            info = id_token.verify_oauth2_token(token, requests.Request(), client_id)
        except ValueError as exc:
            if settings.DEBUG:
                raise InvalidGoogleToken(str(exc)) from exc
            else:
                raise InvalidGoogleToken from exc

        by_google = 'accounts.google.com' in info['iss']
        subject = info['sub']
        email = info.get('email')
        if not all([by_google, subject]):
            raise NotAuthenticated
        if not email:
            raise NotAuthenticated('No access to email')

        return info


class FacebookJwtBackend(SocialJwtBackend):

    def _fill_user_fields(self, user, info, created):
        user.verified = True
        user.fb_user_id = info.get('id', '')

        if created:
            user.first_name = info.get('first_name', '')
            user.last_name = info.get('last_name', '')
            user.accepted_terms_of_use = False

        user.save()

    def _verify_token(self, token):
        """
        Query the facebook GraphAPI to fetch the user info
        """
        try:
            graph = facebook.GraphAPI(access_token=token)
            info = graph.request('/me?fields=first_name,last_name,email')
        except Exception as exc:
            if settings.DEBUG:
                raise InvalidFacebookToken(str(exc)) from exc
            else:
                raise InvalidFacebookToken from exc

        if not info.get('email'):
            raise NotAuthenticated('No access to email')

        return info


class InvalidGoogleToken(NotAuthenticated):
    default_detail = 'Invalid Google ID token'


class InvalidFacebookToken(NotAuthenticated):
    default_detail = 'Invalid Facebook ID token'


def set_jwt_cookies(response, access=None, refresh=None):
    """
    Set access and refresh tokens as cookies to the response
    """
    if access is not None:
        encrypted_access = encrypt(access, settings.COOKIE_SECRET)
        access_cookie_data = get_access_jwt_cookie_data()
        response.set_cookie('access', encrypted_access, **access_cookie_data)
        if settings.DEBUG:
            localhost_access_cookie_data = {**access_cookie_data, 'domain': '127.0.0.1'}
            response.set_cookie('access_local', encrypted_access, **localhost_access_cookie_data)

    if refresh is not None:
        response.set_cookie('refresh', refresh, **get_refresh_jwt_cookie_data())

    return response


def model_backend_login(request, user):
    """Log in the user with a Django Model backend"""
    return auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')


def get_jwtokens(user):
    """
    Get JWTokens for logging user in:
    - refresh token
    - access token
    """
    from account.tokens import OfirioRefreshToken
    refresh = OfirioRefreshToken.for_user(user)

    if jwt_settings.UPDATE_LAST_LOGIN:
        update_last_login(None, user)

    return str(refresh), str(refresh.access_token)


def get_jwt_cookie_data(lifetime):
    cookie = {
        'expires': timezone.now() + lifetime,
        'domain': settings.PROJECT_DOMAIN,
        'path': settings.CSRF_COOKIE_PATH,
        'secure': settings.CSRF_COOKIE_SECURE,
        'samesite': settings.JWT_REFRESH_SAMESITE,
        'httponly': True,  # important!
    }
    return cookie


def get_access_jwt_cookie_data():
    data = get_jwt_cookie_data(jwt_settings.ACCESS_TOKEN_LIFETIME)
    return data


def get_refresh_jwt_cookie_data():
    data = get_jwt_cookie_data(jwt_settings.REFRESH_TOKEN_LIFETIME)
    return data
