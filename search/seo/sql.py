import pandas as pd
from django.conf import settings
from ofirio_common.address_util import build_address, unurlify

from search.enums import PropType3
from search.seo.enums import SeoCategory

default_place_condition = '''
    state_id = %(state_id)s and
    county = %(county)s and
    city = %(city)s and
    zip = %(zip_code)s
'''


def get_seo_table():
    if settings.IS_PRODUCTION:
        return 'seo_links'
    else:
        # this table contains srp which include test properties
        return 'seo_links_test'


def get_facets(cursor, params, all_prop_types=False, near_me=False, max_prop_count=None) -> list:
    seo_table = get_seo_table()
    sql = f'''
        select prop_type, facet
        from {seo_table}
        where section = %(section)s and
              {default_place_condition} and
              facet <> ''
    '''
    if max_prop_count:
        params['max_prop_count'] = max_prop_count
        sql += ' and prop_count < %(max_prop_count)s '
    if all_prop_types:
        # actually we want non-empty prop types
        sql += " and prop_type <> '' "
    else:
        sql += " and prop_type = %(prop_type)s "
    if near_me:
        sql += " and near_me_indexable "
    else:
        sql += " and indexable "
    cursor.execute(sql, params)
    #print(cursor.query.decode('utf-8'))
    return [(x['prop_type'], x['facet']) for x in cursor.fetchall()]


def get_top_buildings(cursor, srp_type, params, search_facet):
    if srp_type not in ('city', 'zip'):
        return None

    srp = params['state_id'] + '/'
    if srp_type == 'city':
        place_condition = 'state_id = %(state_id)s and city = %(city)s'
        srp += params['city']
    else:
        place_condition = 'zip = %(zip_code)s'
        srp += params['zip_code']

    if search_facet:
        srp += f'/{search_facet}'

    sql = f'''
        select building_id, address
        from buildings
        join sitemap_buildings using(building_id)
        where 
            seo_srp = %(srp)s
        order by active_count desc
    '''
    cursor.execute(sql, {**params, **{'srp': srp.lower()}})
    res = cursor.fetchall()
    if not res:
        return None

    top = []
    for row in res:
        addr = row['address']
        address = addr['line']
        top.append({'building_id': row['building_id'], 'address': address})
    return top


def get_nearby_and_popular(cursor, nearby_and_popular, params):
    seo_table = get_seo_table()
    sql = f'''
        select {','.join(nearby_and_popular)}, state_id
        from {seo_table}
        where section = %(section)s and
              {default_place_condition} and
              prop_type = %(prop_type)s and
              facet = ''
    '''
    cursor.execute(sql, params)
    res = cursor.fetchone()
    if not res:
        return {}
    for item in res:
        if res[item]:
            if item in (SeoCategory.POPULAR_ZIPS, SeoCategory.NEARBY_ZIPS):
                res[item] = [{'state': res['state_id'], 'zip': zip_code} for zip_code in res[item].split(',')]
            if item in (SeoCategory.POPULAR_CITIES, SeoCategory.NEARBY_CITIES):
                res[item] = [{'state': res['state_id'], 'city': city} for city in res[item].split(',')]
            if item in (SeoCategory.POPULAR_COUNTIES, SeoCategory.NEARBY_COUNTIES):
                res[item] = [{'state': res['state_id'], 'county': county} for county in res[item].split(',')]
    res.pop('state_id')
    return res or {}


def get_prop_types(cursor, params, srp_type, max_prop_count=None) -> list:
    seo_table = get_seo_table()
    sql = f'''
        select prop_type
        from {seo_table}
        where section = %(section)s and
              {default_place_condition} and
              prop_type <> '' and
              facet = ''
    '''
    if max_prop_count:
        params['max_prop_count'] = max_prop_count
        sql += ' and prop_count < %(max_prop_count)s '
    cursor.execute(sql, params)
    #print(cursor.query.decode('utf-8'))
    res = [x['prop_type'] for x in cursor.fetchall()]
    if params['section'] in ('buy', 'invest') and srp_type == 'zip' and PropType3.TOWNHOUSE in res:
        res.remove(PropType3.TOWNHOUSE)
    return res


def has_invest(cursor, params) -> list:
    seo_table = get_seo_table()
    sql = f'''
        select 0
        from {seo_table}
        where section = 'invest' and
              {default_place_condition}
    '''
    cursor.execute(sql, params)
    #print(cursor.query.decode('utf-8'))
    return len(cursor.fetchall())


def get_max_prop_count(cursor, params) -> float:
    """
    find root page of place without facets and prop types
    and return 90% of prop_count (OT-2856)
    """
    seo_table = get_seo_table()
    sql = f"""
        select prop_count
        from {seo_table}
        where
            section = %(section)s and
            {default_place_condition} and
            prop_type = '' and
            facet = ''
    """
    cursor.execute(sql, params)
    if res := cursor.fetchone():
        return res['prop_count'] * .9
    return .0


def get_sitemap_links(cursor, section, state_id, place_type) -> list:
    """
    returns records from seo_links that correspond to indexable links
    within section, state_id and place_type (cities, zips, counties
    or single state)
    """
    seo_table = get_seo_table()
    place_condition = ' and '.join((
        "county != ''" if place_type == 'county' else "county = ''",
        "city != ''" if place_type == 'city' else "city = ''",
        "zip != ''" if place_type == 'zip' else "zip = ''",
    ))
    sql = f"""
        select prop_type, state_id, facet, city, county, zip, prop_count
        from {seo_table}
        where
            section = %(section)s and
            state_id = %(state_id)s and
            {place_condition} and
            indexable
    """
    cursor.execute(sql, {'state_id': state_id, 'section': section})
    if not (res := cursor.fetchall()):
        return []

    # OT-2864 we need to remove pages with very similar content
    df = pd.DataFrame(res)
    df['include'] = True

    if place_type == 'state':
        idx = df.state_id == state_id
        set_excluded_links(df, idx)
    else:
        for place in df[place_type].unique():
            idx = df[place_type] == place
            set_excluded_links(df, idx)

    return df[df.include == True].to_dict(orient='records')


def set_excluded_links(df, idx):
    """
    mark links that have prop_count > 90% of main page
    (passed as idx) as excluded
    """
    root_idx = idx & (df.facet == '') & (df.prop_type == '')
    max_props = df[root_idx].prop_count.values[0] * .9
    df.loc[idx & (df.prop_count > max_props), 'include'] = False
    df.loc[root_idx, 'include'] = True
