from django.urls import reverse
from rest_framework import status

from account.models import AccessEvent
from account.tests.base import AccountBaseTest
from account.tests.factories import create_user


class AccessLimitTest:
    """Common tests that actually run later, in subclasses"""

    def test_anon_access_event_created(self):
        """
        Works if there is an expected limit for anon user
        """
        if not self.ANON_EXPECTED_LIMIT:
            return

        self.assertFalse(AccessEvent.objects.count())
        self.client.post(self.URL, self.DATA[0])
        self.assertTrue(AccessEvent.objects.count())

    def test_anon_same_access_event_not_created(self):
        """
        If not much time passed,
        same request should not lead to creating another event.
        Works if there is an expected limit for anon user
        """
        if not self.ANON_EXPECTED_LIMIT:
            return

        self.assertEqual(AccessEvent.objects.count(), 0)

        self.client.post(self.URL, self.DATA[0])
        self.assertEqual(AccessEvent.objects.count(), 1)

        self.client.post(self.URL, self.DATA[0])
        self.assertEqual(AccessEvent.objects.count(), 1)

    def test_events_created_for_anon_until_limit_reached(self):
        """
        No access events should be created in DB after limit reached.
        Works if there is an expected limit for anon user
        """
        if not self.ANON_EXPECTED_LIMIT:
            return

        for i in range(self.ANON_EXPECTED_LIMIT):
            self.client.post(self.URL, self.DATA[i])
        self.assertEqual(AccessEvent.objects.count(), self.ANON_EXPECTED_LIMIT)

        self.client.post(self.URL, self.DATA[self.ANON_EXPECTED_LIMIT])
        self.assertEqual(AccessEvent.objects.count(), self.ANON_EXPECTED_LIMIT)

    def test_same_query_works(self):
        """When limit is reached, the same query should still work a few hours"""
        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)

        for i in range(self.FREE_REG_EXPECTED_LIMIT):
            response = self.client.post(self.URL, self.DATA[i])
            self.assertEqual(response.status_code, self.SUCCESS_STATUS)

        response = self.client.post(self.URL, self.DATA[0])
        self.assertEqual(response.status_code, self.SUCCESS_STATUS)

    def test_anon_same_query_works(self):
        """
        When limit is reached, the same query should still work a few hours.
        Works if there is an expected limit for anon user
        """
        if not self.ANON_EXPECTED_LIMIT:
            return

        for i in range(self.ANON_EXPECTED_LIMIT):
            response = self.client.post(self.URL, self.DATA[i])
            self.assertEqual(response.status_code, self.SUCCESS_STATUS)

        response = self.client.post(self.URL, self.DATA[self.ANON_EXPECTED_LIMIT])
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post(self.URL, self.DATA[0])
        self.assertEqual(response.status_code, self.SUCCESS_STATUS)

    def test_anon_user_is_restricted(self):
        """
        Works if there is an expected limit for anon user
        """
        if not self.ANON_EXPECTED_LIMIT:
            return

        for i in range(self.ANON_EXPECTED_LIMIT):
            response = self.client.post(self.URL, self.DATA[i])
            self.assertEqual(response.status_code, self.SUCCESS_STATUS)

        response = self.client.post(self.URL, self.DATA[self.ANON_EXPECTED_LIMIT])
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_verified_user_is_not_restricted(self):
        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)

        for i in range(self.FREE_REG_EXPECTED_LIMIT):
            response = self.client.post(self.URL, self.DATA[i])
            self.assertEqual(response.status_code, self.SUCCESS_STATUS)

        response = self.client.post(self.URL, self.DATA[self.FREE_REG_EXPECTED_LIMIT])
        self.assertEqual(response.status_code, self.SUCCESS_STATUS)


class RentAnalyzerLimitTest(AccessLimitTest, AccountBaseTest):
    URL = reverse('rent_analyzer:rent_analyzer')
    ANON_EXPECTED_LIMIT = 1  # limits expected for an anonymous user
    FREE_REG_EXPECTED_LIMIT = 5
    SUCCESS_STATUS = status.HTTP_200_OK
    FAIL_STATUS = status.HTTP_403_FORBIDDEN
    DATA = [
        {
            'query': f'miami {i}',
            'prop_type2': 'any',
            'distance': 'auto',
            'beds': 'any',
            'baths': 'any',
            'look_back': 3,
            'type': 'address',
        }
        for i in range(12)
    ]

    def test_second_access_event_created(self):
        """
        Request with another query should lead to creating another event,
        since limit for rent analyzer is > 1
        """
        self.assertEqual(AccessEvent.objects.count(), 0)

        self.client.post(self.URL, self.DATA[0])
        self.assertEqual(AccessEvent.objects.count(), 1)

class PropertyReportLimitTest(AccessLimitTest, AccountBaseTest):
    URL = reverse('reports:property_report')
    ANON_EXPECTED_LIMIT = 0  # limits expected for an anonymous user
    FREE_REG_EXPECTED_LIMIT = 1  # limits expected for a free registered user
    SUCCESS_STATUS = status.HTTP_201_CREATED
    FAIL_STATUS = status.HTTP_401_UNAUTHORIZED
    DATA = (
        {'prop_id': 'M9627860216'},
        {'prop_id': 'M9953817139'},
        {'prop_id': 'M9417069959'},
        {'prop_id': 'M5454893686'},
    )


class RentAnalyzerReportLimitTest(AccessLimitTest, AccountBaseTest):
    URL = reverse('reports:rent_analyzer_report')
    ANON_EXPECTED_LIMIT = 0  # limits expected for an anonimous user
    FREE_REG_EXPECTED_LIMIT = 1  # limits expected for a free registered user
    SUCCESS_STATUS = status.HTTP_201_CREATED
    FAIL_STATUS = status.HTTP_401_UNAUTHORIZED
    DATA = [
        {
            'query': f'miami {i}',
            'prop_type2': 'any',
            'distance': 'auto',
            'beds': 'any',
            'baths': 'any',
            'look_back': 3,
            'type': 'address',
        }
        for i in range(8)
    ]


class RentEstimatorAnalyticsLimitTest(AccessLimitTest, AccountBaseTest):
    URL = reverse('rent_analyzer:rent_estimator_analytics')
    ANON_EXPECTED_LIMIT = 1
    FREE_REG_EXPECTED_LIMIT = 5
    SUCCESS_STATUS = status.HTTP_200_OK
    FAIL_STATUS = status.HTTP_403_FORBIDDEN
    DATA = [
        {
            'state': 'CA',
            'zip': f'900{i}',
            'county': 'mogilev',
            'city': 'belinichi',
            'agg_type': 'zip',
            'graph_names': ['days_on_market']
        }
        for i in range(12)
    ]
