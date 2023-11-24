from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from account.serializers import AccountSerializer


class AccountView(APIView):
    permission_classes = IsAuthenticated,
    serializer_class = AccountSerializer
    queryset = ''

    def get(self, request, *args, **kwargs):
        print('request', request)
        serializer = self.serializer_class(request.user)
        print('serializer', serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
