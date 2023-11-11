import json

from django.contrib import messages
from ofirio_common.prop_fin_model import construct_finance_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api_property.common.common import get_analytics_data_for_api_property
from api_property.common.common import get_proforma, can_show_property, get_fields_prop_cache, is_off_market_status, \
    cant_show_price_fields
from api_property.serializers import PropertyFinanceSerializer
from common.utils import get_msg_json


class FinanceView(APIView):
    serializer_class = PropertyFinanceSerializer

    def get_response_data(self, prop_id, model, proforma, acc_wealth_frame, avg_cap_rate):
        data = {
            'prop_id':  prop_id,
            'base': {
                'price':                        model.price,
                'monthly_rent':                 int(model.monthly_rent),
                'down_payment':                 model.down_payment,
                'financing_years':              model.financing_years,
                'interest_rate':                model.interest_rate,
            },
            'main_results': {
                'rental_income':                model.rental_income,
                'expenses':                     model.expenses,
                'cash_flow':                    model.cash_flow,
                'cash_on_cash':                 model.cash_on_cash,
                'cap_rate':                     model.cap_rate,
                'total_return':                 model.total_return,
                'closing_costs':                model.closing_costs,
                'total_cash_needed':            model.total_cash_needed,
                'total_financing':              model.total_financing,
                'total_project':                model.total_project,
                'avg_cap_rate':                 avg_cap_rate
            },
            'detailed': {
                'hoa_fees':                         int(model.hoa_fees_mo),
                'insurance':                        model.insurance_mo,
                'property_taxes':                   int(model.property_taxes_mo),
                'annual_increase_rent':             model.annual_increase_rent,
                'annual_increase_prop':             model.annual_increase_prop,
                'general_inflation':                model.general_inflation,
                'average_length_stay_years':        model.average_length_stay_years,
                'vacancy_per_year_days':            model.vacancy_period,
                'management_fees_percent':          model.management_fees_percent,
                'maintenance_cost_percent':         model.maintenance_cost_percent, #deprecated
                'maintenance_cost_amount':          model.maintenance_cost_amount,
                'overhead_cost_percent':            model.overhead_cost_percent,    #deprecated
                'overhead_cost_amount':             model.overhead_cost_amount,
                'closing_cost_on_purchase_percent': model.closing_cost_on_purchase_percent,
                'closing_cost_on_sale_percent':     model.closing_cost_on_sale_percent,
                'release_fees_amount':              model.release_fees_amount,
            },
            'monthly_cash_flow': {
                'month_rent_less_vacancy':      model.month_rent_less_vacancy,
                'month_management_fees':        model.month_management_fees,
                'month_maintenance_reserves':   int(model.month_maintenance_reserves),
                'month_hoa_fees':               int(model.month_hoa_fees),
                'month_insurance':              model.month_insurance,
                'month_property_taxes':         int(model.month_property_taxes),
                'month_re_lease_fees':          int(model.month_re_lease_fees),
                'month_overhead_miscellanous':  int(model.month_overhead_miscellanous),
                'month_operating_income':       model.month_operating_income,
                'month_loan_payments':          model.month_loan_payments,
                'net_income':                   model.net_income,
                'month_cash_income_loss':       model.month_cash_income_loss,
            },
            'performance': {
                'equity_investment':            model.equity_investment,
                'loan_value':                   model.loan_value,
                'total_investment':             model.total_investment,
                'cash_flow_year1':              model.cash_flow_year1,
                'operating_income_year1':       model.operating_income_year1,
                'net_income_year1':             model.net_income_year1,
                'cap_rate_year1':               model.cap_rate_year1,
                'cash_on_cash_year1':           model.cash_on_cash_year1,
                'one_percent_rule':             model.one_percent_rule,
                'gross_yield':                  model.gross_yield,
                'irr':                          model.irr,
                'operating_expense_ratio_year1':model.operating_expense_ratio_year1,
                'debt_service_coverage_year1':  model.debt_service_coverage_year1,
            },
            'proforma': proforma,
            'accumulated_wealth': json.loads(acc_wealth_frame.to_json(orient='columns')),
        }
        return data

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        prop_id = serializer.data['prop_id']
        avg_cap_rate = None
        if prop := get_fields_prop_cache(prop_id, fields=('data', 'params', 'status', 'address')):
            state_id = prop['address']['state_code']
            county = prop['address']['county']
            city = prop['address']['city']
            zip_code = prop['address']['zip']
            prop_type2 = prop['data']['cleaned_prop_type']

            agg_type = 'zip'
            prop_class = 'sale'
            graph_names = 'overview', 'average_monthly_cap_rate'

            data = get_analytics_data_for_api_property(
                initial_agg_type=agg_type, prop_class=prop_class, prop_type2=prop_type2,
                graph_names=graph_names, state_id=state_id, county=county,
                city=city, zip_code=zip_code, user=request.user, prop_id=prop_id, params=prop['params'])
            avg_cap_rate = ((data.get('graphs') or {}).get('overview') or {}).get('avg_month_cap_rate')
        if not prop:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        elif not can_show_property(request.user, prop_id, prop['params']):
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)
        if is_off_market_status(prop['status']) \
                or cant_show_price_fields(prop['status'], prop['address']['state_code']):
            return Response({'message': 'this property is off market or closed in tx'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            model = construct_finance_model(serializer.validated_data, request.data, prop)
            proforma = get_proforma(model, serializer.data['financing_years'])
            acc_wealth_frame = model.getAccumulatedWealthData()
            data = self.get_response_data(prop_id, model, proforma, acc_wealth_frame, avg_cap_rate)
            return Response(data, status=status.HTTP_200_OK)
