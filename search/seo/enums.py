from django.db import models


class SeoCategory(models.TextChoices):
    BEDROOMS = 'cat_bedrooms'
    AMENITIES = 'cat_amenities'
    LIFESTYLE = 'cat_lifestyle'
    PROP_TYPE = 'cat_prop_type'
    AFFORDABILITY = 'cat_affordability'
    POPULAR_ZIPS = 'cat_popular_zips'
    POPULAR_CITIES = 'cat_popular_cities'
    POPULAR_COUNTIES = 'cat_popular_counties'
    POPULAR_STATES = 'cat_popular_states'
    NEARBY_ZIPS = 'cat_nearby_zips'
    NEARBY_CITIES = 'cat_nearby_cities'
    NEARBY_COUNTIES = 'cat_nearby_counties'
    BUILDINGS = 'cat_buildings'
