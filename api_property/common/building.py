import json
import re
import string
from datetime import datetime
from statistics import median

import pandas as pd
from django.core.serializers.json import DjangoJSONEncoder
from ofirio_common.address_util import get_unit, build_address, urlify
from ofirio_common.helpers import url_to_cdn

from api_property.common.card import ACTIVE_STATUSES, card_badges
from api_property.common.common import is_off_market_status, format_listing_office
from api_property.common.rebates import get_rebate_for_view1
from api_property.constants import SOLD_STATUSES
from api_property.views.property import FormatDict
from common.utils import get_is_test_condition, calculate_distance

EMPTY_VALUES_LIST = ['None', 'Other', '', ' ', None]
PROP_BEDS_MAP = {
    'studio': (0,),
    '1beds': (1,),
    '2beds': (2,),
    '3beds': (3,),
    '4beds': tuple(range(4, 25))
}

SQL_PROP_CARD = '''
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
        c.close_date,
        mc.disclosure_text,
        mc.logo_url,
        case c.prop_class
           when 'rent'
               then mp.last_rent_load_ts
               else mp.last_sales_load_ts
           end last_checked,
        c.update_date
    from prop_cache c
    join prop_photos ph on c.real_prop_id = ph.prop_id
    JOIN parsing_mls_mlsconfig mc on c.data ->> 'mls_type' = mc.originating_system
    JOIN parsing_mls_mlsprovider mp on mc.mls_provider_id = mp.id
'''

PROP_CARD_IN_IDS_SQL = SQL_PROP_CARD + f'''
    where c.real_prop_id in %(prop_ids)s
          {get_is_test_condition(table_alias='c')}
'''

SQL_BUILDING = """
    SELECT 
        b.building_id,
        b.address,
        b.lat,
        b.lon,
        b.active_count,
        b.sold_count,
        b.median_price,
        b.data,
        b.photos,
        b.walkscore,
        b.schools,
        b.summary,
        b.poi,
        s.building_id is not null canonicalized
    FROM buildings b
    LEFT JOIN sitemap_buildings s using(building_id)
    WHERE b.building_id = %(building_id)s
"""


SQL_NEARBY_BUILDINGS = """
    SELECT 
        building_id, 
        photos ->> 0 photo,
        address,
        active_count,
        price_min,
        price_max,
        lat,
        lon
    FROM buildings
    JOIN sitemap_buildings using(building_id)
    WHERE ST_DWithin(
        Geography(ST_MakePoint(lon, lat)),
        Geography(ST_MakePoint(%(lon)s, %(lat)s)),
        5 * 1609.344
    ) 
    AND (median_price >= median_price - 100000 AND median_price <= median_price + 100000)
    AND active_count > 5
    AND building_id != %(building_id)s
    ORDER BY abs(lat-%(lat)s) + abs(lon-%(lon)s)
    LIMIT 8
"""


def get_building(conn, building_id: str):
    with conn.cursor() as cursor:
        cursor.execute(SQL_BUILDING, {'building_id': building_id})
        res = cursor.fetchone()

        if not res:
            return []
    return res


def get_building_props(conn, prop_ids: list):
    with conn.cursor() as cursor:
        cursor.execute(PROP_CARD_IN_IDS_SQL, {'prop_ids': tuple(prop_ids)})
        res = cursor.fetchall()
        if not res:
            return None
    return res


def get_buildings_nearby(conn, building):
    if building:
        building_id = building[0]
        lat, lon = building[2], building[3]
        with conn.cursor() as cursor:
            cursor.execute(SQL_NEARBY_BUILDINGS, {'building_id': building_id, 'lat': lat, 'lon': lon})
            return cursor.fetchall()
    return []


def make_pois_desc(raw_pois):
    park = [x for x in filter(lambda x: x['type'] in ('park', 'garden'), raw_pois)]
    supermarket = [x for x in filter(lambda x: x['type'] in ('supermarket', 'department_store'), raw_pois)]
    return {
        'park': park[0]['list'] if park else [],
        'supermarket': supermarket[0]['list'] if supermarket else [],
    }


def school_desc(data):
    if not data or not data.get('schools'):
        return None

    data = data.get('schools')
    data = pd.DataFrame(data)[['name', 'rating', 'level-codes']].to_dict('records')
    return data


def faq(params):
    desc = []
    quest = ''
    answer = ''
    units_for_sale = params.get('active_count')
    building_name = params['building_name']
    building_addr = params['building_addr']
    city = params['city'].title()
    adr_zip = params['zip_adr']
    avg_price = params['avg_price']
    avg_price_in_zip = params.get('zip_condo_avg_close_price_last_year')
    avg_price_in_zip_1b = params.get('zip_condo_avg_close_price_last_year_1beds')
    avg_price_1b = params.get('avg_price_1b')
    avg_price_in_zip_2b = params.get('zip_condo_avg_close_price_last_year_2beds')
    avg_price_2b = params.get('avg_price_2b')
    avg_price_in_zip_3b = params.get('zip_condo_avg_close_price_last_year_3beds')
    avg_price_3b = params.get('avg_price_3b')
    if units_for_sale > 0:
        beds_for_sale = params['beds_for_sale']

        if beds_for_sale:
            s = '' if units_for_sale == 1 else 's'
            beds_for_sale = {beds: count for beds, count in beds_for_sale.items() if count > 0}
            answer += f'Of the {units_for_sale} unit{s} that are available in {building_name}, '
            list_beds = list(beds_for_sale.keys())
            for count_bedroom in range(len(list_beds)):
                number = beds_for_sale[list_beds[count_bedroom]]
                s = '' if number == 1 else 's'
                answer += f'{number} {list_beds[count_bedroom]} unit{s}'
                if len(list_beds) == 1:
                    answer += '.'
                    break
                elif count_bedroom == len(list_beds) - 2:
                    answer += ' and '
                elif count_bedroom == len(list_beds) - 1:
                    answer += '.'
                else:
                    answer += ', '
            quest = f'How many units are available in {building_name}?'
            desc.append({"question": quest,
                         "answer": answer})
    quest = ''
    answer = ''

    if avg_price and avg_price_in_zip:
        price_perc = round((avg_price / avg_price_in_zip) - 1, 2)
        if price_perc == 0:
            perc_desc = 'the same as'
        elif price_perc > 0:
            perc_desc = 'higher than'
        elif price_perc < 0:
            perc_desc = 'lower than'
            price_perc *= -1
        price_perc = int(100 * price_perc)
        answer = f'The average price of a unit in {building_name} is {perc_desc} the average in {adr_zip}'
        if price_perc == 0:
            answer += '.'
        else:
            answer += f' by {price_perc}% percent.'

        if avg_price_in_zip_1b and avg_price_1b:
            answer += f' On average, one bedroom units in the building are priced at ${round(avg_price_1b):,} as compared ${round(avg_price_in_zip_1b):,} in {adr_zip}.'
        if avg_price_in_zip_2b and avg_price_2b:
            answer += f' Two bedroom units in the building are priced at ${round(avg_price_2b):,} as compared ${round(avg_price_in_zip_2b):,} in {adr_zip}.'
        if avg_price_in_zip_3b and avg_price_3b:
            answer += f' Three bedroom units in the building are priced at ${round(avg_price_3b):,} as compared ${round(avg_price_in_zip_3b):,} in {adr_zip}.'

        quest = f'Are units in {building_addr} expensive compared to apartments in {adr_zip}?'

        desc.append({"question": quest,
                     "answer": answer})

    amenities = amenities if (amenities := params['amenities']) else []
    if len(amenities) > 0:
        quest = f'What amenities does {building_name} have?'
        answer = f'{building_name} has great amenities such as {", ".join(amenities)}.'
        notable_amenities = params['notable_amenities']
        if len(notable_amenities) > 0:
            answer += f' This building has some especially notable amenities. In {city} this building has'
            list_amen = list(notable_amenities.keys())
            for count_amen in range(len(list_amen)):
                answer += f' {list_amen[count_amen].title()} is only present in {round(notable_amenities[list_amen[count_amen]] * 100)}% of other buildings.'
        desc.append({"question": quest,
                     "answer": answer})
    quest = ''
    answer = ''

    if schools := params.get('schools'):
        quest = f'What school districts {building_name} located in?'
        answer = 'This building is located in the following school districts:'

        for i in range(len(schools)):
            codes = schools[i]['level-codes']

            codes = ','.join([x for x in codes.split(',') if x != 'p'])
            school_name = schools[i]["name"]
            rating = schools[i]["rating"]
            code_desc = ''
            if len(codes) > 2:
                code_desc = 'elementary-high'
            elif len(codes) == 1:
                if codes == 'e':
                    code_desc = 'elementary'
                elif codes == 'm':
                    code_desc = 'middle'
                elif codes == 'h':
                    code_desc = 'high'
            elif len(codes) == 2:
                if codes == 'e-m':
                    code_desc = 'elementary-middle'
                elif codes == 'e-h':
                    code_desc = 'elementary-high'
                elif codes == 'm-h':
                    code_desc = 'middle-high'

            answer += f' {school_name} is an {code_desc} school'
            if rating:
                answer += f' has a rating of {rating}.'
            else:
                answer += '.'
        desc.append({"question": quest,
                     "answer": answer})

    min_hoa_fees = params['min_hoa_fees']
    quest = f'Does {building_name} have an HOA?'
    if min_hoa_fees is None or min_hoa_fees == 0:
        answer = f'No, this {building_name} does not have an HOA.'
    else:
        answer = f'Yes {building_name} has a home owners association. The HOA fee is from ${min_hoa_fees:,} per month.'
    desc.append({"question": quest,
                 "answer": answer})

    quest = ''
    answer = ''

    if poi := params.get('pois'):
        quest = f'What parks are close to {building_addr}?'
        if poi.get('park'):
            parks = poi.get('park')
            s = '' if len(parks) == 1 else 's'
            answer = f'There are {len(parks)} park{s} in a 3 mile radius from {building_name}. '
            for park in range(len(parks)):
                name_park = parks[park]['name'] or 'park'
                dist = round(parks[park]['distance'], 2)
                answer += f'{name_park} is {dist}  miles away'
                if park == len(parks) - 2:
                    answer += ' and '
                elif park == len(parks) - 1:
                    answer += '.'
                else:
                    answer += ', '
        else:
            answer = f'There are no parks within 3 miles of {building_name}.'
        desc.append({"question": quest,
                     "answer": answer})
    quest = ''
    answer = ''

    if walkscore := params.get('walkscore'):
        if walkscore.get('walk'):
            score = walkscore.get('walk').get('score')
            answer = f'The walk score is {score}.'
            if score > 89:
                score_desc = "a walker's paradise, daily errands do not require a car"
            elif score > 69 and score <= 89:
                score_desc = "very walkable and most errands can be accomplished on foot"
            elif score > 49 and score <= 69:
                score_desc = "somewhat walkable, some errands can be accomplished on foot"
            elif score >= 25 and score <= 49:
                score_desc = "car-dependent, most errands require a car"
            else:
                score_desc = walkscore.get('walk').get('description').lower()
            answer += f' It is {score_desc}.'
        if walkscore.get('transit'):
            score = walkscore.get('transit').get('score')
            answer += f' The transit score for {building_name} is {score}.'
            score_desc = walkscore.get('transit').get('description').lower()
            answer += f' It is {score_desc}.'
        if walkscore.get('bikeable'):
            score = walkscore.get('bikeable').get('score')
            answer += f' The bike score is {score}.'
            score_desc = walkscore.get('bikeable').get('description').lower()
            answer += f' It is {score_desc}.'
        if len(answer) > 0:
            quest = f'What is the walk score for {building_name}?'
        desc.append({"question": quest,
                     "answer": answer})

    quest = f'What city is {building_name} in?'
    answer = f'{building_name} is located in {city}.'
    desc.append({"question": quest,
                 "answer": answer})

    quest = f'What units are available in {building_name}?'
    units = params['list_units']
    units = ', '.join([str(x) for x in units])
    answer = f'The following units are available for sale in {building_name}: {units}'
    desc.append({"question": quest, "answer": answer})

    return desc


def create_description(params):
    building_name = params['building_name']
    building_addr = params['building_addr']
    year_built = params['year_built']
    stories_total = params['stories_total']
    total_units = params['total_units']
    units_for_sale = params['active_count']
    description = f'<p><span><b>About building:</b></span> {building_name} was built in {year_built} and has '
    if stories_total:
        s = '' if stories_total == '1' else 's'
        description += f'total of {stories_total} floor{s} and '

    description += f'{total_units} units'

    if units_for_sale > 0:
        s = '' if units_for_sale == 1 else 's'
        description += f', out of which {units_for_sale} unit{s} are available for sale. '
    else:
        description += '. '

    sold_last_year = params['sold_last_year']
    description += f'A total of {sold_last_year} appartments were sold in {building_name} over the last year. '
    if sold_last_year > 1:
        days_on_market = params['days_on_market']
        if days_on_market < 36:
            dom_desc = 'quickly'
        elif days_on_market >= 36 and days_on_market <= 74:
            dom_desc = 'moderately'
        else:
            dom_desc = 'slowly'
        description += f'During this time these units were on the market for an average of {days_on_market} days and have sold {dom_desc}. '

    if units_for_sale > 0:
        beds_for_sale = params['beds_for_sale']
        description += 'This building has '
        list_beds = list(beds_for_sale.keys())
        for count_bedroom in range(len(list_beds)):
            number = beds_for_sale[list_beds[count_bedroom]]
            s = '' if number == 1 else 's'
            description += f'{number} {list_beds[count_bedroom]} unit{s}'
            if len(list_beds) == 1:
                description += '. '
                break
            elif count_bedroom == len(list_beds) - 2:
                description += ' and '
            elif count_bedroom == len(list_beds) - 1:
                description += '. '
            else:
                description += ', '

    if units_for_sale > 0:
        low_price = params['low_price']
        high_price = params['high_price']
        if low_price and high_price and low_price > 0 and high_price > 0:
            s = '' if units_for_sale == 1 else 's'
            description += f'</p><p><span><b>Market trends:</b></span> {building_addr} currently has {units_for_sale} unit{s} available for sale ranging from ${low_price:,} to ${high_price:,}. '
        max_cashback = params['max_cashback']
        if max_cashback and max_cashback > 0:
            description += f'Keep in mind that when you purchase one of these units with Ofirio you can get up to ${max_cashback:,} cash back. '

    avg_price = params['avg_price']
    city_price = params.get('city_condo_avg_close_price_last_year')
    city = params['city'].title()
    state = params['state_id'].upper()
    perc_city_price = round((avg_price / city_price - 1) * 100) if city_price else 0
    if perc_city_price > 0:
        city_price_desc = 'higher than'
    if perc_city_price < 0:
        perc_city_price *= -1
        city_price_desc = 'lower than'
    if perc_city_price == 0:
        city_price_desc = 'the same as'
        perc_city_price = ''
    else:
        perc_city_price = str(perc_city_price) + '%'
    description += f'The average price of a unit in this building is {perc_city_price} {city_price_desc} the average price of housing in {city}, {state}. '
    description += '</p><p><span><b>Location:</b></span> '

    if view := params.get('view'):
        result = re.search(r'Water|River|Lake|Ocean', view)
        if result:
            description += 'The building has a great view overlooking the water. '

    pois = None
    parks = None
    supermarket = None
    if pois := params.get('pois'):
        supermarket = pois.get('supermarket')
        parks = pois.get('park')
        if parks:
            if parks[0]['distance'] <= 0.5:
                name_park = parks[0]['name']
                if name_park is None or name_park == '':
                    name_park = 'park'
                park_dist = parks[0]['distance']
                description += f'Those who love nature will appreciate that the building is only {park_dist} miles away from the {name_park}. '

    if params['multi_building']:
        description += f'{building_name} is located in a developed area with many multi-story buildings in a 0.5 radius. '

    if notable_amenities := params.get('notable_amenities'):
        if len(notable_amenities) > 0:
            not_am = ', '.join(notable_amenities.keys())
            description += f'{building_name} has notable ammenities such as: {not_am}. '

    if school := params.get('schools'):
        if len(school) == 1:
            school_name = school[0]['name']
            rating = school[0]['rating']
            description += f'There is one school nearby, {school_name}'
            if rating:
                description += f', which has a rating of {rating} out of 10. '
            else:
                description += '. '
        else:
            how_many_schools = 'two' if len(school) == 2 else 'several'
            school_name_1 = school[0]['name']
            rating_1 = school[0]['rating']
            school_name_2 = school[1]['name']
            rating_2 = school[1]['rating']
            description += f'There are {how_many_schools} schools in a 3 mile radius. {school_name_1} '
            if rating_1 is not None:
                description += f'has a rating of {rating_1} '
            description += f'and {school_name_2}'
            if rating_2 is not None:
                description += f' has a rating of {rating_2}'
            description += '. '
        description += 'Select the tab “Schools” to see more information about other schools. '
    description += '</p><p><span><b>Points of interest:</b></span> '

    if walkable_score := params.get('walkscore'):
        if walkable_score := walkable_score.get('walk', {}).get('score', 0):
            if walkable_score >= 70:
                description += f'The building is located close to many points of interest for residents and has a walkability score of {walkable_score}. '

    if parks:
        if len(parks) == 1:
            name_park = parks[0]['name']
            if name_park is None or name_park == '':
                name_park = ''
            description += f'The {name_park} park is located just under 3 miles away. '
        elif len(parks) == 2:
            name_park_1 = parks[0]['name']
            park_dist_1 = parks[0]['distance']
            if name_park_1 is not None or name_park_1 == '':
                name_park_1 = ''
            name_park_2 = parks[1]['name']
            park_dist_2 = parks[1]['distance']
            if name_park_2 is not None or name_park_2 == '':
                name_park_2 = ''
            description += f'There are two parks in the vicinity of {building_name} - {name_park_1} which is {park_dist_1} miles away'
            description += f' and {name_park_1} which is {park_dist_2} miles away. '
        elif len(parks) > 2:
            description += 'There are several parks in the area, just under 3 miles away: '
            list_park = [x['name'] for x in parks]
            list_park = [x for x in list_park if x != None]
            for i in range(len(list_park)):
                if i == len(list_park) - 2:
                    description += f'{list_park[i]} and '
                elif i == len(list_park) - 1:
                    description += f'{list_park[i]}. '
                else:
                    description += f'{list_park[i]}, '

    if supermarket:
        if len(supermarket) == 1:
            name_supermarket = supermarket[0]['name']
            supermarket_dist = supermarket[0]['distance']
            if name_supermarket is None or name_supermarket == '':
                description += f'The closest supermarket is located {supermarket_dist} miles away. '
            else:
                description += f'The closest supermarket, {name_supermarket} is located {supermarket_dist} miles away. '

        if len(supermarket) > 1:
            description += f'There are {len(supermarket)} supermarkets in a 3 mile radius.'

    return description + '</p>'


def make_prop_card_for_building(prop_id, list_date, close_date, update_date, status, photo, address, badges, price_per_sqft, data, listing_office):
    price = data.get('close_price', 0) if status in SOLD_STATUSES else data['price']
    return {
        'unit': get_unit(address.get('line')),
        'full_address': address.get('full_address'),
        'prop_id': prop_id,
        'price': price,
        'list_date': list_date,
        'close_date': close_date,
        'status': status,
        'photo': photo,
        'beds': data.get('beds'),
        'baths': data.get('baths'),
        'badges': badges,
        'rebate': get_rebate_for_view1(address['state_code'], price, is_off_market_status(status)),
        'mortgage': data.get('estimated_mortgage'),
        'building_size': data.get('building_size'),
        'price_per_sqft': price_per_sqft,
        'update_date': update_date,
        'listing_office': format_listing_office(listing_office, status),
    }


def mls_disclosure(prop):
    if prop[4] == 'off_market':
        return {}

    json_date_to_text = json.dumps(prop[12], cls=DjangoJSONEncoder)
    disclosure_vars = {
        'current_date_year': datetime.now().year,
        'listings_last_updated': f'$%{json.loads(json_date_to_text)}$%',
        'site_owner_office': 'Ofirio New York LLC',
        'site_owner_email': 'help@ofirio.com',
    }
    mapping = FormatDict(**disclosure_vars)
    formatter = string.Formatter()
    text = formatter.vformat((prop[10] or ''), (), mapping)
    return {
        'mls_logo_url': prop[11],
        'mls_last_checked': prop[12],
        'mls_disclosure_text': text,
    }


def group_walkscore(data):
    if not data:
        return None

    if 'walkscore' in data:
        data['walk'] = {'score': data.get('walkscore'), 'description': data.get('description')}

    mapping = {'walk': 'walk', 'transit': 'transit', 'bike': 'bikeable'}
    walkscores = dict()
    for i in mapping.keys():
        if i in data:
            walkscores[mapping[i]] = {
                **{k: v for k, v in data[i].items() if k in ('score', 'description')}
            }
    walkscores['ws_link'] = data['ws_link']
    return walkscores


def group_schools(data):
    '''
    input data is sorted by distance.
    returns groups: elementary, middle, high, private (each max 5) + disclamer
    '''
    if not data or not data.get('schools'):
        return None

    data = data.get('schools')
    for item in data:
        # replace level 'PK,KG,1,2,3,4,5' -> 'PK-5'
        item['level'] = re.sub(r',.*,', '-', item['level'] or '')
        # remove repeating disclamer
        item.pop('rating-description', None)

    elementary = [x for x in data if 'e' in x['level-codes'] and x['type'] != 'private']
    middle = [x for x in data if 'm' in x['level-codes'] and x['type'] != 'private']
    high = [x for x in data if 'h' in x['level-codes'] and x['type'] != 'private']
    private = [x for x in data if x['type'] == 'private']
    return {
        'elementary': elementary[:5],
        'middle': middle[:5],
        'high': high[:5],
        'private': private[:5],
    }


def make_building(building, props: list):
    building_address = {
        'zip': building[1]['zip'],
        'city': building[1]['city'].title(),
        'county': building[1]['county'].title(),
        'state_id': building[1]['state_id'].upper(),
        'line': building[1]['line']
    }

    active_cards = [make_unit_card(prop, 'active') for prop in props if prop[4] in ACTIVE_STATUSES]
    sold_cards = [make_unit_card(prop, 'sold') for prop in props if prop[4] in SOLD_STATUSES]
    other_cards = [make_unit_card(prop, 'other') for prop in props if prop[4] not in (ACTIVE_STATUSES + SOLD_STATUSES)]

    prop_building_sizes = [building_size for i in props if (building_size := i[1].get('building_size')) and building_size > 0]
    prop_beds = [i[1].get('beds') for i in props]
    prop_cashbacks = [x['rebate'] for x in active_cards + sold_cards + other_cards if x['rebate']]
    act_cashbacks = [x['rebate'] for x in active_cards if x['rebate']]
    prices_per_sqft = [price_per_sqft for i in props if (price_per_sqft := i[1].get('price_per_sqft')) and price_per_sqft > 0]
    prop_update_dates = [i[13] for i in props]

    params = building[11]['params']
    params.update({
        'walkscore': group_walkscore(building[9]),
        'schools':  school_desc(building[10]),
        'pois': make_pois_desc(building[-2]),
        'total_units': len(props),
        'active_count': len(active_cards),
        'max_cashback': round(max(act_cashbacks)) if act_cashbacks else None,
        'building_addr': building_address['line'],
    })

    mls_disclosures = []
    for i in props:
        if (mls := mls_disclosure(i)) and mls.get('mls_logo_url') not in [i.get('mls_logo_url') for i in mls_disclosures]:
            mls_disclosures.append(mls)

    walkscore = group_walkscore(building[9])
    schools = group_schools(building[10])

    return {
        'building_id': building[0],
        'canonicalized': building[-1],
        'summary': {
            'building_name': building[11]['building_name'],
            'active_count': len(active_cards),
            'sold_count': len(sold_cards),
            'year_built': building[11]['year_built'],
            'price_min': building[11]['params']['low_price'],
            'price_max': building[11]['params']['high_price'],
            'building_size_min': min(prop_building_sizes) if prop_building_sizes else None,
            'building_size_max': max(prop_building_sizes) if prop_building_sizes else None,
            'beds_min': min(prop_beds) if prop_beds else None,
            'beds_max': max(prop_beds) if prop_beds else None,
            'price_per_sqft': round(median(prices_per_sqft)) if prices_per_sqft else None,
            'days_on_market': building[11]['params']['days_on_market'],
            'cashback': round(median(prop_cashbacks)) if prop_cashbacks else None,
        },
        'address': {
            **building_address,
            **{'full_address': build_address(
                building_address['line'],
                building_address['city'],
                building_address['state_id'],
                building_address['zip']
            )},
            'lat': building[2],
            'lon': building[3]
        },
        'overview': {
            i: building[11]['overview'].get(i)
            for i in ('actual_year', 'apr_rate', 'median_cl_price', 'price_per_sqft', 'count_close', 'count_available')
        },
        'description': create_description(params),
        'faq': faq(params),
        'photos': url_to_cdn(building[8] or []),
        'features': {
            'Building Features': {
                'Building Overview': {
                    i: building[11]['features']['Building Features']['Building Overview'].get(i)
                    for i in ('Building Name', 'Year Built', 'Total Stories', 'Zoning', 'Views')
                },
                **{
                    i: feature
                    for i in ('Amenities', 'Exterior Features', 'Pool', 'Association Fees')
                    if (feature := building[11]['features']['Building Features'].get(i))
                }
            },
            'Most Popular Unit Amenities': building[11]['features'].get('Most Popular Unit Amenities', [])
        },
        'disclosures': {'items': mls_disclosures, 'update_date': max(prop_update_dates)},
        'active': {
            key: [
                x for x in filter(lambda x: x['beds'] in value, active_cards)
            ] for key, value in PROP_BEDS_MAP.items()
        },
        'sold': {
            key: [
                x for x in filter(lambda x: x['beds'] in value, sold_cards)
            ] for key, value in PROP_BEDS_MAP.items()
        },
        'other_statuses': {
            key: [
                x for x in filter(lambda x: x['beds'] in value, other_cards)
            ] for key, value in PROP_BEDS_MAP.items()
        },
        'walkscore': walkscore,
        'schools': schools,
        'chart': building[11]['chart'],
        'poi': building[-2],
    }


def make_unit_card(prop, status):
    return make_prop_card_for_building(
        prop_id=prop[0],
        list_date=prop[7],
        close_date=prop[9],
        update_date=prop[13],
        status=prop[4],
        photo=url_to_cdn(prop[2] if prop[2] else prop[8]),
        address=prop[3],
        badges=card_badges('buy', prop[5].split(','), prop[7], prop[4]),
        price_per_sqft=(
            round(price_per_sqft)
            if (price_per_sqft := prop[1].get('price_per_sqft')) and not is_off_market_status(prop[4])
            else None
        ),
        data=prop[1],
        listing_office=prop[6].get('listing_office'),
    )


def make_building_cards(buildings: list):
    cards = []
    for i in buildings:
        cards.append({
            'building_id': i[0],
            'photo': url_to_cdn(i[1]),
            'address': {
                'line': i[2]['line']
            },
            'active_count': i[3],
            'price_min': i[4],
            'price_max': i[5],
        })
    return cards
