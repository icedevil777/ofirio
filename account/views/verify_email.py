from django.contrib import messages
from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.authentication import get_jwtokens, set_jwt_cookies
from account.emails import RegistrationVerifyAddressEmail
from account.models import EmailAddress
from common.constants import FRONTEND_URLS
from common.utils import get_msg_json


class VerifyEmailView(APIView):
    """
    Mark user as verified if the code from the URL is found and not expired
    """
    def get(self, request, *args, **kwargs):
        email_address = EmailAddress.objects.filter(code=self.kwargs.get('code')).first()
        if email_address and not email_address.is_code_expired:
            if not email_address.verified:
                email_address.verify()

                # log user in
                refresh, access = get_jwtokens(email_address.user)
                response = Response({'access': access}, status=status.HTTP_200_OK)
                set_jwt_cookies(response, access, refresh)
                return response

            messages.error(request, 'Already verified')
            data = {'server_messages': get_msg_json(request)}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

        messages.error(request, 'Verification link expired')
        data = {'server_messages': get_msg_json(request)}
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationEmailView(APIView):
    """
    Generate new verification link and send verification email
    """
    permission_classes = IsAuthenticated,

    def post(self, request, *args, **kwargs):
        email = request.user.email_address
        if email.verified:
            messages.error(request, 'Already verified')
            data = {'server_messages': get_msg_json(request)}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

        email.generate_new_code()
        RegistrationVerifyAddressEmail.send(request.user)
        return Response({}, status=status.HTTP_200_OK)
