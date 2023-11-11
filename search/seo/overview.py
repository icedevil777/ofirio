import json

from django.db import connections
from ofirio_common.enums import PropEsIndex
from ofirio_common.states_constants import states_from_short


def _form_have(value):
    if value == 1:
        return 'has'
    return 'have'


def get_overview(data, total):
    """
    Construct overview text for Search in case of a city
    """
    agg_type = data['type']
    # currently we should show only city
    if agg_type != 'city':
        return None
    state_id = data['state_id'] or ''
    city = data['city'] or ''
    index = data['index']

    market_overview = None
    living_overview = None
    if agg_type == 'geo':
        return {'market_overview': market_overview, 'living_overview': living_overview}

    mapping = {
        'city': 'city_url',
        'state': 'state',
        'county': 'county_url',
        'zip': 'zip'
    }

    if agg_type in ('city', 'county', 'zip'):
        sql = f"""
         SELECT data FROM mls_analytics
            WHERE state_id=%(state_id)s AND
                  {mapping[agg_type]}=%(place_name)s AND
                  agg_type=%(agg_type)s AND
                  graph_name=%(graph_name)s;
        """
    else:
        sql = f"""
                 SELECT data FROM mls_analytics
                    WHERE state_id=%(state_id)s AND
                          agg_type=%(agg_type)s AND
                          graph_name=%(graph_name)s;
                """
    graph_name = 'seo_rent_text' if index == PropEsIndex.SEARCH_RENT else 'seo_sale_text'
    state_id = state_id.upper()
    conn = connections['prop_db']
    with conn.cursor() as cursor:
        cursor.execute(sql, {'state_id': state_id, 'place_name': city,
                             'graph_name': graph_name, 'agg_type': agg_type})
        result = cursor.fetchone()

    if result and result[0]:
        data = json.loads(result[0])
        for key, field in data.items():
            if isinstance(field, float) and int(field) == float(field):
                data[key] = int(field)

        data['total'] = total
        data['beds_have'] = _form_have(data['beds'])
        data['baths_have'] = _form_have(data['baths'])
        if agg_type == 'state':
            data['state_id'] = states_from_short[state_id]
            to_replace = "{place}, "
        else:
            to_replace = ''
        if index == PropEsIndex.SEARCH_RENT:
            market_overview = [
                '{place}, {state_id} is a {market} market, which means homes rent {market_means_first} at a {market_means_second} price. The rent prices are distributed from {first_quantile_close_price} (25th percentile) to {third_quantile_close_price} (75th percentile).'.replace(to_replace, '').format(**data),

                'The median rent in {place}, {state_id} is {median_price} and the average rent is {mean_price}. Rent has {desc_home_price} by {home_price_perc} over the last year from {home_price_back} in {month_name_now} {year_back} to {home_price_now} in {month_name_now} {year_now}. The number of homes listed for rent in {place}, {state_id} has {sold_desc} by {sold_perc} over the last year from {sold_back} in {month_name_now} {year_back} to {sold_now} homes in {month_name_now} {year_now}. As of {month_name_now} {year_now} demand levels, there is {mos} month of supply. Homes spend an average of {dom} days on the market before being rented.'.replace(to_replace, '').format(**data),

               'Homes in {place}, {state_id} have rented for {price_per_sqft_perc} {price_per_sqft_desc} per ft² than they did a year ago. As of {month_name_now} {year_now} the average rent price per square foot is {price_per_sqft_now}. The most popular home rent size in {place}, {state_id} is {size_range} ft² and the most popular rent price range is {price_range}, approximately {price_range_perc} of homes fall in this price range. The most popular bedroom count in {place}, {state_id} is {beds}, which {beds_have} an average rent price of {price_for_beds}. The most popular bathroom count in {place}, {state_id} is {baths}, which {baths_have} an average rent price of {price_for_baths}'.replace(to_replace, '').format(**data),
            ]

        else:
            market_overview = [
                'As of {month_name_now} {year_now} {place}, {state_id} is a {market} which means {market_means}. In {month_name_now} {year_now}, {pie_asking_price_sentence}. If purchasing a home there is {room_negotiate}.'.replace(to_replace, '').format(**data),

                'The median home price {desc_home_price} by {home_price_perc} from {home_price_back} in {month_name_now} {year_back} to {home_price_now} in {month_name_now} {year_now}. The number of homes sold in {place}, {state_id} has {sold_desc} by {sold_perc} over the last year from {sold_back} in {month_name_now} {year_back} to {sold_now} homes in {month_name_now} {year_now}.'.replace(to_replace, '').format(**data),

                'Homes in {place}, {state_id} have sold for {price_per_sqft_perc} {price_per_sqft_desc} per ft² than they did a year ago. As of {month_name_now} {year_now} the average price per square foot is {price_per_sqft_now}.'.replace(to_replace, '').format(**data),
            ]

        living_overview = []

    return {'market_overview': market_overview, 'living_overview': living_overview}
