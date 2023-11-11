from django.db import models


class InsightType(models.TextChoices):
    ASKING_PRICE = 'asking_price', 'Asking Price'
    EST_RENT = 'est_rent', 'Estimated Rent'
    EST_RENT_DISTRIBUTION = 'est_rent_distribution', 'Estimated Rent Distribution'
    ASKING_PRICE_DISTRIBUTION = 'asking_price_distribution', 'Asking Price Distribution'
    CAP_RATE = 'cap_rate', 'Cap Rate'
    SQFT = 'sqft', 'Square Footage'
    PRICE_PER_SQFT = 'price_per_sqft', 'Price per Square Footage'
    YEAR_BUILT = 'year_built', 'Year Built'
    MEDIAN_CAP_RATE_BY_BUILDING_TYPE = 'median_cap_rate_by_building_type', 'Median Cap Rate'
    COUNT_AND_MEDIAN_RENT_BY_BUILDING_TYPE = 'count_and_median_rent_by_building_type', 'Active Listings'
    COUNT_AND_PRICE_BY_BUILDING_TYPE = 'count_and_price_by_building_type', 'Active Listings'
    COUNT_BY_BEDS = 'count_by_beds', 'Active Listings by Bedroom Count'
    COUNT_BY_BATHS = 'count_by_baths', 'Active Listings by Bathroom Count'
    CAP_RATE_AND_RENT_BY_BEDS = 'cap_rate_and_rent_by_beds', 'Cap Rate & Monthly Rent by Bedroom Count'
    CAP_RATE_AND_RENT_BY_BATHS = 'cap_rate_and_rent_by_baths', 'Cap Rate & Monthly Rent by Bathroom Count'
    COUNT_AND_PRICE_BY_BEDS = 'count_and_price_by_beds', 'Market Snapshot'


class PropertyType2(models.TextChoices):
    """
    For Insights
    """
    ANY = 'any', 'Any'
    CONDO_APT = 'condo-apt', 'Condo'
    HOUSE_DUPLEX = 'house-duplex', 'Duplex'


class PropType3(models.TextChoices):
    """
    For filters. These are all possible values of
    'cleaned_prop_type' field in database/elasticsearch
    """
    CONDO_APT = 'condo-apt', 'Condo'
    HOUSE_DUPLEX = 'house-duplex', 'Single Family'
    TOWNHOUSE = 'townhouse', 'Townhome'


class PropType3Rent(models.TextChoices):
    """
    Same as PropType3, but with special names for Rent
    """
    CONDO_APT = 'condo-apt', 'Apartments'
    HOUSE_DUPLEX = 'house-duplex', 'Houses'
    TOWNHOUSE = 'townhouse', 'Townhomes'


class FrontendCleanedPropType(models.TextChoices):
    """
    For filters
    """
    CONDO_APT = 'condos'  # for sale
    APARTMENTS = 'apartments'  # for rent
    HOUSE_DUPLEX = 'houses'
    TOWNHOUSE = 'townhomes'
    HOMES = 'homes'  # means 'any prop type'


class Amenities(models.TextChoices):
    """
    For filters
    """
    WITH_BASEMENT = 'with-basement'
    GARAGE = 'garage'
    WITH_POOL = 'with-pool'
    GYM = 'gym'
    LAUNDRY = 'laundry'
    FIREPLACE = 'fireplace'
    CONDITIONING = 'conditioning'
    WATERFRONT = 'waterfront'
    BALCONY = 'balcony'
    BACKYARD = 'backyard'
    FURNISHED = 'furnished'
