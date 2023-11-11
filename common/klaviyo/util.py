import base64
import json
import logging
import random

import requests

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

import account.models
from account.utils import get_access_status
from api_property.common.common import get_pg_connection
from api_property.common.recommendations import get_similar
from api_property.models import SimilarPropertyNotificationModel, PropertyUpdateModel
from common.klaviyo.helpers import prop_to_klaviyo, read_notification_props
from common.utils import split_to_chunks
from reports.enums import ReportType


User = get_user_model()
logger = logging.getLogger('klaviyo')

# identify/track functions are executed inside celery tasks.
# set timeout to not block celery workers
connect_timeout, read_timeout = 10.0, 60.0
requests_timeout = (connect_timeout, read_timeout)


def add_token(data):
    data['token'] = settings.KLAVIYO_API_KEY


def encode_dict(data):
    s = json.dumps(data)
    b64bytes = base64.b64encode(s.encode('utf-8'))
    return str(b64bytes, "utf-8")


def identify(email, customer_properties=None):
    customer_properties = customer_properties or {}
    if not settings.KLAVIYO_ENABLED:
        return
    url = settings.KLAVIYO_URL + 'api/identify'
    customer_properties['$email'] = email
    data = {'properties': customer_properties}
    add_token(data)
    r = requests.get(url, params={'data': encode_dict(data)}, timeout=requests_timeout)
    logger.info('GET %s, RESPONSE %s, STATUS %s', url, r.text, r.status_code)


def track(email, event, properties=None, **kwargs):
    properties = properties or {}
    if event_id := kwargs.get('event_id'):
        properties.update({'$event_id': event_id})
    if not settings.KLAVIYO_ENABLED:
        return
    url = settings.KLAVIYO_URL + 'api/track'
    data = {
        'event': event,
        'customer_properties': {'$email': email},
        'properties': properties
    }
    add_token(data)
    r = requests.get(url, params={'data': encode_dict(data)}, timeout=requests_timeout)
    logger.info('GET %s, RESPONSE %s, STATUS %s', url, r.text, r.status_code)


def add_user_to_list(email, list_id):
    if not settings.KLAVIYO_ENABLED:
        return
    url = settings.KLAVIYO_URL + f'api/v2/list/{list_id}/members'
    data = {'profiles': [{'email': email}]}
    params = {'api_key': settings.KLAVIYO_PRIVATE_KEY}
    r = requests.post(url, json=data, params=params, timeout=requests_timeout)
    logger.info('POST %s, RESP %s, STATUS %s', url, r.text, r.status_code)


def add_lead_to_list(list_id, lead_params):
    if not settings.KLAVIYO_ENABLED:
        return
    url = settings.KLAVIYO_URL + f'api/v2/list/{list_id}/members'
    data = {'profiles': [{**lead_params}]}
    params = {'api_key': settings.KLAVIYO_PRIVATE_KEY}
    r = requests.post(url, json=data, params=params, timeout=requests_timeout)
    logger.info('POST %s, RESP %s, STATUS %s', url, r.text, r.status_code)


######################################################################
# Custom metrics

klaviyo_date_fmt = '%Y-%m-%d'
def current_time_str():
    return timezone.now().strftime(klaviyo_date_fmt)


def track_rent_analyzer(user_id, search_data):
    user = User.objects.get(pk=user_id)
    track(user.email, 'Searched Rent Analyzer', search_data)


def track_report(user_id, email, report_type):
    if report_type in ReportType:
        report_title = ReportType(report_type).label
    else:
        report_title = 'Unknown'
    track(email, f'Generated {report_title} report')


def track_search_address(email, search_data):
    track(email, 'Searched address', search_data)


def track_search(email, search_data):
    track(email, 'Searched data', search_data)


def track_viewed_property(email, prop_id):
    track(email, 'Viewed Property', {'Item ID': prop_id})


def track_properties_notification(email, main, related, prop_class, topic, subtopic='', prefix='', **kwargs):
    """
    Send provided props to Klaviyo so the user
    received a notification with them.
    - email is an email of a user
    - main is a list of main prop_ids
    - related is a list of related prop_ids
    - prop_class is one of api_property.enums.PropClass choices
    - topic is one of api_property.enums.PropertyNotificationTopic choices
    - subtopic is a separation inside topic
    - if one_prop, then the first prop of [props] will be sent as it is
    """
    subtopic_part = subtopic.title() + ' ' if subtopic else ''
    event = f'{prefix}{topic.label} {subtopic_part}Notification - {prop_class.label}'
    props = {}

    if props_main := read_notification_props(main, prop_class, active=False, photo=False):
        klav_main = [prop_to_klaviyo(p, prop_class) for p in props_main]
        props['main'] = split_to_chunks(klav_main, 2)

    if props_related := read_notification_props(related, prop_class):
        klav_related = [prop_to_klaviyo(p, prop_class) for p in props_related]
        props['related'] = split_to_chunks(klav_related, 2)

    if props:
        track(email, event, {'props': props}, event_id=kwargs.get('event_id'))


def track_favorites(user_id, email):
    favs = account.models.FavoriteProperty.objects.filter(user_id=user_id)
    prop_ids = [f.prop_id for f in favs]
    identify(email, {'Favorite Listings': prop_ids})


def track_add_favorite(fav_id):
    """
    Send this event once when a user adds a prop to favorites
    """
    fav = account.models.FavoriteProperty.objects.get(pk=fav_id)
    if props_main := read_notification_props([fav.prop_id], fav.prop_class,
                                             active=False, photo=False):
        event = f'Favorite property added - {fav.prop_class.title()}'
        props = {'main': [[prop_to_klaviyo(props_main[0], fav.prop_class)]]}

        similars = get_similar(get_pg_connection().cursor(), fav.prop_id, fav.prop_class, [])
        random.shuffle(similars)
        if similar_ids := [s['prop_id'] for s in similars if s['photo']][:4]:
            klav_related = [prop_to_klaviyo(p, fav.prop_class) for p in
                            read_notification_props(similar_ids, fav.prop_class, photo=False)]
            props['related'] = split_to_chunks(klav_related, 2)

        track(fav.user.email, event, {'props': props})


def track_user_status_changed(user_id):
    user = User.objects.get(pk=user_id)
    if user.verified:
        add_user_to_list(user.email, settings.KLAVIYO_NEWSLETTER_LIST_ID)
    access_status = get_access_status(user)
    event = f'{access_status.label} Started Date'
    data = {event: current_time_str(),
            'Plan Status': access_status.label}
    identify(user.email, data)


def track_email_settings(user_id):
    user = User.objects.get(pk=user_id)
    names = {
        'good_deals':                     'Good Deal Properties Subscription',
        'similars':                       'Similar Properties Subscription',
        'prop_updates':                   'Property Updates Notifications Subscription',
        'favorites':                      'Favorite Properties Subscription',
        'favorites_match_notification':   'Similar Favorite Properties Subscription',

        'tips_and_guides':                'Ofirio Tips & Guides Subscription',
        'market_reports_and_updates':     'Market Reports & Updates Subscription',
        'tool_updates':                   'Ofirio Tools Updates Subscription',
        'partner_offers_and_deals':       'Partners Offers & Deals Subscription',
        'properties_you_may_like':        'May Like Properties Subscription'
    }
    obj = user.emailsettings_set.last()
    data = {klaviyo_name: getattr(obj, key) for key, klaviyo_name in names.items()}
    # send initial Plan Status value
    data['Plan Status'] = get_access_status(user).label
    identify(user.email, data)


def track_good_deal_settings(user_id):
    user = User.objects.get(pk=user_id)
    names = {
        'prop_type': 'Home Type',
        'rent_min_price': 'Min Price (Rent)',
        'rent_max_price': 'Max Price (Rent)',
        'buy_min_price': 'Min Price (Buy)',
        'buy_max_price': 'Max Price (Buy)',
        'invest_min_price': 'Min Price (Invest)',
        'invest_max_price': 'Max Price (Invest)',
        'rent_enabled': 'Interested In Rent a Home',
        'buy_enabled': 'Interested In Buy a Home',
        'invest_enabled': 'Interested In Investment Property',
        'beds_min': 'Bedroom count',
        'baths_min': 'Bathroom count',
    }
    gd_settings = user.gooddealsettings_set.first()
    data = {'Good Deal Settings - ' + klaviyo_name: getattr(gd_settings, key)
            for key, klaviyo_name in names.items()}

    cities_key = 'Good Deal Settings - Cities Interested In'
    data[cities_key] = [city.label for city in gd_settings.cities.all()]

    identify(user.email, data)


def track_similars(user_id, email):
    similars = SimilarPropertyNotificationModel.objects.filter(user_id=user_id)
    prop_ids = [f.prop_id for f in similars]
    identify(email, {'Similar Properties PropIDs': prop_ids})


def track_prop_updates(user_id, email):
    prop_updates = PropertyUpdateModel.objects.filter(user_id=user_id)
    prop_ids = [f.prop_id for f in prop_updates]
    identify(email, {'Property Updates PropIDs': prop_ids})
