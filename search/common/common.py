import logging
from copy import deepcopy
from datetime import timedelta, datetime
from unittest import mock

from django.utils import timezone
from ofirio_common.enums import PropEsIndex
from ofirio_common.geocode import calc_center
from rest_framework import exceptions

from api_property.common.common import clean_badges
from search.constants import PROP_TYPE_FRONTEND_MAPPING
from search.utils import prepare_polygon
from common.utils import get_is_test_es_filter


logger = logging.getLogger(__name__)


class ElasticConstructor:
    """
    A converter from request values to Elasticsearch body
    """
    _composite_fields = None
    _geo_shape = None
    _es_query = None
    _es_must = None
    _es_filter = None
    _es_should = None
    _es_sort = None
    _es_aggs = {}
    _sim_nearby_body = None

    def __init__(self, serializer):
        """
        Expect a serializer subclassed from BasePropertyElasticSerializer
        """
        self.data = serializer.validated_data

    def get_composite_fields(self):
        """
        Some fields in ES are identical by nature but have different value,
        because they are precalculated for different cases.
        This method constructs correct Elasticsearch field names
        based on input values (currently financing_years and down_payment).
        """
        if self._composite_fields is None:
            names = 'cash_on_cash', 'total_return', 'cap_rate'
            self._composite_fields = {name: name for name in names}  # default values
            financing_years = self.data['financing_years']
            down_payment = self.data['down_payment']
            if financing_years is not None and down_payment is not None:
                for name in names:
                    field = f'{name}_{financing_years}_{int(down_payment * 100)}'
                    self._composite_fields[name] = field
        return self._composite_fields

    def get_es_query(self):
        """
        Construct 'query' part for ES body
        """
        if self._es_query is None:
            es_should = self.get_es_should()
            self._es_query = {
                'bool': {
                    'must': self.get_es_must(),
                    'filter': self.get_es_filter() + get_is_test_es_filter(),
                    'should': es_should,
                    'minimum_should_match': int(bool(es_should)),
                }
            }
        return self._es_query

    def get_es_must(self):
        """
        Construct 'must' value for ES body.
        Represents list of filters combined using logical OR.
        See examples in unit tests for the explanation
        """
        if self._es_must is None:

            badges = ('is_55_plus', 'is_rehab', 'is_cash_only', 'is_tenant_occupied')

            # opportunity types are combined with OR. only True values considered
            opp_types = badges + ('is_good_deal',)

            # filters are combined with AND. only True values considered
            filters = tuple('hide_' + b for b in badges) + ('parking', 'pet_friendly',
                                                            'furnished', 'short_sale',
                                                            'new_construction', 'gated_community')
            should = []
            for opp_type in opp_types:
                if self.data[opp_type] is True:
                    should.append({'term': {opp_type: True}})

            self._es_must = []
            for fltr in filters:
                if (value := self.data[fltr]) is True:
                    if fltr.startswith('hide_'):
                        fltr = fltr.replace('hide_', '')
                        value = False
                    self._es_must.append({'term': {fltr: value}})

            if should:
                self._es_must.append({'bool': {'should': should}})

            if self.data['utilities']:
                signs = ('utilities included', 'utilities and taxes include',
                         'utilities and taxes included', 'includes all utilities',
                         'include all utilities', 'rent include utilities',
                         'rent includes utilities', 'includes all the utilities')
                self._es_must.append(
                    {'query_string': {
                        'query': '"' + '" OR "'.join(signs) + '"', 'default_field': 'description'},
                    }
                )

            # keywords
            if queries := self._construct_keyword_queries():
                self._es_must.append({'bool': {'should': queries}})

        return self._es_must

    def get_es_filter(self):
        """
        Construct dict for the 'filter' param in ES body
        """
        if self._es_filter is None:

            composite_fields = self.get_composite_fields()

            self._es_filter = []
            state_id = self.data['state_id']
            county = self.data['county']
            city = self.data['city']
            zip_ = self.data['zip']

            self._es_filter.append({'term': {'state_id': 'FL'}})
            if state_id:
                self._es_filter.append({'term': {'state_id': state_id.upper()}})
            if county:
                self._es_filter.append({'term': {'county_url': county}})
            if city:
                self._es_filter.append({'term': {'city_url': city}})
            if zip_:
                self._es_filter.append({'term': {'zip': zip_}})

            if viewport := self.data['viewport']:
                self._es_filter.append(
                    {'geo_bounding_box': {
                        'geo_point': {
                            'bottom_left': {'lat': viewport[0], 'lon': viewport[1]},
                            'top_right': {'lat': viewport[2], 'lon': viewport[3]},
                        }
                    }}
                )
            if statuses := self.data['statuses']:
                self._es_filter.append({'terms': {'status': statuses}})

            if prop_type2 := self.data['prop_type2']:
                self._es_filter.append({'term': {'prop_type2': prop_type2}})
            if cleaned_prop_type := self.data['cleaned_prop_type']:
                remapped_types = [PROP_TYPE_FRONTEND_MAPPING[t] for t in cleaned_prop_type]
                self._es_filter.append({'terms': {'cleaned_prop_type': remapped_types}})

            if price_min := self.data['price_min']:
                self._es_filter.append({'range': {'price': {'gte': price_min}}})
            if price_max := self.data['price_max']:
                self._es_filter.append({'range': {'price': {'lte': price_max}}})

            if self.data['above_price']:
                self._es_filter.append({'range': {'diff_price': {'gt': 0}}})
            if self.data['below_price']:
                self._es_filter.append({'range': {'diff_price': {'lt': 0}}})
            if self.data['price_reduced_recently']:
                dt = (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                self._es_filter.append({'range': {'price_change_date': {'gte': dt}}})
                self._es_filter.append({'term': {'price_change': 'decrease'}})

            if (hoa_fee_max := self.data['hoa_fee_max']) is not None:
                self._es_filter.append({'range': {'hoa_fees': {'lte': hoa_fee_max}}})
            if self.data['include_incomplete_hoa'] is False:
                gte = 1 if hoa_fee_max is None or hoa_fee_max > 1 else hoa_fee_max
                self._es_filter.append({'range': {'hoa_fees': {'gte': gte}}})

            if beds_min := self.data['beds_min']:
                self._es_filter.append({'range': {'beds': {'gte': beds_min}}})
            if beds_max := self.data['beds_max']:
                self._es_filter.append({'range': {'beds': {'lte': beds_max}}})
            if beds_exact := self.data['beds_exact']:
                self._es_filter.append({'terms': {'beds': beds_exact}})
            if baths_min := self.data['baths_min']:
                self._es_filter.append({'range': {'baths': {'gte': baths_min}}})

            if year_built_min := self.data['year_built_min']:
                self._es_filter.append({'range': {'year_built': {'gte': year_built_min}}})
            if year_built_max := self.data['year_built_max']:
                self._es_filter.append({'range': {'year_built': {'lte': year_built_max}}})

            if build_size_min := self.data['build_size_min']:
                self._es_filter.append({'range': {'building_size': {'gte': build_size_min}}})
            if build_size_max := self.data['build_size_max']:
                self._es_filter.append({'range': {'building_size': {'lte': build_size_max}}})

            if lot_size_min := self.data['lot_size_min']:
                self._es_filter.append({'range': {'building_size': {'gte': lot_size_min}}})
            if lot_size_max := self.data['lot_size_max']:
                self._es_filter.append({'range': {'building_size': {'lte': lot_size_max}}})

            # if paid_user: #ONLY FOR PAID
            if cap_rate_min := self.data['cap_rate_min']:
                cap_rate_field = composite_fields['cap_rate']
                self._es_filter.append({'range': {cap_rate_field: {'gte': cap_rate_min}}})
            if predicted_rent_min := self.data['predicted_rent_min']:
                self._es_filter.append({'range': {'predicted_rent': {'gte': predicted_rent_min}}})
            if cash_on_cash_min := self.data['cash_on_cash_min']:
                cash_on_cash_field = composite_fields['cash_on_cash']
                self._es_filter.append({'range': {cash_on_cash_field: {'gte': cash_on_cash_min}}})

            if self.data['luxury']:
                if self.data['index'] == PropEsIndex.SEARCH_RENT:
                    self._es_filter.append({'range': {'price': {'gte': 5000}}})
                else:
                    self._es_filter.append({'range': {'price': {'gte': 850000}}})
            if self.data['cheap']:
                if self.data['index'] == PropEsIndex.SEARCH_RENT:
                    self._es_filter.append({'range': {'price': {'lte': 3000}}})
                else:
                    self._es_filter.append({'range': {'price': {'lte': 350000}}})

            if price_sqft_min := self.data['price_per_sqft_min']:
                self._es_filter.append({'range': {'price_per_sqft': {'gte': price_sqft_min}}})
            if price_sqft_max := self.data['price_per_sqft_max']:
                self._es_filter.append({'range': {'price_per_sqft': {'lte': price_sqft_max}}})
            if cleaned_amenities := self.data['cleaned_amenities']:
                self._es_filter.append(
                    {'match': {
                        'cleaned_amenities': {
                            'query': ' '.join(cleaned_amenities),
                            'operator': 'and',
                        }
                    }}
                )

        return self._es_filter

    def get_es_should(self):
        """
        Construct 'should' value for ES body.
        Represents list of geo polygons where we should search properties
        """
        if self._es_should is None:

            self._es_should = []
            geo_polygons = self.data['geo_polygons'] or []

            for polygon in geo_polygons:
                if polygon:
                    fixed_polygon = prepare_polygon(polygon)
                    if len(fixed_polygon) > 3:
                        shape = {
                            'geo_shape': {
                                'geo_point': {
                                    'shape': {
                                        'type': 'polygon',
                                        'coordinates': [fixed_polygon],
                                    }
                                }
                            }
                        }
                        self._es_should.append(shape)

            if geo_polygons and not self._es_should:  # none of provided polygons are valid
                raise exceptions.ValidationError(
                    {'geo_polygons': ['Not enough points, or they are in a line']}
                )

        return self._es_should

    def _construct_keyword_queries(self):
        """Construct 'match' filter for keywords"""
        queries = []
        search_words = ''

        # merge keywords + amenities
        if keywords := self.data['keywords'].lower():
            search_words += keywords.replace(',', ' ') + ' '
        if keywords := self.data['keyword_amenities']:
            search_words += ' '.join(keywords)

        # add filters
        if self.data['loft']:
            search_words += 'loft '

        if self.data['short_term']:
            search_words += 'short term '

        if search_words:
            for field in 'description', 'features_for_search', 'appliances':
                queries.append(
                    {'match': {field: {'query': search_words.strip(), 'operator': 'and'}}}
                )

        return queries

    def get_es_sort(self):
        """
        Construct value for 'sort' key in ES body
        """
        if self._es_sort is None:
            self._es_sort = {}

            if sort_field := self.data['sort_field']:
                sort_direction = self.data['sort_direction']
                composite_fields = self.get_composite_fields()

                if sort_field == 'default_sort':
                    sort_field = 'scoring'
                    sort_direction == 'desc'  # for default search sort only
                elif sort_field == 'cash_on_cash':
                    sort_field = composite_fields['cash_on_cash']
                elif sort_field == 'total_return':
                    sort_field = composite_fields['total_return']
                elif sort_field == 'cap_rate':
                    sort_field = composite_fields['cap_rate']

                self._es_sort = {sort_field: {'order': sort_direction}}

        return self._es_sort

    def get_es_aggs(self):
        """
        Construct value for 'aggs' key in ES body
        """
        if not self._es_aggs:
            if self.data['map_query']:
                self._es_aggs = {
                    'min_lat': {'min': {'script': 'doc["geo_point"].lat'}},
                    'max_lat': {'max': {'script': 'doc["geo_point"].lat'}},
                    'min_lon': {'min': {'script': 'doc["geo_point"].lon'}},
                    'max_lon': {'max': {'script': 'doc["geo_point"].lon'}},
                }
        return self._es_aggs

    def get_sim_nearby_es_body(self, center, bounds=None, exclude_ids=None):
        """
        Construct ES body for similar properties nearby
        """
        if not self._sim_nearby_body:

            if center := self._find_center(center, self.data['viewport'],
                                           self.data['geo_polygons'], bounds):
                geo_center = {'lat': center[0], 'lon': center[1]}

                query = deepcopy(self.get_es_query())
                self._remove_geo_filtering(query)
                query['bool']['filter'].append(
                    {'geo_distance': {'distance': '20mi', 'geo_point': geo_center}}
                )
                if exclude_ids:
                    query['bool']['must_not'] = [{'ids': {'values': exclude_ids}}]
                self._sim_nearby_body = {
                    'size': 10,
                    'query': query,
                    'sort': [{
                        '_geo_distance': {
                            'geo_point': geo_center,
                            'order': 'asc',
                            'unit': 'mi',
                            'ignore_unmapped': True,
                        }
                    }],
                }

        return self._sim_nearby_body

    def _remove_geo_filtering(self, query):
        """
        Remove from the 'filter' and 'should' all the geo filters
        """
        query_filter = query['bool']['filter']

        # gather indices to remove
        to_remove = set()
        for idx, item in enumerate(query_filter):
            if item.get('geo_bounding_box'):
                to_remove.add(idx)

            if term_keys := item.get('term', {}).keys():
                key = tuple(term_keys)[0]
                if key in ('county', 'county_url', 'city', 'city_url', 'zip'):
                    to_remove.add(idx)

        # remove found indices
        for idx in sorted(to_remove, reverse=True):
            del query_filter[idx]

        # similar approach with drawings in 'should'
        query_should = query['bool']['should']
        to_remove = set()
        for idx, item in enumerate(query_should):
            if item.get('geo_shape'):
                to_remove.add(idx)

        for idx in sorted(to_remove, reverse=True):
            del query_should[idx]

        if query['bool']['should'] == []:
            del query['bool']['should']
            del query['bool']['minimum_should_match']

    def _find_center(self, center, viewport, geo_polygons, bounds):
        points = []
        # currently disable region center
        #center_lat, center_lon = center
        #if center_lat and center_lon:
        #    # OT-2314: set priority geo shape center
        #    return center_lat, center_lon
        if gp := geo_polygons:
            # set highest priority to 'draw on map'
            points = sum(geo_polygons, [])
            center = calc_center(points)
            # NOTE: format here is (lon, lat), hence returned reversed
            return center[::-1]

        elif vp := viewport:
            # set higher priority to bounds
            points = [(vp[0], vp[1]), (vp[2], vp[3])]
        elif bn := bounds:
            # set lower priority to bounds
            points = [(bn[0], bn[1]), (bn[2], bn[3])]

        if points:
            center = calc_center(points)
            return center


def get_badges_search(badges, list_dt):
    if not badges:
        return []
    list_dt = datetime.strptime(list_dt, '%Y-%m-%dT%H:%M:%S')  # 2022-10-05T21:16:55
    list_badges = badges.split(',')
    if (gd_buy := 'good_deal_buy') in list_badges:
        list_badges.remove(gd_buy)
        list_badges.insert(0, gd_buy)
    elif (gd_invest := 'good_deal_invest') in list_badges:
        list_badges.remove(gd_invest)
        list_badges.insert(0, gd_invest)
    elif (gd_rent := 'good_deal_rent') in list_badges:
        list_badges.remove(gd_rent)
        list_badges.insert(0, gd_rent)
    return clean_badges(list_badges, list_dt)


def mock_is_hidden_true(func):
    def wrapper_func(*args, **kwargs):
        with mock.patch('psycopg2.connect') as mock_connect:
            mock_connect.cursor.return_value.fetchall.return_value = True
    return wrapper_func


def mock_is_hidden_false(func):
    def wrapper_func(*args, **kwargs):
        with mock.patch('psycopg2.connect') as mock_connect:
            mock_connect.cursor.return_value.fetchall.return_value = False
    return wrapper_func

