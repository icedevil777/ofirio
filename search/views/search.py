import json
import logging
from copy import deepcopy
from datetime import datetime

from django.contrib import messages
from django.db import connections
from ofirio_common.constants import RESULTS_PER_PAGE
from ofirio_common.enums import PropEsIndex
from ofirio_common.geocode import (
    extract_points_from_geo_shape, get_rect_from_google_location, geocode,
)
from ofirio_common.helpers import url_to_cdn
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

import common.tasks as tasks
from api_property.common.common import get_estimated_mortgage, format_listing_office
from api_property.common.rebates import get_rebate_for_view
from account.enums import UserAccessStatus
from account.models import FavoriteProperty
from account.utils import get_access_status
from common.cache import cache_method_unauth
from common.utils import get_msg_json
from search.common import ElasticConstructor, InsightsHandler
from search.common.common import get_badges_search
# from search.seo.overview import get_overview
from search.enums import InsightType
from search.seo.generators import SeoGenerator
from search.seo.linking_widget import get_seo_links_from_serializer
from search.constants import (
    MAP_ITEMS_LIMIT, PAID_ONLY_FILTERS, PAID_ONLY_SORTS,
)
from search.serializers import SearchQuerySerializer
from search.utils import (
    es_grid_centroid_to_geojson, es_items_to_nested_geojson, estimate_cluster_precision,
    group_close_points, request_elastic, round_distance,
)

logger = logging.getLogger(__name__)


class Search(APIView):
    """
    Search for properties using ElasticSearch
    """
    serializer_class = SearchQuerySerializer

    @cache_method_unauth
    def post(self, request, *args, **kwargs):
        user = request.user
        self.serializer = self.serializer_class(data=request.data)
        # print('self.serializer', self.serializer)
        self.access_status = get_access_status(user)
        is_valid, data, code = self.validate()

        if not is_valid:
            return Response(data, status=code)

        if user.is_authenticated:
            print('user.is_authenticated')
            # tasks.track_search.delay(user.email, self.serializer.data)

        self.es_constructor = ElasticConstructor(self.serializer)
        
        

        center, geo_shape = self.get_geo_shape()

        print('center', center)

        favorite_ids = self.get_favorite_ids(user)


        # main response
        data = self.get_main_response(geo_shape, user, favorite_ids)
        print('data', data)
        total = data['search']['total']
        print('total', total)
        bounds = data['bounds']

        # map response
        if self.serializer.data['map_query']:  # if map query required
            data['map'] = self.get_map_response(
                total, geo_shape, user, favorite_ids, bounds
            )

        # similar nearby
        if total <= 10:
            exclude_ids = [x['prop_id'] for x in data['search']['items']]
            sim_nearby = self.get_sim_nearby(
                bounds, favorite_ids, center, exclude_ids)
            if sim_nearby['items']:
                data['sim_nearby'] = sim_nearby

        return Response(data, status=status.HTTP_200_OK)

    def get_main_response(self, geo_shape, user, favorite_ids):
        """
        Construct basis of the response data
        """
        
        index = self.serializer.validated_data['index']

        # insights data needed for widget_info and seo bottom_text
        try:
            insights_data = InsightsHandler(self.es_constructor).get_insights(index)
                
        except NotFound:
            insights_data = {}

        # ES body, to show items on website side panel
        search_body = self.construct_search_body()
        search_results, total, aggs = self.request_es_items(
            search_body, index, user, favorite_ids,
        )
        true_location = self.serializer.get_location_str(replace_near_me=True)
        data = {
            'mode': self.access_status,
            'seo': self.get_seo(total, insights_data),
            'widget_info': insights_data.get('widget_info'),
            'search': {
                'total': total,
                'start': self.serializer.data['start'],
                'location': true_location,  # tmp for near-me testing
                'items': search_results,
            },
            'geo_shape': geo_shape,
            'meta': get_seo_links_from_serializer(self.serializer),
            'bounds': self.get_bounds(aggs, geo_shape),
            'page': 1 + self.serializer.data['start'] / RESULTS_PER_PAGE,
            # this is old implementation of bottom text generation:
            # 'overview': get_overview(self.serializer.validated_data, total),
        }
        print('data', data)
        return data

    def get_sim_nearby(self, bounds, favorite_ids, center, exclude_ids):
        """
        Return similar properties nearby
        """
        items = []
        map_items = []
        max_distance = 0
        index = self.serializer.validated_data['index']

        if body := self.es_constructor.get_sim_nearby_es_body(center, bounds, exclude_ids):
            es_response = request_elastic(body, index=index)

            for hit in es_response['hits']['hits']:
                src = hit['_source']
                distance = hit.get('sort', [None])[0]

                item = self._construct_item(
                    src, favorite_ids, index=index, for_map=False)
                map_item = self._construct_item(
                    src, favorite_ids, index=index, for_map=True)

                item['center_distance'] = map_item['center_distance'] = round_distance(
                    distance)
                max_distance = distance if (
                    distance or 0) > max_distance else max_distance

                items.append(item)
                map_items.append(map_item)

        sim_nearby = {
            'items': items,
            'map': es_items_to_nested_geojson(map_items),
            'within': round_distance(max_distance),
        }
        return sim_nearby

    def get_map_response(self, total, geo_shape, user, favorite_ids, bounds):
        """
        Construct 'map' part of the response -
        properties or clusters to draw on the map
        """
        index = self.serializer.validated_data['index']
        viewport = self.serializer.validated_data['viewport']
        zoom = self.serializer.validated_data['zoom']
        map_body = self.construct_map_body()

        if total > MAP_ITEMS_LIMIT:  # form clusters if too many items
            cluster_buckets = self.get_cluster_buckets(map_body, index, bounds, zoom, viewport,
                                                       geo_shape)
            map_response = es_grid_centroid_to_geojson(cluster_buckets)

        else:  # form regular items
            map_results, _, _ = self.request_es_items(map_body, index, user,
                                                      favorite_ids, for_map=True)
            map_response = es_items_to_nested_geojson(map_results)

        return map_response

    def get_seo(self, total, insights_data):
        """
        Return title tag, description for meta tag and h1
        """
        generator = SeoGenerator(self.serializer, total, insights_data)
        seo = generator.generate_bottom_text()
        seo.update(generator.generate_tags())
        return seo

    def get_bounds(self, aggs, geo_shape):
        """
        Combine property edges from the aggregation with geo shape points
        and determine bounds of that overall point list
        """
        if self.serializer.validated_data['type'] == 'geo':
            if viewport := self.serializer.validated_data['viewport']:
                return viewport

        bounds = None
        shape_points = extract_points_from_geo_shape(geo_shape)

        prop_edge_points = []
        if aggs and aggs.get('min_lon', {}).get('value') is not None:
            prop_edge_points = [(aggs['min_lon']['value'], aggs['min_lat']['value']),
                                (aggs['max_lon']['value'], aggs['max_lat']['value'])]

        if points := shape_points + prop_edge_points:
            lons, lats = zip(*points)
            bounds = [min(lats), min(lons), max(lats), max(lons)]

        if bounds is None:  # then geocode and get bounds from the returned location
            data = self.serializer.validated_data
            address = ' '.join(
                [data['zip'], data['city'], data['county'], data['state_id']])
            with connections['prop_db_rw'].cursor() as cursor:
                location = geocode(cursor, address=address)
                bounds = get_rect_from_google_location(location)

        return bounds

    def get_geo_shape(self):
        """
        Return geo boundaries and center point of requested region
        """

        def select_geo_shape(cursor):
            res = cursor.fetchone()
            if not res:
                return None, None, None
            try:
                if res[2]:
                    # return lat, lon, shape
                    return res[0], res[1], json.loads(res[2])
                return res[0], res[1], None
            except Exception as exc:
                logger.error('get_geo_shape: Failed to read json from db:')
                logger.exception(exc)

        lat = lon = geo_shape = None
        data = self.serializer.validated_data
        cursor = connections['prop_db'].cursor()

        print('cursor', cursor)
        type_ = data['type']
        state_id = data['state_id']

        if type_ == 'zip':
            zip_code = data['zip']
            sql = '''
                select lat, lon, geo_shape from zip_boundaries
                where state_id = %(state_id)s and
                      zip = %(zip_code)s
                limit 1
            '''
            cursor.execute(sql, {'state_id': state_id.upper(),
                                 'zip_code': zip_code,
                                 })
            lat, lon, geo_shape = select_geo_shape(cursor)

        elif type_ in ('state', 'county', 'city') or (type_ == 'geo' and data['city']):
            county = data['county']
            city = data['city']
            sql = '''
                select lat, lon, geo_shape from geo_boundaries
                where boundary_type = %(type)s and
                      state_id = %(state_id)s
                      {} {}
                limit 1
            '''.format('and county_url = %(county)s' if county else '',
                       'and city_url = %(city)s' if city else '')
            cursor.execute(sql, {'type': 'city' if type_ == 'geo' else type_,
                                 'state_id': state_id.upper(),
                                 'county': county,
                                 'city': city,
                                 })
            lat, lon, geo_shape = select_geo_shape(cursor)

        return (lat, lon), geo_shape

    def request_es_items(self, body, index, user, favorite_ids, for_map=False):
        """
        Method to request ES without aggregations.
        Resulting items are constructed according to user access status
        """
        items = []
        es_response = request_elastic(body, index=index)
        hits = es_response['hits']['hits']
        aggs = es_response.get('aggregations')
        total = es_response['hits']['total']['value']

        for hit in hits:
            item = self._construct_item(
                hit['_source'], favorite_ids, index=index, for_map=for_map,
            )
            items.append(item)

        return items, total, aggs

    def _construct_item(self, source, favorite_ids, index=None, for_map=False):
        """
        Construct resulting item according to provided access status
        """
        item = {}
        composite_fields = self.es_constructor.get_composite_fields()

        item['previews'] = source.get('previews', [])
        if (street_view := source.get('street_view')) and not item['previews']:
            item['previews'] = [street_view]
        if for_map and item['previews']:
            item['previews'] = item['previews'][0]
        item['previews'] = url_to_cdn(item['previews'])

        item['prop_id'] = source['prop_id']
        item['state_id'] = source['state_id']
        item['building_size'] = source['building_size']
        item['address'] = source['address']
        item['geo_point'] = source['geo_point']
        item['price'] = source['price']
        item['beds'] = source['beds']
        item['baths'] = source['baths']
        item['price_change'] = source.get('price_change')
        item['parkings'] = source.get('parkings')
        item['scoring'] = source.get('scoring')
        item['estimated_mortgage'] = get_estimated_mortgage(source.get('is_cash_only', False),
                                                            source.get('month_loan_payments'))
        if index == PropEsIndex.SEARCH_RENT:
            item['pet_friendly'] = source['pet_friendly']
            item['parking'] = source['parking']
            item['laundry'] = 'laundry' in source['cleaned_amenities']

        if not for_map:  # for search results in left panel
            list_dt = datetime.strptime(source['list_date'][:10], '%Y-%m-%d')
            item['favorite'] = source['prop_id'] in favorite_ids
            item['status'] = source.get('status')
            item['list_date'] = source['list_date']
            item['update_date'] = source.get('update_date')
            item['badges'] = get_badges_search(
                source.get('badges'), source['list_date'])
            item['prop_type2'] = source['prop_type2']
            item['cleaned_prop_type'] = source['cleaned_prop_type']
            item['city'] = source['city']
            item['county_name'] = source['county_name']
            item['zip'] = source['zip']
            item['days_on_market'] = (datetime.now() - list_dt).days
            item['zip'] = source['zip']
            item['pet_friendly'] = source['pet_friendly']
            item['parking'] = source['parking']
            # item['laundry'] = 'laundry' in source['cleaned_amenities']
            item['listing_office'] = format_listing_office(
                source.get('listing_office'), source.get('status'))

        # place field only for Invest to reduce response size
        if index == PropEsIndex.SEARCH_INVEST:
            item['is_blurred'] = True  # to hide fields on client

            paid = self.access_status == UserAccessStatus.PREMIUM
            if paid or not source.get('is_high_cap_rate'):
                item['is_blurred'] = False
                item['predicted_rent'] = source.get('predicted_rent')
                item['cash_on_cash'] = source.get(
                    composite_fields['cash_on_cash'])
                item['total_return'] = source.get(
                    composite_fields['total_return'])
                item['cap_rate'] = source.get(composite_fields['cap_rate'])

        if index in (PropEsIndex.SEARCH_INVEST, PropEsIndex.SEARCH_BUY):
            item['rebate'] = get_rebate_for_view(
                source['zip'], item['price'], off_market=False)

        return item

    def get_cluster_buckets(self, map_body, index, bounds, zoom, viewport, geo_shape):
        """
        Construct cluster ES body, request Elastic, and group resulting clusters
        """
        cluster_body = self.construct_cluster_body(
            map_body, bounds, zoom, viewport)
        cluster_results = request_elastic(cluster_body, index)
        cluster_buckets = cluster_results['aggregations']['cluster_agg']['buckets']

        if viewport:
            diagonal_by = [viewport[:2], viewport[2:]]
            treshold = 0.04
        elif geo_shape_points := extract_points_from_geo_shape(geo_shape):
            diagonal_by = geo_shape_points
            treshold = 0.07
        else:
            diagonal_by = None
            treshold = 0.1

        buckets = self.group_close_cluster_buckets(
            cluster_buckets, treshold, diagonal_by)
        return buckets

    def group_close_cluster_buckets(self, cluster_buckets, treshold, diagonal_by=None):
        """
        Convert bucket to format accepted by group_close_points(),
        call it, then convert them back, calculating new doc_count and edges
        """
        points_dict = {}
        for bucket in cluster_buckets:
            location = bucket['centroid_agg']['location']
            point = (location['lat'], location['lon'])
            points_dict[point] = bucket

        groups = group_close_points(points_dict, treshold, diagonal_by)
        result_buckets = []

        for point, point_buckets in groups.items():
            point_total = 0
            lats = []
            lons = []
            for bucket in point_buckets:
                point_total += bucket['doc_count']
                lats.extend([bucket['min_lat']['value'],
                            bucket['max_lat']['value']])
                lons.extend([bucket['min_lon']['value'],
                            bucket['max_lon']['value']])

            bucket['centroid_agg']['location']['lat'] = point[0]
            bucket['centroid_agg']['location']['lon'] = point[1]
            bucket['doc_count'] = point_total
            bucket['centroid_agg']['count'] = point_total
            bucket['min_lat'] = {'value': min(lats)}
            bucket['max_lat'] = {'value': max(lats)}
            bucket['min_lon'] = {'value': min(lons)}
            bucket['max_lon'] = {'value': max(lons)}

            result_buckets.append(bucket)

        return result_buckets

    def validate(self):
        """
        Serializer and access status validation
        """
        is_valid = True
        data = {}
        code = None

        if not self.serializer.is_valid():
            messages.error(self.request, 'Error! Incorrect Search Query')
            is_valid = False
            data = {'errors': self.serializer.errors,
                    'server_messages': get_msg_json(self.request)}
            code = status.HTTP_400_BAD_REQUEST

        # all *registered* users are allowed to use all filters and sorting
        elif self.access_status == UserAccessStatus.ANON:
            # and there is any paid-only filter
            if any(self.serializer.data[fltr] is not None for fltr in PAID_ONLY_FILTERS):
                is_valid = False
                code = status.HTTP_403_FORBIDDEN
            # or any paid-only sorting
            elif self.serializer.data['sort_field'] in PAID_ONLY_SORTS:
                is_valid = False
                code = status.HTTP_403_FORBIDDEN

        return is_valid, data, code

    def construct_search_body(self):
        """
        Construct ES body dict that returns results for the website side panel
        """
        body = {
            'size': RESULTS_PER_PAGE,
            'from': self.serializer.data['start'],
            'track_total_hits': True,
            'query': self.es_constructor.get_es_query(),
            'sort': self.es_constructor.get_es_sort(),
            'aggs': self.es_constructor.get_es_aggs(),
        }
        return body

    def construct_map_body(self):
        """
        Construct ES map body dict that returns results to show on website map
        """
        body = {
            'size': MAP_ITEMS_LIMIT,
            'from': 0,  # search always from 0
            'query': self.es_constructor.get_es_query(),
            # only default sort for map
            'sort': {'default_sort': {'order': 'desc'}},
            'aggs': {},
        }
        return body

    def construct_cluster_body(self, map_body, bounds, zoom, viewport):
        """
        Construct ES map body dict with geohash_grid aggregation
        """
        body = deepcopy(map_body)
        precision = self.get_precision(bounds, zoom, viewport)
        body['size'] = 0
        body['aggs']['cluster_agg'] = {
            'geotile_grid': {
                'field': 'geo_point', 'precision': precision,
            },
            'aggs': {
                'centroid_agg': {'geo_centroid': {'field': 'geo_point'}},
                'min_lat': {'min': {'script': 'doc["geo_point"].lat'}},
                'max_lat': {'max': {'script': 'doc["geo_point"].lat'}},
                'min_lon': {'min': {'script': 'doc["geo_point"].lon'}},
                'max_lon': {'max': {'script': 'doc["geo_point"].lon'}},
            },
        }
        return body

    def get_precision(self, bounds, zoom, viewport):
        """
        Decide what precision to use based on:
        - prop geo bounds
        - zoom level, if viewport and zoom are available
        - geo_shape bounds, if geo_shape has boundary
        """
        if viewport and zoom:
            precision = zoom + 1
        else:
            points = [(bounds[0], bounds[1]), (bounds[2], bounds[3])]
            precision = estimate_cluster_precision(points)
        return precision

    def get_favorite_ids(self, user):
        """
        If user authentificated, get their favorite property IDs
        """
        ids = []
        if user.is_authenticated:
            ids = FavoriteProperty.objects.filter(
                user=user).values_list('prop_id', flat=True)
        return ids
