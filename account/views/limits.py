from rest_framework import generics
from rest_framework.response import Response

from account.models import AccessEvent


class LimitsLeftView(generics.RetrieveAPIView):

    def retrieve(self, request, *args, **kwargs):
        left = AccessEvent.objects.get_limits_left(request)
        return Response(left)
