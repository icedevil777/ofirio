from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api_property.common.common import get_analytics_data_for_api_property, getProp
from api_property.serializers import AnalyticsSerializer


class Analytics(APIView):
    serializer_class = AnalyticsSerializer

    def post(self, request, *args, **kwargs):

        serializer = AnalyticsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        prop_id = serializer.data['prop_id']
        prop = getProp(prop_id)
        if not prop:
            return Response({"response": "there isn't such prop"},
                            status=status.HTTP_404_NOT_FOUND)
        state_id = prop['address']['state_code']
        county = prop['address']['county']
        city = prop['address']['city']
        zip_code = prop['address']['zip']
        prop_type2 = prop['data']['cleaned_prop_type']

        agg_type = serializer.data['agg_type']
        prop_class = serializer.data['prop_class']
        graph_names = tuple(serializer.data['graph_names'])

        data = get_analytics_data_for_api_property(
            initial_agg_type=agg_type, prop_class=prop_class, prop_type2=prop_type2,
            graph_names=graph_names, state_id=state_id, county=county,
            city=city, zip_code=zip_code, user=request.user, prop_id=prop_id, params=prop['params'])
        if not data:
            return Response({"response": "no analytics for your request"},
                            status=status.HTTP_404_NOT_FOUND)

        return Response(data=data, status=status.HTTP_200_OK)
