from unittest.mock import patch

from django.urls import reverse
from rest_framework import status

import search.tests.constants as const
from search.tests.base import SearchBaseTest


AUTOCOMPLETE_URL = reverse('search:city_autocomplete')


@patch('ofirio_common.helpers.Elasticsearch')
class PatchedCityAutocompleteViewTest(SearchBaseTest):
    """
    Tests that actually call Elastic, so Elastic is patched with a mock
    """
    def test_ok(self, es_class_mock):
        """
        Typical success case. Query is 'aventura' and there is one result found
        """
        es_instance_mock = self.setup_es_mock(es_class_mock,
                                              const.ES_AVENTURA_AUTOCOMPLETE_RESPONSE,
                                              const.ES_AVENTURA_AUTOCOMPLETE_AGGS_RESPONSE)
        response = self.client.post(AUTOCOMPLETE_URL, {'query': 'aventura'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_body = {
            'query': {'bool': {'must': [
                {'match': {'searchline': {'query': 'aventura', 'operator': 'and'}}},
                {'term': {'category': 'region'}},
                {'term': {'type': 'city'}},
            ]}},
            'sort': [{'type_priority': {'order': 'desc'}},
                     {'population': {'order': 'desc'}},
                     {'status_priority': {'order': 'asc'}}],
            'track_scores': True,
        }
        search_call = es_instance_mock.search.call_args_list[0]
        self.assertEqual(search_call.kwargs['index'], 'autocomplete')
        self.assertEqual(search_call.kwargs['body'], expected_body)

        expected_body_2 = {
            'query': {'bool': {'must': [{'term': {'type': 'address'}}]}},
            'aggs': {
                'aventura_miami-dade-county_fl_invest-prop': {
                    'filter': {'bool': {'must': [
                        {'term': {'state_id': 'fl'}},
                        {'term': {'county': 'miami-dade-county'}},
                        {'term': {'city': 'aventura'}},
                        {'term': {'category': 'invest-prop'}},
                        {'terms': {'status': ['for_sale', 'under_contract']}},
                    ]}},
                },
                'aventura_miami-dade-county_fl_buy-prop': {
                    'filter': {'bool': {'must': [
                        {'term': {'state_id': 'fl'}},
                        {'term': {'county': 'miami-dade-county'}},
                        {'term': {'city': 'aventura'}},
                        {'term': {'category': 'buy-prop'}},
                        {'terms': {'status': ['for_sale', 'under_contract']}},
                    ]}},
                },
                'aventura_miami-dade-county_fl_rent-prop': {
                    'filter': {'bool': {'must': [
                        {'term': {'state_id': 'fl'}},
                        {'term': {'county': 'miami-dade-county'}},
                        {'term': {'city': 'aventura'}},
                        {'term': {'category': 'rent-prop'}},
                        {'terms': {'status': ['for_rent', 'under_contract']}},
                    ]}},
                },
            },
            'size': 0,
        }
        search_call = es_instance_mock.search.call_args_list[1]
        self.assertEqual(search_call.kwargs['index'], 'autocomplete')
        self.assertEqual(search_call.kwargs['body'], expected_body_2)

        expected_response = {
            'items': [
                {'label': 'Aventura, FL',
                 'type': 'city',
                 'state_id': 'fl',
                 'city': 'aventura',
                 'county': 'miami-dade-county',
                 'invest_count': 701,
                 'buy_count': 1293,
                 'rent_count': 962},
            ],
        }
        self.assertEqual(response.data, expected_response)
