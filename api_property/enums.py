from django.db import models


class GraphsChoices(models.TextChoices):
    asking_price_by_bedroom_count = 'asking_price_by_bedroom_count'
    asking_price_by_price_range = 'asking_price_by_price_range'
    average_monthly_cap_rate = 'average_monthly_cap_rate'
    days_on_market = 'days_on_market'
    home_sales = 'home_sales'
    home_sales_year_over_year = 'home_sales_year_over_year'
    homes_sold_by_bathroom_count = 'homes_sold_by_bathroom_count'
    homes_sold_by_bedroom_count = 'homes_sold_by_bedroom_count'
    homes_sold_by_price_range = 'homes_sold_by_price_range'
    homes_sold_by_size = 'homes_sold_by_size'
    market_condition = 'market_condition'
    median_home_price = 'median_home_price'
    median_price_per_sq_ft = 'median_price_per_sq_ft'
    median_sale_price_vs_list_price = 'median_sale_price_vs_list_price'
    median_sale_to_listratio = 'median_sale_to_listratio'
    median_sold_price_by_bathroom_count = 'median_sold_price_by_bathroom_count'
    median_sold_price_by_bedroom_count = 'median_sold_price_by_bedroom_count'
    months_of_supply = 'months_of_supply'
    new_listings = 'new_listings'
    new_listings_year_over_year = 'new_listings_year_over_year'
    overview = 'overview'
    pie_chart_by_close_price = 'pie_chart_by_close_price'
    pie_sale_speed = 'pie_sale_speed'
    popular_amenities = 'popular_amenities'
    rent_trends_by_bedroom_count = 'rent_trends_by_bedroom_count'
    rented_price_by_bedroom_count = 'rented_price_by_bedroom_count'
    sales_speed_by_bedroom_count = 'sales_speed_by_bedroom_count'
    sales_speed_by_price_range = 'sales_speed_by_price_range'
    sold_homes_and_new_listings = 'sold_homes_and_new_listings'
    year_built = 'year_built'
    yearly_appreciation_rate = 'yearly_appreciation_rate'


class AggTypeChoices(models.TextChoices):
    zip = 'zip', 'Zip'
    city = 'city', 'City'
    county = 'county', 'County'
    state = 'state', 'State'


class PropClassChoices(models.TextChoices):
    sale = 'sale', 'Sale'
    rent = 'rent', 'Rent'
    # rent_estimator = 'rent-estimator', 'Rent Estimator'


class PropClassSimilarChoices(models.TextChoices):
    sale = 'sale', 'Sale'
    rent = 'rent', 'Rent'
    invest = 'invest', 'Invest'


class PopupTypeChoices(models.TextChoices):
    schedule_tour = 'scheduleTour', 'Schedule a Tour'
    ask_question = 'askQuestion', 'Ask a Question'
    check_availability = 'checkAvailability', 'Check Availability'
    rebate = 'rebate', 'Rebate'


class RecommendationsChoices(models.TextChoices):
    buy = 'buy'
    rent = 'rent'
    invest = 'invest'


class RecommendationsCats:
    same_building = 'same_building'
    good_deals = 'good_deals'
    similar_nearby = 'similar_nearby'
    recently_closed = 'recently_closed'
    similar_price = 'similar_price'
    just_listed = 'just_listed'
    price_reduced = 'price_reduced'


class PropertyNotificationTopic(models.TextChoices):
    SIMILAR = 'similar', 'Similar Property'
    GOOD_DEAL = 'good_deal', 'Good Deal'
    PROP_HISTORY = 'prop_history', 'Property History Update'
    FAVORITE_HISTORY = 'favorite_history', 'Favorite Property History Update'
    FAVORITE_SIMILAR = 'favorite_similar', 'Favorite Similar Property'


class PropClass(models.TextChoices):
    INVEST = 'invest'
    BUY = 'buy'
    RENT = 'rent'
