import json

from django.db import connections
from ofirio_common.constants import MAX_RESULT_WINDOW, RESULTS_PER_PAGE
from ofirio_common.enums import AutocompletePropCategory, PropEsIndex
from ofirio_common.address_util import urlify
from ofirio_common.geocode import geocode
from ofirio_common.states_constants import states_from_short
from ofirio_common.address_util import unurlify
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from common.fields import MultipleChoiceListField, TextInputListField
from common.utils import leave_letters_nums
from search.constants import INDEX_INSIGHTS, CLEANED_AMENITIES
from search.enums import InsightType, FrontendCleanedPropType, Amenities


class AutocompleteSerializer(serializers.Serializer):
    query = serializers.CharField(required=True)

    def validate(self, data):
        """Clean query from chars"""
        clean_query = ''
        for char in data['query']:
            if char.isalpha() or char.isdigit():
                clean_query += char
            else:
                clean_query += ' '
        data['query'] = ' '.join(clean_query.split())
        return super().validate(data)


class AutocompleteQuerySerializer(AutocompleteSerializer):
    category = serializers.ChoiceField(choices=AutocompletePropCategory.choices,
                                       default=AutocompletePropCategory.BUY_PROP)


class KeywordAutocompleteSerializer(serializers.Serializer):
    prefix = serializers.CharField(required=True)

    def validate_prefix(self, raw_prefix):
        prefix = ' '.join(str(raw_prefix).lower().split())
        return leave_letters_nums(prefix, also='-/ ')


class AddressRectSerializer(serializers.Serializer):

    query = serializers.CharField(required=True)


class SitemapSerializer(serializers.Serializer):

    state_id = serializers.CharField(required=False, default=None)
    city = serializers.CharField(required=False, default=None)


class PolygonsField(TextInputListField):

    def to_internal_value(self, data):
        polygons = []
        for polygon in data:
            # polygons are strings in tests, don't know why
            if isinstance(polygon, str):
                polygon = json.loads(polygon)

            if not isinstance(polygon, list):
                raise ValidationError('Incorrect geo_polygon format, has to be list')

            for point in polygon:
                if (
                    not isinstance(point, list) or
                    len(point) != 2 or
                    not isinstance(point[0], (int, float)) or
                    not isinstance(point[1], (int, float))
                ):
                    raise ValidationError(f'Incorrect point format {point}')

            polygons.append(polygon)
        return polygons


class BasePropertyElasticSerializer(serializers.Serializer):
    """
    Contains common fields needed to search properties in Elasticsearch
    """
    index = serializers.ChoiceField(choices=PropEsIndex.choices, default=PropEsIndex.SEARCH_BUY)
    type = serializers.ChoiceField(required=True,
        choices=[('state', 'State'),
                 ('county', 'County'),
                 ('city', 'City'),
                 ('zip', 'Zip'),
                 ('geo', 'Geo')]
    )
    state_id = serializers.CharField(required=False, default='')
    county = serializers.CharField(required=False, default='')
    city = serializers.CharField(required=False, default='')
    zip = serializers.CharField(required=False, default='')
    geo_polygons = PolygonsField(required=False, default=None)
    viewport = serializers.CharField(required=False, default='')
    zoom = serializers.FloatField(required=False, default=None)

    # Filters
    prop_type2 = serializers.ChoiceField(required=False, default='',
                                         choices=[('', ''),
                                                  ('condo-apt', 'Condo/Apt'),
                                                  ('house-duplex', 'House/Duplex')]
                                         )
    cleaned_prop_type = MultipleChoiceListField(choices=FrontendCleanedPropType.choices, default=[])
    price_min = serializers.FloatField(required=False, default=None, min_value=0, max_value=20000000)
    price_max = serializers.FloatField(required=False, default=None, min_value=0, max_value=20000000)
    above_price = serializers.BooleanField(default=False, initial=False)
    below_price = serializers.BooleanField(default=False, initial=False)
    price_reduced_recently = serializers.BooleanField(default=False, initial=False)
    beds_min = serializers.FloatField(required=False, default=None, min_value=0, max_value=20)
    beds_max = serializers.FloatField(required=False, default=None, min_value=0, max_value=20)
    beds_exact = TextInputListField(
        child=serializers.FloatField(required=False, default=None, min_value=0, max_value=20),
        required=False, default=None,
    )
    baths_min = serializers.FloatField(required=False, default=None, min_value=0, max_value=20)
    year_built_min = serializers.IntegerField(required=False, default=None, min_value=1600, max_value=2100)
    year_built_max = serializers.IntegerField(required=False, default=None, min_value=1600, max_value=2100)
    build_size_min = serializers.FloatField(required=False, default=None)
    build_size_max = serializers.FloatField(required=False, default=None)
    lot_size_min = serializers.FloatField(required=False, default=None, min_value=0, max_value=20000000)
    lot_size_max = serializers.FloatField(required=False, default=None, min_value=0, max_value=20000000)
    price_per_sqft_min = serializers.FloatField(required=False, default=None, min_value=0, max_value=20000000)
    price_per_sqft_max = serializers.FloatField(required=False, default=None, min_value=0, max_value=20000000)
    hoa_fee_max = serializers.FloatField(required=False, default=None, min_value=0, max_value=20000000)
    include_incomplete_hoa = serializers.BooleanField(default=True, initial=True)
    keywords = serializers.CharField(required=False, default='')
    amenities = serializers.CharField(required=False, default='')

    # seo: facets related to amenity/beds/price filter
    facets = TextInputListField(
        child=serializers.CharField(required=False, default=''),
        required=False, default=None,
    )
    near_me = serializers.BooleanField(default=False, initial=False)
    user_location = serializers.JSONField(required=False, default=None)
    user_county = serializers.HiddenField(default=None)

    # select boxes: opportunity types. will be combined with OR
    # initial state: all False, because we don't want to select any option from the start
    is_good_deal = serializers.BooleanField(default=False, initial=False)
    is_55_plus = serializers.BooleanField(default=False, initial=False)
    is_rehab = serializers.BooleanField(default=False, initial=False)
    is_cash_only = serializers.BooleanField(default=False, initial=False)
    is_tenant_occupied = serializers.BooleanField(default=False, initial=False)
    parking = serializers.BooleanField(default=False, initial=False)
    pet_friendly = serializers.BooleanField(default=False, initial=False)
    furnished = serializers.BooleanField(default=False, initial=False)
    short_sale = serializers.BooleanField(default=False, initial=False)
    new_construction = serializers.BooleanField(default=False, initial=False)

    # opportunity type filters. will be combined with AND
    hide_is_55_plus = serializers.BooleanField(default=False, initial=False)
    hide_is_rehab = serializers.BooleanField(default=False, initial=False)
    hide_is_cash_only = serializers.BooleanField(default=False, initial=False)
    hide_is_tenant_occupied = serializers.BooleanField(default=False, initial=False)

    luxury = serializers.BooleanField(default=False, initial=False)
    cheap = serializers.BooleanField(default=False, initial=False)
    loft = serializers.BooleanField(default=False, initial=False)
    utilities = serializers.BooleanField(default=False, initial=False)
    gated_community = serializers.BooleanField(default=False, initial=False)
    short_term = serializers.BooleanField(default=False, initial=False)

    # Filters only allowed for Trail/Premium users
    cap_rate_min = serializers.FloatField(required=False, default=None, min_value=0, max_value=1)
    predicted_rent_min = serializers.IntegerField(required=False, default=None, min_value=0, max_value=25000)
    cash_on_cash_min = serializers.FloatField(required=False, default=None, min_value=0, max_value=1)

    # Values used in ES sorting when sort_field in ('cash_on_cash', 'total_return')
    down_payment = serializers.FloatField(required=False, default=None, min_value=0.2, max_value=0.5)
    financing_years = serializers.IntegerField(required=False, default=None, min_value=15, max_value=30)
    statuses = serializers.HiddenField(default=['for_sale', 'under_contract'])

    def _parse_georect(self, georect_str):
        """
        Parse geo rectangle points from text value in correct order
        """
        georect = []
        if georect_str:
            try:
                georect = [float(c) for c in georect_str.strip().split(',')]
                if georect[0] > georect[2]:
                    # replace points if format is incorrect
                    georect = [georect[2], georect[3],
                               georect[0], georect[1]]
            except (ValueError, TypeError, AttributeError, IndexError):
                raise ValidationError('Incorrect viewport format')
        return georect

    def validate(self, data):
        type_ = data['type']
        state_id = data['state_id']
        county = data['county']
        city = data['city']
        zip_ = data['zip']
        financing_years = data['financing_years']
        down_payment = data['down_payment']
        amenities = data['amenities']
        zoom = data['zoom']

        data['viewport'] = self._parse_georect(data['viewport'])

        # if zero sized viewport, disable it
        if vp := data['viewport']:
            if vp[0] == vp[2] and vp[1] == vp[3]:
                data['viewport'] = []

        if data['user_location'] and not isinstance(data['user_location'], dict):
            raise ValidationError('user_location invalid format')

        if zoom is not None:
            if zoom < 1:
                data['zoom'] = 1
            if zoom > 22:
                data['zoom'] = 22

        if type_ == "state" \
                and not state_id:
            raise ValidationError('Incorrect state search query most probably '
                                  'cause you did not indicate state_id field')

        if type_ == "county" \
                and not state_id \
                and not county:
            raise ValidationError('Incorrect county search query most probably'
                                  'you should indicate state_id and county fields')
        if type_ == "city" \
                and not state_id \
                and not county \
                and not city:
            raise ValidationError('Incorrect city search query most probably'
                                  'you should indicate state_id county and city fields')
        if type_ == "zip" \
                and not zip_:
            raise ValidationError('Incorrect zip search query most probably '
                                  'cause you did not indicate zip field')

        if type_ == "geo" and data['near_me']:
            user_state, user_county, user_city = self.find_user_city(data)
            data['state_id'] = user_state.lower()
            data['city'] = user_city
            # search will be performed by state_id/city, user_county is required for SEO widget
            data['user_county'] = user_county

        if financing_years:
            allowed = (15, 30)
            if financing_years not in allowed:
                raise ValidationError({
                    'financing_years': [f'Value not allowed. Allowed values: {allowed}'],
                })
            if down_payment is None:
                raise ValidationError({
                    'down_payment': ['Required because financing_years is specified'],
                })

        if down_payment:
            allowed = (0.2, 0.3, 0.4, 0.5)
            if down_payment not in allowed:
                raise ValidationError({
                    'down_payment': [f'Value not allowed. Allowed values: {allowed}'],
                })
            if down_payment is None:
                raise ValidationError({
                    'financing_years': ['Required because down_payment is specified'],
                })

        data['cleaned_amenities'] = []
        data['keyword_amenities'] = []
        if amenities:
            requested_amenities_set = sorted(set(amenities.lower().split(',')))
            for amenity in requested_amenities_set:
                if amenity not in Amenities:
                    raise ValidationError({
                        'amenities': ['Unknown amenity: ' + amenity]
                    })
                if amenity in CLEANED_AMENITIES:
                    # amenity can be found in cleaned_amenities field;
                    # with-pool, with-basement will be replaced with pool, basement
                    data['cleaned_amenities'].append(amenity.replace('with-', ''))
                else:
                    # amenity can be found only by keywords
                    data['keyword_amenities'].append(amenity)
        pt = data['cleaned_prop_type']
        if data['index'] == PropEsIndex.SEARCH_RENT:
            if 'condos' in pt:
                raise ValidationError('You cant choose "condos" in rent index')
            data['statuses'] = ['for_rent', 'under_contract']
        else:
            if 'apartments' in pt:
                raise ValidationError('You cant choose "apartments" in not rent index')

        return super().validate(data)

    def get_location_str(self, replace_near_me=False):
        ''' return string representation of place where we search for properties.
            useful to debug "near-me" location '''
        data = self.data
        type_ = data['type']
        state_id = data['state_id'].upper()
        if type_ == 'zip':
            return '{}, {}'.format(data['zip'], state_id)
        elif type_ == 'state':
            return states_from_short.get(state_id)
        elif type_ == 'county':
            return '{}, {}'.format(unurlify(data['county']), state_id)
        elif type_ == 'city':
            return '{}, {}'.format(unurlify(data['city']), state_id)
        elif type_ == 'geo':
            if not data['near_me']:
                # geo search on map
                return ''
            elif replace_near_me:
                return '{}, {}'.format(unurlify(data['city']), state_id)
            else:
                return 'Near Me'

    def find_user_city(self, data):
        """
        request google reverse-geocoder for city.
        san-francisco is default if location is undefined or outside the US
        """
        city = 'san-francisco'
        county = 'san-francisco-county'
        state_id = 'CA'
        user_location = data['user_location']
        if not user_location or not user_location.get('lat') or not user_location.get('lon'):
            return state_id, county, city

        # NOTE: it's bad to create one more connection here. better reuse connection from search view
        cursor = connections['prop_db_rw'].cursor()
        location = geocode(cursor, coords=user_location)
        if not location:
            return state_id, county, city

        address = location['address_components']
        country = [x for x in address if x['types'] == ['country', 'political']]
        if not country or country[0]['short_name'] != 'US':
            return state_id, county, city

        try:
            state_id = [
                x for x in address if x['types'] == ['administrative_area_level_1', 'political']
            ][0]['short_name']
            county = [
                x for x in address if x['types'] == ['administrative_area_level_2', 'political']
            ][0]['short_name']
            if county.endswith(' County'):
                county = county.replace(' County', '')

            if possible_cities := [
                    x for x in address if x['types'] == ['locality', 'political']]:
                city = possible_cities[0]['long_name']
            else:
                city = [
                    x for x in address if x['types'] == [
                        'political', 'sublocality', 'sublocality_level_1']
                ][0]['long_name']
        except IndexError:
            # city not found
            city = 'san-francisco'
            county = 'san-francisco-county'
            state_id = 'CA'

        return urlify(state_id), urlify(county, is_county=True), urlify(city)


class SearchQuerySerializer(BasePropertyElasticSerializer):
    """
    For Search view
    """
    map_query = serializers.BooleanField(default=False)
    sort_field = serializers.ChoiceField(required=False, default='default_sort',
        choices=[('default_sort', 'Default Sort'),
                 ('price', 'Price'),
                 ('year_built', 'Year Built'),
                 ('list_date', 'List Date'),
                 ('update_date', 'Update Date'),
                 ('scoring', 'Scoring'),
                 ('building_size', 'Building Size'),
                 ('beds', 'Beds'),

                 ('predicted_rent', 'Predicted Rent'),
                 ('cap_rate', 'Cap Rate'),
                 ('cash_on_cash', 'Cash on Cash'),
                 ('total_return', 'Total Return')]
    )
    sort_direction = serializers.ChoiceField(required=False, default='desc',
        choices=[('asc', 'ASC'),
                 ('desc', 'DESC')]
    )
    start = serializers.IntegerField(default=0)

    def validate(self, data):
        data = super().validate(data)

        max_possible_start = MAX_RESULT_WINDOW - RESULTS_PER_PAGE
        if data['start'] > max_possible_start:
            data['start'] = max_possible_start

        # if zero sized viewport, force map_query to False
        if vp := data['viewport']:
            if vp[0] == vp[2] and vp[1] == vp[3]:
                data['map_query'] = False

        sort_field = data['sort_field']
        sort_direction = data['sort_direction']
        if sort_field and not sort_direction:
            raise ValidationError('Sort direction and sort field are required')

        return data


class InsightsSerializer(BasePropertyElasticSerializer):
    """
    For Insights view
    """
    insights = MultipleChoiceListField(choices=InsightType.choices, required=False)

    def validate(self, data):
        """
        - check that requested insights are available for the requested index
        - set all available insights for the requested index if 'insights' field is empty
        """
        index = data['index']
        if not data.get('insights'):
            data['insights'] = []
        else:
            requested_insights = set(data['insights'])
            available_insights = set(INDEX_INSIGHTS[index])
            if outlaw_insights := requested_insights - available_insights:
                insights = ', '.join(outlaw_insights)
                raise ValidationError({'insights': f'Not available for {index} index: {insights}'})

            data['insights'] = list(set(data['insights']))
        return super().validate(data)


class MortgageSerializer(serializers.Serializer):

    down_payment = serializers.FloatField(required=True)
    financing_years = serializers.IntegerField(required=True)
    interest_rate = serializers.FloatField(required=True)
    prop_details = serializers.JSONField(required=True)

    def validate(self, data):

        prop_details = data['prop_details']

        try:
            if len(prop_details) == 0:
                raise ValidationError('Empty prop_details list')

            if len(prop_details) > 20:
                raise ValidationError('Prop_details list so long')

            for prop in prop_details:
                if not isinstance(prop['prop_id'], str):
                    raise ValidationError('Incorrect variable number format')
                if not isinstance(prop['price'], (int, float)):
                    raise ValidationError('Incorrect variable number format')
                if not isinstance(prop['market_rent'], (int, float)):
                    raise ValidationError('Incorrect variable number format')

        except Exception:
            raise ValidationError('Incorrect prop_details JSON format')

        return data
