from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.emails import ContactUsEmail
from common.serializers import ContactUsSerializer
from common.utils import notify_telegram


class ContactUsView(APIView):
    serializer_class = ContactUsSerializer

    def post(self, request,*args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if not serializer.is_valid():
            data = {'errors': serializer.errors}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        notify_telegram('#contact_us', serializer.data)
        ContactUsEmail.send(serializer.data)
        return Response({}, status=status.HTTP_200_OK)
