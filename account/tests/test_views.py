import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from account.tests.base import AccountBaseTest
from account.tests.factories import create_user
from api_property.models import PropCity


User = get_user_model()
LOGIN_URL = reverse('account:login')
LOGOUT_URL = reverse('account:logout')
ACCOUNT_URL = reverse('account:account')
RESTORE_PASSWORD_URL = reverse('account:restore_password')
# USER_WARNINGS.terms_of_use_not_accepted
USER_WARNINGS_TERMS_OF_USE_NOT_ACCEPTED = 'terms_of_use_not_accepted'
WEAK_PASSWORDS = (
    '  qWe123$\t',  # side spaces
    'b8x6d',  # short
    '2938467',  # only nums
    'circus',  # common
    'spamspam7',  # similar to email
    'peaoighskdbg',  # only latin chars
    '1 1 1 1',  # no letters
    '1 asfsdfdgkdsgkljsdgsjfjdsfuhewougfhsdgjbfjghklsnfvxd;nb 1 1 1',  # long
)


class LimitsLeftViewTest(AccountBaseTest):
    URL = reverse('account:limits_left')
    RENT_ANALYZER_URL = reverse('rent_analyzer:rent_analyzer')
    RENT_ANALYZER_DATA = {
        'query': 'miami',
        'prop_type2': 'any',
        'distance': 'auto',
        'beds': 'any',
        'baths': 'any',
        'look_back': 3,
        'type': 'address',
    }

    def test_not_authenticated(self):
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = {
            'rent_analyzer_search': 1,
            'rent_estimator_analytics': 1,
            'rent_analyzer_report': 0,
            'property_report': 0,
        }
        self.assertEqual(expected, response.data)

    def test_ok(self):
        user = create_user()
        self.client.force_authenticate(user=user)

        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anon_limit_left_changed(self):
        """Anon user should be able to make one analyzer request with results"""
        response = self.client.get(self.URL)
        self.assertEqual(response.data['rent_analyzer_search'], 1)

        # rent analyzer request without data returned. Must NOT be counted
        rent_analyzer_data = self.RENT_ANALYZER_DATA.copy()
        rent_analyzer_data['query'] = 'florida'
        response = self.client.post(self.RENT_ANALYZER_URL, rent_analyzer_data)
        self.assertFalse(response.data.get('items'))
        response = self.client.get(self.URL)
        self.assertEqual(response.data['rent_analyzer_search'], 1)

        # rent analyzer request with data returned. Must be counted.
        # Limit left must be 0, because only one request is allowed for anon user
        response = self.client.post(self.RENT_ANALYZER_URL, self.RENT_ANALYZER_DATA)
        self.assertTrue(response.data['items'])
        response = self.client.get(self.URL)
        self.assertEqual(response.data['rent_analyzer_search'], 0)

        # subsequent new requests must be disallowed, and limit left must still be 0
        rent_analyzer_data = self.RENT_ANALYZER_DATA.copy()
        rent_analyzer_data['query'] = 'miami spam'
        response = self.client.post(self.RENT_ANALYZER_URL, rent_analyzer_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.get(self.URL)
        self.assertEqual(response.data['rent_analyzer_search'], 0)


class AccountViewTest(AccountBaseTest):

    def test_not_authed(self):
        response = self.client.get(ACCOUNT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_verified_status_reg_by_email(self):
        """
        If user registered by email,
        'verified' should be True/False whether the address is confirmed
        """
        user = create_user(self.valid_user_data)

        # user object is cached when using self.client.force_authenticate()
        # and not re-read from DB in the following requests,
        # so we need to log in by some other way, for example with our API,
        # to avoid DRF's caching
        self.api_login(self.valid_user_data)

        response = self.client.get(ACCOUNT_URL)
        self.assertFalse(response.data['verified'])

        # user clicks on verification URL
        self.client.get(user.email_address.get_verification_url())

        response = self.client.get(ACCOUNT_URL)
        self.assertTrue(response.data['verified'])

    def test_password_change_required(self):
        """
        If user changed password more than 90 days ago,
        a warning must returned.
        """
        user = create_user(self.valid_user_data)
        self.api_login(self.valid_user_data)

        response = self.client.get(ACCOUNT_URL)
        self.assertFalse(response.data['warnings'])

        user.password_changed_at = timezone.now() - timedelta(days=91)
        user.save()
        response = self.client.get(ACCOUNT_URL)
        self.assertIn('password_change_required', response.data['warnings'])

    def test_fields(self):
        """
        Check /api/account returned fields
        """
        user = create_user(self.valid_user_data)
        self.api_login(self.valid_user_data)

        response = self.client.get(ACCOUNT_URL)
        self.assertIn('pk', response.data)
        self.assertIn('email', response.data)
        self.assertIn('first_name', response.data)
        self.assertIn('last_name', response.data)
        self.assertIn('is_admin', response.data)
        self.assertIn('is_team', response.data)
        self.assertIn('verified', response.data)
        self.assertIn('access_status', response.data)
        self.assertIn('warnings', response.data)
        self.assertIn('favorites_qty', response.data)


class EmailSettingsTest(AccountBaseTest):
    URL = reverse('account:email_settings')
    valid_initial_e_settings_response = {'similars': False, 'good_deals': False,
                                         'prop_updates': False, 'favorites': False,
                                         'tips_and_guides': True,
                                         'market_reports_and_updates': True,
                                         'tool_updates': True,
                                         'partner_offers_and_deals': True,
                                         'favorites_match_notification': False,
                                         'properties_you_may_like': True}
    def test_not_authed(self):
        response = self.client.post(self.URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_added_to_new_user(self):
        user = create_user()
        self.client.force_authenticate(user=user)
        response = self.client.get(self.URL)
        self.assertEqual(response.data, self.valid_initial_e_settings_response)

    def test_only_indicated_fields_changed(self):
        user = create_user()
        self.client.force_authenticate(user=user)

        self.client.post(self.URL, data={'similars': True})
        response_data = self.client.get(self.URL).data
        valid_response = self.valid_initial_e_settings_response.copy()

        self.assertNotEqual(response_data.pop('similars'),
                            valid_response.pop('similars'))  # should be changed
        self.assertEqual(response_data, valid_response)

    def test_different_requests(self):
        user = create_user()
        self.client.force_authenticate(user=user)
        for var in (13, 'test', json.dumps(None),):  # should be remembered that 1, 0
                                # can be written as true/false on models/serializers.BooleanFeield
            response = self.client.post(self.URL, data={'similars': var})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GoodDealSettingsTest(AccountBaseTest):
    URL = reverse('account:good_deal_settings')
    default_gd_settings = {
        'cities': [], 'prop_type': None, 'rent_min_price': 200, 'rent_max_price': 20000,
        'buy_min_price': 10000, 'buy_max_price': 10000000, 'invest_min_price': 10000,
        'invest_max_price': 10000000, 'rent_enabled': False, 'buy_enabled': False,
        'invest_enabled': False, 'beds_min': None, 'baths_min': None,
    }
    _cities = [{'city': 'aventura', 'county': 'miami-dade', 'state_id': 'FL',
                'label': 'Aventura, FL'}]
    data = {
        'email': 'rossulbricht@gmail.com',
        'cities': _cities,
    }

    def test_added_to_new_user(self):
        """
        New user has default good deal settings
        """
        user = create_user()
        self.client.force_authenticate(user=user)

        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.default_gd_settings)

    def test_get_not_authed(self):
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_not_authed_empty_email(self):
        """
        Can't create/update if there is no email and no authorization
        """
        response = self.client.post(self.URL, data={'buy_enabled': True})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_only_indicated_field_changed(self):
        """
        Get existing settings, change one value,
        read again and ensure the value changed
        """
        user = create_user()
        self.client.force_authenticate(user=user)

        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        new_buy_enabled = not response.data['buy_enabled']
        response = self.client.post(self.URL, data={'buy_enabled': new_buy_enabled,
                                                    'cities': self._cities})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected = self.default_gd_settings.copy()
        expected['buy_enabled'] = new_buy_enabled
        expected['cities'] = self._cities

        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected)

    def test_create_new_user_if_unknown_email(self):
        self.assertFalse(User.objects.filter(email=self.data['email']))

        response = self.client.post(self.URL, self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(User.objects.filter(email=self.data['email']))

    def test_city_created(self):
        self.assertFalse(PropCity.objects.all())
        response = self.client.post(self.URL, self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(PropCity.objects.count(), 1)
        self.assertEqual(PropCity.objects.filter(city='aventura').count(), 1)

    def test_user_exists(self):
        """
        If user exists but not authed, settings should be updated,
        and also a phone if it was empty
        """
        self.assertEqual(User.objects.count(), 0)
        user = create_user()
        self.assertEqual(User.objects.count(), 1)

        new_buy_enabled = not self.default_gd_settings['buy_enabled']
        data = {
            'email': user.email,
            'phone': '123456789',
            'buy_enabled': new_buy_enabled,
            'cities': self._cities,
        }
        response = self.client.post(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().phone, '123456789')

        expected = self.default_gd_settings.copy()
        expected['buy_enabled'] = new_buy_enabled
        expected['cities'] = self._cities

        self.client.force_authenticate(user=user)
        response = self.client.get(self.URL)
        self.assertEqual(response.data, expected)

    def test_city_not_created_twice(self):
        """
        Ensure same city do not created twice
        """
        self.assertEqual(PropCity.objects.count(), 0)
        response = self.client.post(self.URL, self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(PropCity.objects.count(), 1)

        data = self.data.copy()
        data['cities'][0]['label'] = 'new label'
        response = self.client.post(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(PropCity.objects.count(), 1)

        city_qs = PropCity.objects.filter(city='aventura')
        self.assertEqual(city_qs.count(), 1)
        self.assertEqual(city_qs.first().label, 'Aventura, FL')

    def test_invalid_email(self):
        response = self.client.post(self.URL, {'email': 'asjkhd'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dont_update_phone_if_exists(self):
        """
        If account with such an email doesn't exist, but the phone exists,
        we should create account, but don't fill the phone
        """
        self.assertEqual(User.objects.count(), 0)
        user = create_user({'phone': '123456789'})
        self.assertEqual(User.objects.count(), 1)

        data = self.data.copy()
        data['phone'] = '123456789'
        response = self.client.post(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 2)

        self.assertFalse(User.objects.filter(email=data['email']).first().phone)
        self.assertTrue(User.objects.filter(email=user.email).first().phone)

    def test_email_sent(self):
        """
        Email with a link to set password should be sent
        """
        self.assertFalse(mail.outbox)
        self.client.post(self.URL, self.data)
        self.assertTrue(mail.outbox)

        user = User.objects.first()
        outbox_mail = mail.outbox[-1]
        self.assertEqual(outbox_mail.to, [user.email])

        html_body = outbox_mail.alternatives[0][0]  # TODO: check body
        self.assertEqual(outbox_mail.subject, 'Set Password To Complete Your Account')

    def test_null_data_sent(self):
        """
        Test for the bug with null values
        """
        user = create_user()
        self.client.force_authenticate(user=user)
        gds = user.gooddealsettings_set.first()
        gds.beds_min = 1
        gds.save()

        data = json.dumps({
            'cities': self._cities,
            'beds_min': None,
            'prop_type': None,
            'buy_enabled': True,
        })
        response = self.client.post(self.URL, data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['beds_min'], None)
        self.assertEqual(response.data['prop_type'], None)
        self.assertEqual(response.data['buy_enabled'], True)

    def test_rent_remains_enabled(self):
        """
        Test for the bug when some fields resets to defaults
        """
        user = create_user()
        self.client.force_authenticate(user=user)
        gds = user.gooddealsettings_set.first()
        gds.buy_enabled = True
        gds.rent_enabled = True
        gds.rent_max_price = 6_123
        gds.rent_min_price = 1_987
        gds.save()

        data = json.dumps({
            'beds_min': None,
            'buy_enabled': True,
            'buy_max_price': 6_598_000,
            'buy_min_price': 3_007_000,
            'cities': self._cities,
            'email': '',
            'phone': '',
            'price_max': 6_598_000,
            'price_min': 3_007_000,
            'prop_type': None,
        })
        response = self.client.post(self.URL, data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rent_enabled'], True)
        self.assertEqual(response.data['rent_max_price'], 6_123)
        self.assertEqual(response.data['rent_min_price'], 1_987)

    def test_email_settings_becomes_enabled(self):
        """
        Test for the bug when some fields resets to defaults
        """
        user = create_user()
        self.client.force_authenticate(user=user)
        self.assertEqual(user.emailsettings_set.first().good_deals, False)

        response = self.client.post(self.URL, {'buy_enabled': True, 'cities': self._cities})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(user.emailsettings_set.first().good_deals, True)

    def test_add_city(self):
        """
        If add_city is true, the cities should be added to existing ones
        """
        cities_1 = [{'city': 'aventura', 'county': 'miami-dade-county',
                     'state_id': 'FL', 'label': 'Aventura, FL'}]
        cities_2 = [{'city': 'homestead', 'county': 'miami-dade-couty',
                     'state_id': 'FL', 'label': 'Homestead, FL'}]
        user = create_user()
        self.client.force_authenticate(user=user)

        # post one city
        response = self.client.post(self.URL, {'buy_enabled': True, 'cities': cities_1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.URL)
        self.assertEqual(len(response.data['cities']), 1)
        city_names = [c['city'] for c in response.data['cities']]
        self.assertIn('aventura', city_names)

        # post another city
        response = self.client.post(self.URL, {'cities': cities_2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.URL)
        self.assertEqual(len(response.data['cities']), 1)
        city_names = [c['city'] for c in response.data['cities']]
        self.assertIn('homestead', city_names)

        # post first city again but with add_city=True
        response = self.client.post(self.URL, {'cities': cities_1, 'add_city': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.URL)
        self.assertEqual(len(response.data['cities']), 2)
        city_names = [c['city'] for c in response.data['cities']]
        self.assertIn('aventura', city_names)
        self.assertIn('homestead', city_names)
