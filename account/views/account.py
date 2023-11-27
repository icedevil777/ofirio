import jwt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from djangoproject.settings import SECRET_KEY
from account.serializers import AccountSerializer


class AccountView(APIView):
    permission_classes = IsAuthenticated,
    serializer_class = AccountSerializer
    queryset = ''

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # def get(self, request, *args, **kwargs):
        # if request.COOKIES['refresh']:
        #     refresh = request.COOKIES['refresh']
        #     print('refresh', refresh)

            # dict = jwt.decode(refresh, "secret", algorithms=['RS256'])
            # print('dict', dict)

           
        # serializer = self.serializer_class( )
        # print('serializer', serializer.data)

        # return Response(serializer.data, status=status.HTTP_200_OK)
