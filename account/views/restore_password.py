from django.contrib import messages
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from account.emails import PasswordResetRequestedEmail, PasswordResetSuccessfullyEmail
from account.models import RestorePasswordCheck
from account.serializers import (
    RestorePasswordSerializer, RestorePasswordCheckSerializer, RestorePasswordChangeSerializer,
)
from common.utils import get_msg_json, extract_first_error


User = get_user_model()


class RestorePasswordView(APIView):
    """
    Restore password
    """
    serializer_class = RestorePasswordSerializer
    queryset = ''

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            messages.error(request, 'Email is required')
            data = {}
            data['errors'] = serializer.errors
            data['server_messages'] = get_msg_json(request)
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if user := User.objects.filter(email=serializer.data['email']).first():
            PasswordResetRequestedEmail.send(user)

        return Response({}, status=status.HTTP_200_OK)


class RestorePasswordCheckView(APIView):
    """
    Check Restore Password Code
    """
    serializer_class = RestorePasswordCheckSerializer
    queryset = ''

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            messages.error(request, 'Restore code is required')
            data = {'server_messages': get_msg_json(request)}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if RestorePasswordCheck.objects.find_active(serializer.data['restore_code']):
            messages.success(request, 'Restore code is correct')
            data = {'server_messages': get_msg_json(request)}
            return Response(data, status=status.HTTP_200_OK)

        messages.error(request, 'Incorrect restore code')
        data = {'server_messages': get_msg_json(request)}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)


class RestorePasswordChangeView(APIView):
    """
    Restore Password
    """
    serializer_class = RestorePasswordChangeSerializer
    queryset = ''

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})

        if not serializer.is_valid():
            messages.error(request, extract_first_error(serializer))
            data = {'errors': serializer.errors, 'server_messages': get_msg_json(request)}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if check := RestorePasswordCheck.objects.find_active(serializer.data['restore_code']):
            # update password
            user = User.objects.get(email=check.email)
            user.set_password(serializer.data['password_new'])
            user.save()

            # update restore object
            check.used = True
            check.save()

            if not user.email_address.verified:
                user.email_address.verify()

            PasswordResetSuccessfullyEmail.send(user)

            messages.success(request, 'Password successfully changed, please try to log in!')
            data = {'server_messages': get_msg_json(request)}
            return Response(data, status=status.HTTP_200_OK)

        messages.error(request, 'Incorrect restore link. Please create a new request '
                                '(The link is active for only one hour!)')
        data = {'server_messages': get_msg_json(request)}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
