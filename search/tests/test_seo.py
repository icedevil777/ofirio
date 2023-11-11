from unittest.mock import patch

from django.urls import reverse
from rest_framework import status

from common.tests.base import PortalBaseTest
from search.tests import constants
from search.seo.generators import SeoGenerator
from search.serializers import SearchQuerySerializer
from search.views import Search


class SeoTagsGeneratorTest(PortalBaseTest):
    '''test h1, description, title'''

    def test_facets(self):
        self._test_exact_facets(
            'search-buy', [],
            ['gym', 'under-9999', '1-bedrooms'],
            '1 Bedroom Homes Under $9999 With Gym',
            '1 Bedroom Homes Under $9999 With Gym for Sale in Miami, FL Real Estate',
        )
        self._test_exact_facets(
            'search-rent', ['apartments'],
            ['gym', 'balcony', 'parking'],
            'Apartments With Gym, With Balcony and With Parking',
            'Apartments With Gym, With Balcony and With Parking for Rent in Miami, FL',
        )
        self._test_exact_facets(
            'search-invest', [],
            ['studio', 'cheap', 'waterfront'],
            'Studio Cheap Waterfront Homes',
            'Investment Properties in Miami, FL',
        )
        self._test_exact_facets(
            'search-rent', ['houses'],
            ['pet-friendly', 'conditioning', 'luxury'],
            'Pet Friendly Luxury Houses With Air Conditioning',
            'Pet Friendly Luxury Houses With Air Conditioning for Rent in Miami, FL',
        )
        self._test_exact_facets(
            'search-buy', ['houses'],
            ['5-bedrooms', 'loft'],
            '5 Bedroom Loft Single Family Homes',
            '5 Bedroom Loft Single Family Homes for Sale in Miami, FL Real Estate',
        )
        self._test_exact_facets(
            'search-invest', [],
            ['gym', 'under-900000', '0-bedrooms'],
            'Studio Homes Under $900000 With Gym',
            'Investment Properties in Miami, FL',
        )
        self._test_exact_facets(
            'search-invest', ['condos'],
            ['gym', 'under-900000', '0-bedrooms'],
            'Studio Condos Under $900000 With Gym',
            'Miami, FL Investment Studio Condos Under $900000 With Gym',
        )

    def _test_exact_facets(self, index, prop_types, facets, expected_prop_type, expected_h1):
        data = {
            'start': 0,
            'map_query': False,
            'index': index,
            'type': 'city',
            'cleaned_prop_type': prop_types,
            'state_id': 'fl',
            'city': 'miami',
            'facets': facets,
        }
        serializer = SearchQuerySerializer(data=data)
        if not serializer.is_valid():
            raise Exception('serializer errors %s' % serializer.errors)
        generator = SeoGenerator(serializer, number_search_results=43)
        res = generator.generate_tags()
        # print(index, prop_types)
        # print(facets)
        # print(generator.prop_type_with_facets)
        # print(res['h1'])
        self.assertEqual(generator.prop_type_with_facets, expected_prop_type)
        self.assertEqual(res['h1'], expected_h1)


class SeoBottomTextTest(PortalBaseTest):

    def test_random_seed(self):
        ''' should be the equal for the same input parameters,
            should be different for different input parameters '''
        s1 = self.get_seed('search-buy', [], [])
        s2 = self.get_seed('search-buy', [], [])
        self.assertEqual(s1, s2)

        s1 = self.get_seed('search-buy', [], ['gym'])
        s2 = self.get_seed('search-buy', [], [])
        self.assertNotEqual(s1, s2)

        # multiple facets are not indexable and are interpreted like no facets at all by generator
        s1 = self.get_seed('search-buy', [], [])
        s2 = self.get_seed('search-buy', [], ['gym', 'under-900000'])
        self.assertEqual(s1, s2)

        s1 = self.get_seed('search-buy', [], [])
        s2 = self.get_seed('search-buy', ['houses'], [])
        self.assertNotEqual(s1, s2)

        s1 = self.get_seed('search-buy', ['condos'], [])
        s2 = self.get_seed('search-buy', ['houses'], [])
        self.assertNotEqual(s1, s2)

        # multiple prop types are not indexable and are interpreted like no prop types at all by generator
        s1 = self.get_seed('search-buy', [], [])
        s2 = self.get_seed('search-buy', ['condos', 'houses'], [])
        self.assertEqual(s1, s2)

    def get_seed(self, index, prop_types, facets):
        data = {
            'map_query': False,
            'index': index,
            'type': 'city',
            'cleaned_prop_type': prop_types,
            'state_id': 'ca',
            'city': 'brentwood',
            'facets': facets,
        }
        serializer = SearchQuerySerializer(data=data)
        if not serializer.is_valid():
            raise Exception('serializer errors %s' % serializer.errors)
        generator = SeoGenerator(serializer, insights_data={})
        return generator.random_seed

    def test_place(self):
        data = {
            'map_query': False,
            'index': 'search-rent',
            'type': 'city',
            'cleaned_prop_type': ['houses'],
            'state_id': 'fl',
            'city': 'jacksonville',
            'facets': [],
        }
        serializer = SearchQuerySerializer(data=data)
        if not serializer.is_valid():
            raise Exception('serializer errors %s' % serializer.errors)
        generator = SeoGenerator(serializer, insights_data={})
        self.assertEqual(generator.place, '/rent/fl/jacksonville/houses')
        self.assertEqual(generator.place_type, '/rent/city/houses')

        data = {
            'map_query': False,
            'index': 'search-buy',
            'type': 'state',
            'cleaned_prop_type': [],
            'state_id': 'fl',
            'facets': ['cheap'],
        }
        serializer = SearchQuerySerializer(data=data)
        if not serializer.is_valid():
            raise Exception('serializer errors %s' % serializer.errors)
        generator = SeoGenerator(serializer, insights_data={})
        self.assertEqual(generator.place, '/buy/fl/cheap')
        self.assertEqual(generator.place_type, '/buy/state/cheap')

    def test_spin_texts(self):
        data = {
            'map_query': False,
            'index': 'search-rent',
            'type': 'zip',
            'cleaned_prop_type': [],
            'state_id': 'fl',
            'zip': '33161',
            'facets': [],
        }
        serializer = SearchQuerySerializer(data=data)
        if not serializer.is_valid():
            raise Exception('serializer errors %s' % serializer.errors)
        generator = SeoGenerator(serializer, insights_data={})
        res = generator.generate_bottom_text()
        self.assertTrue('to find a rental' in res['bottom_text'])
        self.assertTrue(res['faq'] is None)

        data = {
            'map_query': False,
            'index': 'search-buy',
            'type': 'city',
            'cleaned_prop_type': ['townhomes'],
            'state_id': 'fl',
            'city': 'orlando',
            'facets': [],
        }
        serializer = SearchQuerySerializer(data=data)
        if not serializer.is_valid():
            raise Exception('serializer errors %s' % serializer.errors)
        generator = SeoGenerator(serializer, insights_data={})
        res = generator.generate_bottom_text()
        self.assertTrue('Townhomes for sale in Orlando' in res['bottom_text'])
        self.assertTrue(res['faq'] is None)

    def test_personal_texts(self):
        data = {
            'map_query': False,
            'index': 'search-invest',
            'type': 'state',
            'cleaned_prop_type': [],
            'state_id': 'fl',
            'facets': [],
        }
        serializer = SearchQuerySerializer(data=data)
        if not serializer.is_valid():
            raise Exception('serializer errors %s' % serializer.errors)
        generator = SeoGenerator(serializer, insights_data={})
        res = generator.generate_bottom_text()
        self.assertTrue('buy investment property in Florida' in res['bottom_text'])
        self.assertTrue(res['faq'] is not None)
        self.assertEqual(
            res['faq'][1]['question'],
            'Is Florida Real Estate a Good Investment?'
        )

        data = {
            'map_query': False,
            'index': 'search-rent',
            'type': 'city',
            'cleaned_prop_type': ['apartments'],
            'state_id': 'fl',
            'city': 'jacksonville',
            'facets': [],
        }
        serializer = SearchQuerySerializer(data=data)
        if not serializer.is_valid():
            raise Exception('serializer errors %s' % serializer.errors)
        generator = SeoGenerator(serializer, insights_data={})
        res = generator.generate_bottom_text()
        self.assertTrue('Jacksonville Apartments and Cost of Living' in res['bottom_text'])
        self.assertEqual(
            res['faq'][1]['question'],
            'Is Rent Expensive in Jacksonville Florida?'
        )

        data = {
            'map_query': False,
            'index': 'search-buy',
            'type': 'city',
            'cleaned_prop_type': [],
            'state_id': 'fl',
            'city': 'miami',
            'facets': [],
        }
        serializer = SearchQuerySerializer(data=data)
        if not serializer.is_valid():
            raise Exception('serializer errors %s' % serializer.errors)
        generator = SeoGenerator(serializer, insights_data={})
        res = generator.generate_bottom_text()
        self.assertFalse(res['bottom_text'] is None)
        self.assertEqual(
            res['faq'][0]['question'],
            'Life in Miami — What Is the Average Home Cost in Miami?'
        )

        data = {
            'map_query': False,
            'index': 'search-buy',
            'type': 'city',
            'cleaned_prop_type': [],
            'state_id': 'ny',
            'city': 'great-neck',
            'facets': [],
        }
        serializer = SearchQuerySerializer(data=data)
        if not serializer.is_valid():
            raise Exception('serializer errors %s' % serializer.errors)
        generator = SeoGenerator(serializer, insights_data={})
        res = generator.generate_bottom_text()
        self.assertFalse(res['bottom_text'] is None)
        self.assertEqual(
            res['faq'][0]['question'],
            'How much does a house cost in Great Neck, New York?'
        )

    def test_near_me(self):
        data = {
            'map_query': False,
            'index': 'search-buy',
            'type': 'geo',
            'cleaned_prop_type': [],
            'facets': [],
            'near_me': True,
        }
        serializer = SearchQuerySerializer(data=data)
        if not serializer.is_valid():
            raise Exception('serializer errors %s' % serializer.errors)
        generator = SeoGenerator(serializer, insights_data={})
        res = generator.generate_bottom_text()

        self.assertTrue(res['bottom_text'] is None)
        self.assertTrue(res['faq'] is None)
        self.assertEqual(generator.place, '/buy/ca')
        self.assertEqual(generator.place_type, '/buy/')

    def test_buy_city(self):
        data = {
            'map_query': False,
            'index': 'search-buy',
            'type': 'city',
            'cleaned_prop_type': ['condos'],
            'state_id': 'ca',
            'city': 'san-francisco',
            'facets': [],
        }
        serializer = SearchQuerySerializer(data=data)
        if not serializer.is_valid():
            raise Exception('serializer errors %s' % serializer.errors)
        generator = SeoGenerator(serializer, insights_data={})
        res = generator.generate_bottom_text()
        self.assertTrue('condos all over the United States' in res['bottom_text'])
        self.assertTrue(res['faq'] is None)
        self.assertEqual(generator.place, '/buy/ca/san-francisco/condos')
        self.assertEqual(generator.place_type, '/buy/city/condos')

        data = {
            'map_query': False,
            'index': 'search-buy',
            'type': 'city',
            'state_id': 'ca',
            'city': 'san-francisco',
            'facets': ['luxury'],
        }
        serializer = SearchQuerySerializer(data=data)
        if not serializer.is_valid():
            raise Exception('serializer errors %s' % serializer.errors)
        generator = SeoGenerator(serializer, insights_data={})
        res = generator.generate_bottom_text()
        self.assertTrue('luxury homes available in all price' in res['bottom_text'])
        self.assertTrue(res['faq'] is None)
        self.assertEqual(generator.place, '/buy/ca/san-francisco/luxury')
        self.assertEqual(generator.place_type, '/buy/city/luxury')


class SeoTagsAPITest(PortalBaseTest):
    url = reverse('search:search')

    @patch('ofirio_common.helpers.Elasticsearch')
    def test_state_tags_for_buy_without_prop_type(self, es_class_mock):
        self.setup_es_mock(es_class_mock, constants.ES_EMPTY_SEARCH_RESPONSE)
        data = {
            'index': 'search-buy',
            'state_id': 'oh',
            'type': 'state',
        }
        resp = self.client.post(self.url, data=data)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(resp.data)
        self.assertIn('seo', resp.data)
        self.assertIsNotNone(resp.data['seo'])
        self.assertIn('h1', resp.data['seo'])
        self.assertIn('title', resp.data['seo'])
        self.assertIn('description', resp.data['seo'])
        self.assertIsNotNone(resp.data['seo']['h1'])
        self.assertIsNotNone(resp.data['seo']['title'])
        self.assertIsNotNone(resp.data['seo']['description'])

        self.assertEqual(resp.data['seo']['h1'], 'Homes for Sale in Ohio Real Estate')
        self.assertEqual(resp.data['seo']['title'], 'Homes for Sale in Ohio 🏡 Real Estate | Ofirio.com')
        self.assertEqual(resp.data['seo']['description'], (
            'Explore over 0 homes for sale in Ohio on Ofirio. Find your '
            'perfect place - View listing photos, compare prices, and a lot more.'
        ))

    @patch('ofirio_common.helpers.Elasticsearch')
    def test_state_tags_for_buy_with_prop_type(self, es_class_mock):
        self.setup_es_mock(es_class_mock, constants.ES_EMPTY_SEARCH_RESPONSE)
        data = {
            'index': 'search-buy',
            'state_id': 'oh',
            'type': 'state',
            'cleaned_prop_type': ['condos']
        }
        resp = self.client.post(self.url, data=data)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(resp.data)
        self.assertIn('seo', resp.data)
        self.assertIsNotNone(resp.data['seo'])
        self.assertIn('h1', resp.data['seo'])
        self.assertIn('title', resp.data['seo'])
        self.assertIn('description', resp.data['seo'])
        self.assertIsNotNone(resp.data['seo']['h1'])
        self.assertIsNotNone(resp.data['seo']['title'])
        self.assertIsNotNone(resp.data['seo']['description'])

        self.assertEqual(resp.data['seo']['h1'], 'Condos for Sale in Ohio Real Estate')
        self.assertEqual(resp.data['seo']['title'], 'Condos for Sale in Ohio 🏡 Real Estate | Ofirio.com')
        self.assertEqual(resp.data['seo']['description'], (
            'Explore over 0 condos for sale in Ohio on Ofirio. Find your '
            'perfect place - View listing photos, compare prices, and a lot more.'
        ))

    @patch('ofirio_common.helpers.Elasticsearch')
    def test_state_tags_for_buy_with_several_prop_types(self, es_class_mock):
        self.setup_es_mock(es_class_mock, constants.ES_EMPTY_SEARCH_RESPONSE)
        data = {
            'index': 'search-buy',
            'state_id': 'oh',
            'type': 'state',
            'cleaned_prop_type': ['condos', 'townhomes', 'houses']
        }
        resp = self.client.post(self.url, data=data)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(resp.data)
        self.assertIn('seo', resp.data)
        self.assertIsNotNone(resp.data['seo'])
        self.assertIn('h1', resp.data['seo'])
        self.assertIn('title', resp.data['seo'])
        self.assertIn('description', resp.data['seo'])
        self.assertIsNotNone(resp.data['seo']['h1'])
        self.assertIsNotNone(resp.data['seo']['title'])
        self.assertIsNotNone(resp.data['seo']['description'])

        self.assertEqual(resp.data['seo']['h1'], 'Homes for Sale in Ohio Real Estate')
        self.assertEqual(resp.data['seo']['title'], 'Homes for Sale in Ohio 🏡 Real Estate | Ofirio.com')
        self.assertEqual(resp.data['seo']['description'], (
            'Explore over 0 homes for sale in Ohio on Ofirio. Find your '
            'perfect place - View listing photos, compare prices, and a lot more.'
        ))

    @patch('ofirio_common.helpers.Elasticsearch')
    def test_county_tags_for_buy_without_prop_type(self, es_class_mock):
        self.setup_es_mock(es_class_mock, constants.ES_EMPTY_SEARCH_RESPONSE)
        data = {
            'index': 'search-buy',
            'county': 'lorain-county',
            'state_id': 'oh',
            'type': 'county',
        }
        resp = self.client.post(self.url, data=data)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(resp.data)
        self.assertIn('seo', resp.data)
        self.assertIsNotNone(resp.data['seo'])
        self.assertIn('h1', resp.data['seo'])
        self.assertIn('title', resp.data['seo'])
        self.assertIn('description', resp.data['seo'])
        self.assertIsNotNone(resp.data['seo']['h1'])
        self.assertIsNotNone(resp.data['seo']['title'])
        self.assertIsNotNone(resp.data['seo']['description'])

        self.assertEqual(resp.data['seo']['h1'], 'Homes for Sale in Lorain County, OH Real Estate')
        self.assertEqual(resp.data['seo']['title'], 'Homes for Sale in Lorain County, OH 🏡 Real Estate | Ofirio.com')
        self.assertEqual(resp.data['seo']['description'], (
            'Explore 0 homes for sale in Lorain County, OH.View listing photos, compare '
            'prices, filter and find exactly what you are looking for in your new Home.'
        ))

    @patch('ofirio_common.helpers.Elasticsearch')
    def test_county_tags_for_buy_with_prop_type(self, es_class_mock):
        self.setup_es_mock(es_class_mock, constants.ES_EMPTY_SEARCH_RESPONSE)
        data = {
            'index': 'search-buy',
            'county': 'lorain-county',
            'state_id': 'oh',
            'type': 'county',
            'cleaned_prop_type': ['townhomes']
        }
        resp = self.client.post(self.url, data=data)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(resp.data)
        self.assertIn('seo', resp.data)
        self.assertIsNotNone(resp.data['seo'])
        self.assertIn('h1', resp.data['seo'])
        self.assertIn('title', resp.data['seo'])
        self.assertIn('description', resp.data['seo'])
        self.assertIsNotNone(resp.data['seo']['h1'])
        self.assertIsNotNone(resp.data['seo']['title'])
        self.assertIsNotNone(resp.data['seo']['description'])

        self.assertEqual(resp.data['seo']['h1'], 'Townhomes for Sale in Lorain County, OH Real Estate')
        self.assertEqual(resp.data['seo']['title'],
                         'Townhomes for Sale in Lorain County, OH 🏡 Real Estate | Ofirio.com')
        self.assertEqual(resp.data['seo']['description'], (
            'Explore 0 townhomes for sale in Lorain County, OH.View listing photos, compare '
            'prices, filter and find exactly what you are looking for in your new Home.'
        ))

    @patch('ofirio_common.helpers.Elasticsearch')
    def test_county_tags_for_buy_with_several_prop_types(self, es_class_mock):
        self.setup_es_mock(es_class_mock, constants.ES_EMPTY_SEARCH_RESPONSE)
        data = {
            'index': 'search-buy',
            'county': 'lorain-county',
            'state_id': 'oh',
            'type': 'county',
            'cleaned_prop_type': ['condos', 'townhomes', 'houses']
        }
        resp = self.client.post(self.url, data=data)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(resp.data)
        self.assertIn('seo', resp.data)
        self.assertIsNotNone(resp.data['seo'])
        self.assertIn('h1', resp.data['seo'])
        self.assertIn('title', resp.data['seo'])
        self.assertIn('description', resp.data['seo'])
        self.assertIsNotNone(resp.data['seo']['h1'])
        self.assertIsNotNone(resp.data['seo']['title'])
        self.assertIsNotNone(resp.data['seo']['description'])

        self.assertEqual(resp.data['seo']['h1'], 'Homes for Sale in Lorain County, OH Real Estate')
        self.assertEqual(resp.data['seo']['title'], 'Homes for Sale in Lorain County, OH 🏡 Real Estate | Ofirio.com')
        self.assertEqual(resp.data['seo']['description'], (
            'Explore 0 homes for sale in Lorain County, OH.View listing photos, compare '
            'prices, filter and find exactly what you are looking for in your new Home.'
        ))

    @patch('ofirio_common.helpers.Elasticsearch')
    def test_city_tags_for_buy_without_prop_type(self, es_class_mock):
        self.setup_es_mock(es_class_mock, constants.ES_EMPTY_SEARCH_RESPONSE)
        data = {
            'index': 'search-buy',
            'state_id': 'tx',
            'type': 'city',
            'city': 'missouri-city',
        }
        resp = self.client.post(self.url, data=data)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(resp.data)
        self.assertIn('seo', resp.data)
        self.assertIsNotNone(resp.data['seo'])
        self.assertIn('h1', resp.data['seo'])
        self.assertIn('title', resp.data['seo'])
        self.assertIn('description', resp.data['seo'])
        self.assertIsNotNone(resp.data['seo']['h1'])
        self.assertIsNotNone(resp.data['seo']['title'])
        self.assertIsNotNone(resp.data['seo']['description'])

        self.assertEqual(resp.data['seo']['h1'], 'Homes for Sale in Missouri City, TX Real Estate')
        self.assertEqual(resp.data['seo']['title'], 'Homes for Sale in Missouri City, TX 🏡 Real Estate | Ofirio.com')
        self.assertEqual(resp.data['seo']['description'], (
            'Explore 0 Missouri City homes for sale in Texas. View listing photos, '
            'compare prices, filter and find exactly what you are looking for in your new Home.'
        ))

    @patch('ofirio_common.helpers.Elasticsearch')
    def test_city_tags_for_buy_with_prop_type(self, es_class_mock):
        self.setup_es_mock(es_class_mock, constants.ES_EMPTY_SEARCH_RESPONSE)
        data = {
            'index': 'search-buy',
            'state_id': 'tx',
            'type': 'city',
            'city': 'missouri-city',
            'cleaned_prop_type': ['condos']
        }
        resp = self.client.post(self.url, data=data)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(resp.data)
        self.assertIn('seo', resp.data)
        self.assertIsNotNone(resp.data['seo'])
        self.assertIn('h1', resp.data['seo'])
        self.assertIn('title', resp.data['seo'])
        self.assertIn('description', resp.data['seo'])
        self.assertIsNotNone(resp.data['seo']['h1'])
        self.assertIsNotNone(resp.data['seo']['title'])
        self.assertIsNotNone(resp.data['seo']['description'])

        self.assertEqual(resp.data['seo']['h1'], 'Condos for Sale in Missouri City, TX Real Estate')
        self.assertEqual(resp.data['seo']['title'], 'Condos for Sale in Missouri City, TX 🏡 Real Estate | Ofirio.com')
        self.assertEqual(resp.data['seo']['description'], (
            'Explore 0 Missouri City condos for sale in Texas. View listing photos, '
            'compare prices, filter and find exactly what you are looking for in your new Home.'
        ))

    @patch('ofirio_common.helpers.Elasticsearch')
    def test_city_tags_for_buy_with_several_prop_types(self, es_class_mock):
        self.setup_es_mock(es_class_mock, constants.ES_EMPTY_SEARCH_RESPONSE)
        data = {
            'index': 'search-buy',
            'state_id': 'tx',
            'type': 'city',
            'city': 'missouri-city',
            'cleaned_prop_type': ['condos', 'townhomes', 'houses']
        }
        resp = self.client.post(self.url, data=data)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(resp.data)
        self.assertIn('seo', resp.data)
        self.assertIsNotNone(resp.data['seo'])
        self.assertIn('h1', resp.data['seo'])
        self.assertIn('title', resp.data['seo'])
        self.assertIn('description', resp.data['seo'])
        self.assertIsNotNone(resp.data['seo']['h1'])
        self.assertIsNotNone(resp.data['seo']['title'])
        self.assertIsNotNone(resp.data['seo']['description'])

        self.assertEqual(resp.data['seo']['h1'], 'Homes for Sale in Missouri City, TX Real Estate')
        self.assertEqual(resp.data['seo']['title'], 'Homes for Sale in Missouri City, TX 🏡 Real Estate | Ofirio.com')
        self.assertEqual(resp.data['seo']['description'], (
            'Explore 0 Missouri City homes for sale in Texas. View listing photos, '
            'compare prices, filter and find exactly what you are looking for in your new Home.'
        ))

    @patch('ofirio_common.helpers.Elasticsearch')
    def test_zip_tags_for_buy_without_prop_type(self, es_class_mock):
        self.setup_es_mock(es_class_mock, constants.ES_EMPTY_SEARCH_RESPONSE)
        data = {
            'index': 'search-buy',
            'state_id': 'nv',
            'type': 'zip',
            'zip': 89108
        }
        resp = self.client.post(self.url, data=data)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(resp.data)
        self.assertIn('seo', resp.data)
        self.assertIsNotNone(resp.data['seo'])
        self.assertIn('h1', resp.data['seo'])
        self.assertIn('title', resp.data['seo'])
        self.assertIn('description', resp.data['seo'])
        self.assertIsNotNone(resp.data['seo']['h1'])
        self.assertIsNotNone(resp.data['seo']['title'])
        self.assertIsNotNone(resp.data['seo']['description'])

        self.assertEqual(resp.data['seo']['h1'], '89108, NV Homes for Sale Real Estate')
        self.assertEqual(resp.data['seo']['title'], '89108, NV Homes for Sale 🏡 Real Estate | Ofirio.com')
        self.assertEqual(resp.data['seo']['description'], (
            'Explore 0 homes for sale in 89108, NV. View listing photos, compare '
            'prices, filter and find exactly what you are looking for in your new Home.'
        ))

    @patch('ofirio_common.helpers.Elasticsearch')
    def test_zip_tags_for_buy_with_prop_type(self, es_class_mock):
        self.setup_es_mock(es_class_mock, constants.ES_EMPTY_SEARCH_RESPONSE)
        data = {
            'index': 'search-buy',
            'state_id': 'nv',
            'type': 'zip',
            'zip': 89108,
            'cleaned_prop_type': ['townhomes']
        }
        resp = self.client.post(self.url, data=data)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(resp.data)
        self.assertIn('seo', resp.data)
        self.assertIsNotNone(resp.data['seo'])
        self.assertIn('h1', resp.data['seo'])
        self.assertIn('title', resp.data['seo'])
        self.assertIn('description', resp.data['seo'])
        self.assertIsNotNone(resp.data['seo']['h1'])
        self.assertIsNotNone(resp.data['seo']['title'])
        self.assertIsNotNone(resp.data['seo']['description'])

        self.assertEqual(resp.data['seo']['h1'], '89108, NV Townhomes for Sale Real Estate')
        self.assertEqual(resp.data['seo']['title'], '89108, NV Townhomes for Sale 🏡 Real Estate | Ofirio.com')
        self.assertEqual(resp.data['seo']['description'], (
            'Explore 0 townhomes for sale in 89108, NV. View listing photos, compare '
            'prices, filter and find exactly what you are looking for in your new Home.'
        ))

    @patch('ofirio_common.helpers.Elasticsearch')
    def test_zip_tags_for_buy_with_several_prop_types(self, es_class_mock):
        self.setup_es_mock(es_class_mock, constants.ES_EMPTY_SEARCH_RESPONSE)
        data = {
            'index': 'search-buy',
            'state_id': 'nv',
            'type': 'zip',
            'zip': 89108,
            'cleaned_prop_type': ['condos', 'townhomes', 'houses']
        }
        resp = self.client.post(self.url, data=data)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(resp.data)
        self.assertIn('seo', resp.data)
        self.assertIsNotNone(resp.data['seo'])
        self.assertIn('h1', resp.data['seo'])
        self.assertIn('title', resp.data['seo'])
        self.assertIn('description', resp.data['seo'])
        self.assertIsNotNone(resp.data['seo']['h1'])
        self.assertIsNotNone(resp.data['seo']['title'])
        self.assertIsNotNone(resp.data['seo']['description'])

        self.assertEqual(resp.data['seo']['h1'], '89108, NV Homes for Sale Real Estate')
        self.assertEqual(resp.data['seo']['title'], '89108, NV Homes for Sale 🏡 Real Estate | Ofirio.com')
        self.assertEqual(resp.data['seo']['description'], (
            'Explore 0 homes for sale in 89108, NV. View listing photos, compare '
            'prices, filter and find exactly what you are looking for in your new Home.'
        ))
