import re
import json
import os
import logging
from datetime import datetime, timedelta
from functools import lru_cache

import geopandas as gpd
import pandas as pd
import shapely.wkt
from django.conf import settings
from django.db import connections
from ofirio_common.enums import EsIndex, PropClass2
from ofirio_common.helpers import get_elastic_search
from ofirio_common.states_constants import states_from_short
from shapely.geometry import Point
from elasticsearch.exceptions import NotFoundError as ESNotFoundError

from account.enums import UserAccessStatus
from account.utils import get_access_status
from api_property.enums import AggTypeChoices, PropClass
from api_property.constants import PAID_ANALYTICS_GRAPHS, ALLOWED_TO_REBATE_ZIP,\
    ALLOWED_TO_REBATE_STATE
from api_property.common import stubs
from common.utils import get_is_test_condition, get_pg_connection


logger = logging.getLogger(__name__)


def format_listing_office(value, status):
    if not value or status == 'off_market':
        return None
    return re.sub(r'\s+', ' ', value).strip()


def get_cursor_decode_jsonb(conn):
    if conn:
        cursor = conn.cursor()
        # pg connection decodes json by itself
        decode_jsonb = lambda x: x
    else:
        cursor = connections['prop_db'].cursor()
        decode_jsonb = json.loads
    return cursor, decode_jsonb


def getProp(prop_id, conn=None):
    """Get property by prop_id from prop_cache"""
    cursor, decode_jsonb = get_cursor_decode_jsonb(conn)

    res = get_raw_prop(prop_id, cursor)
    if not res:
        # will return 404 Not Found
        return False

    data = decode_jsonb(res[7])
    features = regroup_features(decode_jsonb(res[10]), res[2] == 'off_market')
    badges = res[3].split(',') if res[3] else []
    public_records = decode_jsonb(res[14]) or []
    data = {
        'prop_id': res[0],
        'state_id': res[1],
        'status': res[2],
        'badges': badges,
        'list_date': res[4],
        'update_date': res[5],
        'params': decode_jsonb(res[6]),
        'data': data,
        'address': decode_jsonb(res[8]),
        'photos': decode_jsonb(res[9]) if res[9] else [],
        'features': features,
        'schools': decode_jsonb(res[11]) if res[11] else [],
        'tax_history': decode_jsonb(res[12]),
        'prop_history': decode_jsonb(res[13]),
        'public_records': public_records,
        'last_price_change': decode_jsonb(res[15]) if res[15] else {},
        'prop_class': res[16],
        'disclosure_text': res[17],
        'logo_url': res[18],
        'last_checked': res[19],
        'similar_str': res[20],
        'street_view': res[21],
        'building_id': res[22]
    }
    return data


def get_raw_prop(prop_id, cursor):
    SQL = f"""
       SELECT  c.prop_id,
               c.state_id,
               c.status,
               c.badges,
               c.list_date,
               c.update_date,
               c.params,
               c.data,
               c.address,
               pp.photos,
               c.features,
               c.schools,
               c.tax_history,
               c.prop_history,
               c.public_records,
               c.last_price_change,
               c.prop_class,
               mc.disclosure_text,
               mc.logo_url,
               case c.prop_class
                   when 'rent'
                       then mp.last_rent_load_ts
                       else mp.last_sales_load_ts
                   end last_checked,
               c.similar_str,
               pp.street_view,
               c.building_id
       FROM prop_cache c
       LEFT JOIN parsing_mls_mlsconfig mc on c.data ->> 'mls_type' = mc.originating_system
       LEFT JOIN parsing_mls_mlsprovider mp on mc.mls_provider_id = mp.id 
       LEFT JOIN prop_photos pp on c.real_prop_id = pp.prop_id
       WHERE c.prop_id=%(prop_id)s
             {get_is_test_condition(table_alias='c')}
    """

    cursor.execute(SQL, {'prop_id': prop_id})
    return cursor.fetchone()

def get_estimated_mortgage(cash_only, est_mortgage):
    if cash_only is False:
        return est_mortgage
    return None


def get_fields_prop_cache(prop_id, fields: tuple, conn=None):
    """Get prop_cache fields by prop_id """
    cursor, decode_jsonb = get_cursor_decode_jsonb(conn)
    SQL = f"""
            SELECT {','.join(fields)} from prop_cache
            WHERE prop_id=%(prop_id)s
    """
    cursor.execute(SQL, {'prop_id': prop_id})
    res = cursor.fetchone()
    if not res:
        return None
    res_dict = {field: res[idx] for idx, field in enumerate(fields)}
    for key, value in res_dict.items():
        if key in ('params', 'data', 'address', 'photos', 'features', 'schools',
                   'tax_history', 'prop_history', 'public_records', 'last_price_change'):
            res_dict[key] = decode_jsonb(value if value else [])
    return res_dict


def get_fields_postprocessed(prop_id, prop_class, fields: tuple, conn=None):
    """Get postprocessed_* fields by prop_id """

    cursor, decode_jsonb = get_cursor_decode_jsonb(conn)
    table = 'postprocessed_rent' if prop_class == 'rent' else 'postprocessed_sales'
    SQL = f"""
            SELECT {','.join(fields)} from {table}
            WHERE prop_id=%(prop_id)s
    """
    cursor.execute(SQL, {'prop_id': prop_id})
    res = cursor.fetchone()
    if not res:
        return None
    res_dict = {field: res[idx] for idx, field in enumerate(fields)}
    for key, value in res_dict.items():
        if key in ('features', 'fin_model_details', 'params', 'comparables'):
            res_dict[key] = decode_jsonb(value if value else [])
    return res_dict


def prop_has_invest_view(prop):
    ''' should hide invest view for off-market properties '''
    if settings.INVEST_ENABLED:
        return prop['status'] != 'off_market' and prop['params'].get('has_invest_view', False)
    return False


# will return dict or string
def convert_feature_list(rows):
    result = {}
    if not rows:
        return result
    separator = ': '
    # find features in form 'key: value'
    features = [r for r in rows if separator in r]
    # find features in form 'value' and join them to 1 string
    items = ', '.join(r for r in rows if separator not in r)
    if len(features) > 0:
        # at least 1 item found in form 'key: value', we should convert rows to common dict
        for row in features:
            key, value = row.split(separator, 1)
            result[key] = value
        # add items if there are any
        if items:
            if 'Other' in result:
                result['Other'] += ', ' + items
            else:
                result['Other'] = items
    elif items:
        # all features are just values
        result['Features'] = items

    return result


def regroup_features(features, off_market):
    result = {}
    for cat, subcats in features.items():
        for subcat, rows in subcats.items():
            features[cat][subcat] = convert_feature_list(rows)
    if rows := features.get('Features', {}).pop('Building and Construction', {}):
        features['Building and Construction'] = rows
    cats = ('Listing',
            'Building and Construction',
            'Exterior',
            'Interior',
            'Features',
            'Community',
            )
    # empty categories should be removed
    for c in cats:
        if value := features.pop(c, None):
            result[c] = value
    if rows := features.pop('', {}).pop('Legal and finance', {}):
        result['Legal and finance'] = rows
    if not off_market and \
            not result.get('Listing', {}).get('Listing Information', {}).get('Originating MLS') \
            and (src := result.get('Listing', {}).get('Listing Information', {}).get('Source')):
        result['Listing']['Listing Information']['Originating MLS'] = src

    if off_market:
        result['Listing'].pop('Listing Information', None)

    return result


# GET only prop data for multiple props (max=20)
# prop_id=>data dict
def getPropsData(prop_ids):
    cursor = connections['prop_db'].cursor()

    SQL = f"""
               SELECT  prop_id,
                       data
               FROM prop_cache 
               WHERE prop_id in %(prop_ids)s
               {get_is_test_condition()}
       """

    cursor.execute(SQL, {
        'prop_ids': tuple([str(item) for item in prop_ids]),
    })
    res = cursor.fetchall()

    data = {}
    for pos in res:
        data[pos[0]] = json.loads(pos[1])

    return data


# GET prop status, return prop_id=>prop_status dict
def get_status_params_for_favorites(prop_ids):
    if not prop_ids:
        return {}

    cursor = connections['prop_db'].cursor()

    SQL = f"""
               SELECT  prop_id,
                       status, 
                       params
               FROM prop_cache 
               WHERE prop_id in %(prop_ids)s
               {get_is_test_condition()}
       """

    cursor.execute(SQL, {
        'prop_ids': tuple(prop_ids),
    })
    res = cursor.fetchall()

    data = {}
    for pos in res:
        data[pos[0]] = {'status': pos[1], 'params': json.loads(pos[2])}

    return data


def getPropAddressStr(prop):
    address = ''
    if line := prop['address']['line']:
        address += line + ', '
    if city := prop['address']['city']:
        address += city + ', '
    address += prop['address']['state_code'] + ', '
    address += prop['address']['zip']

    return address


def get_proforma(model, financing_years):
    proforma_years = [1, 2, 3, 5, 10, 20, 30]
    if financing_years == 15:
        proforma_years = [1, 2, 3, 5, 10, 15]
    if financing_years == 25:
        proforma_years = [1, 2, 3, 5, 10, 25]

    propforma_frame = model.getProforma(proforma_years)
    proforma = json.loads(propforma_frame.to_json(orient='columns'))
    return proforma


def validate_graphs(graphs):
    ''' validate that all graph values are not null except popular_amenities'''
    return all(v for k, v in graphs.items() if k != 'popular_amenities')


def get_analytics_data_for_api_property(initial_agg_type, prop_class, prop_type2, graph_names,
                                        city=None, zip_code=None, county=None, state_id=None,
                                        user=None, prop_id=None, params=None):
    agg_types = [x for x, y in AggTypeChoices.choices]
    idx = agg_types.index(initial_agg_type)
    # iterate aggregation types from current to widest (zip -> city -> county)
    for i in range(idx, len(agg_types)):
        agg_type = agg_types[i]
        data = get_analytics_data(
            agg_type=agg_type, prop_class=prop_class, prop_type2=prop_type2,
            graph_names=graph_names,
            state_id=state_id, county=county, city=city, zip_code=zip_code,
            user=user, prop_id=prop_id, params=params)
        if validate_graphs(data):
            return {'graphs': data, 'agg_type': agg_type}
        # if any graphs are null, we should try wider aggregation
    # error 404: not enough data:
    return {}


def get_analytics_data(agg_type, prop_class, prop_type2, graph_names,
                       city=None, zip_code=None, county=None, state_id=None,
                       user=None, prop_id=None, params=None):
    if user and (set(graph_names) & PAID_ANALYTICS_GRAPHS) \
            and not can_show_property(user, prop_id, params):
        if prop_class == 'sale':
            res = [(name, getattr(stubs, name)[0]) for name in graph_names]
        else:
            res = [(name, getattr(stubs, name)[1]) for name in graph_names]
    else:
        cursor = connections['prop_db'].cursor()

        SQL = """
                   SELECT graph_name, data
                   FROM mls_analytics WHERE
                   prop_class=%(prop_class)s
                   and graph_name in %(graph_names)s
                   and agg_type=%(agg_type)s
                   and state_id=%(state_id)s
                   and prop_type2=%(prop_type2)s"""

        if agg_type == 'county':
            SQL += ' and county=%(county)s '
        elif agg_type == 'city':
            SQL += ' and county=%(county)s '
            SQL += ' and city=%(city)s '
        elif agg_type == 'zip':
            SQL += ' and zip=%(zip_code)s '

        cursor.execute(SQL, {
            'state_id': state_id,
            'county': county,
            'city': city,
            'zip_code': zip_code,
            'agg_type': agg_type,
            'prop_class': prop_class,
            'prop_type2': prop_type2,
            'graph_names': graph_names
        })

        res = cursor.fetchall()

    # init all requested graphs with null
    graphs = {graph_name: None for graph_name in graph_names}
    for graph_name, data in res:
        if (not data or data == 'null'):
            continue
        else:
            graph = json.loads(data)
            if graph.get('datasets', None) == []:
                continue
            if graph.get('datasets', [{}])[0].get('data') == []:
                continue
            update_analytics_meta(graph, agg_type=agg_type,
                                  prop_type2=prop_type2, city=city,
                                  zip_code=zip_code, county=county,
                                  state_id=state_id)
            graphs[graph_name] = graph
    return graphs


def update_analytics_meta(data, agg_type=None, prop_type2=None, city=None,
                          zip_code=None, county=None, state_id=None):
    new_meta = {'_details': dict(
        _agg_type=agg_type,
        _prop_type2=prop_type2,
        _city=city,
        _zip_code=zip_code,
        _county=county,
        _state_id=state_id,
        _state_name=states_from_short.get(state_id),
    )}
    if data.get('meta'):
        data['meta'].update(new_meta)
    else:
        data['meta'] = new_meta


def elastic_is_available_by_id(prop_id):
    try:
        elastic = get_elastic_search()
        # raises exception if not found:
        return elastic.get(EsIndex.SEARCH_INVEST, prop_id, _source_includes='is_high_cap_rate')
    except ESNotFoundError:
        return None


def can_show_property(user, prop_id, params=None):
    ''' free users cannot view properties with high cap rate '''
    access_status = get_access_status(user)
    if access_status == UserAccessStatus.PREMIUM:
        return True
    return not get_is_hidden(prop_id, params)


def get_is_hidden(prop_id, params=None):
    if params:
        return params.get('is_high_cap_rate') or False
    sql = "select params -> 'is_high_cap_rate' from prop_cache where prop_id = %(prop_id)s"
    cursor = get_pg_connection().cursor()
    cursor.execute(sql, {'prop_id': prop_id})
    is_hidden = cursor.fetchone()
    return is_hidden[0] if is_hidden else False


def get_us_blocks(st_code):
    filename = settings.BASE_DIR / 'data/blocks/processed_data' / (st_code + '_blocks.csv')
    if not os.path.isfile(filename):
        return None
    blocks_frame = pd.read_csv(filename, converters={'block_id': str, 'county_fips': str})
    blocks_frame.set_index('block_id', inplace=True)
    blocks_frame = gpd.GeoDataFrame(blocks_frame)
    blocks_frame.geometry = blocks_frame.geometry.apply(lambda x: shapely.wkt.loads(x))
    return blocks_frame


def func_point(row):
    lon = row.address_lon
    lat = row.address_lat
    if lat and lon:
        return Point(lon, lat)


def func_point2(lat, lon):
    if lat and lon:
        return Point(lon, lat)


def block_number(point_address, frame_blocks, county_fips=None):
    if frame_blocks is None:
        return None
    if point_address:
        for row in frame_blocks[frame_blocks.county_fips == county_fips].itertuples()\
                if county_fips else frame_blocks.itertuples():
            if point_address.within(row.geometry) is True:
                return row.Index  # block_id


def clean_data_for_api_property(data, prop_class, cant_show_price=False, off_market=False,
                                cash_only=False):
    ''' can be used only for /api/property '''
    unused_fields_common = ('hoa_fees', 'lot_size', 'mls_type', 'prop_type2', 'monthly_tax',
                            'cleaned_amenities', 'monthly_insurance',)
    if prop_class == 'rent':
        [data.pop(field, None) for field in unused_fields_common]
        remove_price = True
    else:
        [data.pop(field, None) for field in
         unused_fields_common + ('median', 'days_on_market', 'cap_rate')]
        remove_price = False
    clean_sensitive_data(data, cant_show_price, off_market, remove_price=remove_price)
    if est := data.get('estimated_mortgage'):
        data['estimated_mortgage'] = get_estimated_mortgage(cash_only, est_mortgage=est)
    return data


def clean_sensitive_data(data, cant_show_price=False, off_market=False, remove_price=True):
    fields = set()
    if cant_show_price:
        fields |= {
            "predicted_rent", "price_per_sqft", "estimated_mortgage",
            "diff_price", "diff_price_per_sqft", 'apr_rate',
        }
    if off_market:
        fields |= {
            'lot_size', 'price_per_sqft', 'description', 'apr_rate',
            'diff_price', 'diff_price_per_sqft', 'estimated_mortgage', 'diff_size',
        }
    if fields:
        if remove_price:
            fields.add('price')
        for key in fields:
            if data.get(key) is not None:
                data[key] = None


def clean_premium_data(item):
    for key in ('cap_rate', 'est_rent', 'total_return', 'cash_on_cash'):
        item[key] = None


def clean_badges(badges, list_date):
    if badges and 'new' in badges and list_date < datetime.now() - timedelta(days=7):
        badges.remove('new')
        return badges
    return badges


def is_off_market_status(status):
    return status == 'off_market'



def cant_show_price_fields(status, state):
    if state in ('Texas', 'TX') and status in ('closed', 'rented', 'sold'):
        return True
    return False


def is_suitable_prop_class_returned_from_db(prop_class2, prop_class, has_invest_view):
    """prop_class2 is rent/sales and prop_class buy/invest/rent
        If user choose prop_class buy and ask for property that is rent we will get error 
        so this function check cases like that"""
    if not prop_class2 or not prop_class:
        return False
    if prop_class2 not in (PropClass2.SALES, PropClass2.RENT) \
            or prop_class not in (PropClass.BUY, PropClass.INVEST, PropClass.RENT):
        return False
    if prop_class == PropClass.INVEST and not has_invest_view:
        return False
    if prop_class2 == PropClass2.SALES and prop_class in (PropClass.BUY, PropClass.INVEST):
        return True
    if prop_class2 == PropClass.RENT and prop_class == PropClass2.RENT:
        return True
    return False


def check_right_sighs_to_sheets(attrs):
    for key, value in attrs.items():
        if isinstance(value, str) and value.startswith('='):
            attrs[key] = f'|{value}'
    return attrs
