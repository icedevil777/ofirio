from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from account.authentication import get_jwtokens, set_jwt_cookies


User = get_user_model()


class AcceptTermsOfUseView(APIView):
    """
    Accept Terms Of Use
    """
    permission_classes = IsAuthenticated,

    def post(self, request, *args, **kwargs):
        request.user.accepted_terms_of_use = True
        request.user.save()
        refresh, access = get_jwtokens(request.user)
        response = Response({'access': access}, status=status.HTTP_200_OK)
        set_jwt_cookies(response, access, refresh)
        return response
