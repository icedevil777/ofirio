import shutil
from unittest import mock

from django.db import connections
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.test import override_settings
from django.urls import reverse
from ofirio_common import helpers as common_helpers
from rest_framework.test import APITestCase


# Changes in Django settings that will be applied while running tests.
# Also databases are configured in djangoproject.test_runners.PortalTestRunner.setup_databases
TEST_SETTINGS = {
    'RENT_ANALYZER_CALCULATION_MODEL': 'rent_analyzer.common.rent_analyzer_model.MockRentAnalyzerCalculation',
    'SERVE_MEDIA': True,
    'DEFAULT_FILE_STORAGE': 'django.core.files.storage.FileSystemStorage',
    'MEDIA_ROOT': settings.BASE_DIR / 'media_test',
    'KLAVIYO_ENABLED': False,
    'KLAVIYO_API_KEY': 'test_api_key',
    'KLAVIYO_PRIVATE_KEY': 'test_private_key',
    'KLAVIYO_NEWSLETTER_LIST_ID': 'test_list_id',
    'CELERY_TASK_ALWAYS_EAGER': True,
    'STRIPE_HTTP_CLIENT': 'subscriptions.providers.MockResponseStripeHttpClient',
    'STRIPE_WEBHOOK_SECRET': 'test',
    'STRIPE_SECRET_KEY': 'test',
    'INTERCOM_TOKEN': '',
    'INTERCOM_ENABLED': False,
    'TG_BOT_TOKEN': '',
    'IS_PRODUCTION': False,
    'WP_CLIENT_CLASS': 'blog.wp_client.DummyWordPressClient',
    'COOKIE_SECRET': 'j]NVr[GzV~4F<P9Pfv76Wi2s+/Vq7YQv',
    'GEOCODE_BACKEND': 'ofirio_common.geocode.geocode_fake',
    'DRF_RECAPTCHA_TESTING': True,
    'INVEST_ENABLED': False,  # OT-2686 / OT-3162
}


@override_settings(**TEST_SETTINGS)
class PortalBaseTest(APITestCase):
    databases = 'default', 'prop_db', 'prop_db_rw'

    def setUp(self):
        super().setUp()
        cache.clear()
        # save initial row_factory of global connection
        con = connections['prop_db']
        self.__initial_row_factory = con.connection.row_factory

    def tearDown(self):
        # delete media files created during tests
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

        # Destroy Elasticsearch object so mock can be created in the next test
        common_helpers._ES = None

        # restore row_factory of global connection, because it may change in common.utils.get_dict_cursor
        con = connections['prop_db']
        con.connection.row_factory = self.__initial_row_factory
        super().tearDown()

    def api_login(self, creds):
        """
        Log in using our main API login endpoint
        """
        response = self.client.post(reverse('account:login'), creds)

        # Put OfAuth header into each subsequent request
        if access_token := response.data.get('access'):
            headers = {'HTTP_OFAUTH': f'Bearer {access_token}'}
            self.client.defaults.update(headers)

        return response

    def api_logout(self):
        """
        Log out using our main API logout endpoint
        """
        response = self.client.post(reverse('account:logout'))
        self.client.defaults.pop('HTTP_OFAUTH', None)
        return response

    def google_login(self, email, verify_mock):
        """
        Log in with Google
        """
        self.api_logout()
        verify_mock.return_value = {
            'email': email,
            'iss': 'https://accounts.google.com',
            'sub': '100130648042630285837',
        }
        response = self.client.post(reverse('account:google_login'), {'token': 'y.e.u'})
        auth_headers = {'HTTP_OFAUTH': f'Bearer {response.data["access"]}'}
        return auth_headers

    def facebook_login(self, email, verify_mock):
        """
        Log in with Facebook
        """
        self.api_logout()
        verify_mock.return_value = {
            'email': email,
            'id': '2798861843590837',
        }
        response = self.client.post(reverse('account:facebook_login'), {'token': 'y.e.u'})
        auth_headers = {'HTTP_OFAUTH': f'Bearer {response.data["access"]}'}
        return auth_headers

    def setup_es_mock(self, es_class_mock, *responses, method=None):
        """
        Setup mock so es.search() and es.get() will return provided responses
        with the same order
        """
        es_instance_mock = mock.MagicMock()
        if len(responses) == 1:
            if method == 'get':
                es_instance_mock.get = mock.MagicMock(return_value=responses[0])
            else:
                es_instance_mock.search = mock.MagicMock(return_value=responses[0])
        else:
            if method == 'get':
                es_instance_mock.get.side_effect = responses
            else:
                es_instance_mock.search.side_effect = responses
        es_class_mock.return_value = es_instance_mock
        return es_instance_mock


def run_commit_hooks():
    """
    Fake transaction commit to run delayed on_commit functions.
    Got from the article goo.gl/qq51Hf
    """
    vldt = 'django.db.backends.base.base.BaseDatabaseWrapper.validate_no_atomic_block'
    with mock.patch(vldt, lambda x: False):
        transaction.get_connection().run_and_clear_commit_hooks()
