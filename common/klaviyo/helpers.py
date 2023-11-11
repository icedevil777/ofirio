from django.db import connections

from ofirio_common.address_util import build_address
from ofirio_common.helpers import url_to_cdn

from api_property.common.common import is_off_market_status
from api_property.common.prop_representation import humanize_status
from api_property.common.rebates import get_rebate_for_view
from api_property.constants import ACTIVE_STATUS_MAP, SOLD_STATUSES
from api_property.enums import PropClass
from common.utils import humanize_price
from search.seo.sitemaps import ask_socket_for_one_url


def read_notification_props(ntf_props, prop_class, active=True, photo=True):
    """
    Read various fields of provided props from prop_cache
    for Klaviyo track property notification events
    """
    props = []
    if not ntf_props:
        return props

    where = ['c.prop_id IN %(prop_ids)s']
    if active:
        where.append(f"c.status = '{ACTIVE_STATUS_MAP[prop_class]}'")
    if photo:
        where.append("pp.photos IS NOT NULL")
        where.append("pp.photos != '[]'")

    keys = ('prop_id', 'status', 'image', 'address_line', 'address_city', 'address_state_code',
            'address_zip', 'price', 'est_mort', 'cap_rate', 'est_rent', 'close_price')
    sql = """
        SELECT
            c.prop_id,
            c.status,
            pp.photos ->> 0 image,
            c.address ->> 'line' address_line,
            c.address ->> 'city' address_city,
            c.address ->> 'state_code' address_state_code,
            c.address ->> 'zip' address_zip,
            c.data ->> 'price' price,
            c.data ->> 'estimated_mortgage' est_mort,
            c.data ->> 'cap_rate' cap_rate,
            c.data ->> 'predicted_rent' est_rent,
            c.data ->> 'close_price' close_price
        FROM prop_cache c
        LEFT JOIN prop_photos pp on c.real_prop_id = pp.prop_id
        WHERE
    """ + ' AND '.join(where)

    with connections['prop_db'].cursor() as cursor:
        cursor.execute(sql, {'prop_ids': tuple(ntf_props)})
        for fetched_prop in cursor.fetchall():
            prop = dict(zip(keys, fetched_prop))
            prop['prop_class'] = prop_class
            close_price = prop.pop('close_price')
            if prop['status'] in SOLD_STATUSES:
                prop['price'] = close_price
            props.append(prop)

    return props


def prop_to_klaviyo(prop, prop_class):
    """
    Convert property to Klaviyo representation
    """
    full_address = build_address(prop['address_line'], prop['address_city'],
                                 prop['address_state_code'], prop['address_zip'])
    klav_prop = {
        'prop_id': prop['prop_id'],
        'prop_class': prop_class,
        'image': url_to_cdn(prop['image']),
        'url': ask_socket_for_one_url(prop['prop_id'], full_address),
        'price': humanize_price(prop['price']),
        'status': humanize_status(prop['status']),
        'title': full_address,
    }
    if prop_class == PropClass.BUY:
        rebate = get_rebate_for_view(prop['address_zip'], int(prop['price']),
                                     is_off_market_status(prop['status']))
        klav_prop['rebate'] = humanize_price(rebate)
        klav_prop['est_mort'] = humanize_price(prop['est_mort'])
    elif prop_class == PropClass.INVEST:
        klav_prop['cap_rate'] = prop['cap_rate']
        klav_prop['est_rent'] = prop['est_rent']

    return klav_prop
