from datetime import datetime, timedelta

from ofirio_common.helpers import url_to_cdn

from api_property.constants import SOLD_STATUSES
from common.utils import get_is_test_condition
from api_property.enums import RecommendationsChoices
from api_property.common.common import (
    cant_show_price_fields, clean_sensitive_data, get_is_hidden,
    clean_premium_data, get_estimated_mortgage, is_off_market_status,
    format_listing_office,
)
from api_property.common.rebates import get_rebate_for_view


ACTIVE_STATUSES = ('for_sale', 'for_rent', 'under_contract')

PROP_CARD_SQL = '''
    select
        c.prop_id,
        c.data,
        ph.photos->0 photo,
        c.address,
        c.status,
        c.badges,
        c.params,
        c.list_date,
        ph.street_view,
        c.close_date
    from prop_cache c
    join prop_photos ph on c.real_prop_id = ph.prop_id
'''

PROP_CARD_BY_ID_SQL = PROP_CARD_SQL + f'''
    where c.prop_id = any(%(prop_ids)s)
          {get_is_test_condition(table_alias='c')}
'''

PROP_CARD_IN_IDS_SQL = PROP_CARD_SQL + f'''
    where c.prop_id in %(prop_ids)s
          {get_is_test_condition(table_alias='c')}
'''

PROP_CARD_BY_ID_AND_PROP_CLASS_SQL = PROP_CARD_SQL + f'''
    where c.prop_id = any(%(prop_ids)s) and c.prop_class = %(prop_class)s
              {get_is_test_condition(table_alias='c')}
'''


def get_prop_class_from_section(section):
    return 'sales' if section in (RecommendationsChoices.buy, RecommendationsChoices.invest)\
        else RecommendationsChoices.rent


def card_badges(section, badges, list_date, status):
    res = []
    if status in ACTIVE_STATUSES and list_date > datetime.now() - timedelta(days=7):
        res.append('new')
    if f'good_deal_{section}' in badges:
        res.append('good_deal')
    return res


def make_cards(section, res_prop_cache, blur=False):
    """ section may be buy/rent/invest
        res_prop_cache is a list of tuples returned by PROP_CARD_SQL
    """
    result = []
    for prop in res_prop_cache:
        prop_id = prop[0]
        data = prop[1]
        photo = prop[2] if prop[2] else prop[8]
        addr = prop[3]
        status = prop[4]
        badges = prop[5]
        params = prop[6]
        list_date = prop[7]
        price = data.get('close_price', 0) if status in SOLD_STATUSES else data['price']

        cant_show_price = cant_show_price_fields(status, addr['state_code'])
        off_market = status == 'off_market'
        clean_sensitive_data(data, cant_show_price, off_market)
        if section != RecommendationsChoices.rent:
            data['estimated_mortgage'] = get_estimated_mortgage(params.get('is_cash_only'),
                                                                data['estimated_mortgage'])
        listing_office = params.get('listing_office')
        item = make_prop_card(
            section, prop_id, price, data, addr, photo, status, badges, list_date, listing_office,
        )
        if blur and get_is_hidden(prop_id, params):
            clean_premium_data(item)
        result.append(item)
    return result


def make_prop_card(section, prop_id, price, data,
                   address, photo, status, badges, list_date, listing_office):
    '''price may be hidden in `data`, so for rebate we take it from `price`'''
    item = {
        'beds': data['beds'],
        'baths': data['baths'],
        'photo': url_to_cdn(photo),
        'price': price,
        'status': select_status(status),
        'badges': card_badges(section, badges, list_date, status),
        'address': address['full_address'],
        'prop_id': prop_id,
        'building_size': data['building_size'],
        'listing_office': format_listing_office(listing_office, status),
    }
    if section in (RecommendationsChoices.buy, RecommendationsChoices.invest):
        item.update({
            'rebate': get_rebate_for_view(address['zip'], price, is_off_market_status(status)),
        })
    if section == RecommendationsChoices.buy:
        item.update({
            'est_mortgage': data['estimated_mortgage'],
        })
    if section == RecommendationsChoices.invest:
        item.update({
            'cap_rate': data.get('cap_rate'),
            'est_rent': data.get('predicted_rent'),
            'total_return': data.get('total_return'),
            'cash_on_cash': data.get('cash_on_cash'),
        })
    return item


def select_status(status):
    if status in ACTIVE_STATUSES:
        return None
    return status


def make_prop_card_es(section, prop):
    list_date = datetime.strptime(prop['list_date'], '%Y-%m-%dT%H:%M:%S')  # 2022-10-05T21:16:55
    item = {
        'beds': prop['beds'],
        'baths': prop['baths'],
        'photo': url_to_cdn(prop['previews'][0] if prop['previews'] else prop['street_view']),
        'price': prop['price'],
        'status': select_status(prop['status']),
        'badges': card_badges(section, prop['badges'], list_date, prop['status']),
        'address': prop['address'],
        'prop_id': prop['prop_id'],
        'building_size': prop['building_size'],
        'listing_office': format_listing_office(prop.get('listing_office'), prop['status']),
    }
    if section in (RecommendationsChoices.buy, RecommendationsChoices.invest):
        item.update({
            'rebate': get_rebate_for_view(prop['zip'], prop['price'], off_market=False),
        })
    if section == RecommendationsChoices.buy:
        item.update({
            'est_mortgage': prop['month_loan_payments'],
        })
    if section == RecommendationsChoices.invest:
        item.update({
            'cap_rate': prop['cap_rate'],
            'est_rent': prop['predicted_rent'],
            'total_return': prop['total_return'],
            'cash_on_cash': prop['cash_on_cash'],
        })
    return item
