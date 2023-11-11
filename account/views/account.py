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
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
