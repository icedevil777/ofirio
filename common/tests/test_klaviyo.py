from unittest import mock
from unittest.mock import patch

from django.urls import reverse

from account.tests.factories import create_user
from common.tests.base import PortalBaseTest
from search.common.common import mock_is_hidden_true
from search.tests.constants import ES_LOW_CAP_RATE_RESPONSE


class KlaviyoTest(PortalBaseTest):

    @mock.patch('account.authentication.GoogleJwtBackend._verify_token')
    @mock.patch('common.klaviyo.util.identify', side_effect=mock.MagicMock())
    @mock.patch('common.klaviyo.util.add_user_to_list', side_effect=mock.MagicMock())
    def test_user_registration(self, add_to_list_mock, identify_mock, verify_mock):
        user = create_user()

        # user is unverified and cannot be added to klaviyo list
        self.assertFalse(add_to_list_mock.call_args_list)

        email, params = identify_mock.call_args_list[0][0]
        self.assertEqual(email, user.email)
        self.assertEqual(params, {'Good Deal Properties Subscription': False,
                                  'Similar Properties Subscription': False,
                                  'Property Updates Notifications Subscription': False,
                                  'Favorite Properties Subscription': False,
                                  'Similar Favorite Properties Subscription': False,

                                  'Ofirio Tips & Guides Subscription': True,
                                  'Market Reports & Updates Subscription': True,
                                  'Ofirio Tools Updates Subscription': True,
                                  'Partners Offers & Deals Subscription': True,
                                  'May Like Properties Subscription': True,
                                  'Plan Status': 'Unverified'})

        headers = self.google_login(user.email, verify_mock)
        _, params = identify_mock.call_args_list[-1][0]
        self.assertEqual(params['Plan Status'], 'Premium')

        # user got verified and should be added to klaviyo list
        email, list_id = add_to_list_mock.call_args_list[0][0]
        self.assertEqual(email, user.email)
        self.assertEqual(list_id, 'test_list_id')
        
    @patch('ofirio_common.helpers.Elasticsearch')
    @mock.patch('common.klaviyo.util.identify', side_effect=mock.MagicMock())
    @mock.patch('common.klaviyo.util.track', side_effect=mock.MagicMock())
    @mock_is_hidden_true
    def test_view_property(self, track_mock, identify_mock, es_class_mock):
        user = create_user()
        self.client.force_authenticate(user=user)
        self.setup_es_mock(es_class_mock, ES_LOW_CAP_RATE_RESPONSE, method='get')
        # view property
        prop_data = {'prop_id': 'M9627860216'}
        response = self.client.post(
            reverse('api_property:property'), prop_data)
        email, event, params = track_mock.call_args_list[0][0]
        self.assertEqual(email, user.email)
        self.assertEqual(event, 'Viewed Property')
        self.assertEqual(params, {'Item ID': 'M9627860216'})

        # add property to favorites
        fav_data = {
            'prop_id': 'M9627860216',
            'action': 'create',
            'prop_class': 'invest',
        }
        response = self.client.post(reverse('api_property:favorite'), fav_data)
        _, params = identify_mock.call_args_list[1][0]
        self.assertEqual(params, {'Favorite Listings': ['M9627860216']})

        fav_data['prop_id'] = 'CC666AC9B5D6B9C22B5C'
        response = self.client.post(reverse('api_property:favorite'), fav_data)
        _, params = identify_mock.call_args_list[2][0]
        self.assertEqual(params, {'Favorite Listings': ['M9627860216', 'CC666AC9B5D6B9C22B5C']})

        fav_data['action'] = 'delete'
        response = self.client.post(reverse('api_property:favorite'), fav_data)
        _, params = identify_mock.call_args_list[3][0]
        self.assertEqual(params, {'Favorite Listings': ['M9627860216']})
