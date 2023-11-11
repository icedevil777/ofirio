from rest_framework.mixins import UpdateModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from account.models import EmailSettings
from account.serializers import EmailSettingsSerializer


class EmailSettingsView(UpdateModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = EmailSettingsSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ('get', 'post')

    def get_object(self):
        return EmailSettings.objects.get(user=self.request.user)
