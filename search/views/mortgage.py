from django.contrib import messages

from ofirio_common.prop_fin_model import FinanceModel
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from api_property.common.common import getPropsData
from common.utils import get_msg_json
from search.serializers import MortgageSerializer


class Mortgage(APIView):

    serializer_class = MortgageSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            messages.error(request, 'Error! Incorrect query')
            data = {'errors': serializer.errors, 'server_messages': get_msg_json(request)}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

        down_payment = serializer.data['down_payment']
        financing_years = serializer.data['financing_years']
        interest_rate = serializer.data['interest_rate']
        prop_details = serializer.data['prop_details']

        #Load prop data
        prop_ids = []
        for prop in prop_details:
            prop_ids.append(prop['prop_id'])
        prop_ids = prop_ids[:20] #request only first 20 items
        data = getPropsData(prop_ids)

        result = []
        for prop in prop_details:

            prop_id = prop['prop_id']
            price = prop['price']
            market_rent = prop['market_rent']

            #get data from prop
            if prop_id not in data: continue

            hoa_fees = data[prop_id]['hoa_fees']
            monthly_insurance = data[prop_id]['monthly_insurance']
            monthly_tax = data[prop_id]['monthly_tax']

            model = FinanceModel(price              = price,
                                 monthly_rent       = market_rent,
                                 down_payment       = down_payment,
                                 financing_years    = financing_years,
                                 interest_rate      = interest_rate,
                                 hoa_fees           = hoa_fees,
                                 insurance          = monthly_insurance,
                                 property_taxes     = monthly_tax)

            result.append({
                'prop_id': prop_id,
                'cash_on_cash': model.cash_on_cash,
                'total_return': model.total_return
            })

        data = {'result': result}
        return Response(data, status=status.HTTP_200_OK)
