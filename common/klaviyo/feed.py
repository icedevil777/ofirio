from datetime import datetime, timedelta

from django.contrib.humanize.templatetags.humanize import intcomma
from ofirio_common.address_util import build_address
from ofirio_common.helpers import url_to_cdn

from api_property.common.common import is_off_market_status
from api_property.common.rebates import get_rebate_for_view
from common.klaviyo.constants import KLAVIYO_PROP_TYPE_SALES, KLAVIYO_PROP_TYPE_RENT


def define_categories(item, section):
    if section == 'buy':
        cats = define_categories_buy(item)
    if section == 'rent':
        cats = define_categories_rent(item)
    if section == 'invest':
        cats = define_categories_invest(item)
    state = item['address_state_code']
    return [f'{state} {section.title()}: {cat}' for cat in cats]


def is_new(item):
    return item['list_date'] > datetime.now() - timedelta(days=7)


def define_beds_cat(item):
    if item['beds'] >= 6:
        return 'Beds 6+'
    else:
        return f"Beds {item['beds']}"


def define_sales_price_cat(item):
    if item['price'] < 100000:
        return 'Price <100k'
    elif item['price'] >= 800000:
        return 'Price >800k'
    else:
        for price_low, price_high in (
                (100, 200),
                (200, 300),
                (300, 400),
                (400, 500),
                (500, 600),
                (600, 700),
                (700, 800)):
            if price_low * 1000 <= item['price'] < price_high * 1000:
                return f'Price {price_low}..{price_high}k'


def define_categories_rent(item):
    type_cat = 'Type - ' + KLAVIYO_PROP_TYPE_RENT[item['prop_type']]
    bed_cat = define_beds_cat(item)

    if item['price'] < 200:
        price_cat = 'Price <200'
    elif item['price'] >= 15000:
        price_cat = 'Price >15,000'
    else:
        for price_low, price_high in (
                (200, 500),
                (500, 1000),
                (1000, 1500),
                (1500, 2000),
                (2000, 2500),
                (2500, 3000),
                (3000, 3500),
                (3500, 4000),
                (4000, 4500),
                (4500, 5000),
                (5000, 6000),
                (6000, 7000),
                (7000, 8000),
                (8000, 9000),
                (9000, 10000),
                (10000, 11000),
                (11000, 12000),
                (12000, 13000),
                (13000, 14000),
                (14000, 15000)):
            if price_low <= item['price'] < price_high:
                price_cat = f'Price {price_low:,}-{price_high:,}'

    cats = [type_cat, bed_cat, price_cat]
    if is_new(item):
        cats.append('New Properties')
    if 'good_deal_rent' in item['badges']:
        cats.append('Good Deals')
    if 'pet_friendly' in item['badges']:
        cats.append('Pet Friendly')
    return cats


def define_categories_invest(item):
    type_cat = 'Type - ' + KLAVIYO_PROP_TYPE_SALES[item['prop_type']]
    price_cat = define_sales_price_cat(item)
    bed_cat = define_beds_cat(item)

    cats = []
    if is_new(item):
        cats.append('New Properties')
    if 'good_deal_invest' in item['badges']:
        cats.append('Good Deals')
    if item['cap_rate'] is None:
        # possible bug when property with cap rate NaN has invest view
        return cats

    cap_rate = 'CapR>5%' if item['cap_rate'] >= .05 else 'CapR<5%'
    cats.extend([f'{x} {cap_rate}' for x in (type_cat, bed_cat, price_cat)])
    return cats


def define_categories_buy(item):
    type_cat = 'Type - ' + KLAVIYO_PROP_TYPE_SALES[item['prop_type']]
    price_cat = define_sales_price_cat(item)
    bed_cat = define_beds_cat(item)

    cats = [type_cat, bed_cat, price_cat]
    if is_new(item):
        cats.append('New Properties')
    if 'good_deal_buy' in item['badges']:
        cats.append('Good Deals')
    return cats


def build_feed_item(prop, url, section):
    ''' convert property to klaviyo feed representation '''
    item = {}
    item['$id'] = prop['prop_id']
    item['$link'] = url
    item['$image_link'] = url_to_cdn(prop['image'])
    if item['$image_link']:
        item['$image_link'] += '?width=320&quality=70&aspect_ratio=3%3A2'
    item['$title'] = build_address(
        prop['address_line'], prop['address_city'],
        prop['address_state_code'], prop['address_zip'],
    )
    item['$description'] = '-'  # could not be empty because of klaviyo requirements
    item['$price'] = prop['price']
    # looks like klaviyo feed template doesn't work with string price
    #item['price'] = '$' + intcomma(prop['price'] or 0)
    item['categories'] = define_categories(prop, section)
    if section == 'invest':
        item['cap_rate'] = prop['cap_rate']
        item['pred_rent'] = prop['predicted_rent']
    if section == 'buy':
        rebate = get_rebate_for_view(prop['address_zip'], prop['price'],
                                     is_off_market_status(prop['status']))
        item['rebate'] = rebate
        item['est_mort'] = prop['estimated_mortgage']
    return item
