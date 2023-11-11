from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.models import EmailSettings
from api_property.serializers import PropUpdatesSerializer


class PropUpdatesView(viewsets.ModelViewSet):
    serializer_class = PropUpdatesSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = 'get', 'post', 'delete'

    def get_queryset(self):
        props = self.request.user.props_updates.all().order_by('-created_at')
        return props

    def create(self, request, *args, **kwargs):
        if not self.get_queryset():
            e_setting_obj = EmailSettings.objects.get(user=request.user)
            e_setting_obj.prop_updates = True
            e_setting_obj.save()
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        resp = super().list(request, *args, **kwargs)
        data = resp.data
        return Response(data[0] if data else data, resp.status_code)
