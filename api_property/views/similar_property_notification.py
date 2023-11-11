from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.models import EmailSettings
from api_property.serializers import SimilarPropertyNotificationSerializer


class SimilarNotificationView(viewsets.ModelViewSet):
    serializer_class = SimilarPropertyNotificationSerializer
    permission_classes = (IsAuthenticated, )
    http_method_names = ('get', 'post', 'delete', )  # get: list, post: create, delete: destroy

    def get_queryset(self):
        props = self.request.user.similar_props.all().order_by('-created_at')
        return props

    def create(self, request, *args, **kwargs):
        if not self.get_queryset():
            e_setting_obj = EmailSettings.objects.get(user=request.user)
            e_setting_obj.similars = True
            e_setting_obj.save()
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        resp = super().list(request)
        data = resp.data[0] if resp.data else resp.data
        return Response(data, resp.status_code)
