from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from api_property.common.common import get_fields_prop_cache
from api_property.serializers import PropertyIdSerializer


class TaxHistory(APIView):
    serializer_class = PropertyIdSerializer

    def post(self, request,*args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        prop_id = serializer.data['prop_id']
        prop = get_fields_prop_cache(prop_id, fields=('tax_history', ))
        if not prop:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        else:
            data = {
                'prop_id': prop_id,
                'tax_history': prop['tax_history'] or []
            }
            return Response(data, status=status.HTTP_200_OK)
