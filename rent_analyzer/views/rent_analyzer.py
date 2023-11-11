import logging

from rest_framework import exceptions, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

import common.tasks as tasks
from account.enums import AccessType
from account.models import AccessEvent
from account.permissions import RequestsLimit
from account.utils import is_premium
from api_property.common import stubs
from api_property.common.common import get_is_hidden
from rent_analyzer.serializers import RentAnalyzerSearchSerializer
from rent_analyzer.common.rent_analyzer_model import get_rent_analyzer_calculation_model


logger = logging.getLogger(__name__)


class RentAnalyzerRequestsLimit(RequestsLimit):

    def has_permission(self, request, view):
        if request.data.get('prop_id', '').strip():
            return True
        else:
            return super().has_permission(request, view)


class RentAnalyzer(CreateAPIView):
    permission_classes = RentAnalyzerRequestsLimit,
    serializer_class = RentAnalyzerSearchSerializer
    access_type = AccessType.RENT_ANALYZER_SEARCH

    def create(self, request, *args, **kwargs):

        if (prop_id := request.data.get('prop_id', '').strip()) and not is_premium(request.user) \
                and get_is_hidden(prop_id):
            return Response(getattr(stubs, 'rent_analyzer_prop_id'), status=status.HTTP_200_OK)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        if request.user.is_authenticated:
            tasks.track_rent_analyzer.delay(request.user.id, serializer.validated_data)

        model = get_rent_analyzer_calculation_model()(**serializer.validated_data)

        if not model.address:
            return Response({'not': 'not model address'}, status=status.HTTP_400_BAD_REQUEST)

        if not model.found:
            return Response({'message': 'model not found'}, status=status.HTTP_404_NOT_FOUND)

        response_keys = 'address', 'rent', 'stat', 'tables', 'items'
        data = {key: getattr(model, key) for key in response_keys}

        AccessEvent.objects.remember_access(
            request, self.access_type, serializer.validated_data,
        )
        return Response(data, status=status.HTTP_200_OK)

    def permission_denied(self, request, message=None, code=None):
        """
        If request is not permitted, always raise PermissionDenied
        """
        raise exceptions.PermissionDenied(detail=message, code=code)
