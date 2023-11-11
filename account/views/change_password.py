from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from account.emails import PasswordChangedEmail
from account.serializers import ChangePasswordSerializer
from common.utils import get_msg_json, extract_first_error


User = get_user_model()


class ChangePasswordView(APIView):
    serializer_class = ChangePasswordSerializer
    queryset = ''

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Need to authenticate')
            data = {'server_messages': get_msg_json(request)}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data, context={'request': request})

        if not serializer.is_valid():
            messages.error(request, extract_first_error(serializer))
            data = {'errors': serializer.errors, 'server_messages': get_msg_json(request)}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        password_old = serializer.data['password_old']
        password_new = serializer.data['password_new']

        if check_password(password_old, request.user.password):
            user = User.objects.get(email=request.user.email)
            user.set_password(password_new)
            user.save()

            # prevent logout after changing password
            update_session_auth_hash(request, user)

            PasswordChangedEmail.send(user)

            messages.success(request, 'Password is succesfully updated')
            data = {'server_messages': get_msg_json(request)}
            return Response(data, status=status.HTTP_200_OK)

        else:
            messages.error(request, 'Incorrect current password')
            data = {'server_messages': get_msg_json(request)}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
