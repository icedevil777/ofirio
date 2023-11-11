import json
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken

from account.authentication import InvalidFacebookToken, InvalidGoogleToken
from account.emails import RegistrationVerifyAddressEmail
from account.models import EmailAddress
from account.tokens import OfirioRefreshToken
from account.tests.base import AccountBaseTest
from account.tests.factories import create_user


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


class BaseLoginViewTest:
    """Universal tests for login API"""
    url = None
    cookie_key = None
    response_error_key = None

    def test_no_such_email(self):
        response = self._login(self.valid_user_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_password_field(self):
        response = self._login({'email': 'test@ofirio.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_ok_cookie_set(self):
        user = create_user(self.valid_user_data)
        response = self._login(self.valid_user_data)
        self.assertTrue(response.cookies[self.cookie_key].value)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_wrong_pswd(self):
        user = create_user(self.valid_user_data)
        response = self._login({'email': 'test@ofirio.com', 'password': '876?wRoNg'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn(self.cookie_key, response.cookies)
        self.assertIn(self.response_error_key, response.data)

    def test_access_after_login(self):
        user = create_user(self.valid_user_data)
        response = self._login(self.valid_user_data)

        response = self.client.get(ACCOUNT_URL)
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertIn('email', response.data)
        self.assertIn('first_name', response.data)


class JwtLoginViewTest(BaseLoginViewTest, AccountBaseTest):
    url = reverse('account:login')
    cookie_key = 'refresh'
    response_error_key = 'server_messages'

    def _login(self, creds):
        return self.api_login(creds)


class SessionLoginViewTest(BaseLoginViewTest, AccountBaseTest):
    url = reverse('account:session_login')
    cookie_key = 'sessionid'
    response_error_key = 'server_messages'

    def _login(self, creds):
        return self.client.post(self.url, creds)


class BaseSocialJwtLoginViewTest:

    def test_new_user(self, verify_mock):
        verify_mock.return_value = self.payload

        response = self.client.post(self.url, self.data)
        self.assertTrue(response.cookies['refresh'].value)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_existing_user(self, verify_mock):
        verify_mock.return_value = self.payload
        user = create_user(self.valid_user_data)

        response = self.client.post(self.url, self.data)
        self.assertTrue(response.cookies['refresh'].value)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_access_after_login(self, verify_mock):
        login_method = getattr(self, self.test_login_method_name)
        headers = login_method(self.payload['email'], verify_mock)
        response = self.client.get(ACCOUNT_URL, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('email', response.data)
        self.assertIn('first_name', response.data)

    def test_access_if_inactive(self, verify_mock):
        verify_mock.return_value = self.payload
        user = create_user(self.valid_user_data)
        user.is_active = False
        user.save()

        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_token(self, verify_mock):
        verify_mock.side_effect = self.invalid_token_exception()

        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_become_verified(self, verify_mock):
        """
        If user registered by social,
        it should be automaticaly marked as verified
        """
        user = create_user(self.valid_user_data)
        self.api_login(self.valid_user_data)

        response = self.client.get(ACCOUNT_URL)
        self.assertFalse(response.data['verified'])

        login_method = getattr(self, self.test_login_method_name)
        headers = login_method(user.email, verify_mock)
        response = self.client.get(ACCOUNT_URL, **headers)
        self.assertTrue(response.data['verified'])

    def test_accepted_terms_of_use(self, verify_mock):
        """
        If users registered by social,
        they should accept terms of use separately
        """
        login_method = getattr(self, self.test_login_method_name)
        headers = login_method(self.valid_user_data['email'], verify_mock)
        response = self.client.get(ACCOUNT_URL, **headers)
        self.assertIn('terms_of_use_not_accepted', response.data['warnings'])

    def test_remember_social(self, verify_mock):
        """
        If a user logged in by social, remember its social user_id in a field
        """
        user = create_user(self.valid_user_data)
        self.assertFalse(getattr(user, self.social_user_id_field))

        login_method = getattr(self, self.test_login_method_name)
        login_method(self.payload['email'], verify_mock)
        user.refresh_from_db()
        self.assertTrue(getattr(user, self.social_user_id_field))


@patch('account.authentication.GoogleJwtBackend._verify_token')
class GoogleJwtLoginViewTest(BaseSocialJwtLoginViewTest, AccountBaseTest):
    url = reverse('account:google_login')
    payload = {
        'email': 'test@ofirio.com',
        'iss': 'https://accounts.google.com',
        'sub': '100130648042630285837',
    }
    data = {'token': 'e.y.u'}  # token could be any since we mock the verify method
    test_login_method_name = 'google_login'
    invalid_token_exception = InvalidGoogleToken
    social_user_id_field = 'google_user_id'


@patch('account.authentication.FacebookJwtBackend._verify_token')
class FacebookJwtLoginViewTest(BaseSocialJwtLoginViewTest, AccountBaseTest):
    url = reverse('account:facebook_login')
    payload = {
        'email': 'test@ofirio.com',
        'first_name': 'Eric',
        'id': '2798861843590837',
        'last_name': 'Idle',
    }
    data = {'token': 'e.y.u'}  # token could be any since we mock the verify method
    test_login_method_name = 'facebook_login'
    invalid_token_exception = InvalidFacebookToken
    social_user_id_field = 'fb_user_id'


class LogoutViewTest(AccountBaseTest):
    """Test logout API"""

    def test_logout_after_nothing(self):
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_after_login(self):
        """
        Ensure refresh token deleted. Access token will work
        for 5 minutes after logout, but it's the intended JWT behavior
        """
        user = create_user(self.valid_user_data)
        response = self.api_login(self.valid_user_data)
        self.assertIn('refresh', response.cookies)

        response = self.client.post(LOGOUT_URL)
        self.assertFalse(self.client.cookies['refresh'].value)

    def test_expired_token(self):
        access = 'cWD5Z9HcDM+PTsF1E3KderDrBGsrsDdFaU0i+gkSIhKf++6mKYjiIIWmCw2MSZnultgki5Srikq3IVyogyJpSYyQ5yIVmDSOxERwYsbKRsmQMWghA7YjmS0fb4z6srLOZbMHE7i6KedNy4AypnM+NqQOf3GvrAMMhtlYOXZxW0Vy184svokEHPLn3zYescEc8oOG4eoQmI83utwQ0WW+EJo32mjR6+NAxjJeF6NSR+DjS4mSvUHOyXNe9peVAC/GjLc/esisiOAe8wq/VgtQnciPtjVQLyhYZzvhwwKcBBvASz14NDaYfbW5SiCeI+c3RVxo43PuLSJ1D9OnYsO6+EIS0u9Y/b6zlNYbSxkL2k77wcQWWbks7aGFiMHBy+lLjt/qrZtnVXAHSDJ0yroO0lPD/UjTDohFgoPODZlYB1V1/92BEyXm/2Wv0ZbxjkicEPoESQcs+ad1o09tI70Jhy4k6C0/i3nZ/4u2z1D2mDdM/ih3HxQWXSRAjrflMx8vEhKQjCRYJvNSNnNYxCQvhSM2hVRvRRqaUVo960G8FSmKwz4/rxDKTELPmIeBj0MLDwDBATW0VQESBdikWOToh/SRrFFqdDFRsARERgW1LkS7nirDYwllSv5jMxfm/U2YjVzsZa7XATePHlOvrhZEgwlRUCfPg6VeqrhHxLeHFi0kko3ydOZvqK73sd+5Mew3sFxkwjL3n79XNIGXOyoAnA=='
        response = self.client.post(LOGOUT_URL, HTTP_OFAUTH=f'Bearer {access}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RefreshViewTest(AccountBaseTest):
    """Test Refresh token API"""
    url = reverse('account:refresh')

    def test_no_token(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_correct_token(self):
        user = create_user(self.valid_user_data)
        self.api_login(self.valid_user_data)

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(response.data['access'])
        self.assertTrue(response.cookies['access'].value)

    def test_expired_token(self):
        user = create_user(self.valid_user_data)
        response = self.api_login(self.valid_user_data)

        # modify token, make it expired
        refresh_token = OfirioRefreshToken(response.cookies['refresh'].value)
        refresh_token.set_exp(from_time=timezone.now() - timedelta(days=40),
                              lifetime=timedelta(days=30))

        # send it back
        response = self.client.post(self.url, HTTP_COOKIE=f'refresh={refresh_token}')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['code'], 'token_not_valid')

    def test_wrong_sig_token(self):
        user = create_user(self.valid_user_data)
        response = self.api_login(self.valid_user_data)

        # modify token, malform its signature
        refresh_token = response.cookies['refresh'].value + 'a'

        # send it back
        response = self.client.post(self.url, HTTP_COOKIE=f'refresh={refresh_token}')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['code'], 'token_not_valid')

    def test_invalid_access_token(self):
        """
        Expired access token in headers must not prevent getting a new one
        """
        user = create_user(self.valid_user_data)
        response = self.api_login(self.valid_user_data)

        # make access token invalid
        access = response.data['access'] + 'a'

        # send it back
        response = self.client.post(self.url, HTTP_OFAUTH=f'Bearer {access}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['access'])

    def test_user_fields_in_returned_access_token(self):
        """
        Ensure 'first_name' and other custom fields from the User model
        are in the access token that the Refresh API returned
        """
        user = create_user(self.valid_user_data)
        response = self.api_login(self.valid_user_data)

        # pull refresh api
        refresh_token = response.cookies['refresh'].value
        response = self.client.post(self.url, HTTP_COOKIE=f'refresh={refresh_token}')

        # check the access token it returned has all the info
        access_token = AccessToken(response.data['access'])
        required_fields = (
            'pk', 'email', 'first_name', 'last_name', 'phone', 'is_admin', 'is_team', 'verified',
            'access_status', 'warnings', 'favorites_qty', 'access_status',
        )
        for field in required_fields:
            self.assertIn(field, access_token)


class AccessTokenTest(AccountBaseTest):
    """Test Access authorization token"""

    def test_no_token(self):
        response = self.client.get(ACCOUNT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_correct_token(self):
        user = create_user(self.valid_user_data)
        response = self.api_login(self.valid_user_data)

        self.assertTrue(response.data['access'])
        self.assertTrue(response.cookies['access'])

        response = self.client.get(ACCOUNT_URL)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

    def test_expired_token(self):
        user = create_user(self.valid_user_data)
        response = self.api_login(self.valid_user_data)

        # modify token, make it expired
        access_token = AccessToken(response.data['access'])
        access_token.set_exp(from_time=timezone.now() - timedelta(minutes=6),
                             lifetime=timedelta(minutes=5))
        headers = {'HTTP_OFAUTH': f'Bearer {access_token}'}

        # send it back
        response = self.client.get(ACCOUNT_URL, **headers)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        resp_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(resp_data['code'], 'token_not_valid')

    def test_user_fields_in_token(self):
        """
        Ensure 'first_name' and other custom fields from the User model
        are in the access token
        """
        user = create_user(self.valid_user_data)
        response = self.api_login(self.valid_user_data)

        access_token = AccessToken(response.data['access'])
        required_fields = (
            'pk', 'email', 'first_name', 'last_name', 'phone', 'is_admin', 'is_team', 'verified',
            'access_status', 'warnings', 'favorites_qty', 'access_status',
        )
        for field in required_fields:
            self.assertIn(field, access_token)

    def test_wrong_sig_token(self):
        user = create_user(self.valid_user_data)
        response = self.api_login(self.valid_user_data)

        # modify token, malform its signature
        access_token = response.data['access'] + 'a'
        headers = {'HTTP_OFAUTH': f'Bearer {access_token}'}

        # send it back
        response = self.client.get(ACCOUNT_URL, **headers)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        resp_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(resp_data['code'], 'token_not_valid')

    def test_wrong_email_in_token(self):
        user = create_user(self.valid_user_data)
        response = self.api_login(self.valid_user_data)

        # modify token, replace its email
        access_token = AccessToken(response.data['access'])
        access_token['email'] = 'spam@banana.fly'
        headers = {'HTTP_OFAUTH': f'Bearer {access_token}'}

        # send it back
        response = self.client.get(ACCOUNT_URL, **headers)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        resp_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(resp_data['code'], 'user_not_found')

    def test_no_email_in_token(self):
        user = create_user(self.valid_user_data)
        response = self.api_login(self.valid_user_data)

        # modify token, replace its email
        access_token = AccessToken(response.data['access'])
        del access_token['email']
        headers = {'HTTP_OFAUTH': f'Bearer {access_token}'}

        # send it back
        response = self.client.get(ACCOUNT_URL, **headers)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        resp_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(resp_data['code'], 'token_not_valid')

    def test_user_inactive(self):
        user = create_user(self.valid_user_data)
        response = self.api_login(self.valid_user_data)

        # inactivate user
        user.is_active = False
        user.save()

        # check access
        response = self.client.get(ACCOUNT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        resp_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(resp_data['code'], 'user_inactive')


class RegistrationViewTest(AccountBaseTest):
    URL = reverse('account:registration')

    def test_already_authentificated(self):
        user = create_user()
        self.client.force_authenticate(user=user)

        response = self.client.post(self.URL, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_data = {
            'server_messages': [
                {'level': 'error', 'message': 'Already authentificated'},
            ],
        }
        self.assertEqual(response.data, expected_data)

    def test_empty_data(self):
        response = self.client.post(self.URL, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_messages = [{'level': 'error', 'message': 'This field is required.'}]
        self.assertEqual(expected_messages, response.data['server_messages'])
        self.assertIn('email', response.data['errors'])
        self.assertIn('password', response.data['errors'])

    def test_invalid_email(self):
        user_data = {'email': 'not_email', 'password': 'qWe123$'}
        response = self.client.post(self.URL, user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_messages = [{'level': 'error', 'message': 'Enter a valid email address.'}]
        self.assertEqual(expected_messages, response.data['server_messages'])
        self.assertIn('email', response.data['errors'])

    def test_valid_data(self):
        response = self.client.post(self.URL, self.valid_user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertIn('server_messages', response.data)
        self.assertIn('access', response.data)

    def test_already_exists(self):
        user = create_user(self.valid_user_data)
        response = self.client.post(self.URL, self.valid_user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_data = {
            'server_messages': [
                {'level': 'error', 'message': 'User with test@ofirio.com already exist'},
            ],
        }
        self.assertEqual(response.data, expected_data)

    def test_verification_email_sent(self):
        self.assertFalse(mail.outbox)
        self.client.post(self.URL, self.valid_user_data)
        self.assertTrue(mail.outbox)

        user = User.objects.first()
        self.assertTrue(user.email_address.sent_at)
        self.assertEqual(mail.outbox[-1].to, [user.email])

    def test_verification_email_has_code(self):
        self.client.post(self.URL, self.valid_user_data)
        user = User.objects.first()

        outbox_message = mail.outbox[-1]
        html_body = outbox_message.alternatives[0][0]
        self.assertEqual(outbox_message.subject, 'Verify Your Email Address')
        self.assertIn(user.email_address.code, html_body)

    def test_weak_passwords(self):
        for password in WEAK_PASSWORDS:
            user_data = {'email': 'spam@banana.fly', 'password': password}
            response = self.client.post(self.URL, user_data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('password', response.data['errors'])

    def test_refresh_cookie_set(self):
        """
        A cookie with Refresh JWToken is a sign that JWT login
        happened within the registration
        """
        response = self.client.post(reverse('account:registration'), self.valid_user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.cookies['refresh'].value)


class VerifyEmailViewTest(AccountBaseTest):

    def test_code_created_with_entry(self):
        # email_address.code must be created immediately, even if not sent
        user = create_user()
        self.assertTrue(user.email_address.code)

    def test_absent_code(self):
        verification_url = reverse('account:verify_email', kwargs={'code': '1234'})
        response = self.client.get(verification_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_expired_code(self):
        user = create_user()
        RegistrationVerifyAddressEmail.send(user)
        verification_url = user.email_address.get_verification_url()

        email_address = user.email_address
        email_address.sent_at -= timedelta(days=365*100)
        email_address.save()

        response = self.client.get(verification_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # TODO: verify server_messages

    def test_already_verified(self):
        user = create_user()
        email_address = user.email_address
        self.assertFalse(email_address.verified)
        email_address.verify()
        self.assertTrue(email_address.verified)

        verification_url = email_address.get_verification_url()
        response = self.client.get(verification_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # TODO: verify server_messages

    def test_logged_in_after_verification_url(self):
        # create user, send verification
        user = create_user()
        RegistrationVerifyAddressEmail.send(user)

        email_address = EmailAddress.objects.get(user=user)
        verification_url = email_address.get_verification_url()
        self.assertFalse(self.is_authenticated())

        # open verification link, check that user is authenticated
        response = self.client.get(verification_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class RestorePasswordViewTest(AccountBaseTest):

    def test_empty_email(self):
        response = self.client.post(RESTORE_PASSWORD_URL, {'email': ''})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_messages = [{'level': 'error', 'message': 'Email is required'}]
        self.assertEqual(expected_messages, response.data['server_messages'])
        self.assertIn('email', response.data['errors'])

    def test_invalid_email(self):
        response = self.client.post(RESTORE_PASSWORD_URL, {'email': 'not_email'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_messages = [{'level': 'error', 'message': 'Email is required'}]
        self.assertEqual(expected_messages, response.data['server_messages'])
        self.assertIn('email', response.data['errors'])

    def test_absent_email(self):
        response = self.client.post(RESTORE_PASSWORD_URL, {'email': 'test@ofirio.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mail_sent(self):
        self.assertFalse(mail.outbox)

        user = create_user({'email': 'test@ofirio.com'})
        response = self.client.post(RESTORE_PASSWORD_URL, {'email': 'test@ofirio.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(mail.outbox)

    def test_correct_mail(self):
        user_data = {'email': 'test@ofirio.com', 'first_name': 'Graham', 'last_name': 'Chapman'}
        user = create_user(user_data)
        response = self.client.post(RESTORE_PASSWORD_URL, {'email': 'test@ofirio.com'})

        outbox_message = mail.outbox[-1]
        html_body = outbox_message.alternatives[0][0]
        self.assertEqual(outbox_message.subject, 'Password Reset Requested')
        self.assertIn(user.last_restore_password_check.restore_code, html_body)
        self.assertIn('Graham Chapman', html_body)


class RestorePasswordCheckViewTest(AccountBaseTest):
    URL = reverse('account:restore_password_check')

    def test_empty_code(self):
        response = self.client.post(self.URL, {'restore_code': ''})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_messages = [{'level': 'error', 'message': 'Restore code is required'}]
        self.assertEqual(expected_messages, response.data['server_messages'])

    def test_invalid_code(self):
        response = self.client.post(self.URL, {'restore_code': 's' * 32})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_messages = [{'level': 'error', 'message': 'Incorrect restore code'}]
        self.assertEqual(expected_messages, response.data['server_messages'])

    def test_valid_code(self):
        user = create_user({'email': 'test@ofirio.com'})
        response = self.client.post(RESTORE_PASSWORD_URL, {'email': 'test@ofirio.com'})
        restore_code = user.last_restore_password_check.restore_code

        response = self.client.post(self.URL, {'restore_code': restore_code})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = {
            'server_messages': [
                {'level': 'success', 'message': 'Restore code is correct'},
            ],
        }
        self.assertEqual(response.data, expected_data)


class RestorePasswordChangeViewTest(AccountBaseTest):
    URL = reverse('account:restore_password_change')

    def test_empty_code(self):
        response = self.client.post(self.URL, {'restore_code': '', 'password_new': 'qWe13$'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_messages = [{'level': 'error', 'message': 'This field may not be blank.'}]
        self.assertEqual(expected_messages, response.data['server_messages'])

    def test_empty_password(self):
        response = self.client.post(self.URL, {'restore_code': 's' * 32, 'password_new': ''})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_messages = [{'level': 'error', 'message': 'This field may not be blank.'}]
        self.assertEqual(expected_messages, response.data['server_messages'])

    def test_invalid_code(self):
        response = self.client.post(self.URL, {'restore_code': 's' * 32, 'password_new': 'qWe13$'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        msg = (
            'Incorrect restore link. Please create a new request '
            '(The link is active for only one hour!)'
        )
        expected_messages = [{'level': 'error', 'message': msg}]
        self.assertEqual(expected_messages, response.data['server_messages'])

    def test_valid_code(self):
        user = create_user({'email': 'test@ofirio.com'})
        self.client.post(RESTORE_PASSWORD_URL, {'email': 'test@ofirio.com'})
        restore_code = user.last_restore_password_check.restore_code

        response = self.client.post(
            self.URL, {'restore_code': restore_code, 'password_new': 'qWe13$'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = {
            'server_messages': [
                {
                    'level': 'success',
                    'message': 'Password successfully changed, please try to log in!',
                },
            ],
        }
        self.assertEqual(response.data, expected_data)

    def test_mail_sent(self):
        self.assertFalse(mail.outbox)

        user = create_user({'email': 'test@ofirio.com'})
        self.client.post(RESTORE_PASSWORD_URL, {'email': 'test@ofirio.com'})
        restore_code = user.last_restore_password_check.restore_code

        response = self.client.post(
            self.URL, {'restore_code': restore_code, 'password_new': 'qWe13$'},
        )
        self.assertEqual(len(mail.outbox), 2)

    def test_correct_mail(self):
        user = create_user({'email': 'test@ofirio.com'})
        self.client.post(RESTORE_PASSWORD_URL, {'email': 'test@ofirio.com'})
        restore_code = user.last_restore_password_check.restore_code
        self.client.post(self.URL, {'restore_code': restore_code, 'password_new': 'qWe13$'})

        last_mail = mail.outbox[-1]
        self.assertEqual(last_mail.subject, 'Password Reset Successfully')

    def test_weak_passwords(self):
        user = create_user({'email': 'spam@banana.fly'})
        response = self.client.post(RESTORE_PASSWORD_URL, {'email': 'spam@banana.fly'})
        restore_code = user.last_restore_password_check.restore_code

        for password in WEAK_PASSWORDS:
            restore_data = {'restore_code': restore_code, 'password_new': password}
            response = self.client.post(self.URL, restore_data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('password_new', response.data['errors'])


class ChangePasswordViewTest(AccountBaseTest):
    URL = reverse('account:change_password')

    def test_not_authed(self):
        response = self.client.post(self.URL)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_data(self):
        user = create_user(self.valid_user_data)
        self.api_login(self.valid_user_data)

        response = self.client.post(self.URL)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_current_password(self):
        user = create_user(self.valid_user_data)
        self.api_login(self.valid_user_data)

        data = {'password_old': 'qWe123$_wrong', 'password_new': '499sPaM_!'}
        response = self.client.post(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_success(self):
        user = create_user(self.valid_user_data)
        pwd_hash_before = user.password
        self.api_login(self.valid_user_data)

        data = {'password_old': 'sPam123$', 'password_new': '499sPaM_!'}
        self.assertFalse(mail.outbox)
        response = self.client.post(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(mail.outbox)

        user.refresh_from_db()
        pwd_hash_after = user.password
        self.assertNotEqual(pwd_hash_before, pwd_hash_after)

    def test_weak_passwords(self):
        user = create_user({'email': 'spam@banana.fly', 'password': 'sPam123$'})
        self.client.force_authenticate(user=user)

        for password in WEAK_PASSWORDS:
            data = {'password_old': 'sPam123$', 'password_new': password}
            response = self.client.post(self.URL, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('password_new', response.data['errors'])
