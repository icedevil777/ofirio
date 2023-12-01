from datetime import timedelta

from django.utils import timezone
from celery import shared_task

import account.models
import common.klaviyo.util as ku
import common.intercom_util as iu
from djangoproject.celery import app as celery_app


@shared_task
def track_favorites(*a, **kw):
    ku.track_favorites(*a, **kw)


@shared_task
def track_add_favorite(*a, **kw):
    ku.track_add_favorite(*a, **kw)


@shared_task
def track_email_settings(*a, **kw):
    ku.track_email_settings(*a, **kw)


@shared_task
def track_good_deal_settings(*a, **kw):
    ku.track_good_deal_settings(*a, **kw)


@shared_task
def track_similars(*a, **kw):
    ku.track_similars(*a, **kw)


@shared_task
def track_prop_updates(*a, **kw):
    ku.track_prop_updates(*a, **kw)


@shared_task
def track_report(*a, **kw):
    ku.track_report(*a, **kw)

@shared_task
def track_rent_analyzer(*a, **kw):
    ku.track_rent_analyzer(*a, **kw)

@shared_task
def track_search_address(*a, **kw):
    ku.track_search_address(*a, **kw)

@shared_task
def track_search(*a, **kw):
    print('track_search')
    ku.track_search(*a, **kw)

@shared_task
def track_user_status_changed(*a, **kw):
    ku.track_user_status_changed(*a, **kw)

@shared_task
def track_viewed_property(*a, **kw):
    ku.track_viewed_property(*a, **kw)


@shared_task
def send_to_intercom(*a, **kw):
    iu.send_to_intercom(*a, **kw)


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    """Here we add all the periodic tasks"""
    sender.add_periodic_task(timedelta(days=1), remove_garbage.s(), name='remove_garbage')


@celery_app.task
def remove_garbage(*a, **kw):
    """Task to remove old entries in DB"""
    # remove old anonymous access events
    threshold = timezone.now() - timedelta(days=30)
    events = account.models.AccessEvent.objects.filter(created_at__lt=threshold).exclude(
        ip_address__isnull=True).exclude(ip_address__exact='')
    return events.delete()


@shared_task
def add_lead_to_list(*a, **kw):
    return ku.add_lead_to_list(*a, **kw)
