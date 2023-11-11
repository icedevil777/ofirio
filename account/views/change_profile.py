from django.contrib import messages
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from account.serializers import ChangeProfileSerializer
from common.utils import get_msg_json


User = get_user_model()


class ChangeProfileView(APIView):
    """
    Change Profile
    """
    serializer_class = ChangeProfileSerializer
    queryset = ''

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Need to authenticate')
            data = {'server_messages': get_msg_json(request)}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            messages.error(request, 'Incorrect profile data')
            data = {}
            data['errors'] = serializer.errors
            data['server_messages'] = get_msg_json(request)
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        first_name = serializer.data['first_name']
        last_name = serializer.data['last_name']
        phone = serializer.data['phone']

        user = User.objects.get(email=request.user.email)
        user.first_name = first_name
        user.last_name = last_name
        user.phone = phone
        user.save()

        messages.success(request, 'Profile data changed')
        data = {'server_messages': get_msg_json(request)}
        return Response(data, status=status.HTTP_200_OK)
