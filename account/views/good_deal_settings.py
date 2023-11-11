from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from account.models import GoodDealSettings
from account.serializers import GoodDealSettingsSerializer


class GoodDealSettingsApiView(UpdateModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    Retrieve data for a Blog tab on the main page
    """
    permission_classes = (AllowAny,)
    serializer_class = GoodDealSettingsSerializer
    queryset = ''

    def get_object(self):
        if self.request.user.is_authenticated:
            return GoodDealSettings.objects.get(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """
        Check authentication only on GET
        """
        if not request.user.is_authenticated:
            raise NotAuthenticated
        resp = super().retrieve(request, *args, **kwargs)
        return resp
