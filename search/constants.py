from ofirio_common.enums import AutocompletePropCategory, PropEsIndex, PropClass2

from search.enums import InsightType, FrontendCleanedPropType, PropType3, Amenities


MAP_ITEMS_LIMIT = 200
PAID_ONLY_FILTERS = 'cap_rate_min', 'predicted_rent_min', 'cash_on_cash_min'
PAID_ONLY_SORTS = 'predicted_rent', 'cap_rate', 'cash_on_cash', 'total_return'


# amenities that can be found in cleaned_amenities field,
# sometimes it's better than keyword search.
# see get_cleaned_amenities in parsing_mls/property_handlers/base.py (playground)
# for actual list
CLEANED_AMENITIES = {
    Amenities.WITH_BASEMENT,
    Amenities.GARAGE,
    Amenities.WITH_POOL,
    Amenities.LAUNDRY,
    Amenities.WATERFRONT,
    Amenities.FURNISHED,
    Amenities.CONDITIONING
}


# this is mapping for prop type label incoming from fromtend to /api/search
PROP_TYPE_FRONTEND_MAPPING = {
    FrontendCleanedPropType.CONDO_APT: PropType3.CONDO_APT,  # buy/invest section
    FrontendCleanedPropType.APARTMENTS: PropType3.CONDO_APT,  # rent section
    FrontendCleanedPropType.HOUSE_DUPLEX: PropType3.HOUSE_DUPLEX,
    FrontendCleanedPropType.TOWNHOUSE: PropType3.TOWNHOUSE,
}


# this is mapping for prop type returned by backend in seo categories
PROP_TYPE_FRONTEND_REVERSE_MAPPING = {
    PropClass2.RENT: {
        None: FrontendCleanedPropType.HOMES,
        PropType3.CONDO_APT: FrontendCleanedPropType.APARTMENTS,
        PropType3.HOUSE_DUPLEX: FrontendCleanedPropType.HOUSE_DUPLEX,
        PropType3.TOWNHOUSE: FrontendCleanedPropType.TOWNHOUSE,
    },
    PropClass2.SALES: {
        None: FrontendCleanedPropType.HOMES,
        PropType3.CONDO_APT: FrontendCleanedPropType.CONDO_APT,
        PropType3.HOUSE_DUPLEX: FrontendCleanedPropType.HOUSE_DUPLEX,
        PropType3.TOWNHOUSE: FrontendCleanedPropType.TOWNHOUSE,
    },
}


# These insights need a base value of 95 percentile for specified field
PERCENTILE_95_BASED_INSIGHTS = {
    InsightType.ASKING_PRICE.value: 'price',
    InsightType.EST_RENT.value: 'predicted_rent',
    InsightType.CAP_RATE.value: 'cap_rate',
    InsightType.SQFT.value: 'building_size',
    InsightType.YEAR_BUILT.value: 'year_built',
    InsightType.PRICE_PER_SQFT.value: 'price_per_sqft',
    InsightType.EST_RENT_DISTRIBUTION.value: 'predicted_rent',
    InsightType.ASKING_PRICE_DISTRIBUTION.value: 'price',
}


INT_MEDIAN_AVG_RANGE_INSIGHTS = (
    InsightType.ASKING_PRICE.value,
    InsightType.EST_RENT.value,
    InsightType.SQFT.value,
    InsightType.YEAR_BUILT.value,
)


INDEX_INSIGHTS = {
    PropEsIndex.SEARCH_INVEST: {
        InsightType.ASKING_PRICE,
        InsightType.EST_RENT,
        InsightType.EST_RENT_DISTRIBUTION,
        InsightType.CAP_RATE,
        InsightType.SQFT,
        InsightType.PRICE_PER_SQFT,
        InsightType.YEAR_BUILT,
        InsightType.MEDIAN_CAP_RATE_BY_BUILDING_TYPE,
        InsightType.COUNT_AND_MEDIAN_RENT_BY_BUILDING_TYPE,
        InsightType.COUNT_BY_BEDS,
        InsightType.COUNT_BY_BATHS,
        InsightType.CAP_RATE_AND_RENT_BY_BEDS,
        InsightType.CAP_RATE_AND_RENT_BY_BATHS,
    },
    PropEsIndex.SEARCH_BUY: {
        InsightType.ASKING_PRICE,
        InsightType.ASKING_PRICE_DISTRIBUTION,
        InsightType.PRICE_PER_SQFT,
        InsightType.COUNT_BY_BEDS,
        InsightType.COUNT_BY_BATHS,
        InsightType.SQFT,
        InsightType.YEAR_BUILT,
        InsightType.COUNT_AND_PRICE_BY_BUILDING_TYPE,
        InsightType.COUNT_AND_PRICE_BY_BEDS,
    },
    PropEsIndex.SEARCH_RENT: {
        InsightType.ASKING_PRICE,
        InsightType.ASKING_PRICE_DISTRIBUTION,
        InsightType.PRICE_PER_SQFT,
        InsightType.COUNT_BY_BEDS,
        InsightType.COUNT_BY_BATHS,
        InsightType.YEAR_BUILT,
        InsightType.COUNT_AND_PRICE_BY_BEDS,
        InsightType.COUNT_AND_PRICE_BY_BUILDING_TYPE,
        InsightType.SQFT,
    },
}

AUTOCOMPLETE_TYPE_TO_ID_FIELD_MAPPING = {
    'state': 'state_id',
    'county': 'county',
    'city': 'city',
    'zip': 'zip',
    'address': 'address',
}

AUTOCOMPLETE_PROP_CATEGORY_TO_COUNT_FIELD = {
    AutocompletePropCategory.BUY_PROP: 'buy_count',
    AutocompletePropCategory.INVEST_PROP: 'invest_count',
    AutocompletePropCategory.RENT_PROP: 'rent_count',
}
