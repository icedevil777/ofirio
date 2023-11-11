from ofirio_common.enums import PropEsIndex, PropClass2
from search.seo.enums import SeoCategory
from search.enums import FrontendCleanedPropType


ES_INDEX_TO_SRP_SECTION = {
    PropEsIndex.SEARCH_INVEST: 'invest',
    PropEsIndex.SEARCH_RENT: 'rent',
    PropEsIndex.SEARCH_BUY: 'buy',
}


SRP_SECTION_TO_PROP_CLASS = {
    'invest': PropClass2.SALES,
    'buy': PropClass2.SALES,
    'rent': PropClass2.RENT,
}


SECTION_TO_STATUS = {
    'invest': 'sale',
    'buy': 'sale',
    'rent': 'rent',
}


# frontend to frontend mapping
FRONTEND_PROP_TYPE_TO_LONG = {
    PropClass2.RENT: {
        None: 'Homes',
        FrontendCleanedPropType.APARTMENTS: 'Apartments',
        FrontendCleanedPropType.HOUSE_DUPLEX: 'Houses',
        FrontendCleanedPropType.TOWNHOUSE: 'Townhomes',
    },
    PropClass2.SALES: {
        None: 'Homes',
        FrontendCleanedPropType.CONDO_APT: 'Condos',
        FrontendCleanedPropType.HOUSE_DUPLEX: 'Single Family Homes',
        FrontendCleanedPropType.TOWNHOUSE: 'Townhomes',
    },
}


# facets as they come from frontend
FACET_BEFORE_PROP_TYPE = (
    'studio',
    'x-bedrooms',  # x can be any number
    'cheap',
    'no-hoa',
    'loft',
    'luxury',
    'short-term',
    'waterfront',
    '55-community',
    'senior-housing',
    'gated',
    'furnished',
    'pet-friendly',
    'student-housing',
    'corporate',
    'utilities',
    'military',
    'short-sale',
)


FACET_AFTER_PROP_TYPE = (
    'gym',
    'balcony',
    'parking',
    'with-pool',
    'with-basement',
    'garage',
    'laundry',
    'fireplace',
    'conditioning',
    'balcony',
    'backyard',
)


FACET_TO_FRONTEND = {
    'gym': 'With Gym',
    'loft': 'Loft',
    'cheap': 'Cheap',
    'gated': 'Gated',
    'garage': 'With Garage & Parking',
    'luxury': 'Luxury',
    'no-hoa': 'No HOA',
    'balcony': 'With Balcony',
    'laundry': 'With Laundry',
    'parking': 'With Parking',
    'backyard': 'With Back Yard',
    'military': 'Military Housing',
    'corporate': 'Corporate Housing',
    'fireplace': 'With Fireplace',
    'furnished': 'Furnished',
    'utilities': 'Utilities',
    'with-pool': 'With Pool',
    'short-sale': 'Short Sale',
    'short-term': 'Short Term',
    'waterfront': 'Waterfront',
    '55-community': '55+ communities',
    'conditioning': 'With Air Conditioning',
    'pet-friendly': 'Pet Friendly',
    'with-basement': 'With Basement',
    'senior-housing': 'Senior Housing',
    'student-housing': 'Student Housing',
}


# keys are indexable facets as stored in seo_links table
FACET_TO_SEO_CAT = {
    '0-beds': SeoCategory.BEDROOMS,
    '1-beds': SeoCategory.BEDROOMS,
    '2-beds': SeoCategory.BEDROOMS,
    '3-beds': SeoCategory.BEDROOMS,
    '4-beds': SeoCategory.BEDROOMS,
    '5-beds': SeoCategory.BEDROOMS,
    '6-beds': SeoCategory.BEDROOMS,

    'cheap': SeoCategory.AFFORDABILITY,
    'no-hoa': SeoCategory.AFFORDABILITY,
    'under-500': SeoCategory.AFFORDABILITY,
    'under-600': SeoCategory.AFFORDABILITY,
    'under-700': SeoCategory.AFFORDABILITY,
    'under-800': SeoCategory.AFFORDABILITY,
    'under-900': SeoCategory.AFFORDABILITY,
    'under-1000': SeoCategory.AFFORDABILITY,
    'under-1500': SeoCategory.AFFORDABILITY,
    'under-100000': SeoCategory.AFFORDABILITY,
    'under-200000': SeoCategory.AFFORDABILITY,
    'under-300000': SeoCategory.AFFORDABILITY,

    'loft': SeoCategory.LIFESTYLE,
    'luxury': SeoCategory.LIFESTYLE,
    'short-term': SeoCategory.LIFESTYLE,
    '55-community': SeoCategory.LIFESTYLE,
    'senior-housing': SeoCategory.LIFESTYLE,

    'gym': SeoCategory.AMENITIES,
    'gated': SeoCategory.AMENITIES,
    'balcony': SeoCategory.AMENITIES,
    'parking': SeoCategory.AMENITIES,
    'with-pool': SeoCategory.AMENITIES,
    'furnished': SeoCategory.AMENITIES,
    'waterfront': SeoCategory.AMENITIES,
    'pet-friendly': SeoCategory.AMENITIES,
    'with-basement': SeoCategory.AMENITIES,
}
