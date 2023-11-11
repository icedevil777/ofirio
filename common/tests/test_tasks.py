from datetime import timedelta

from account.models import AccessEvent
from common.tasks import remove_garbage
from common.tests.base import PortalBaseTest


class RemoveGarbageTest(PortalBaseTest):

    def test_remove_access_events(self):
        # create old access event
        ae = AccessEvent.objects.create(ip_address='1.1.1.1', query={})
        ae.created_at = ae.created_at - timedelta(days=31)
        ae.save()

        # it must be removed after the task executed
        remove_garbage.delay()
        self.assertFalse(AccessEvent.objects.count())
