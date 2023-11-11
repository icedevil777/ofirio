from api_property.enums import PropClass


PAID_ANALYTICS_GRAPHS = frozenset((
    'yearly_appreciation_rate',
    'year_built',
    'sales_speed_by_price_range',
    'pie_chart_by_close_price',
    'popular_amenities',
    'sold_homes_and_new_listings',
    'market_condition',
    'days_on_market',
    'median_sold_price_by_bathroom_count',
    'median_sold_price_by_bedroom_count',
    'months_of_supply',
    'pie_sale_speed',
    'asking_price_by_price_range',
    'asking_price_by_bedroom_count',
    'sales_speed_by_bedroom_count',
    'average_monthly_cap_rate',  # only for 'sale' prop class
))

ALLOWED_TO_REBATE_COUNTY = (
    'Los Angeles',
    'Miami-Dade',
    'Broward',
    'Palm Beach',
)

ALLOWED_TO_REBATE_ZIP = ()

ALLOWED_TO_REBATE_STATE = (
    'AZ',
    'AR',
    'CA',
    'CO',
    'CT',
    'DC',
    'DE',
    'FL',
    'GA',
    'HI',
    'ID',
    'IL',
    'IN',
    'KY',
    'ME',
    'MD',
    'MA',
    'MI',
    'MN',
    'MT',
    'NE',
    'NV',
    'NH',
    'NJ',
    'NM',
    'NY',
    'NC',
    'ND',
    'OH',
    'PA',
    'RI',
    'SC',
    'SD',
    'TX',
    'UT',
    'VT',
    'VA',
    'WA',
    'WV',
    'WI',
    'WY',
)


ACTIVE_STATUS_MAP = {
    PropClass.BUY: 'for_sale',
    PropClass.INVEST: 'for_sale',
    PropClass.RENT: 'for_rent',
}

LAST_SEARCH_AUTOCOMPLETE_HIERARCHY = {
    'zip': 'city',
    'city': 'county',
    'county': 'state',
    'state': None
}

MINIMUM_PROPERTY_COUNT = 4

SOLD_STATUSES = ('sold', 'closed')
