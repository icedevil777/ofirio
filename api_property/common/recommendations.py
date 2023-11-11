import time
import logging

import numpy as np
import pandas as pd
from django.conf import settings
from ofirio_common.address_util import (
    urlify, replace_synonyms, get_building_address,
)

from account.enums import UserAccessStatus
from account.utils import get_access_status
from api_property.constants import SOLD_STATUSES
from api_property.enums import RecommendationsCats
from api_property.common.errors import NoPropertyError
from api_property.common.card import make_cards, PROP_CARD_BY_ID_SQL


logger = logging.getLogger('recommendations')


def get_ids(df) -> list:
    '''returns minimum 3 maximum 8 first prop_ids from df'''
    if len(df) < 3:
        return []
    return list(df.head(8).index)


def get_similar(cursor, prop_id:str, section:str, exclude_prop_ids:list) -> list:
    '''
    Returns similar properties with all necessary info.
    Args:
        cursor: regular pg connection cursor
        prop_id: property to search recommendation for
        section: one of RecommendationsChoices (buy/rent/invest)
        exclude_prop_ids: prop ids to exclude from results
    Test:
    >>> c = get_pg_connection().cursor()
    >>> get_similar(c, 'ADF6FE51135EF9803C05', 'buy', [])
    [..list of items..]
    '''
    # blur_invest=False because method is used for registered users only
    cls = SimilarProps(cursor, prop_id, section, blur_invest=False)
    ids = cls.get_similar_nearby([prop_id] + (exclude_prop_ids or []))
    props = cls.get_full_info(ids)
    props = [x for x in props if x[4] in cls.active_statuses]  # OT-2821
    items = cls.make_item_list(props)
    return items


class SimilarProps:
    '''
    Methods to get different types of recommendations for single property.
    Search for similar properties in small_prop_cache view, which is
    managed by playground with command rebuild_small_prop_cache.
    This view is optimized for search, its content is renewed hourly,
    for a small interval it might be inconsistent with prop_cache table.
    '''

    base_sql = '''
        select
            prop_id {select}
        from small_prop_cache where
            city_class_type = %(subj_city_class_type)s and
            status in %(statuses)s and
            not prop_id = any(%(exclude_prop_ids)s) and
            {invest_filter}
            {category_filter}
    '''
    dist_filter = '''
        ST_DWithin(
            Geography(ST_MakePoint(lon, lat)),
            Geography(ST_MakePoint(%(subj_lon)s, %(subj_lat)s)),
            10 * 1609.344)
    '''
    invest_filter = '''
        has_invest_view = true and
    '''
    photos_filter = '''
        has_photos = true
    '''
    same_building_id_filter = '''
        building_id=%(building_id)s
    '''
    same_building_addr_filter = '''
        line like %(subj_building_address)s
    '''
    price_filter = '''
        price between {min_price} and {max_price}
    '''
    bed_bath_filter = '''
        beds between %(beds_min)s and %(beds_max)s and
        baths between %(subj_baths)s - 1 and %(subj_baths)s + 1
    '''
    size_filter = '''
        building_size between %(size_min)s and %(size_max)s
    '''

    def __init__(self, cursor, prop_id, section, blur_invest=True, user=None):
        ''' `user` can be omitted if blur_invest = False
        '''
        cursor.execute('''
            select data, address, status, building_id
            from prop_cache where prop_id = %(prop_id)s
        ''', {'prop_id': prop_id})
        if not (prop := cursor.fetchone()):
            raise NoPropertyError

        self.cursor = cursor
        self.prop_id = prop_id
        self.section = section
        self.prop_class = 'rent' if section == 'rent' else 'sales'
        if blur_invest and self.section == 'invest':
            access_status = get_access_status(user)
            self.blur_invest = access_status != UserAccessStatus.PREMIUM
        else:
            self.blur_invest = False

        data = prop[0]
        addr = prop[1]
        status = prop[2]
        city = addr['city_url']
        baths = data['baths']
        self.lat = addr['lat']
        self.lon = addr['lon']
        self.beds = data['beds']
        self.price = data.get('close_price', 0) if status in SOLD_STATUSES else data['price']
        self.size = data['building_size'] or 0
        self.state_id = addr['state_code']
        self.zip_code = addr['zip']
        self.prop_type2 = data['prop_type2']
        self.building_id = prop[3]
        self.building_address = replace_synonyms(urlify(
            get_building_address(addr['line'], self.prop_type2)
        )) + '%'

        self.init_price_filters()
        self.price_diff = lambda price: abs(self.price - price)

        if self.prop_class == 'sales':
            self.active_statuses = 'for_sale',
            self.closed_statuses = 'closed', 'sold'
            if section == 'invest':
                good_deal_badge = '%good_deal_invest%'
            else:
                good_deal_badge = '%good_deal_buy%'
        else:
            self.active_statuses = 'for_rent',
            self.closed_statuses = 'closed', 'rented',
            good_deal_badge = '%good_deal_rent%'

        city_class_type = f'{city}-{self.prop_class}-{self.prop_type2}'
        self.base_sql_params = {
            'subj_lat': self.lat,
            'subj_lon': self.lon,
            'subj_zip': self.zip_code,
            'beds_min': self.beds - 1,
            'beds_max': self.beds + 1,
            'subj_baths': baths,
            'subj_price': self.price,
            'size_min': self.size - 500,
            'size_max': self.size + 500,
            'subj_city_class_type': city_class_type,
            'subj_building_address': self.building_address,
            'building_id': self.building_id,
            'good_deal_badge': good_deal_badge,
            'statuses': self.active_statuses,
            'exclude_prop_ids': [],
        }

    def init_price_filters(self):
        if self.prop_class == 'sales':
            delta = 50000
        else:
            delta = 500

        # price filters should be integer for SQL to use price index
        self.min_narrow_price = int(self.price - delta)
        self.max_narrow_price = int(self.price + delta)

        self.min_wide_price = int(self.price * .5)
        self.max_wide_price = int(self.price * 1.5)

        self.min_middle_price = int(max(self.price - delta, self.price * .8))
        self.max_middle_price = int(min(self.price + delta, self.price * 1.2))

        self.wide_price_filter = self.price_filter.format(**{
            'min_price': self.min_wide_price,
            'max_price': self.max_wide_price,
        })
        self.narrow_price_filter = self.price_filter.format(**{
            'min_price': self.min_narrow_price,
            'max_price': self.max_narrow_price,
        })
        self.middle_price_filter = self.price_filter.format(**{
            'min_price': self.min_middle_price,
            'max_price': self.max_middle_price,
        })

    def get_recommendations(self) -> dict:
        cats = {}
        exclude_ids = [self.prop_id]
        if self.prop_type2 == 'condo-apt':
            if ids := self.get_same_building(exclude_ids):
                cats[RecommendationsCats.same_building] = ids
                exclude_ids.extend(ids)
        ids = self.get_similar_nearby(exclude_ids)
        cats[RecommendationsCats.similar_nearby] = ids
        cats.update(self.get_common_similar(exclude_ids + ids))
        cats[RecommendationsCats.recently_closed] = self.get_just_closed()
        all_props = self.make_items(cats)
        if settings.INVEST_ENABLED:
            ordered_cats = self.order_cats_invest(cats, all_props)
        else:
            ordered_cats = self.order_cats_portal(cats, all_props)
        return ordered_cats

    def order_cats_invest(self, cats:dict, all_props:dict) -> list:
        '''
        Make an ordered list of categories as required on UI. max 5 categories returned
        Args:
            cats: mapping category name -> list of prop ids
            all_props: mapping prop_id -> prop_info
        '''
        ordered_cats = [None] * 7
        cat_priority = (
            RecommendationsCats.recently_closed,
            RecommendationsCats.same_building,
            RecommendationsCats.good_deals,
            RecommendationsCats.similar_nearby,
            RecommendationsCats.similar_price,
            RecommendationsCats.price_reduced,
            RecommendationsCats.just_listed,
        )

        position = 0
        for cat in cat_priority:
            ids = cats.get(cat) or []
            props = [all_props[_id] for _id in ids if _id in all_props]
            if len(props) >= 3:
                ordered_cats[position] = {
                    'title': cat,
                    'props': self.make_item_list(props),
                }
                position += 1
        return ordered_cats[:5]

    def order_cats_portal(self, cats:dict, all_props:dict) -> list:
        '''
        Make an ordered list of categories as required on UI. max 5 categories returned
        Args:
            cats: mapping category name -> list of prop ids
            all_props: mapping prop_id -> prop_info
        '''
        ordered_cats = [None] * 6
        cat_priority = (
            RecommendationsCats.same_building,
            RecommendationsCats.good_deals,
            RecommendationsCats.similar_nearby,
            RecommendationsCats.similar_price,
            RecommendationsCats.price_reduced,
            RecommendationsCats.just_listed,
        )

        position = 0
        for cat in cat_priority:
            ids = cats.get(cat) or []
            props = [all_props[_id] for _id in ids if _id in all_props]
            if len(props) >= 3:
                ordered_cats[position] = {
                    'title': cat,
                    'props': self.make_item_list(props),
                }
                position += 1
        # fixed position for just_closed
        if ids := cats.get(RecommendationsCats.recently_closed):
            props = [all_props.get(_id) for _id in ids]
            ordered_cats.insert(2, {
                'title': RecommendationsCats.recently_closed,
                'props': self.make_item_list(props),
            })
        return ordered_cats[:5]

    def get_full_info(self, prop_ids: list) -> list:
        '''returns list of prop info required to make cards'''
        if not prop_ids:
            return []
        self.cursor.execute(PROP_CARD_BY_ID_SQL, {'prop_ids': prop_ids})
        return self.cursor.fetchall()

    def make_items(self, cats: dict) -> dict:
        '''
        Returns prop_id -> prop card mapping for all props in recommendations.
        Properties with invalid statuses (e.g. "sold" property in similar
        nearby category) are discarded
        Args:
            cats: mapping category name -> list of prop ids
        '''
        prop_ids = sum([ids for x, ids in cats.items() if ids], [])
        props = self.get_full_info(prop_ids)

        # OT-2821 we need to verify that properties we request from prop_cache
        # are active, because small_prop_cache may have outdated statuses
        closed_prop_ids = cats.get(RecommendationsCats.recently_closed)
        return {
            x[0]: x for x in props
            if x[0] in closed_prop_ids or x[4] in self.active_statuses
            # x[0] is prop_id, x[4] is status
        }

    def make_item_list(self, props: list) -> list:
        '''returns list of recommendation cards'''
        return make_cards(self.section, props, self.blur_invest)

    def get_same_building(self, exclude_ids) -> list:
        '''only for condo: search properties with the same address'''
        if not self.building_address or (self.state_id == 'FL' and not self.building_id):
            return []

        category_filter = self.same_building_addr_filter
        if self.state_id == 'FL':
            category_filter = self.same_building_id_filter
        df = self.fetch_props(
            category_filter=category_filter,
            exclude_prop_ids=exclude_ids,
            select=', price',
            dtypes=[('price', int)],
        )
        return get_ids(df.sort_values(by='price', ascending=True, key=self.price_diff))

    def get_similar_nearby(self, exclude_ids) -> list:
        '''returns similar by beds/baths/build.size/price'''

        category_filter = f'''
            {self.middle_price_filter} and
            {self.bed_bath_filter} and
            {self.photos_filter} and
            {self.dist_filter}
            {'and ' + self.size_filter if self.size else ''}
        '''
        df = self.fetch_props(
            category_filter=category_filter,
            exclude_prop_ids=exclude_ids,
            select=', lat, lon',
            dtypes=[('lat', float), ('lon', float)],
        )
        df['approx_dist'] = (df.lat - self.lat) ** 2 + (df.lon - self.lon) ** 2
        return get_ids(df.sort_values(by='approx_dist', ascending=True))

    def get_common_similar(self, exclude_ids) -> dict:
        ''' returns good_deal, just_listed, similar_price, price_reduced.
            categories are combined because they use the same sql query '''
        res = {}

        category_filter = f'''
            {self.middle_price_filter} and
            {self.photos_filter} and
            {self.dist_filter}
        '''
        df = self.fetch_props(
            category_filter=category_filter,
            exclude_prop_ids=exclude_ids,
            select='''
                , lat
                , lon
                , zip
                , price
                , price_reduced
                , list_date
                , badges like %(good_deal_badge)s good_deal
            ''',
            dtypes=[
                ('lat', float),
                ('lon', float),
                ('zip', (str, 5)),
                ('price', int),
                ('price_reduced', bool),
                ('list_date', int),
                ('good_deal', bool),
            ],
        )
        if len(df) < 3:
            return res

        df['approx_dist'] = (df.lat - self.lat) ** 2 + (df.lon - self.lon) ** 2

        # good deal
        idx = (
            (df.good_deal == True) &
            (df.price >= self.min_middle_price) &
            (df.price <= self.max_middle_price)
        )
        if len(subframe := df[idx]) >= 3:
            res[RecommendationsCats.good_deals] = ids = get_ids(
                subframe.sort_values(by='approx_dist', ascending=True)
            )
            df.drop(index=ids, inplace=True)

        # similar price
        idx = (df.price >= self.min_narrow_price) & (df.price <= self.max_narrow_price)
        idx_zip = idx & (df.zip == self.zip_code)
        if len(subframe := df[idx_zip]) >= 3:
            # try search by zip
            res[RecommendationsCats.similar_price] = ids = get_ids(
                subframe.sort_values(by='price', ascending=True, key=self.price_diff)
            )
            df.drop(index=ids, inplace=True)
        elif len(subframe := df[idx]) >= 3:
            res[RecommendationsCats.similar_price] = ids = get_ids(
                subframe.sort_values(by='price', ascending=True, key=self.price_diff)
            )
            df.drop(index=ids, inplace=True)

        # price_reduced
        idx = (
            (df.price_reduced == True) &
            (df.price >= self.min_middle_price) &
            (df.price <= self.max_middle_price)
        )
        if len(subframe := df[idx]) >= 3:
            res[RecommendationsCats.price_reduced] = ids = get_ids(
                subframe.sort_values(by='approx_dist', ascending=True)
            )
            df.drop(index=ids, inplace=True)

        # just_listed -- look back 7 days ago
        idx = df.list_date > time.time() - 7 * 24 * 60 * 60
        idx_zip = idx & (df.zip == self.zip_code)
        if len(subframe := df[idx_zip]) >= 3:
            # try search by zip
            res[RecommendationsCats.just_listed] = get_ids(
                subframe.sort_values(by='list_date', ascending=False)
            )
        elif len(subframe := df[idx]) >= 3:
            res[RecommendationsCats.just_listed] = get_ids(
                df.sort_values(by='list_date', ascending=False)
            )

        return res

    def get_just_closed(self) -> list:
        if self.state_id == 'TX':
            return []
        # no photos filter because all closed properties in small_prop_cache have photos
        category_filter = f'''
            {self.wide_price_filter} and
            {self.bed_bath_filter} and
            {self.dist_filter}
            {'and ' + self.size_filter if self.size else ''}
        '''
        params = {
            'statuses': self.closed_statuses,
            'beds_min': self.beds,
            'beds_max': self.beds,
            'size_min': self.size - 300,
            'size_max': self.size + 300,
        }
        df = self.fetch_props(
            category_filter=category_filter,
            params=params,
            select=', close_date',
            dtypes=[('close_date', int)],
        )
        return get_ids(df.sort_values(by='close_date', ascending=False))

    def fetch_props(self, category_filter, params=None,
                    exclude_prop_ids=None, select=None, dtypes=None):
        ''' reads similar properties in materialized view and
            returns dataframe with necessary fields
        '''
        invest_filter = self.invest_filter if self.section == 'invest' else ''

        sql = self.base_sql.format(**{
            'select': select or '',
            'invest_filter': invest_filter,
            'category_filter': category_filter,
        })
        params = {
            **self.base_sql_params,
            **(params or {}),
            'exclude_prop_ids': exclude_prop_ids or [],
        }

        t1 = time.time()
        self.cursor.execute(sql, params)
        logger.debug(self.cursor.query.decode())

        t2 = time.time()
        ex_time = (t2 - t1)*1000
        res = self.cursor.fetchall()

        fetch_time = (time.time() - t2)*1000
        logger.debug(
            f'execute {ex_time:.2f}ms, fetch {fetch_time:.2f}ms ({len(res)} rows)')

        df = pd.DataFrame(
            np.array(res, [('prop_id', (str, 21))] + (dtypes or []))
        )
        return df.set_index('prop_id')
