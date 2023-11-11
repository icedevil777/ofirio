from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from account.models import EmailSettings
from api_property.serializers import FavoriteSerializer


class FavoriteView(ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated, )
    http_method_names = ('get', 'post', 'delete', )  # get: list, post: create, delete: destroy

    def get_queryset(self):
        props = self.request.user.favoriteproperty_set.all().order_by('-created_at')
        return props

    def get_object(self):
        """
        If 'identifier' is digits only, get object by pk. Otherwise get it by prop_id.
        In the future prop_class can be added in the URL too if needed
        """
        field = 'pk' if self.kwargs.get('identifier', '').isdigit() else 'prop_id'
        queryset = self.get_queryset()
        filter_kwargs = {field: self.kwargs['identifier']}
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    def create(self, request, *args, **kwargs):
        if not self.get_queryset():
            e_setting_obj = EmailSettings.objects.get(user=request.user)
            e_setting_obj.favorites = True
            e_setting_obj.favorites_match_notification = True
            e_setting_obj.save()
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        resp = super().list(request)
        data = resp.data[0] if resp.data else resp.data
        return Response(data, resp.status_code)

    def destroy(self, request, *args, **kwargs):
        field = 'pk' if self.kwargs.get('identifier', '').isdigit() else 'prop_id'
        filter_kwargs = {field: self.kwargs['identifier']}
        self.get_queryset().filter(**filter_kwargs).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
