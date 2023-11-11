from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import exceptions

from account.enums import AccessType
from account.models import AccessEvent
from account.permissions import RequestsLimit
from api_property.common.common import get_analytics_data_for_api_property
from rent_analyzer.serializers import AnalyticsSerializer


class Analytics(CreateAPIView):
    permission_classes = RequestsLimit,
    serializer_class = AnalyticsSerializer
    access_type = AccessType.RENT_ESTIMATOR_ANALYTICS

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        agg_type = serializer.data['agg_type']
        graph_names = tuple(serializer.data['graph_names'])
        state_id = serializer.data['state']
        county = serializer.data.get('county')
        if county and county.lower().endswith(' county'):
            # google geocoder returns county names with 'County' appendix,
            # and counties in our database don't contain it
            county = county[:-len(' county')]
        zip_code = serializer.data.get('zip')
        city = serializer.data.get('city')
        prop_type2 = serializer.data['prop_type2']

        data = get_analytics_data_for_api_property(
            initial_agg_type=agg_type, prop_class='rent-estimator', prop_type2=prop_type2,
            graph_names=graph_names, state_id=state_id, county=county,
            city=city, zip_code=zip_code)
        if not data:
            return Response(status=status.HTTP_404_NOT_FOUND)

        AccessEvent.objects.remember_access(
            request, self.access_type, serializer.validated_data,
        )

        # TODO: two dicts are combined for compatibility.
        # when frontend is ready, only `data` should be returned
        return Response(data={**data, **data['graphs']}, status=status.HTTP_200_OK)

    def permission_denied(self, request, message=None, code=None):
        """
        If request is not permitted, always raise PermissionDenied
        """
        raise exceptions.PermissionDenied(detail=message, code=code)
