import io
import json
from copy import deepcopy

from django.template.loader import render_to_string
from django.utils import timezone
from ofirio_common.prop_fin_model import construct_finance_model
from rest_framework import exceptions, status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.enums import AccessType
from account.models import AccessEvent
from account.permissions import RequestsLimit
from rent_analyzer.common.rent_analyzer_model import get_rent_analyzer_calculation_model
from rent_analyzer.enums import PropertyType
from rent_analyzer.serializers import RentAnalyzerSearchSerializer
from api_property.common import prop_representation
from api_property.common.common import getProp, get_proforma
from api_property.serializers import PropertyFinanceSerializer
from common.pdf import generate_pdf
from common.utils import generate_random_hex_str, read_binary_file, read_text_file
from reports.enums import ReportType
from reports.models import Report
from reports.serializers import CreatedReportSerializer, ReportSerializer


class ReportList(ListAPIView):
    """List all the user reports"""
    permission_classes = IsAuthenticated,
    serializer_class = ReportSerializer

    def get_queryset(self):
        return Report.objects.filter(user=self.request.user)


class BaseCreateReportView(CreateAPIView):
    """
    Base View for creating PDF views.
    """
    permission_classes = IsAuthenticated, RequestsLimit
    context_safe_text_files = {}
    context_unsafe_text_files = {}
    context_binary_files = {}

    def generate_filename(self):
        """
        Generate report filename
        """
        now = timezone.now()
        timestamp = f'{now.year}{now.month:02d}{now.day}{now.hour}{now.minute}'
        key = generate_random_hex_str()
        report_type = self.report_type.replace('_', '-')
        filename = f'ofirio-{report_type}-{timestamp}-{key}.pdf'
        return filename

    def generate_pdf(self, request, serializer, calculated_data):
        context = {
            'user': request.user,
            'query': serializer.validated_data,
            'data': calculated_data,
        }
        files_context = self.get_files_context()

        # it MUST ALWAYS be this direction, not vice versa (not files_context.update(context))
        # Otherwise users may put their own value for our context key in request,
        # and if that value is a local path, the file's content returned in PDF
        context.update(files_context)

        html = render_to_string(self.template, context)
        pdf = generate_pdf(html)
        return pdf

    def get_files_context(self):
        context = {}
        for context_var, file_path in self.context_safe_text_files.items():
            context[context_var] = read_text_file(file_path, as_safe=True)
        for context_var, file_path in self.context_unsafe_text_files.items():
            context[context_var] = read_text_file(file_path, as_safe=False)
        for context_var, file_path in self.context_binary_files.items():
            context[context_var] = read_binary_file(file_path)
        return context

    def calculate(self, query, raw_query):
        """
        Method to perform and return specific calculations in a subclass.
        Results are placed in model's 'data' field
        """
        return {}

    def get_calc_data_to_save(self, calculated):
        """Redefine in a subclass if you need to save only some of the calculated data"""
        return calculated

    def get_list_data(self, query, calculated):
        """Redefine in a subclass to prepare data for list_data model field"""
        return {}

    def create(self, request, *args, **kwargs):
        """
        Main logic happens here. It:
        - validates serializer against request.data
        - calculates or take from DB additional data (call self.calculate() method)
        - generates PDF file
        - saves model with all the data
        - returns correct http response
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        query = deepcopy(serializer.validated_data)
        calculated_data = self.calculate(query, request.data)
        list_data = self.get_list_data(query, calculated_data)
        pdf_bytes = self.generate_pdf(request, serializer, calculated_data)
        filename = self.generate_filename()
        filtered_calc_data = self.get_calc_data_to_save(calculated_data)

        report = Report(
            user=request.user,
            report_type=self.report_type,
            query=serializer.validated_data,
            data=filtered_calc_data,
            list_data=list_data,
        )
        report.report_file.save(filename, io.BytesIO(pdf_bytes), save=False)
        report.save()

        AccessEvent.objects.remember_access(
            request, self.access_type, serializer.validated_data,
        )
        serializer = CreatedReportSerializer(report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RentAnalyzerReportCreateView(BaseCreateReportView):
    serializer_class = RentAnalyzerSearchSerializer
    queryset = ''
    access_type = AccessType.RENT_ANALYZER_REPORT
    report_type = ReportType.RENT_ANALYZER
    template = 'reports/rent-analyzer.html'
    context_safe_text_files = {
        'reset_css': 'reports/static/css/reset.css',
        'styles_css': 'reports/static/css/rent-analyzer-styles.css',
        'report_css': 'reports/static/css/rent-analyzer-report.css',
        'logo_full_svg': 'reports/static/img/logo-full.svg',
    }
    model_attrs_for_context = 'address', 'rent', 'stat', 'tables', 'items'

    def get_calc_data_to_save(self, calculated):
        """Prepare data for saving in 'data' model field"""
        filtered = {
            'address': calculated['address'],
            'rent': calculated['rent'],
            'stat': calculated['stat'],
        }
        return filtered

    def get_list_data(self, query, calculated):
        list_data = {
            'beds': query.get('beds'),
            'baths': query.get('baths'),
            'address': query.get('query'),
        }
        return list_data

    def convert_items(self, calculated_data):
        """
        Convert:
        - tech prop type names to label ones
        - location string to coordinates
        """
        property_types = dict(PropertyType.choices)

        for item in calculated_data['items']:
            prop_type = item.get('prop_type2')
            if prop_type:
                item['prop_type2'] = property_types.get(prop_type, prop_type)

            try:
                loc_strings = item.get('location')[1:-1].split(',')
                item['lat'] = float(loc_strings[0])
                item['lon'] = float(loc_strings[1])
            except Exception:
                pass

    def calculate(self, query, raw_query):
        """Calculate all the values used in report template"""
        model = get_rent_analyzer_calculation_model()(**query)

        if not model.address:
            raise exceptions.ValidationError
        if not model.found:
            raise exceptions.NotFound

        calculated_data = {attr: getattr(model, attr) for attr in self.model_attrs_for_context}
        self.convert_items(calculated_data)
        return calculated_data


class PropertyReportCreateView(BaseCreateReportView):
    serializer_class = PropertyFinanceSerializer
    queryset = ''
    access_type = AccessType.PROPERTY_REPORT
    report_type = ReportType.PROPERTY
    template = 'reports/property.html'
    context_safe_text_files = {
        'reset_css': 'reports/static/css/reset.css',
        'styles_css': 'reports/static/css/property-styles.css',
        'report_css': 'reports/static/css/property-report.css',
        'logo_full_svg': 'reports/static/img/logo-full.svg',
        'house_checkmark_svg': 'reports/static/img/house-checkmark.svg',
        'house_foundament_structural_svg': 'reports/static/img/house-foundament-structural.svg',
        'rich_chair_svg': 'reports/static/img/rich-chair.svg',
        'nature_svg': 'reports/static/img/nature.svg',
        'team_svg': 'reports/static/img/team.svg',
        'clipboard_checkmark_svg': 'reports/static/img/clipboard-checkmark.svg',
        'house_gear_inside_svg': 'reports/static/img/house-gear-inside.svg',
        'house_dollar_inside_svg': 'reports/static/img/house-dollar-inside.svg',
    }
    model_attrs_for_context = (
        'cap_rate', 'cash_on_cash', 'total_return', 'cash_flow', 'expenses', 'rental_income',
        'price', 'monthly_rent', 'down_payment', 'financing_years', 'interest_rate',
        'management_fees', 'month_maintenance_reserves', 'month_hoa_fees', 'month_insurance',
        'month_property_taxes', 'month_re_lease_fees', 'month_overhead_miscellanous',
        'month_operating_income', 'month_loan_payments', 'net_income', 'cash_flow',
        'annual_increase_rent', 'annual_increase_prop', 'general_inflation',
        'average_length_stay_years', 'management_fees_percent', 'maintenance_cost_amount',
        'overhead_cost_amount', 'closing_cost_on_purchase_percent', 'closing_cost_on_sale_percent',
        'equity_investment', 'loan_value', 'total_investment', 'operating_income_year1',
        'net_income_year1', 'cash_flow_year1', 'cap_rate_year1', 'cash_on_cash_year1',
        'one_percent_rule', 'gross_yield', 'irr', 'operating_expense_ratio_year1',
        'debt_service_coverage_year1', 'month_rent_less_vacancy', 'month_cash_income_loss',
    )

    def get_calc_data_to_save(self, calculated):
        """Prepare data for saving in 'data' model field"""
        prop = calculated.get('prop', {})
        prop_data = prop.get('data', {})
        prop_data_attrs = (
            'beds', 'baths', 'price', 'garage', 'median', 'year_built', 'monthly_tax',
            'building_size', 'predicted_rent', 'price_per_sqft', 'monthly_insurance',
        )
        filtered = {
            'data': {attr: prop_data.get(attr) for attr in prop_data_attrs},
            'address': prop.get('address', {}),
        }
        return filtered

    def get_list_data(self, query, calculated):
        prop_data = calculated['prop'].get('data', {})
        list_data = {
            'beds': prop_data.get('beds'),
            'baths': prop_data.get('baths'),
            'address': calculated['prop'].get('address', {}).get('line')
        }
        return list_data

    def calc_tax_percents(self, tax_history):
        """Calculate percent for each year's tax"""
        for idx, ass in enumerate(tax_history):
            if idx == len(tax_history) - 1:
                ass['percent'] = ''
            else:
                diff = ass['tax'] - tax_history[idx+1]['tax']
                sign = ''
                if diff > 0:
                    sign = '+'
                elif diff < 0:
                    sign = '-'
                percent = 100 * abs(diff) / ass['tax']
                ass['percent'] = f'{sign}{abs(percent):.2f}'

    def calculate(self, query, raw_query):
        """Get prop from DB and calculate all the values used in report template"""
        prop_id = query.pop('prop_id')
        prop = getProp(prop_id)
        if not prop:
            raise exceptions.NotFound

        prop['summary'] = prop_representation.build_summary(prop, humanize=True)
        self.calc_tax_percents(prop['tax_history'])

        model = construct_finance_model(query, raw_query, prop)
        accumulated_wealth = json.loads(model.getAccumulatedWealthData().to_json(orient='columns'))

        calculated_data = {attr: getattr(model, attr) for attr in self.model_attrs_for_context}

        calculated_data['prop'] = prop
        calculated_data['proforma'] = get_proforma(model, query['financing_years'])
        calculated_data['acc_wealth_last_year'] = list(accumulated_wealth['year'].keys())[-1]
        calculated_data['accumulated_wealth'] = accumulated_wealth
        calculated_data['tax_history_years'] = [item.get('year') for item in prop['tax_history']][::-1]
        calculated_data['tax_history_taxes'] = [item.get('tax') for item in prop['tax_history']][::-1]

        return calculated_data
