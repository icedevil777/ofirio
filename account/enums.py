from django.db import models


class AccessType(models.TextChoices):
    """
    Unique name of a user action which can
    be used e.g. for restricting access
    """
    RENT_ANALYZER_SEARCH = 'rent_analyzer_search', 'Rent Analyzer Search'
    RENT_ANALYZER_REPORT = 'rent_analyzer_report', 'Rent Analyzer Report'
    PROPERTY_REPORT = 'property_report', 'Property Report'
    RENT_ESTIMATOR_ANALYTICS = 'rent_estimator_analytics', 'Rent Estimator Analytics'


class UserAccessStatus(models.TextChoices):
    ANON = 'anon', 'Anonymous'
    UNVERIFIED = 'unverified', 'Unverified'
    PREMIUM = 'premium', 'Premium'
