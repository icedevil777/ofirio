from django.contrib import messages
from rest_framework.views import APIView
from rest_framework import status, exceptions
from rest_framework.response import Response

from account.authentication import get_jwtokens, set_jwt_cookies
from account.serializers import FacebookJwtLoginSerializer, GoogleJwtLoginSerializer
from common.utils import get_msg_json


class SocialJwtLoginView(APIView):
    """
    Base view for social authentication using JWT
    """
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, 'Already authenticated')
            data = {'server_messages': get_msg_json(request)}
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.serializer_class(data=request.data, context={'request': request})

        try:
            serializer.is_valid(raise_exception=True)
        except exceptions.NotAuthenticated as e:
            messages.error(request, e.detail)
            data = {'server_messages': get_msg_json(request)}
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

        refresh, access = get_jwtokens(serializer.validated_data['user'])
        response = Response({'access': access}, status=status.HTTP_200_OK)
        set_jwt_cookies(response, access, refresh)
        return response


class GoogleJwtLoginView(SocialJwtLoginView):
    """
    Login a user by info from Google One Tap (also named "Sign In With Google")
    """
    serializer_class = GoogleJwtLoginSerializer
    queryset = ''


class FacebookJwtLoginView(SocialJwtLoginView):
    """
    Login a user by info from Facebook
    """
    serializer_class = FacebookJwtLoginSerializer
    queryset = ''
