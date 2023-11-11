import logging

from django.contrib import messages
from ofirio_common.enums import AutocompleteCategory, AutocompletePropCategory, EsIndex
from ofirio_common.address_util import urlify, replace_synonyms
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from common.utils import get_msg_json, get_is_test_es_filter
from search.constants import AUTOCOMPLETE_PROP_CATEGORY_TO_COUNT_FIELD as CATEGORY_TO_COUNT_FIELD
from search.constants import AUTOCOMPLETE_TYPE_TO_ID_FIELD_MAPPING as TYPE_TO_ID_FIELD
from search.serializers import AutocompleteSerializer, AutocompleteQuerySerializer
from search.utils import request_elastic

logger = logging.getLogger(__name__)
ACTIVE_STATUSES = ('for_sale', 'for_rent', 'under_contract')
MAX_RESULTS = 10


class BaseAutocomplete(APIView):
    """
    Autocomplete by any part of address line
    """
    serializer_class = None

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            messages.error(request, 'Error! Empty query')
            data = {'errors': serializer.errors, 'server_messages': get_msg_json(request)}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        es_body = self.construct_body(serializer)
        es_response = request_elastic(es_body, EsIndex.AUTOCOMPLETE)
        hits = es_response['hits']['hits']

        aggs = []
        if agg_body := self.construct_agg_body(hits, serializer):
            aggs = request_elastic(agg_body, EsIndex.AUTOCOMPLETE)['aggregations']

            if 'zips_of_city' in aggs:
                zip_body = self.construct_agg_zips_body(aggs, serializer)
                zips_aggs = request_elastic(zip_body, EsIndex.AUTOCOMPLETE)['aggregations']
                aggs['zips_of_city'] = zips_aggs['zips_of_city']

        results = self.construct_results(hits, aggs, serializer)
        return Response({'items': results}, status=status.HTTP_200_OK)


class Autocomplete(BaseAutocomplete):
    """
    Autocomplete by any part of address line
    """
    serializer_class = AutocompleteQuerySerializer

    def construct_agg_zips_body(self, hits, serializer):
        zips = [key for i in hits['zips_of_city'].get('zips', {}).get('buckets', {}) if (key := i.get('key'))]
        aggs = {
            "zips": {
                "terms": {
                    "field": "zip"
                }
            }
        }
        body = {
            'query': {'bool': {'must': [
                {'term': {'type': 'address'}},
                {'term': {'category': serializer.data['category']}},
                {"terms": {"status": ["for_sale", "under_contract"]}}
            ]}},
            'aggs': {'zips_of_city': {'filter': {"terms": {"zip": zips}}, 'aggs': aggs}},
            'size': 0,
        }
        return body

    def construct_agg_body(self, hits, serializer):
        """
        Construct body with aggregations if there are regions in hits
        """
        aggs = {}

        # add agg for each region to retrieve its prop count
        for hit in hits:
            src = hit['_source']
            if src['category'] == 'region':
                filters = [
                    # OT-2902: rent section is currently disabled.
                    # Here are active statuses only for 'buy'.
                    {'term': {'state_id': src['state_id']}},
                ]
                if src['type'] in ('county', 'city', 'zip'):
                    filters.append({'term': {src['type']: src[src['type']]}})
                aggs[self._get_agg_name(hit)] = {'filter': {'bool': {'must': filters}}}

        # if only one city in results, request its zips too
        if city_hit := self.get_city_if_one(hits):
            aggs['zips_of_city'] = {
                'filter': {'term': {'city': city_hit['_source']['city']}},
                'aggs': {'zips': {'terms': {'field': 'zip'}}},
            }

        body = {}
        if aggs:
            body = {
                'query': {'bool': {'must': [
                    {'term': {'type': 'address'}},
                    {'term': {'state_id': 'fl'}},
                    {'term': {'category': serializer.data['category']}},
                    {'terms': {'status': ['for_sale', 'under_contract']}}
                ]}},
                'aggs': aggs,
                'size': 0,
            }
        return body

    def construct_results(self, hits, aggs, serializer):
        """Merge hits with aggs, then sort the results"""
        results = []

        # convert hits to results
        for hit in hits:
            if not (result := self.convert_hit(hit, serializer)):
                continue
            if hit['_source']['type'] not in ('building', 'address'):
                result['prop_count'] = aggs[self._get_agg_name(hit)]['doc_count']
            results.append(result)

        # convert city zips if present
        city_zip_results = []
        if city_hit := self.get_city_if_one(hits):
            for bucket in aggs['zips_of_city']['zips']['buckets']:
                zip_result = {
                    'label': f'{bucket["key"]}, {city_hit["_source"]["state_id"].upper()}',
                    'type': 'zip',
                    'state_id': city_hit['_source']['state_id'],
                    'zip': bucket['key'],
                    'county': city_hit['_source']['county'],
                    'prop_count': bucket['doc_count'],
                }
                city_zip_results.append(zip_result)

        return self.sort_results(results, city_zip_results)

    def sort_results(self, es_items, side_items):
        """
        Sort by score and type, and apply various empiric sorting rules
        """
        es_items = sorted(es_items, key=lambda x: x.pop('_score'), reverse=True)  # by score
        es_items = sorted(es_items, key=lambda x: x.get('prop_count', 0), reverse=True)  # by count
        side_items = sorted(side_items, key=lambda x: x['prop_count'], reverse=True)  # by count

        # sort by priority
        priority = ('state', 'city', 'zip', 'county', 'building', 'address')
        if len(self._find_indices(es_items, 'county', raw=False)) == 1:  # if only one county
            priority = ('state', 'county', 'city', 'zip', 'address')  # apply different priority
        items = []
        for type_ in priority:
            for item in es_items:
                if item['type'] == type_:
                    items.append(item)

        # insert side items after the first item
        res_items = []
        if side_items:
            if items:
                res_items += [items[0]]
            res_items += side_items
            res_items += items[1:]
        else:
            res_items = items

        return res_items[:MAX_RESULTS]

    def convert_hit(self, hit, serializer):
        """
        Convert Elasticsearch hit to response item
        """
        src = hit['_source']
        type_ = src['type']
        query = serializer.data['query'].strip()
        normalized_query = replace_synonyms(urlify(query))

        item = {
            'label': src['label'],
            'type': type_,
            'state_id': src['state_id'],
            '_score': hit['_score'],
        }
        if type_ == 'state':
            item['state_name'] = src['state']
        elif type_ == 'county':
            item['county'] = src['county']
        elif type_ == 'city':
            item['city'] = src['city']
            item['county'] = src['county']
        elif type_ == 'zip':
            item['zip'] = src['zip']
            item['city'] = src['city']
            item['county'] = src['county']
        elif type_ == 'building':
            item['zip'] = src['zip']
            item['city'] = src['city']
            item['county'] = src['county']
            item['building_id'] = src['building_id']
            item['building_name'] = src['building_name']
        elif type_ == 'address':
            # OT-2574 inactive properties can be returned only by full match with:
            # prop_id, mls_number, address line
            if (query not in (src['prop_id'], src['mls_number']) and
                    src['status'] not in ACTIVE_STATUSES and
                    src['address_line_norm'] not in normalized_query):
                return None
            item['prop_id'] = src['prop_id']
            item['city'] = src['city']
            item['zip'] = src['zip']
            item['county'] = src['county']

        return item

    def construct_body(self, serializer):
        """
        Construct ES body from serializer
        """
        query = serializer.data['query'].strip()
        category = serializer.data['category']

        should = [
            {'bool': {'must': [  # a bool query for search by prop_id and mls_number
                {'multi_match': {'query': query, 'fields': ['prop_id', 'mls_number'], 'operator': 'and'}},
                {'terms': {'category': [category, AutocompleteCategory.REGION]}},
            ]}},
            {'bool': {'must': [  # a bool query for regions search
                {'match': {'searchline': {'query': query, 'operator': 'and'}}},
                {'terms': {'category': [AutocompleteCategory.REGION]}},
            ]}},
            {'bool': {'must': [  # a bool query for search by building_name
                {'match': {'building_name': {'query': query, 'operator': 'and'}}},
                {'term': {'category': AutocompleteCategory.BUILDING}},
            ]}},
        ]

        # if there are digits, add a bool query for addresses
        if any(char.isdigit() for char in query):
            should.extend([
                {'bool': {'must': [
                    {'match': {'searchline': {
                        'query': query, 'operator': 'and',
                    }}},
                    {'term': {'category': AutocompleteCategory.BUILDING}}]}},
                # autocomplete search for active properties
                {'bool': {'must': [
                    {'match': {'searchline': {
                        'query': query, 'analyzer': 'synonym', 'operator': 'and',
                    }}},
                    {'terms': {'category': [category]}},
                ]}},
            ])

        body = {
            'size': MAX_RESULTS * 2,  # OT-3076 request more items from elastic to apply sort in python
            'query': {
                'bool': {
                    'minimum_should_match': 1,
                    'should': should,
                    'filter': get_is_test_es_filter(),
                },
            },
            'sort': [
                {'type_priority': {'order': 'desc'}},
                {'population': {'order': 'desc'}},
                {'status_priority': {'order': 'asc'}},
            ],
            'track_scores': True,
        }
        return body

    def get_city_if_one(self, hits):
        """Return city hit if it's only one in the list"""
        city_indices = self._find_indices(hits, 'city')
        if len(city_indices) == 1:
            return hits[city_indices[0]]

    def _find_indices(self, hits, type_, raw=True):
        """Find hit indices with provided type"""
        if raw:
            hits = [hit['_source'] for hit in hits]
        return [i for i, hit in enumerate(hits) if hit['type'] == type_]

    def _get_agg_name(self, hit):
        """Construct agg name based on type of the provided region hit"""
        src = hit['_source']
        type_ = src['type']
        id_field = TYPE_TO_ID_FIELD[type_]
        if type_ == 'state':
            name = f'{type_}_{src[id_field]}_{src["state_id"]}'
        else:
            name = f'{type_}_{src[id_field]}_{src["county"]}_{src["state_id"]}'
        return name


class CityAutocomplete(BaseAutocomplete):
    """
    Autocomplete by City, among all the categories
    """
    serializer_class = AutocompleteSerializer

    def construct_body(self, serializer):
        """
        Construct ES body from serializer
        """
        query = serializer.data['query'].strip()
        body = {
            'query': {'bool': {'must': [
                {'match': {'searchline': {'query': query, 'operator': 'and'}}},
                {'term': {'category': AutocompleteCategory.REGION}},
                {'term': {'type': 'city'}},
            ]}},
            'sort': [
                {'type_priority': {'order': 'desc'}},
                {'population': {'order': 'desc'}},
                {'status_priority': {'order': 'asc'}},
            ],
            'track_scores': True,
        }
        return body

    def construct_agg_body(self, hits, serializer):
        """
        Construct body with aggregations if there are regions in hits
        """
        aggs = {}
        for hit in hits:
            src = hit['_source']
            filters = [{'term': {'state_id': src['state_id']}},
                       {'term': {'county': src['county']}},
                       {'term': {'city': src['city']}}]
            for agg_name, category in self._gen_agg_names(hit).items():
                category_filters = [{'term': {'category': category}}]
                st_1 = 'for_rent' if category == AutocompletePropCategory.RENT_PROP else 'for_sale'
                category_filters += [{'terms': {'status': [st_1, 'under_contract']}}]
                aggs[agg_name] = {'filter': {'bool': {'must': filters + category_filters}}}

        body = {}
        if aggs:
            body = {
                'query': {'bool': {'must': [{'term': {'type': 'address'}}]}},
                'aggs': aggs,
                'size': 0,
            }
        return body

    def construct_results(self, hits, aggs, serializer):
        """
        Merge hits with aggs, then sort the results
        """
        results = []

        # convert hits to results
        for hit in hits:
            result = self.convert_hit(hit)
            for agg_name, category in self._gen_agg_names(hit).items():
                count_field = CATEGORY_TO_COUNT_FIELD[category]
                result[count_field] = aggs[agg_name]['doc_count']
            results.append(result)

        return self.sort_results(results)

    def convert_hit(self, hit):
        """
        Convert Elasticsearch hit to response item
        """
        src = hit['_source']
        item = {
            'label': src['label'],
            'type': 'city',
            'state_id': src['state_id'],
            '_score': hit['_score'],
            'city': src['city'],
            'county': src['county'],
        }
        return item

    def sort_results(self, results):
        """
        Sort by score and type, and apply various empiric sorting rules
        """
        results = sorted(results, key=lambda x: x.pop('_score'), reverse=True)  # by score

        for count_field in CATEGORY_TO_COUNT_FIELD.values():  # by count
            results = sorted(results, key=lambda x: x.get(count_field, 0), reverse=True)

        return results

    def _gen_agg_names(self, hit):
        """
        Construct unique aggregation names for each category
        """
        src = hit['_source']
        names = {}
        for category in AutocompletePropCategory.values:
            name = f'{src["city"]}_{src["county"]}_{src["state_id"]}_{category}'
            names[name] = category
        return names
