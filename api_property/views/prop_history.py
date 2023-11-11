from django.db import connections
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from api_property.common.common import is_off_market_status
from api_property.serializers import PropertyIdSerializer


def get_listed_ev_name(prop_class):
    if prop_class == 'rent':
        return 'Listed for rent'
    else:
        return 'Listed'


def get_closed_ev_name(prop_class):
    if prop_class == 'rent':
        return 'Rented'
    else:
        return 'Sold'


def build_mls_events(res, hide_close_price, is_off_market=False):
    mls_events = []
    for (prop_class, prop_id, listing_id, source_mls,
         list_date, close_date, list_price, close_price, updated_at) in res:

        if list_date:
            # create 'listed' event
            event_name = get_listed_ev_name(prop_class)
            mls_events.append({
                "listing_id": listing_id,
                "prop_id": prop_id,
                "date": list_date,
                "price": list_price,
                "mls_name": source_mls,
                "event_name": event_name,
                "price_changed": None,
            })

        if close_date:
            # create 'closed' event
            event_name = get_closed_ev_name(prop_class)
            mls_events.append({
                "listing_id": listing_id,
                "prop_id": prop_id,
                "date": close_date,
                "price": None if hide_close_price else close_price,
                "mls_name": source_mls,
                "event_name": event_name,
                "price_changed": None,
            })

        if is_off_market:
            mls_events.append({
                "listing_id": listing_id,
                "prop_id": prop_id,
                "date": updated_at,
                "price": None,
                "mls_name": source_mls,
                "event_name": 'Listing Removed',
                "price_changed": None,
            })

    return mls_events


def build_price_events(res):
    price_events = []
    prev_price = None
    price_changed = None
    for prop_id, price, update_date in res:
        price_changed = price - prev_price if prev_price else None
        price_events.append({
            "listing_id": None,
            "prop_id": prop_id,
            "date": update_date,
            "price": price,
            "mls_name": None,
            "event_name": 'Price Changed',
            "price_changed": price_changed,
        })
        prev_price = price
    return price_events


def get_prop_history(prop_id):
    cursor = connections['prop_db'].cursor()
    SQL = """
            SELECT zip, address ->> 'address_line_norm', prop_class, state_id, real_prop_id
            FROM prop_cache
            WHERE prop_id=%(prop_id)s
    """
    cursor.execute(SQL, {'prop_id': prop_id})
    res = cursor.fetchone()
    if not res:
        return []

    hide_close_price = res[3] == 'TX'
    prop_class = res[2]
    real_prop_id = res[4]
    if res[0] and res[1]:
        address_zip_line = res[0] + '-' + res[1]
        SQL = """
                SELECT
                    prop_class,
                    prop_id,
                    listing_id,
                    source_mls,
                    list_date,
                    close_date,
                    list_price,
                    close_price,
                    updated_at
                FROM all_props
                WHERE address_zip_line = %(address_zip_line)s
        """
        if prop_class == 'rent':
            # for rent properties show only rent history, for sales combine all
            SQL += "and prop_class = 'rent'"
        cursor.execute(SQL, {'address_zip_line': address_zip_line})
        res = cursor.fetchall()
        SQL = """
            SELECT status FROM prop_cache WHERE prop_id = %(prop_id)s
        """
        cursor.execute(SQL, {'prop_id': prop_id})
        prop_status = cursor.fetchone()[-1]
        mls_events = build_mls_events(res, hide_close_price, is_off_market_status(prop_status))
    else:
        mls_events = []

    SQL = """
            SELECT
                prop_id,
                price,
                update_date
            FROM price_history
            WHERE prop_id = %(real_prop_id)s
            ORDER BY update_date
    """
    cursor.execute(SQL, {'real_prop_id': real_prop_id})
    res = cursor.fetchall()
    price_events = build_price_events(res)

    # set original list price to mls event 'listed'
    if price_events:
        # get original price
        original_price = price_events[0]['price']
        for ev in mls_events:
            if ev['prop_id'] == prop_id and ev['event_name'].startswith('Listed'):
                ev['price'] = original_price
                break

    return sorted(mls_events[:15] + price_events[1:15], key=event_sort_key, reverse=True)


def event_sort_key(ev):
    '''if close/listed dates are the same, listed should be before closed'''
    if ev['event_name'].startswith('Listed'):
        order = 0
    else:
        order = 1
    date = ev['date']
    # import pdb;pdb.set_trace()
    if ev['event_name'] != 'Price Changed':
        # save precise time for price change,
        # it can be changes multiple times a day.
        # but truncate date for list/close
        # because mls may have no precise time for 'Closed' event
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    return date, order


class PropHistory(APIView):
    serializer_class = PropertyIdSerializer

    def post(self, request,*args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        prop_id = serializer.data['prop_id']
        history = get_prop_history(prop_id)
        data = {
            'prop_id': prop_id,
            'prop_history': history,
        }
        return Response(data, status=status.HTTP_200_OK)
