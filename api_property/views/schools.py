from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api_property.serializers import PropertyIdSerializer
from api_property.common.common import get_fields_prop_cache


class SchoolsView(APIView):
    serializer_class = PropertyIdSerializer

    def post(self, request,*args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        prop_id = serializer.data['prop_id']
        prop = get_fields_prop_cache(prop_id, fields=('schools', ))
        if not prop:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {
                'prop_id': prop_id,
                'schools': prop['schools'] if prop['schools']!={} else None,
            }
            return Response(data, status=status.HTTP_200_OK)
