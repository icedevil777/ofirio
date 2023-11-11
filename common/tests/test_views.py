from unittest.mock import patch, MagicMock

from django.urls import reverse
from rest_framework import status

from common.models import ContactUs
from common.tests.base import PortalBaseTest


@patch('requests.get', side_effect=MagicMock())
@patch('requests.post', side_effect=MagicMock())
class ContactUsViewTest(PortalBaseTest):
    URL = reverse('common:contact_us')
    VALID_DATA = {
        'full_name': 'Graham Spam',
        'email': 'test@ofirio.com',
        'message': 'SpaM sPam spAm',
    }

    def test_empty(self, requests_post_mock, requests_get_mock):
        response = self.client.post(self.URL)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_response_ok(self, requests_post_mock, requests_get_mock):
        response = self.client.post(self.URL, self.VALID_DATA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('common.emails.ContactUsEmail.send', side_effect=MagicMock())
    def test_email_sent(self, email_send_mock, requests_post_mock, requests_get_mock):
        self.client.post(self.URL, self.VALID_DATA)
        self.assertTrue(email_send_mock.call_args_list)

    def test_db_object_created(self, requests_post_mock, requests_get_mock):
        self.assertFalse(ContactUs.objects.count())
        self.client.post(self.URL, self.VALID_DATA)
        self.assertTrue(ContactUs.objects.count())
