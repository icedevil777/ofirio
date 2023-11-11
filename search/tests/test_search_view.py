import json
from unittest.mock import patch, MagicMock
from unittest import skip

from django.core.cache import cache as dj_cache
from django.urls import reverse
from django.test import override_settings
from rest_framework import status

import search.tests.constants as const
from account.tests.factories import create_user
from account.utils import get_access_status
from search.tests.base import SearchBaseTest


SEARCH_URL = reverse('search:search')


class SearchViewTest(SearchBaseTest):

    def test_no_query(self):
        response = self.client.post(SEARCH_URL)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_financing_years_out_of_range(self):
        """
        Allowed values for financing_years are (15, 30)
        """
        data = {
            'type': 'state',
            'state_id': 'FL',
            'start': 0,
            'map_query': True,
            'financing_years': 4,
            'down_payment': 0.2,
        }
        response = self.client.post(SEARCH_URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('financing_years', response.data['errors'])

    def test_down_payment_not_in_allowed(self):
        """
        down_payment is 0.35 which is not in the list of valid values
        """
        data = {
            'type': 'state',
            'state_id': 'FL',
            'start': 0,
            'map_query': True,
            'financing_years': 15,
            'down_payment': 0.35,
        }
        response = self.client.post(SEARCH_URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('down_payment', response.data['errors'])

    def test_financing_years_only(self):
        """
        financing_years without down_payment is not valid
        """
        data = {
            'type': 'state',
            'state_id': 'FL',
            'start': 0,
            'map_query': True,
            'financing_years': 15,
        }
        response = self.client.post(SEARCH_URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('down_payment', response.data['errors'])

    def test_unknown_cleaned_prop_type(self):
        data = {
            'type': 'state',
            'state_id': 'FL',
            'start': 0,
            'map_query': True,
            'cleaned_prop_type': ['1234'],
        }
        response = self.client.post(SEARCH_URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cleaned_prop_type', response.data['errors'])


@patch('ofirio_common.helpers.Elasticsearch')
class PatchedSearchViewTest(SearchBaseTest):
    """
    Tests that actually call Elastic, so Elastic is patched with a mock
    """
    def test_nothing_found(self, es_class_mock):
        """
        Check that even if nothing found, all the main keys returned
        """
        self.setup_es_mock(es_class_mock, const.ES_EMPTY_SEARCH_RESPONSE)
        user = create_user()
        self.client.force_authenticate(user=user)

        response = self.client.post(SEARCH_URL, const.SEARCH_STATE_DATA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Though it's empty reponse, the keys must be there
        self.assertIn('total', response.data['search'])
        self.assertIn('start', response.data['search'])
        self.assertIn('items', response.data['search'])
        self.assertIn('features', response.data['map'])

    def test_cache_hit(self, es_class_mock):
        """
        Check that cache is used for search
        """
        data = {'type': 'state', 'state_id': 'FL'}
        key = f'{SEARCH_URL}|{{}}|{json.dumps({k: data[k] for k in sorted(data)})}'
        self.assertFalse(dj_cache.get(key))

        self.setup_es_mock(es_class_mock, const.ES_EMPTY_SEARCH_RESPONSE)
        self.client.post(SEARCH_URL, data)
        self.assertTrue(dj_cache.get(key))

    @patch('search.common.insights_handler.InsightsHandler.get_insights', return_value={})
    def test_unverified_user_prop_fields(self, ins_mock, es_class_mock):
        """
        Ensure free user does not receive any paid-only field
        """
        self.setup_es_mock(es_class_mock, const.ES_FLORIDA_SEARCH_RESPONSE)
        user = create_user()
        self.client.force_authenticate(user=user)

        response = self.client.post(SEARCH_URL, {'index': 'search-invest',
                                                 **const.SEARCH_STATE_DATA})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check one of the found items has no estimated data since the user has not paid
        # 751AB568FFD63EFD8A86 has is_high_cap_rate = False, so we expose predicted fields
        search_item = response.data['search']['items'][0]
        self.assertEqual(search_item['prop_id'], '751AB568FFD63EFD8A86')
        self.assertIsNone(search_item.get('predicted_rent'))
        self.assertIsNone(search_item.get('cap_rate'))
        self.assertIsNone(search_item.get('cash_on_cash'))
        self.assertIsNone(search_item.get('total_return'))

        map_item = self.find_prop_in_map_response('751AB568FFD63EFD8A86', response)
        self.assertIsNone(map_item.get('predicted_rent'))
        self.assertIsNone(map_item.get('cap_rate'))
        self.assertIsNone(map_item.get('cash_on_cash'))
        self.assertIsNone(map_item.get('total_return'))

        # 8154C17F502066BBB0AB has is_high_cap_rate = True, so predicted fields should be hidden
        search_item = response.data['search']['items'][1]
        self.assertIsNotNone(search_item['predicted_rent'])
        self.assertIsNotNone(search_item['cap_rate'])
        self.assertIsNotNone(search_item['cash_on_cash'])
        self.assertIsNotNone(search_item['total_return'])

        map_item = self.find_prop_in_map_response('8154C17F502066BBB0AB', response)
        self.assertIsNotNone(map_item['predicted_rent'])
        self.assertIsNotNone(map_item['cap_rate'])
        self.assertIsNotNone(map_item['cash_on_cash'])
        self.assertIsNotNone(map_item['total_return'])

    @patch('search.common.insights_handler.InsightsHandler.get_insights', return_value={})
    def test_paid_user_prop_fields(self, ins_mock, es_class_mock):
        """
        Ensure paid user receives all the fields that are paid-only
        """
        self.setup_es_mock(es_class_mock, const.ES_FLORIDA_SEARCH_RESPONSE)
        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)

        response = self.client.post(SEARCH_URL, {'index': 'search-invest',
                                                 **const.SEARCH_STATE_DATA})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check one of the found items has all the estimated fields, since the user has paid
        search_item = response.data['search']['items'][0]
        self.assertEqual(search_item['prop_id'], '751AB568FFD63EFD8A86')
        self.assertIn('predicted_rent', search_item)
        self.assertIn('cap_rate', search_item)
        self.assertIn('cash_on_cash', search_item)
        self.assertIn('total_return', search_item)

        map_item = self.find_prop_in_map_response('751AB568FFD63EFD8A86', response)
        self.assertEqual(map_item['prop_id'], '751AB568FFD63EFD8A86')
        self.assertIn('predicted_rent', map_item)
        self.assertIn('cap_rate', map_item)
        self.assertIn('cash_on_cash', map_item)
        self.assertIn('total_return', map_item)

    @patch('search.common.insights_handler.InsightsHandler.get_insights', return_value={})
    def test_sort_by_financing_years_and_down_payment(self, ins_mock, es_class_mock):
        """
        Check that the correct ES body is constructed based on input data
        """
        es_instance_mock = self.setup_es_mock(es_class_mock, const.ES_FLORIDA_SEARCH_RESPONSE)

        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)
        self.assertEqual(get_access_status(user), 'premium')

        self._test_sort_by_financing_years_and_down_payment(
            es_instance_mock, 'cash_on_cash', 15, .3,
        )
        self._test_sort_by_financing_years_and_down_payment(
            es_instance_mock, 'total_return', 30, .2,
        )
        self._test_sort_by_financing_years_and_down_payment(
            es_instance_mock, 'cap_rate', 30, .4,
        )

    def _test_sort_by_financing_years_and_down_payment(self, es_instance_mock, field,
                                                       financing_years, down_payment):
        data = {
            'index': 'search-invest',
            'type': 'state',
            'state_id': 'FL',
            'start': 0,
            'map_query': True,
            'financing_years': financing_years,
            'down_payment': down_payment,
            'sort_field': field,
        }
        response = self.client.post(SEARCH_URL, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_body = {
            'size': 30,
            'from': 0,
            'track_total_hits': True,
            'query' : {
                'bool': {
                    'must': [],
                    'filter': [
                        {'term': {'state_id': 'FL'}},
                        {'terms': {'status': ['for_sale', 'under_contract']}},
                    ],
                    'should': [],
                    'minimum_should_match': 0,
                }
            },
            'sort': {f'{field}_{financing_years}_{int(down_payment*100)}': {'order': 'desc'}},
            'aggs': {
                'min_lat': {'min': {'script': 'doc["geo_point"].lat'}},
                'max_lat': {'max': {'script': 'doc["geo_point"].lat'}},
                'min_lon': {'min': {'script': 'doc["geo_point"].lon'}},
                'max_lon': {'max': {'script': 'doc["geo_point"].lon'}},
            },
        }
        # -3 is the 1st query in a call
        last_search_call = es_instance_mock.search.call_args_list[-3]
        self.assertEqual(last_search_call.kwargs['index'], 'search-invest')
        self.assertEqual(last_search_call.kwargs['body'], expected_body)

    @patch('search.common.insights_handler.InsightsHandler.get_insights', return_value={})
    def test_correct_cash_on_cash_and_total_return(self, ins_mock, es_class_mock):
        """
        If financing_years and down_payment are specified,
        cap_rate, cash_on_cash and total_return must be returned according to them
        (the ones with postfix *_15_30 in this case),
        not just raw 'cash_on_cash' and 'total_return' from ES,
        """
        self.setup_es_mock(es_class_mock, const.ES_FLORIDA_SEARCH_RESPONSE)

        # paid user since a free one is not allowed to see cash_on_cash and total_return at all
        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)

        data = {
            'index': 'search-invest',
            'type': 'state',
            'state_id': 'FL',
            'start': 0,
            'map_query': True,
            'financing_years': 15,
            'down_payment': 0.3,
        }
        response = self.client.post(SEARCH_URL, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        search_item = response.data['search']['items'][0]
        self.assertEqual(search_item['prop_id'], '751AB568FFD63EFD8A86')
        self.assertEqual(search_item['cash_on_cash'], -0.0783)
        self.assertEqual(search_item['total_return'], 0.0618)
        self.assertEqual(search_item['cap_rate'], 0.0218)

    @override_settings(IS_PRODUCTION=True)
    @patch('search.common.insights_handler.InsightsHandler.get_insights', return_value={})
    def test_is_test_filter_on_prod(self, ins_mock, es_class_mock):
        es_instance_mock = self.setup_es_mock(es_class_mock, const.ES_FLORIDA_SEARCH_RESPONSE)

        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)

        data = {
            'type': 'state',
            'state_id': 'FL',
            'start': 0,
            'map_query': True,
        }
        response = self.client.post(SEARCH_URL, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        first_search_call = es_instance_mock.search.call_args_list[0]
        self.assertTrue({'term': {'is_test': False}} in
                        first_search_call.kwargs['body']['query']['bool']['filter'])

    @patch('search.common.insights_handler.InsightsHandler.get_insights', return_value={})
    def test_correct_cash_on_cash_filter(self, ins_mock, es_class_mock):
        """
        cash_on_cash_min filter must be applied according to
        financing_years and down_payment values
        """
        es_instance_mock = self.setup_es_mock(es_class_mock, const.ES_FLORIDA_SEARCH_RESPONSE)

        # paid user since a free one is not allowed to see cash_on_cash and total_return at all
        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)

        data = {
            'index': 'search-invest',
            'type': 'state',
            'state_id': 'FL',
            'start': 0,
            'map_query': True,
            'financing_years': 30,
            'down_payment': 0.5,
            'cash_on_cash_min': 0.03,
        }
        response = self.client.post(SEARCH_URL, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_body = {
            'size': 30,
            'from': 0,
            'track_total_hits': True,
            'query' : {
                'bool': {
                    'must': [],
                    'filter': [
                        {'term': {'state_id': 'FL'}},
                        {'terms': {'status': ['for_sale', 'under_contract']}},
                        {'range': {'cash_on_cash_30_50': {'gte': 0.03}}},
                    ],
                    'should': [],
                    'minimum_should_match': 0,
                }
            },
            'sort': {'scoring': {'order': 'desc'}},
            'aggs': {
                'min_lat': {'min': {'script': 'doc["geo_point"].lat'}},
                'max_lat': {'max': {'script': 'doc["geo_point"].lat'}},
                'min_lon': {'min': {'script': 'doc["geo_point"].lon'}},
                'max_lon': {'max': {'script': 'doc["geo_point"].lon'}},
            },
        }
        first_search_call = es_instance_mock.search.call_args_list[0]
        self.assertEqual(first_search_call.kwargs['index'], 'search-invest')
        self.assertEqual(first_search_call.kwargs['body'], expected_body)

    @patch('search.common.insights_handler.InsightsHandler.get_insights', return_value={})
    def test_free_user_filters(self, ins_mock, es_class_mock):
        """
        Check that all the filters are accepted if requested by free user,
        except for estimated ones
        """
        es_instance_mock = self.setup_es_mock(es_class_mock, const.ES_FLORIDA_SEARCH_RESPONSE)

        data_with_allowed_filters = {
            'type': 'state',
            'state_id': 'FL',
            'start': 0,
            'map_query': True,
            'zoom': 5,

            # filters
            'price_min': 100000,
            'price_max': 200000,
            'hoa_fee_max': 0,
            'include_incomplete_hoa': False,
            'beds_min': 2,
            'beds_max': 5,
            'baths_min': 2,
            'year_built_min': 1950,
            'year_built_max': 2020,
            'build_size_min': 10,
            'build_size_max': 20,
            'status_for_sale': True,
            'status_pending': True,
            'status_sold': True,
            'is_good_deal': True,
            'is_55_plus': True,
            'is_rehab': False,
            'is_cash_only': False,
        }

        data_with_disallowed_filters = {
            'type': 'state',
            'state_id': 'FL',
            'start': 0,
            'map_query': True,
            'zoom': 5,

            # forbidden filters
            'cap_rate_min': 0.5,
            'predicted_rent_min': 1000,
            'cash_on_cash_min': 0.5,
        }

        # 1. check anon user: some filters are forbidden
        response = self.client.post(SEARCH_URL, data_with_allowed_filters)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(SEARCH_URL, data_with_disallowed_filters)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 2. check authorised user: all filters are available
        user = create_user()
        self.client.force_authenticate(user=user)
        self.assertEqual(get_access_status(user), 'unverified')

        response = self.client.post(SEARCH_URL, data_with_allowed_filters)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(SEARCH_URL, data_with_disallowed_filters)
        # currently unverified users are able to filter by these fields
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('search.common.insights_handler.InsightsHandler.get_insights', return_value={})
    def test_paid_user_filters(self, ins_mock, es_class_mock):
        """
        Check that all the filters are accepted if requested by paid user,
        including estimated ones
        """
        es_instance_mock = self.setup_es_mock(es_class_mock, const.ES_FLORIDA_SEARCH_RESPONSE)

        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)
        self.assertEqual(get_access_status(user), 'premium')

        data_with_all_filters = {
            'type': 'state',
            'state_id': 'FL',
            'start': 0,
            'map_query': True,
            'zoom': 5,

            # filters
            'price_min': 100000,
            'price_max': 200000,
            'beds_min': 2,
            'beds_max': 5,
            'baths_min': 2,
            'year_built_min': 1950,
            'year_built_max': 2020,
            'build_size_min': 10,
            'build_size_max': 20,
            'status_for_sale': True,
            'status_pending': True,
            'status_sold': True,
            'is_good_deal': True,
            'is_55_plus': True,
            'is_rehab': False,
            'is_cash_only': False,

            # paid-only filters
            'cap_rate_min': 0.5,
            'predicted_rent_min': 1000,
            'cash_on_cash_min': 0.5,
        }
        response = self.client.post(SEARCH_URL, data_with_all_filters)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('search.common.insights_handler.InsightsHandler.get_insights', return_value={})
    def test_free_user_sorts(self, ins_mock, es_class_mock):
        """
        Check that all the sortings are accepted if requested by free user,
        except for estimated ones
        """
        es_instance_mock = self.setup_es_mock(es_class_mock, const.ES_FLORIDA_SEARCH_RESPONSE)

        allowed_sorts = (
            {'sort_field': 'default_sort', 'sort_direction': 'asc'},
            {'sort_field': 'price', 'sort_direction': 'asc'},
            {'sort_field': 'year_built', 'sort_direction': 'asc'},
            {'sort_field': 'list_date', 'sort_direction': 'asc'},
            {'sort_field': 'update_date', 'sort_direction': 'asc'},
        )

        disallowed_sorts = (
            {'sort_field': 'predicted_rent', 'sort_direction': 'asc'},
            {'sort_field': 'cap_rate', 'sort_direction': 'asc'},
            {'sort_field': 'cash_on_cash', 'sort_direction': 'asc'},
            {'sort_field': 'total_return', 'sort_direction': 'asc'},
        )
        # 1. check anon user: some sortings are forbidden
        for sort_part in allowed_sorts:
            response = self.client.post(SEARCH_URL, {**const.SEARCH_STATE_DATA, **sort_part})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        for sort_part in disallowed_sorts:
            response = self.client.post(SEARCH_URL, {**const.SEARCH_STATE_DATA, **sort_part})
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 2. check authorised user: all sortings are available
        user = create_user()
        self.client.force_authenticate(user=user)
        self.assertEqual(get_access_status(user), 'unverified')

        for sort_part in allowed_sorts:
            response = self.client.post(SEARCH_URL, {**const.SEARCH_STATE_DATA, **sort_part})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        for sort_part in disallowed_sorts:
            response = self.client.post(SEARCH_URL, {**const.SEARCH_STATE_DATA, **sort_part})
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('search.common.insights_handler.InsightsHandler.get_insights', return_value={})
    def test_paid_user_sorts(self, ins_mock, es_class_mock):
        """
        Check that all the sortings are accepted if requested by paid user,
        including estimated ones
        """
        es_instance_mock = self.setup_es_mock(es_class_mock, const.ES_FLORIDA_SEARCH_RESPONSE)

        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)
        self.assertEqual(get_access_status(user), 'premium')

        allowed_sorts = (
            {'sort_field': 'default_sort', 'sort_direction': 'asc'},
            {'sort_field': 'price', 'sort_direction': 'asc'},
            {'sort_field': 'year_built', 'sort_direction': 'asc'},
            {'sort_field': 'list_date', 'sort_direction': 'asc'},
            {'sort_field': 'update_date', 'sort_direction': 'asc'},
            {'sort_field': 'predicted_rent', 'sort_direction': 'asc'},
            {'sort_field': 'cap_rate', 'sort_direction': 'asc'},
            {'sort_field': 'cash_on_cash', 'sort_direction': 'asc'},
            {'sort_field': 'total_return', 'sort_direction': 'asc'},
        )
        for sort_part in allowed_sorts:
            response = self.client.post(SEARCH_URL, {**const.SEARCH_STATE_DATA, **sort_part})
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('search.common.insights_handler.InsightsHandler.get_insights', return_value={})
    def test_cluster_aggregation(self, ins_mock, es_class_mock):
        """
        Simulate large response and check that the second ES request
        has cluster aggregation
        """
        es_instance_mock = self.setup_es_mock(
            es_class_mock,
            const.ES_LARGE_TOTAL_SEARCH_RESPONSE, const.ES_GRID_BUCKETS_RESPONSE,
        )
        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)

        data = {
            'type': 'state',
            'state_id': 'FL',
            'start': 0,
            'map_query': True,
            'viewport': '26.120815,-84.283363,28.883059,-78.971473',
            'zoom': 5,
        }
        response = self.client.post(SEARCH_URL, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        first_call = es_instance_mock.search.call_args_list[0]
        second_call = es_instance_mock.search.call_args_list[1]

        self.assertEqual(first_call.kwargs['body']['size'], 30)
        self.assertEqual(second_call.kwargs['body']['size'], 0)
        self.assertIn('cluster_agg', second_call.kwargs['body']['aggs'])

    @patch('search.common.insights_handler.InsightsHandler.get_insights', return_value={})
    def test_prop_grouping(self, ins_mock, es_class_mock):
        """
        Check props with the same coordinates are grouped,
        forming invalid geojson
        """
        es_instance_mock = self.setup_es_mock(es_class_mock, const.ES_FLORIDA_SEARCH_RESPONSE)

        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)

        response = self.client.post(SEARCH_URL, const.SEARCH_STATE_DATA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        first_lvl_features = response.data['map']['features']
        self.assertEqual(len(first_lvl_features), 2)

        for feature in first_lvl_features:
            # should be one prop
            if feature['type'] == 'Feature':
                self.assertEqual(feature['properties']['prop_id'], 'M5454893686')

            # should be two props with equal geometry
            elif feature['type'] == 'FeatureCollection':
                feature_1, feature_2 = feature['features']
                self.assertEqual(feature_1['properties']['prop_id'], '751AB568FFD63EFD8A86')
                self.assertEqual(feature_2['properties']['prop_id'], '8154C17F502066BBB0AB')
                self.assertEqual(feature_1['geometry'], feature_2['geometry'])

    @patch('search.common.insights_handler.InsightsHandler.get_insights', return_value={})
    def test_boundaries(self, ins_mock, es_class_mock):
        """
        Check that clusters in cluster aggregation has rectangle boundaries,
        and that response itself has overall bounds
        """
        es_instance_mock = self.setup_es_mock(
            es_class_mock,
            const.ES_LARGE_TOTAL_SEARCH_RESPONSE, const.ES_GRID_BUCKETS_RESPONSE,
        )
        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)

        data = {
            'type': 'state',
            'state_id': 'FL',
            'start': 0,
            'map_query': True,
            'viewport': '26.120815,-84.283363,28.883059,-78.971473',
            'zoom': 5,
        }
        response = self.client.post(SEARCH_URL, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['bounds'])

        for feature in response.data['map']['features']:
            bounds = feature['properties']['geo_bounds']
            self.assertEqual(len(bounds), 4)

    @patch('search.common.insights_handler.InsightsHandler.get_insights', return_value={})
    def test_sim_nearby(self, ins_mock, es_class_mock):
        """
        Check that similar nearby query correctly formed,
        and that Elastic response correctly converts into our response
        """
        es_instance_mock = self.setup_es_mock(
            es_class_mock,
            const.ES_FLORIDA_SEARCH_RESPONSE,
            const.ES_EMPTY_SEARCH_RESPONSE,
            const.ES_FLORIDA_SIM_NEARBY_RESPONSE,
        )
        response = self.client.post(SEARCH_URL, const.SEARCH_STATE_DATA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('items', response.data['sim_nearby'])
        self.assertIn('map', response.data['sim_nearby'])
        self.assertIn('within', response.data['sim_nearby'])

        sim_nearby_call = es_instance_mock.search.call_args_list[2]
        self.assertEqual(sim_nearby_call.kwargs['body'], const.EXPECTED_ES_BODY_FLORIDA_SIM_NEARBY)

    @skip("OT-2314: why do we skip viewport here?")
    def test_viewport_sim_nearby(self, es_class_mock):
        """
        Ensure viewport is skipped when doing 'similar nearby' query
        """
        es_instance_mock = self.setup_es_mock(
            es_class_mock,
            const.ES_FLORIDA_SEARCH_RESPONSE,
            const.ES_EMPTY_SEARCH_RESPONSE,
            const.ES_FLORIDA_SIM_NEARBY_RESPONSE,
        )
        data = {
            'type': 'state',
            'state_id': 'FL',
            'start': 0,
            'map_query': True,
            'viewport': '26.120815,-84.283363,28.883059,-78.971473',
            'zoom': 5,
        }
        response = self.client.post(SEARCH_URL, data)
        sim_nearby_call = es_instance_mock.search.call_args_list[2]
        self.assertEqual(sim_nearby_call.kwargs['body'], const.EXPECTED_ES_BODY_FLORIDA_SIM_NEARBY)


@patch('ofirio_common.helpers.Elasticsearch')
class SearchFilteringTest(SearchBaseTest):
    """
    Test how some filters in search works
    """
    @patch('search.common.insights_handler.InsightsHandler.get_insights', return_value={})
    def test_keywords(self, ins_mock, es_class_mock):
        """
        Search with keywords
        """
        es_instance_mock = self.setup_es_mock(es_class_mock,
                                              const.ES_FLORIDA_SEARCH_RESPONSE_NO_MAP_QUERY)
        data = {
            'type': 'state',
            'state_id': 'FL',
            'start': 0,
            'keywords': 'beautiful,dishwasher',
        }
        response = self.client.post(SEARCH_URL, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_call_body = {
            'aggs': {},
            'from': 0,
            'query': {'bool': {
                'filter': [{'term': {'state_id': 'FL'}},
                                          {'terms': {'status': ['for_sale', 'under_contract']}}],
                'minimum_should_match': 0,
                'must': [{'bool': {'should': [
                    {'match': {'description': {'operator': 'and',
                                               'query': 'beautiful dishwasher'}}},
                    {'match': {'features_for_search': {'operator': 'and',
                                                       'query': 'beautiful dishwasher'}}},
                    {'match': {'appliances': {'operator': 'and',
                                              'query': 'beautiful dishwasher'}}},
                ]}}],
                'should': [],
            }},
            'size': 30,
            'sort': {'scoring': {'order': 'desc'}},
            'track_total_hits': True,
        }
        call_body = es_class_mock().search.call_args_list[0].kwargs['body']
        self.assertEqual(call_body, expected_call_body)

    @patch('search.common.insights_handler.InsightsHandler.get_insights', return_value={})
    def test_amenities(self, ins_mock, es_class_mock):
        """
        Search with amenities
        """
        es_instance_mock = self.setup_es_mock(es_class_mock,
                                              const.ES_FLORIDA_SEARCH_RESPONSE_NO_MAP_QUERY)
        data = {
            'type': 'state',
            'state_id': 'FL',
            'start': 0,
            'amenities': 'beautiful,dishwasher,gym',
        }
        response = self.client.post(SEARCH_URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors']['amenities'][0],
                         'Unknown amenity: beautiful')

        data = {
            'type': 'state',
            'state_id': 'FL',
            'start': 0,
            'amenities': 'laundry,gym,with-pool',
            'keywords': 'beautiful,dishwasher',
        }
        response = self.client.post(SEARCH_URL, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_call_body = {
            'aggs': {},
            'from': 0,
            'query': {'bool': {
                'filter': [{'term': {'state_id': 'FL'}},
                           {'terms': {'status': ['for_sale', 'under_contract']}},
                           {'match': {'cleaned_amenities': {'operator': 'and',
                                                            'query': 'laundry pool'}}}],
                'minimum_should_match': 0,
                'must': [{'bool': {'should': [
                    {'match': {'description': {'operator': 'and',
                                               'query': 'beautiful dishwasher gym'}}},
                    {'match': {'features_for_search': {'operator': 'and',
                                                       'query': 'beautiful dishwasher gym'}}},
                    {'match': {'appliances': {'operator': 'and',
                                              'query': 'beautiful dishwasher gym'}}},
                ]}}],
                'should': []},
            },
            'size': 30,
            'sort': {'scoring': {'order': 'desc'}},
            'track_total_hits': True,
        }
        call_body = es_class_mock().search.call_args_list[0].kwargs['body']
        self.assertEqual(call_body, expected_call_body)

    @patch('search.common.insights_handler.InsightsHandler.get_insights', return_value={})
    def test_multipolygon(self, ins_mock, es_class_mock):
        """
        Check that the correct ES body is constructed when geo_polygons provided
        """
        es_instance_mock = self.setup_es_mock(es_class_mock, const.ES_FLORIDA_SEARCH_RESPONSE)

        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)

        data = {
            'index': 'search-invest',
            'type': 'state',
            'state_id': 'FL',
            'start': 0,
            'map_query': True,
            'geo_polygons': [
                [[68.1, -81.20], [38.6, -97.35], [38.6, -97.45], [38.6, -97.55]],
                [[39.7, -98.55], [39.8, -98.65], [39.9, -98.75], [39.9, -98.75], [39.7, -98.55]],
            ],
            'zoom': 5,
        }
        response = self.client.post(SEARCH_URL, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_body = {
            'size': 30,
            'from': 0,
            'track_total_hits': True,
            'query' : {
                'bool': {
                    'must': [],
                    'filter': [
                        {'term': {'state_id': 'FL'}},
                        {'terms': {'status': ['for_sale', 'under_contract']}},
                    ],
                    'should': [
                        {'geo_shape': {
                            'geo_point': {
                                'shape': {
                                    'type': 'polygon',
                                    'coordinates': [
                                        [[68.1, -81.20], [38.6, -97.35],
                                        [38.6, -97.55], [68.1, -81.20]],
                                    ],
                                }
                            }
                        }},
                        {'geo_shape': {
                            'geo_point': {
                                'shape': {
                                    'type': 'polygon',
                                    'coordinates': [
                                        [[39.7, -98.55], [39.8, -98.65],
                                        [39.9, -98.75], [39.7, -98.55]],
                                    ],
                                }
                            }
                        }},
                    ],
                    'minimum_should_match': 1,
                }
            },
            'sort': {'scoring': {'order': 'desc'}},
            'aggs': {
                'min_lat': {'min': {'script': 'doc["geo_point"].lat'}},
                'max_lat': {'max': {'script': 'doc["geo_point"].lat'}},
                'min_lon': {'min': {'script': 'doc["geo_point"].lon'}},
                'max_lon': {'max': {'script': 'doc["geo_point"].lon'}},
            },
        }
        first_search_call = es_instance_mock.search.call_args_list[0]
        self.assertEqual(first_search_call.kwargs['index'], 'search-invest')
        self.assertEqual(first_search_call.kwargs['body'], expected_body)

    @patch('search.common.insights_handler.InsightsHandler.get_insights', return_value={})
    def test_polygon(self, ins_mock, es_class_mock):
        """
        Check that the correct ES body is constructed when geo_polygons provided
        """
        es_instance_mock = self.setup_es_mock(es_class_mock, const.ES_FLORIDA_SEARCH_RESPONSE)

        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)

        data = {
            'index': 'search-invest',
            'type': 'state',
            'state_id': 'FL',
            'start': 0,
            'map_query': True,
            'geo_polygons': [
                [[39.7, -98.55], [39.8, -98.65], [39.9, -98.75], [39.9, -98.75], [39.7, -98.55]],
            ],
            'zoom': 5,
        }
        response = self.client.post(SEARCH_URL, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_body = {
            'size': 30,
            'from': 0,
            'track_total_hits': True,
            'query' : {
                'bool': {
                    'must': [],
                    'filter': [
                        {'term': {'state_id': 'FL'}},
                        {'terms': {'status': ['for_sale', 'under_contract']}},
                    ],
                    'should': [
                        {'geo_shape': {
                            'geo_point': {
                                'shape': {
                                    'type': 'polygon',
                                    'coordinates': [
                                        [[39.7, -98.55], [39.8, -98.65],
                                        [39.9, -98.75], [39.7, -98.55]],
                                    ],
                                }
                            }
                        }},
                    ],
                    'minimum_should_match': 1,
                }
            },
            'sort': {'scoring': {'order': 'desc'}},
            'aggs': {
                'min_lat': {'min': {'script': 'doc["geo_point"].lat'}},
                'max_lat': {'max': {'script': 'doc["geo_point"].lat'}},
                'min_lon': {'min': {'script': 'doc["geo_point"].lon'}},
                'max_lon': {'max': {'script': 'doc["geo_point"].lon'}},
            },
        }
        first_search_call = es_instance_mock.search.call_args_list[0]
        self.assertEqual(first_search_call.kwargs['index'], 'search-invest')
        self.assertEqual(first_search_call.kwargs['body'], expected_body)


@patch('ofirio_common.helpers.Elasticsearch')
class SearchMustFilteringTest(SearchBaseTest):
    """
    Check that the correct ES body is constructed when filters by badges provided
    """
    DATA = {
        'type': 'state',
        'state_id': 'FL',
        'start': 0,
        'map_query': False,
        'zoom': 5,
    }

    def init(self, es_class_mock):
        es_instance_mock = self.setup_es_mock(es_class_mock,
                                              const.ES_FLORIDA_SEARCH_RESPONSE_NO_MAP_QUERY)
        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)
        return es_instance_mock

    @patch('search.common.insights_handler.InsightsHandler.get_insights', return_value={})
    def test_default_case(self, ins_mock, es_class_mock):
        es_instance_mock = self.init(es_class_mock)

        filters = {}
        expected_must = []
        response = self.client.post(SEARCH_URL, {**self.DATA, **filters})
        call = es_instance_mock.search.call_args_list[0]
        self.assertEqual(call.kwargs['body']['query']['bool']['must'], expected_must)

    @patch('search.common.insights_handler.InsightsHandler.get_insights', return_value={})
    def test_all_false(self, ins_mock, es_class_mock):
        es_instance_mock = self.init(es_class_mock)
        filters = {
            'is_good_deal': False,
            'is_rehab': False,
            'is_55_plus': False,
            'is_cash_only': False,
            'hide_is_rehab': False,
            'hide_is_55_plus': False,
            'hide_is_cash_only': False,
        }
        expected_must = []
        response = self.client.post(SEARCH_URL, {**self.DATA, **filters})
        call = es_instance_mock.search.call_args_list[0]
        self.assertEqual(call.kwargs['body']['query']['bool']['must'], expected_must)

    @patch('search.common.insights_handler.InsightsHandler.get_insights', return_value={})
    def test_exclude_55_plus(self, ins_mock, es_class_mock):
        es_instance_mock = self.init(es_class_mock)
        filters = {
            'hide_is_55_plus': True,
        }
        expected_must = [{'term': {'is_55_plus': False}}]
        response = self.client.post(SEARCH_URL, {**self.DATA, **filters})
        call = es_instance_mock.search.call_args_list[0]
        self.assertEqual(call.kwargs['body']['query']['bool']['must'], expected_must)

    @patch('search.common.insights_handler.InsightsHandler.get_insights', return_value={})
    def test_exclude_all(self, ins_mock, es_class_mock):
        """
        Exclude all what we can exclude
        """
        es_instance_mock = self.init(es_class_mock)
        filters = {
            'hide_is_rehab': True,
            'hide_is_55_plus': True,
            'hide_is_cash_only': True,
        }
        expected_must = [{'term': {'is_55_plus': False}},
                         {'term': {'is_rehab': False}},
                         {'term': {'is_cash_only': False}}]
        response = self.client.post(SEARCH_URL, {**self.DATA, **filters})
        call = es_instance_mock.search.call_args_list[0]
        self.assertEqual(call.kwargs['body']['query']['bool']['must'], expected_must)

    @patch('search.common.insights_handler.InsightsHandler.get_insights', return_value={})
    def test_good_deals_but_no_cash_only(self, ins_mock, es_class_mock):
        """
        Show good deals, but not cash-only
        """
        es_instance_mock = self.init(es_class_mock)
        filters = {
            'is_good_deal': True,
            'hide_is_cash_only': True,
        }
        expected_must = [{'term': {'is_cash_only': False}},
                         {'bool': {'should': [{'term': {'is_good_deal': True}}]}}]
        response = self.client.post(SEARCH_URL, {**self.DATA, **filters})
        call = es_instance_mock.search.call_args_list[0]
        self.assertEqual(call.kwargs['body']['query']['bool']['must'], expected_must)

    @patch('search.common.insights_handler.InsightsHandler.get_insights', return_value={})
    def test_only_rehab_opportunities(self, ins_mock, es_class_mock):
        es_instance_mock = self.init(es_class_mock)
        filters = {
            'is_good_deal': False,
            'is_rehab': True,
            'is_55_plus': False,
            'is_cash_only': False,
        }
        expected_must = [{'bool': {'should': [{'term': {'is_rehab': True}}]}}]
        response = self.client.post(SEARCH_URL, {**self.DATA, **filters})
        call = es_instance_mock.search.call_args_list[0]
        self.assertEqual(call.kwargs['body']['query']['bool']['must'], expected_must)

    @patch('search.common.insights_handler.InsightsHandler.get_insights', return_value={})
    def test_55_plus_cash_only(self, ins_mock, es_class_mock):
        es_instance_mock = self.init(es_class_mock)
        filters = {
            'is_good_deal': False,
            'is_rehab': False,
            'is_55_plus': True,
            'is_cash_only': True,
        }
        expected_must = [{'bool': {'should': [{'term': {'is_55_plus': True}},
                                              {'term': {'is_cash_only': True}}]}}]
        response = self.client.post(SEARCH_URL, {**self.DATA, **filters})
        call = es_instance_mock.search.call_args_list[0]
        self.assertEqual(call.kwargs['body']['query']['bool']['must'], expected_must)

    @patch('search.common.insights_handler.InsightsHandler.get_insights', return_value={})
    def test_disable_all_filters(self, ins_mock, es_class_mock):
        """
        Disable all filters, all properties will be returned
        """
        es_instance_mock = self.init(es_class_mock)
        filters = {
            'hide_is_rehab': False,
            'hide_is_55_plus': False,
            'hide_is_cash_only': False,
        }
        expected_must = []
        response = self.client.post(SEARCH_URL, {**self.DATA, **filters})
        call = es_instance_mock.search.call_args_list[0]
        self.assertEqual(call.kwargs['body']['query']['bool']['must'], expected_must)

    @patch('search.common.insights_handler.InsightsHandler.get_insights', return_value={})
    def test_good_deals_only(self, ins_mock, es_class_mock):
        es_instance_mock = self.init(es_class_mock)
        filters = {
            'is_good_deal': True,
            'is_rehab': False,
            'is_55_plus': False,
            'is_cash_only': False,
        }
        expected_must = [{'bool': {'should': [{'term': {'is_good_deal': True}}]}}]
        response = self.client.post(SEARCH_URL, {**self.DATA, **filters})
        call = es_instance_mock.search.call_args_list[0]
        self.assertEqual(call.kwargs['body']['query']['bool']['must'], expected_must)
