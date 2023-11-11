from unittest.mock import patch, MagicMock

from django.urls import reverse
from django.test import override_settings
from rest_framework import status

from account.models import FavoriteProperty, CustomUser
from account.tests.base import AccountBaseTest
from account.tests.factories import create_user
from account.utils import get_access_status
from api_property.models import ContactAgent
from api_property.tests.base import PropertyBaseTest
from api_property.tests.constants import PROP_673, PROP_8BE
from common.tests.base import PortalBaseTest
from search import utils as search_utils
from search.common.common import mock_is_hidden_false, mock_is_hidden_true
from search.tests.constants import (
    ES_HIGH_CAP_RATE_RESPONSE,
    ES_LOW_CAP_RATE_RESPONSE,
)

PROP_ID_VALID_DATA = {'prop_id': 'M9627860216'}
HIDDEN_PROPERTY = 'CC666AC9B5D6B9C22B5C'  # has prop_cache.is_test = true


@patch('ofirio_common.helpers.Elasticsearch')
class PropertyViewTest(PropertyBaseTest):
    """Tests for Property View"""

    URL = reverse('api_property:property')

    @override_settings(IS_PRODUCTION=True)
    @mock_is_hidden_false
    def test_hidden_prop_on_prod(self, *a, **kw):
        response = self.client.post(self.URL, {'prop_id': HIDDEN_PROPERTY})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @override_settings(IS_PRODUCTION=False)
    @mock_is_hidden_false
    def test_hidden_prop_on_test_env(self, *a, **kw):
        response = self.client.post(self.URL, {'prop_id': HIDDEN_PROPERTY})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock_is_hidden_false
    def test_not_authed(self, es_class_mock):
        self.setup_es_mock(es_class_mock, ES_LOW_CAP_RATE_RESPONSE, method='get')
        response = self.client.post(self.URL, PROP_ID_VALID_DATA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock_is_hidden_true
    def test_success(self, es_class_mock):
        self.setup_es_mock(es_class_mock, ES_LOW_CAP_RATE_RESPONSE, method='get')
        user = create_user()
        self.client.force_authenticate(user=user)

        response = self.client.post(self.URL, PROP_ID_VALID_DATA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['prop_id'], 'M9627860216')

        expected_data_keys = (
            'status', 'update_date', 'data', 'address', 'photos', 'summary', 'features',
            'favorite',
        )
        for key in expected_data_keys:
            self.assertIn(key, response.data)


class TaxHistoryViewTest(PropertyBaseTest):
    """Tests for TaxHistory View"""

    URL = reverse('api_property:tax_history')

    def test_not_authed(self):
        response = self.client.post(self.URL, PROP_ID_VALID_DATA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PropHistoryViewTest(PropertyBaseTest):
    """Tests for PropHistory View"""

    URL = reverse('api_property:prop_history')

    def test_not_authed(self):
        response = self.client.post(self.URL, PROP_ID_VALID_DATA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SchoolsViewTest(PropertyBaseTest):
    """Tests for Schools View"""

    URL = reverse('api_property:schools')

    def test_not_authed(self):
        response = self.client.post(self.URL, PROP_ID_VALID_DATA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


@patch('ofirio_common.helpers.Elasticsearch')
class FinanceViewTest(PropertyBaseTest):
    """Tests for Finance View"""

    URL = reverse('api_property:finance')
    VALID_DATA = {
        'prop_id': 'M9627860216',
    }

    def tearDown(self):
        search_utils._ES = None
        super().tearDown()

    @mock_is_hidden_true
    def test_not_authed(self, es_class_mock):
        """
        Anon user cannot receive finance estimation info
        for properties with high cap rate
        """
        self.setup_es_mock(es_class_mock, ES_HIGH_CAP_RATE_RESPONSE)
        response = self.client.post(self.URL, self.VALID_DATA)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @mock_is_hidden_true
    def test_not_authed2(self, es_class_mock):
        """
        Anon user allowed to receive finance estimation info
        for properties with low cap rate
        """
        self.setup_es_mock(es_class_mock, ES_LOW_CAP_RATE_RESPONSE)
        response = self.client.post(self.URL, self.VALID_DATA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock_is_hidden_true
    def test_unverified_user(self, es_class_mock):
        """
        A free user (the one that does not have Trial or Premium access status)
        cannot receive finance estimation info
        for properties with high cap rate
        """
        self.setup_es_mock(es_class_mock, ES_HIGH_CAP_RATE_RESPONSE)
        user = create_user({})
        self.client.force_authenticate(user=user)

        response = self.client.post(self.URL, self.VALID_DATA)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @mock_is_hidden_true
    def test_unverified_user2(self, es_class_mock):
        """
        A free user (the one that does not have Trial or Premium access status)
        allowed to receive finance estimation info
        for properties with low cap rate
        """
        self.setup_es_mock(es_class_mock, ES_LOW_CAP_RATE_RESPONSE)
        user = create_user({})
        self.client.force_authenticate(user=user)

        response = self.client.post(self.URL, self.VALID_DATA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock_is_hidden_false
    def test_verified_user(self, es_class_mock):
        """
        A free user (the one that does not have Trial or Premium access status)
        cannot receive finance estimation info
        for properties with high cap rate
        """
        user = create_user({'verified': True})
        self.assertEqual(get_access_status(user), 'verified')
        self.client.force_authenticate(user=user)

        response = self.client.post(self.URL, self.VALID_DATA)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @mock_is_hidden_false
    def test_verified_user2(self, es_class_mock):
        """
        A free user (the one that does not have Trial or Premium access status)
        allowed to  receive finance estimation info
        for properties with low cap rate
        """
        self.setup_es_mock(es_class_mock, ES_LOW_CAP_RATE_RESPONSE)
        user = create_user({'verified': True})
        self.assertEqual(get_access_status(user), 'verified')
        self.client.force_authenticate(user=user)

        response = self.client.post(self.URL, self.VALID_DATA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_empty_prop_id(self, es_class_mock):
        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)
        invalid_data = {'prop_id': ''}

        response = self.client.post(self.URL, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_prop_not_found(self, es_class_mock):
        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)
        invalid_data = {'prop_id': 'M1111111111'}

        response = self.client.post(self.URL, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_success(self, es_class_mock):
        self.setup_es_mock(es_class_mock, ES_HIGH_CAP_RATE_RESPONSE)
        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)

        response = self.client.post(self.URL, self.VALID_DATA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['prop_id'], 'M9627860216')

        expected_data_keys = (
            'base', 'main_results', 'detailed', 'monthly_cash_flow', 'performance', 'proforma',
            'accumulated_wealth',
        )
        for key in expected_data_keys:
            self.assertIn(key, response.data)

        expected_base_keys = (
            'price', 'monthly_rent', 'down_payment', 'financing_years', 'interest_rate',
        )
        for key in expected_base_keys:
            self.assertIn(key, response.data['base'])

    def test_down_payment_1_if_cash(self, es_class_mock):
        """
        If down_payment is not set and a property has is_cash_only==True,
        down_payment must be 1 instead of the usual default 0.2
        """
        self.setup_es_mock(es_class_mock, ES_HIGH_CAP_RATE_RESPONSE)
        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)

        response = self.client.post(self.URL, {'prop_id': 'M9980428774'})
        self.assertEqual(response.data['base']['down_payment'], 1)


@patch('common.klaviyo.util.get_pg_connection')
@patch('common.klaviyo.util.get_similar')
@patch('common.klaviyo.util.track')
@patch('common.klaviyo.util.read_notification_props')
@patch('common.klaviyo.helpers.ask_socket_for_one_url')
class FavoriteViewTest(PropertyBaseTest):
    """Tests for Favorite View"""

    URL = reverse('api_property:favorite')
    VALID_DATA = {
        'prop_id': 'M9627860216',
        'prop_class': 'buy'
    }

    def test_not_authed(self, _, _1, _2, _3, _4):
        response = self.client.post(self.URL, self.VALID_DATA)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_to_fav(self, _, _1, _2, _3, _4):
        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)

        self.assertEqual(FavoriteProperty.objects.count(), 0)
        response = self.client.post(self.URL, self.VALID_DATA)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FavoriteProperty.objects.count(), 1)

        favorite = FavoriteProperty.objects.first()
        self.assertEqual(favorite.prop_id, 'M9627860216')
        self.assertEqual(favorite.user.pk, user.pk)

        self.assertTrue(favorite.estimated_rent)

    def test_delete_from_fav_by_pk(self, _, _1, _2, _3, _4):
        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)

        self.assertEqual(FavoriteProperty.objects.count(), 0)
        self.client.post(self.URL, self.VALID_DATA)
        self.assertEqual(FavoriteProperty.objects.count(), 1)

        delete_url = reverse('api_property:favorite_delete',
                             args=[FavoriteProperty.objects.first().pk])
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(FavoriteProperty.objects.count(), 0)

    def test_delete_from_fav_by_prop_id(self, _, _1, _2, _3, _4):
        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)

        self.assertEqual(FavoriteProperty.objects.count(), 0)
        self.client.post(self.URL, self.VALID_DATA)
        self.assertEqual(FavoriteProperty.objects.count(), 1)

        delete_url = reverse('api_property:favorite_delete',
                             args=[FavoriteProperty.objects.first().prop_id])
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(FavoriteProperty.objects.count(), 0)

    def test_create_without_photo(self, _, _1, _2, _3, _4):
        """User adds a prop that has no photo"""
        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)

        response = self.client.post(self.URL, {'prop_id': 'M5454893686',
                                               'prop_class': 'buy'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FavoriteProperty.objects.count(), 1)
        self.assertEqual(FavoriteProperty.objects.first().prop_id, 'M5454893686')

    def test_klaviyo_called(self, socket_mock, read_mock, track_mock, get_similar_mock, _):
        # main, related
        read_mock.side_effect = [[PROP_8BE], [PROP_673]]

        get_similar_mock.return_value = [{'prop_id': '67350E9C4288BE92C6B7', 'photo': '.'}]
        user = create_user()
        self.client.force_authenticate(user=user)

        response = self.client.post(self.URL, {'prop_id': '8BE92C6B767350E9C428',
                                               'prop_class': 'buy'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(socket_mock.called)
        self.assertTrue(read_mock.called)
        self.assertTrue(track_mock.called)
        self.assertTrue(get_similar_mock.called)

        # check klaviyo.track payload
        payload = track_mock.call_args[0][2]['props']

        self.assertEqual(len(payload['main'][0]), 1)
        self.assertEqual(payload['main'][0][0]['prop_id'], '8BE92C6B767350E9C428')

        self.assertEqual(len(payload['related'][0]), 1)
        self.assertEqual(payload['related'][0][0]['prop_id'], '67350E9C4288BE92C6B7')

    def test_fav_settings_updated(self, socket_mock, read_mock, track_mock, get_similar_mock, _):
        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)

        self.assertEqual(user.emailsettings_set.first().favorites, False)
        self.assertEqual(user.emailsettings_set.first().favorites_match_notification, False)

        response = self.client.post(self.URL, self.VALID_DATA)

        self.assertEqual(user.emailsettings_set.first().favorites, True)
        self.assertEqual(user.emailsettings_set.first().favorites_match_notification, True)


class CommonTestContactAgent:
    """Tests for ContactAgent View"""

    def test_not_authed(self):
        response = self.client.post(self.URL, self.VALID_DATA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('api_property.emails.ContactAgentEmail.send', side_effect=MagicMock())
    def test_agent_email_sent(self, email_send_mock):
        self.client.post(self.URL, self.VALID_DATA)
        self.assertTrue(email_send_mock.call_args_list)

    @patch('api_property.emails.ThanksForInterestEmail.send', side_effect=MagicMock())
    def test_thank_email_sent(self, email_send_mock):
        self.client.post(self.URL, self.VALID_DATA)
        self.assertTrue(email_send_mock.call_args_list)

    def test_db_object_created(self):
        self.assertFalse(ContactAgent.objects.count())

        self.client.post(self.URL, self.VALID_DATA)
        self.assertTrue(ContactAgent.objects.count())

    @patch('common.sheets.add_to_google_sheets.delay', side_effect=MagicMock())
    def test_right_signs(self, google_sheets_mock):
        data = self.VALID_DATA.copy()
        name = '=fooo'
        data['full_name'] = name
        response = self.client.post(self.URL, data)
        full_name = google_sheets_mock.call_args_list[0][0][0]['full_name']
        self.assertEqual(full_name, f'|{name}')

    def test_user_not_created(self):
        self.client.post(self.URL, self.VALID_DATA)
        self.assertFalse(CustomUser.objects.filter(email='bal@lab.ba').first())

    def test_user_created_and_change_e_settings_and_similar(self):
        data = self.VALID_DATA.copy()
        data['enable_alerts'] = True  # past
        self.client.post(self.URL, data)
        user = CustomUser.objects.get(email='bal@lab.ba')  # don't need assert cause Get should
        self.assertTrue(user.similar_props.all())          # return exeption if user not exists


class ScheduleTourTest(CommonTestContactAgent, PortalBaseTest):
    URL = reverse('api_property:schedule_tour')
    VALID_DATA = {
        'prop_id': '8BE92C6B767350E9C428',
        'full_name': 'Terry Gilliam',
        'email': 'bal@lab.ba',
        'phone': '+555555555',
        'url': '/p/33740-skiff-aly-unit-3109-de-19958/8BE92C6B767350E9C428',
        'recaptcha': 'jj',
        'enable_alerts': False,
        'schedule_tour_date': '2045-06-12',
        'schedule_tour_time': '8:00am',
        'tour_type': 'in_person',
    }

    @patch('requests.get', side_effect=MagicMock())
    @patch('requests.post', side_effect=MagicMock())
    def test_tg_called(self, requests_post_mock, requests_get_mock):
        """
        Check Telegram requested, and that
        all the required info is in the message
        """
        self.client.post(self.URL, self.VALID_DATA)
        self.assertTrue(requests_post_mock.call_args_list)

        text = requests_post_mock.call_args_list[0].args[1]['text']
        self.assertIn('bal@lab.ba', text)  # email
        self.assertIn('Terry Gilliam', text)  # name
        self.assertIn('555555555', text)  # phone
        self.assertIn('buy', text)  # prop_class
        self.assertIn('897000', text)  # price
        self.assertIn('33740-skiff-aly-unit-3109-de-19958', text)  # url
        self.assertIn('2045-06-12', text)  # tour date
        self.assertIn('08:00:00', text)  # tour time
        self.assertIn('in_person', text)  # tour type
        self.assertIn(
            '/p/33740-skiff-aly-unit-3109-de-19958/8BE92C6B767350E9C428',
            text)  # link

    def test_schedule_tour_date(self):
        data = self.VALID_DATA.copy()
        data['schedule_tour_date'] = '2020-06-06'   # past
        response = self.client.post(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RebateViewTest(CommonTestContactAgent, PortalBaseTest):
    URL = reverse('api_property:rebate')
    VALID_DATA = {
        'prop_id': '8BE92C6B767350E9C428',
        'full_name': 'Terry Gilliam',
        'email': 'bal@lab.ba',
        'phone': '+555555555',
        'enable_alerts': False,
        'request': 'please spam',
        'url': '/p/33740-skiff-aly-unit-3109-de-19958/8BE92C6B767350E9C428',
        'recaptcha': 'jj',
        'best_time_to_call': 'noon',
    }

    @patch('requests.get', side_effect=MagicMock())
    @patch('requests.post', side_effect=MagicMock())
    def test_tg_called(self, requests_post_mock, requests_get_mock):
        """
        Check Telegram requested, and that
        all the required info is in the message
        """

        self.client.post(self.URL, self.VALID_DATA)
        self.assertTrue(requests_post_mock.call_args_list)

        text = requests_post_mock.call_args_list[0].args[1]['text']
        self.assertIn('bal@lab.ba', text)  # email
        self.assertIn('Terry Gilliam', text)  # name
        self.assertIn('555555555', text)  # phone
        self.assertIn('buy', text)  # prop_class
        self.assertIn('897000', text)  # price
        self.assertIn('33740-skiff-aly-unit-3109-de-19958', text)  # url
        self.assertIn('noon', text)  # best time to call
        self.assertIn('6727.5', text)  # rebate
        self.assertIn(
            '/p/33740-skiff-aly-unit-3109-de-19958/8BE92C6B767350E9C428',
            text)  # link


        self.assertNotIn(': 33740 Skiff Aly Unit 3109', text)  # address
        self.assertNotIn(': 8BE92C6B767350E9C428', text)  # prop_id


class CheckAvailabilityTest(CommonTestContactAgent, PortalBaseTest):
    URL = reverse('api_property:check_availability')
    VALID_DATA = {
        'prop_id': 'R8BE92C6B767350E9C428',
        'full_name': 'Terry Gilliam',
        'email': 'bal@lab.ba',
        'phone': '+555555555',
        'url': '/p/33740-skiff-aly-unit-3109-de-19958/R8BE92C6B767350E9C428',
        'recaptcha': 'jj',
        'enable_alerts': False,
        'move_in_date': '2067-06-06',
    }

    @patch('requests.get', side_effect=MagicMock())
    @patch('requests.post', side_effect=MagicMock())
    def test_tg_called(self, requests_post_mock, requests_get_mock):
        """
        Check Telegram requested, and that
        all the required info is in the message
        """

        self.client.post(self.URL, self.VALID_DATA)
        self.assertTrue(requests_post_mock.call_args_list)

        text = requests_post_mock.call_args_list[0].args[1]['text']
        self.assertIn('bal@lab.ba', text)  # email
        self.assertIn('Terry Gilliam', text)  # name
        self.assertIn('555555555', text)  # phone
        self.assertIn('rent', text)  # prop_class
        self.assertIn('897000', text)  # price
        self.assertIn('33740-skiff-aly-unit-3109-de-19958', text)  # url
        self.assertIn('2067-06-06', text)  # move in date
        self.assertIn(
            '/p/33740-skiff-aly-unit-3109-de-19958/R8BE92C6B767350E9C428',
            text)  # link

        self.assertNotIn(': 33740 Skiff Aly Unit 3109', text)  # address
        self.assertNotIn(': R8BE92C6B767350E9C428', text)  # prop_id

    def test_schedule_tour_date(self):
        data = self.VALID_DATA.copy()
        data['move_in_date'] = '2020-06-06'  # past
        response = self.client.post(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AskQuestionTest(CommonTestContactAgent, PortalBaseTest):
    URL = reverse('api_property:ask_question')
    VALID_DATA = {
        'prop_id': '8BE92C6B767350E9C428',
        'full_name': 'Terry Gilliam',
        'email': 'bal@lab.ba',
        'phone': '+555555555',
        'request': 'please spam',
        'url': '/p/33740-skiff-aly-unit-3109-de-19958/M9627860216',
        'recaptcha': 'jj',
        'enable_alerts': False,
        'prop_class': 'buy',
    }

    @patch('requests.get', side_effect=MagicMock())
    @patch('requests.post', side_effect=MagicMock())
    def test_tg_called(self, requests_post_mock, requests_get_mock):
        """
        Check Telegram requested, and that
        all the required info is in the message
        """

        self.client.post(self.URL, self.VALID_DATA)
        self.assertTrue(requests_post_mock.call_args_list)

        text = requests_post_mock.call_args_list[0].args[1]['text']
        self.assertIn('bal@lab.ba', text)  # email
        self.assertIn('Terry Gilliam', text)  # name
        self.assertIn('555555555', text)  # phone
        self.assertIn('buy', text)  # prop_class
        self.assertIn('897000', text)  # price
        self.assertIn('33740-skiff-aly-unit-3109-de-19958', text)  # url
        self.assertIn('please spam', text)  # message

        self.assertNotIn(': 33740 Skiff Aly Unit 3109', text)  # address
        self.assertNotIn(': 8BE92C6B767350E9C428', text)  # prop_id

    def test_not_found_by_prop_class(self):
        data = self.VALID_DATA.copy()
        data['prop_class'] = 'rent'
        response = self.client.post(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OnlyParamsRebateViewTest(CommonTestContactAgent, PortalBaseTest):
    URL = reverse('api_property:only_params_rebate')
    VALID_DATA = {
        'prop_id': '8BE92C6B767350E9C428',
        'url': '/p/33740-skiff-aly-unit-3109-de-19958/8BE92C6B767350E9C428',
        'full_name': 'Terry Gilliam',
        'email': 'bal@lab.ba',
        'phone': '+555555555',
        'recaptcha': 'jj',
        'best_time_to_call': 'noon',
    }

    @patch('requests.get', side_effect=MagicMock())
    @patch('requests.post', side_effect=MagicMock())
    def test_tg_called(self, requests_post_mock, requests_get_mock):
        """
        Check Telegram requested, and that
        all the required info is in the message
        """
        self.client.post(self.URL, self.VALID_DATA)
        self.assertTrue(requests_post_mock.call_args_list)

        text = requests_post_mock.call_args_list[0].args[1]['text']
        self.assertIn('bal@lab.ba', text)  # email
        self.assertIn('Terry Gilliam', text)  # name
        self.assertIn('555555555', text)  # phone
        self.assertIn('noon', text)  # best time to call

    def test_user_created_and_change_e_settings_and_similar(self):
        pass

    @patch('common.sheets.add_to_google_sheets.delay', side_effect=MagicMock())
    def test_fields_in_sheets(self, google_sheets_mock):
        response = self.client.post(self.URL, self.VALID_DATA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        args = google_sheets_mock.call_args_list[0][0][0]
        self.assertEqual(args['prop']['prop_id'], '8BE92C6B767350E9C428')
        self.assertEqual(args['prop']['address']['full_address'], 'fooooooo')
        self.assertIn('/p/33740-skiff-aly-unit-3109-de-19958/8BE92C6B767350E9C428', args['url'])


@patch('ofirio_common.helpers.Elasticsearch')
class AnalyticsViewTest(PropertyBaseTest):
    ANALYTICS_VALID_DATA = {
        "prop_id": "8BE92C6B767350E9C428",
        "agg_type": "city",
        "prop_class": "sale",
        "graph_names": ["new_listings_year_over_year"]
    }
    URL = reverse('api_property:analytics')

    ES_HIGH_RESPONSE = {'_index': 'search-20211209145340',
                        '_type': '_doc',
                        '_id': '8BE92C6B767350E9C428',
                        '_version': 1,
                        '_seq_no': 664,
                        '_primary_term': 1,
                        'found': True,
                        '_source': {'zip': '33028',
                                    'city': 'apalachicola',
                                    'county_name': 'franklin',
                                    'state_id': 'FL',
                                    'is_high_cap_rate': True,
                                    'cleaned_prop_type': 'house-duplex'}}
    ES_LOW_RESPONSE = {'_index': 'search-20211209145340',
                       '_type': '_doc',
                       '_id': '8BE92C6B767350E9C428',
                       '_version': 1,
                       '_seq_no': 664,
                       '_primary_term': 1,
                       'found': True,
                       '_source': {'zip': '33028',
                                   'city': 'apalachicola',
                                   'county_name': 'franklin',
                                   'state_id': 'FL',
                                   'cleaned_prop_type': 'house-duplex',
                                   'is_high_cap_rate': False}}

    def test_analytics_status_without_sub(self, es_class_mock):
        self.setup_es_mock(es_class_mock, self.ES_LOW_RESPONSE, method='get')
        response = self.client.post(self.URL, self.ANALYTICS_VALID_DATA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data,
                         {'graphs': {'new_listings_year_over_year':
                             {'meta': {'_details': {
                                 '_agg_type': 'city',
                                 '_prop_type2': 'house-duplex',
                                 '_city': 'apalachicola',
                                 '_zip_code': '33028',
                                 '_county': 'franklin',
                                 '_state_id': 'FL',
                                 '_state_name': 'Florida'}},
                                 'labels': ['range_price',
                                            'At asking price'],
                                 'datasets': [{'data': [{'max': 300000,
                                                         'min': 160000},
                                                        1.0],
                                               'name': 0,
                                               'type': 'plain'},
                                              {'data': [{'max': 450000,
                                                         'min': 300000},
                                                        1.0],
                                               'name': 1,
                                               'type': 'plain'}]}},
                             'agg_type': 'city'})

    def test_analytics_status_with_sub(self, es_class_mock):
        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)
        self.setup_es_mock(es_class_mock, self.ES_HIGH_RESPONSE, method='get')
        response = self.client.post(self.URL, self.ANALYTICS_VALID_DATA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AffordabilityViewTest(PropertyBaseTest):
    VALID_DATA = {'prop_id': '8BE92C6B767350E9C428',
                  'price': 123.0,
                  'down_payment': 0.2,
                  'interest_rate': 0.033,
                  'loan_type': 15,
                  'yearly_insurance': 123.0,
                  'prop_tax_est': 123.0,
                  'monthly_hoa': 123.0}

    INVALID_DATA = {'prop_id': '8BE92C6B767350E9C428',
                    'price': 'test',
                    'down_payment': 'test',
                    'interest_rate': 'test',
                    'loan_type': 'test',
                    'yearly_insurance': 'test',
                    'prop_tax_est': 'test',
                    'monthly_hoa': 'test'}

    LOW_DOWN_PAYMENT_DATA = {'prop_id': '8BE92C6B767350E9C428',
                             'down_payment': 0.18}

    URL = reverse('api_property:affordability')

    def test_affordability_status(self):
        response = self.client.post(self.URL, self.VALID_DATA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(self.URL, self.INVALID_DATA)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_mortgage(self):
        response = self.client.post(self.URL, self.LOW_DOWN_PAYMENT_DATA)
        self.assertTrue(response.data['mortgage insurance'])

        response = self.client.post(self.URL, self.VALID_DATA)
        with self.assertRaises(KeyError):
            response.data['mortgage insurance']


class SimilarNotificationViewTest(AccountBaseTest):
    GET_POST_URL = reverse('api_property:similar_notification')

    def test_authed(self):
        user = create_user()
        self.client.force_authenticate(user=user)

        response = self.client.get(self.GET_POST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_authed(self):
        response = self.client.get(self.GET_POST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_similar_notification_post(self):
        user = create_user()
        self.client.force_authenticate(user=user)

        response = self.client.post(self.GET_POST_URL,
                                    {'prop_id': '8BE92C6B767350E9C428', 'prop_class': 'buy'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        not_valid_response = self.client.post(self.GET_POST_URL,
                                              {'prop_id': '8BE92C6B767350E9C428',
                                               'prop_class': 'buy'})  # the same prop again
        self.assertEqual(not_valid_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_email_setting(self):
        user = create_user()
        self.client.force_authenticate(user=user)

        e_settings_before_add_similar = self.client.get(reverse('account:email_settings'))

        self.client.post(self.GET_POST_URL,
                         {'prop_id': '8BE92C6B767350E9C428', 'prop_class': 'buy'})
        e_settings_after_add_similar = self.client.get(reverse('account:email_settings'))
        self.assertNotEqual(e_settings_before_add_similar.data.pop('similars'),
                            e_settings_after_add_similar.data.pop('similars'))
        self.assertEqual(e_settings_before_add_similar.data, e_settings_after_add_similar.data)

    def test_similar_notification_delete(self):
        user = create_user()
        self.client.force_authenticate(user=user)
        self.client.post(self.GET_POST_URL,
                         {'prop_id': '8BE92C6B767350E9C428', 'prop_class': 'buy'})  # add prop
        obj = user.similar_props.get(prop_id='8BE92C6B767350E9C428', user=user)
        del_url = reverse('api_property:similar_notification_delete', args=[obj.pk])
        response = self.client.delete(del_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response_second = self.client.delete(del_url)  # try delete already deleted
        self.assertEqual(response_second.status_code, status.HTTP_404_NOT_FOUND)


class PropUpdatesViewTest(AccountBaseTest):
    URL = reverse('api_property:prop_updates')

    def test_create_authed(self):
        user = create_user()
        self.client.force_authenticate(user=user)

        response = self.client.post(self.URL, {'prop_id': '8BE92C6B767350E9C428',
                                               'prop_class': 'buy'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['price'], 897000)
        self.assertEqual(response.data['status'], 'for_sale')

    def test_create_not_authed(self):
        response = self.client.post(self.URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_email_settings_changed(self):
        user = create_user()
        self.client.force_authenticate(user=user)
        self.assertEqual(user.emailsettings_set.first().prop_updates, False)

        response = self.client.post(self.URL, {'prop_id': '8BE92C6B767350E9C428',
                                               'prop_class': 'buy'})
        self.assertEqual(user.emailsettings_set.first().prop_updates, True)
