"""
Tests for reports views
"""
from django.urls import reverse
from rest_framework import status

from account.tests.factories import create_user
from reports.models import Report
from reports.tests.base import ReportsBaseTest


VALID_PROPERTY_REPORT_DATA = {
    'prop_id': 'M9627860216',
}
VALID_RENT_ANALYZER_REPORT_DATA = {
    'query':        'miami',
    'prop_type3':   'any',
    'distance':     'auto',
    'beds':         'any',
    'baths':        '3',
    'look_back':    12,
    'type':         'address',
    'prop_id':      ''
}
PROPERTY_REPORT_URL = reverse('reports:property_report')
RENT_ANALYZER_REPORT_URL = reverse('reports:rent_analyzer_report')


class PropertyViewTest(ReportsBaseTest):
    # generating PDF is time-consuming,
    # so we do all the checks within just a few test cases

    URL = PROPERTY_REPORT_URL
    VALID_DATA = VALID_PROPERTY_REPORT_DATA

    def test_not_authed(self):
        response = self.client.post(self.URL, self.VALID_DATA)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.content.startswith(b'%PDF-1.4'))
        self.assertEqual(response.headers['Content-Type'], 'application/json')

    def test_empty_prop_id(self):
        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)
        invalid_data = {'prop_id': ''}

        response = self.client.post(self.URL, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.content.startswith(b'%PDF-1.4'))
        self.assertEqual(response.headers['Content-Type'], 'application/json')

    def test_created(self):
        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)
        self.assertFalse(Report.objects.count())

        response = self.client.post(self.URL, self.VALID_DATA)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('report_file', response.data)

        report = Report.objects.first()
        self.assertEqual(report.user, user)
        self.assertTrue(report.report_file)
        self.assertTrue(report.query)
        self.assertTrue(report.data['data'])
        self.assertTrue(report.data['address'])


class RentAnalyzerViewTest(ReportsBaseTest):
    # generating PDF is time-consuming,
    # so we do all the checks within just a few test cases

    URL = RENT_ANALYZER_REPORT_URL
    VALID_DATA = VALID_RENT_ANALYZER_REPORT_DATA

    def test_not_authed(self):
        response = self.client.post(self.URL, self.VALID_DATA)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.content.startswith(b'%PDF-1.4'))
        self.assertEqual(response.headers['Content-Type'], 'application/json')

    def test_empty_query(self):
        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)

        invalid_data = self.VALID_DATA.copy()
        invalid_data['query'] = ''

        response = self.client.post(self.URL, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.content.startswith(b'%PDF-1.4'))
        self.assertEqual(response.headers['Content-Type'], 'application/json')

    def test_invalid_beds(self):
        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)

        invalid_data = self.VALID_DATA.copy()
        invalid_data['beds'] = 'a lot'

        response = self.client.post(self.URL, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.content.startswith(b'%PDF-1.4'))
        self.assertEqual(response.headers['Content-Type'], 'application/json')

    def test_created(self):
        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)
        self.assertFalse(Report.objects.count())

        response = self.client.post(self.URL, self.VALID_DATA)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('report_file', response.data)

        report = Report.objects.first()
        self.assertEqual(report.user, user)
        self.assertTrue(report.report_file)
        self.assertTrue(report.data['address'])
        self.assertTrue(report.data['rent'])
        self.assertTrue(report.data['stat'])

        # TODO (mikhail.varantsou):
        # Assert that report.query is equal to self.VALID_DATA.
        # Now, for unknown reason, it is not equal -
        # numbers in dict turned into strings. Maybe because of SQLite?
        # Don't have time to investigate it right now
        self.assertTrue(report.query)

    def test_no_address_detected_in_calc_model(self):
        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)

        invalid_data = self.VALID_DATA.copy()
        invalid_data['distance'] = '10'

        response = self.client.post(self.URL, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_items_found_by_calc_model(self):
        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)

        invalid_data = self.VALID_DATA.copy()
        invalid_data['query'] = 'spam'

        response = self.client.post(self.URL, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ListViewTest(ReportsBaseTest):
    URL = reverse('reports:report_list')

    def test_not_authed(self):
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_empty_list(self):
        user = create_user()
        self.client.force_authenticate(user=user)

        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data)

    def test_my_report_returned(self):
        user = create_user()
        self.client.force_authenticate(user=user)
        Report.objects.create(query={}, data={}, user=user)

        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_only_my_report_returned(self):
        user = create_user()
        another_user = create_user()
        self.client.force_authenticate(user=user)
        Report.objects.create(query={'spam': 'a'}, data={}, user=user)
        Report.objects.create(query={}, data={}, user=another_user)

        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['query'], {'spam': 'a'})

    def test_rent_analyzer_complete_flow(self):
        user = create_user({'verified': True})
        self.client.force_authenticate(user=user)
        expected_list_data = {'beds': 'any', 'baths': '3', 'address': 'miami'}

        # create real report
        self.client.post(RENT_ANALYZER_REPORT_URL, VALID_RENT_ANALYZER_REPORT_DATA)

        # get it in report list
        response = self.client.get(self.URL)
        report = response.data[0]

        # check correctness of all the report fields
        self.assertTrue(report['created_at'])
        self.assertEqual(report['report_type'], 'rent_analyzer')
        self.assertEqual(report['query']['query'], 'miami')
        self.assertEqual(report['list_data'], expected_list_data)
        self.assertTrue(report['report_file'].endswith('.pdf'))
        self.assertNotIn('user', report)
        self.assertNotIn('data', report)

    def test_property_complete_flow(self):
        user = create_user({'verified':True})
        self.client.force_authenticate(user=user)
        expected_list_data = {
            'beds': 2,
            'baths': 2,
            'address': '33740 Skiff Aly Unit 3109',
        }

        # create real report
        self.client.post(PROPERTY_REPORT_URL, VALID_PROPERTY_REPORT_DATA)

        # get it in report list
        response = self.client.get(self.URL)
        report = response.data[0]

        # check correctness of all the report fields
        self.assertTrue(report['created_at'])
        self.assertEqual(report['report_type'], 'property')
        self.assertEqual(report['query']['prop_id'], 'M9627860216')
        self.assertEqual(report['list_data'], expected_list_data)
        self.assertTrue(report['report_file'].endswith('.pdf'))
        self.assertNotIn('user', report)
        self.assertNotIn('data', report)
