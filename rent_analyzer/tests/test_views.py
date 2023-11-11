from django.urls import reverse
from rest_framework import status

from account.tests.factories import create_user
from rent_analyzer.tests.base import RentAnalyzerTest


RENT_ANALYZER_URL = reverse('rent_analyzer:rent_analyzer')
VALID_RENT_ANALYZER_DATA = {
    'query': 'miami 2',
    'prop_type2': 'any',
    'distance': 'auto',
    'beds': 'any',
    'baths': 'any',
    'look_back': 3,
    'type': 'address',
}
VALID_RENT_ANALYZER_DATA_1 = {
    'query': 'miami 3',
    'prop_type2': 'any',
    'distance': 'auto',
    'beds': 'any',
    'baths': 'any',
    'look_back': 3,
    'type': 'address',
}


class RentAnalyzerViewTest(RentAnalyzerTest):

    def test_anon_same_request(self):
        """
        One request is allowed for anon user,
        and the same request must not count as new
        """
        response = self.client.post(RENT_ANALYZER_URL, VALID_RENT_ANALYZER_DATA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(RENT_ANALYZER_URL, VALID_RENT_ANALYZER_DATA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anon_two_diff_requests(self):
        """One unique request is allowed for anon user"""
        response = self.client.post(RENT_ANALYZER_URL, VALID_RENT_ANALYZER_DATA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(RENT_ANALYZER_URL, VALID_RENT_ANALYZER_DATA_1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unverified_two_diff_requests(self):
        """
        Up to 10 requests are allowed for unverified user.
        But here is only a check that two works
        """
        user = create_user({'verified': False})
        self.client.force_authenticate(user=user)

        response = self.client.post(RENT_ANALYZER_URL, VALID_RENT_ANALYZER_DATA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(RENT_ANALYZER_URL, VALID_RENT_ANALYZER_DATA_1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_verified_two_diff_requests(self):
        """
        Up to 10 requests are allowed for verified user.
        But here is only a check that two works
        """
        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)

        response = self.client.post(RENT_ANALYZER_URL, VALID_RENT_ANALYZER_DATA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(RENT_ANALYZER_URL, VALID_RENT_ANALYZER_DATA_1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_premium_two_diff_requests(self):
        """
        Unlimited number of requests are allowed for premium user.
        But here is only a check that two works
        """
        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)

        response = self.client.post(RENT_ANALYZER_URL, VALID_RENT_ANALYZER_DATA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(RENT_ANALYZER_URL, VALID_RENT_ANALYZER_DATA_1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
