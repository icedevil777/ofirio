from functools import lru_cache

import pandas as pd
from django.conf import settings

from common.cache import simple_cache_by_static_key
from api_property.constants import ALLOWED_TO_REBATE_STATE, ALLOWED_TO_REBATE_ZIP


@lru_cache(maxsize=1)
def get_no_rebate_zips():
    path = settings.BASE_DIR / 'data/uszips-cached.csv'
    us_zips = pd.read_csv(path, usecols=['zip', 'state_id'], dtype=str)
    allowed_zips = frozenset(us_zips[us_zips.state_id.isin(ALLOWED_TO_REBATE_STATE)].zip.values)
    allowed_zips |= frozenset(ALLOWED_TO_REBATE_ZIP)
    # allowed zips ~ 33k, all zips ~ 41k
    return frozenset(us_zips.zip.values) - allowed_zips


def get_rebate_percent_and_split(price):
    rebate_percent = None
    ofirio_percent = 0.2
    if price < 150_000:
        pass
    elif price in range(150_000, 350_000):
        rebate_percent = 0.0025
        ofirio_percent = 0.2
    elif price in range(350_000, 750_000):
        rebate_percent = 0.005
        ofirio_percent = 0.25
    elif price in range(750_000, 1_000_000):
        rebate_percent = 0.0075
        ofirio_percent = 0.3
    elif price in range(1_000_000, 2_000_000):
        rebate_percent = 0.01
        ofirio_percent = 0.35
    elif price in range(2_000_000, 4_000_000):
        rebate_percent = 0.015
        ofirio_percent = 0.4
    elif price >= 4_000_000:
        rebate_percent = 0.02
        ofirio_percent = 0.5
    return rebate_percent, ofirio_percent


def get_split_rebate_off_market(price):
    ofirio_percent = 0.25
    if price < 150_000:
        total = 0.03
        seller_saving = False
    else:  # price >= 150_000
        total = 0.015
        seller_saving = True
    return ofirio_percent, total, seller_saving


def get_full_rebate(zip_code: str = None, price=None, off_market=False, check_=True, state_id: str = None) -> dict:
    if not price:
        return {}
    if check_:
        if state_id and state_id not in ALLOWED_TO_REBATE_STATE:
            return {}
        if zip_code and zip_code in get_no_rebate_zips():
            return {}
    if off_market is False:
        total_commission = price * 0.03
        rebate_percent, ofirio_percent = get_rebate_percent_and_split(price)
        agent_percent = 1 - ofirio_percent
        if not rebate_percent:
            ofirio_commission = total_commission * ofirio_percent
            agent_commission = total_commission * agent_percent
            rebate = None
        else:
            rebate = price * rebate_percent
            rest_of_commission = (total_commission - rebate)
            ofirio_commission = rest_of_commission * ofirio_percent
            agent_commission = rest_of_commission * agent_percent

    else:
        ofirio_percent, total_percent, seller_saving = get_split_rebate_off_market(price)
        total_commission = price * total_percent
        agent_percent = 1 - ofirio_percent
        ofirio_commission = total_commission * ofirio_percent
        agent_commission = total_commission * agent_percent
        if not seller_saving:
            rebate = None
            rebate_percent = None
        else:
            rebate = total_commission
            rebate_percent = total_percent
    return {'rebate': rebate,
            'rebate_percent': rebate_percent,
            'ofirio_commission': ofirio_commission,
            'ofirio_percent': ofirio_percent,
            'agent_commission': agent_commission,
            'agent_percent': agent_percent, }


def get_rebate_without_check(price, off_market):
    return get_full_rebate(price=price, off_market=off_market, check_=False).get('rebate', None)


def get_rebate_for_view(zip_code, price, off_market):
    return get_full_rebate(zip_code, price, off_market).get('rebate', None)


# TODO: use this function instead of get_rebate_for_view. this one is much faster
def get_rebate_for_view1(state_id, price, off_market):
    return get_full_rebate(state_id=state_id, price=price, off_market=off_market).get('rebate', None)
