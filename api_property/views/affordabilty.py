from math import fabs

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ofirio_common.prop_fin_model import construct_finance_model
from api_property.common.common import is_off_market_status, get_fields_prop_cache, cant_show_price_fields
from api_property.serializers import AffordabilitySerializer


class AffordabilityView(APIView):
    serializer_class = AffordabilitySerializer

    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        prop_id = serializer.data['prop_id']
        prop = get_fields_prop_cache(prop_id, fields=('data', 'params', 'status', 'address'))

        if not prop:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        if is_off_market_status(prop['status']) \
                or cant_show_price_fields(prop['status'], prop['address']['state_code']):
            return Response({'message': 'this property is off market or closed in tx'},
                            status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        data['financing_years'] = data['loan_type']
        data['property_taxes'] = data['prop_tax_est']
        data['hoa_fees'] = data['monthly_hoa']
        data['insurance'] = data['monthly_insurance']

        model = construct_finance_model(data, request.data, prop)
        items = {'interest_payment': fabs(model.month_loan_payments),
                 'prop_taxes'      : model.property_taxes_mo,
                 'hoa_fees':         model.hoa_fees_mo,
                 'insurance':        model.insurance_mo, }
        if data['down_payment'] < 0.2:
            items['mortgage insurance'] = model.loan_value * 0.007 / 12

        return Response(data=items, status=status.HTTP_200_OK)
