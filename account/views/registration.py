from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from account.authentication import get_jwtokens, set_jwt_cookies
from account.emails import RegistrationVerifyAddressEmail
from account.serializers import UserSerializer
from common.utils import extract_first_error, get_msg_json


User = get_user_model()


class RegistrationView(APIView):
    """
    Registration
    """
    serializer_class = UserSerializer
    queryset = ''

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, 'Already authentificated')
            data = {'server_messages': get_msg_json(request)}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            messages.error(request, extract_first_error(serializer))
            data = {'errors': serializer.errors, 'server_messages': get_msg_json(request)}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        try:
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            messages.error(request, f'User with {email} already exist')
            data = {'server_messages': get_msg_json(request)}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            user = User.objects.create_user(**serializer.validated_data)
            RegistrationVerifyAddressEmail.send(user)

            refresh, access = get_jwtokens(user)
            messages.success(request, 'You are successfully registered')
            data = {'access': access, 'server_messages': get_msg_json(request)}

            # for testing purposes
            if settings.DEBUG:
                data['verification_code'] = user.email_address.code

            response = Response(data, status=status.HTTP_201_CREATED)
            set_jwt_cookies(response, access, refresh)
            return response

        except Exception:
            messages.error(request, 'Registration error')
            data = {'server_messages': get_msg_json(request)}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
