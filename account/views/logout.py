import logging

from django.conf import settings
from django.contrib import auth, messages
from rest_framework.generics import CreateAPIView
from rest_framework import status
from rest_framework.response import Response

from common.serializers import EmptySerializer
from common.utils import get_msg_json


logger = logging.getLogger(__name__)


class LogoutView(CreateAPIView):
    """
    Logout both from Session and from JWT authentications
    """
    serializer_class = EmptySerializer
    queryset = ''

    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            auth.logout(request)

        messages.info(request, 'You are successfully logout')
        data = {'server_messages': get_msg_json(request)}

        response = Response(data, status=status.HTTP_200_OK)
        response.delete_cookie('refresh', domain=settings.PROJECT_DOMAIN,
                                          path=settings.CSRF_COOKIE_PATH)
        response.delete_cookie('access', domain=settings.PROJECT_DOMAIN,
                                         path=settings.CSRF_COOKIE_PATH)
        response.delete_cookie('access_local', domain='127.0.0.1',
                                               path=settings.CSRF_COOKIE_PATH)
        return response
