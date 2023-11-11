from django.urls import reverse
from rest_framework import status

from common.tests.base import PortalBaseTest


class AccountBaseTest(PortalBaseTest):
    valid_user_data = {'email': 'test@ofirio.com', 'password': 'sPam123$'}

    def is_authenticated(self):
        response = self.client.get(reverse('account:account'))
        return response.status_code == status.HTTP_200_OK
