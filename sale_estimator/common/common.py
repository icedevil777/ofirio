import pandas as pd
from django.conf import settings


def get_beds_from_prop(beds):
    if beds > 5:
        return 5
    return beds


def get_baths_from_prop(baths):
    if baths > 4:
        return 4.0
    return float(baths)


def get_baths_from_choices(baths):
    if baths == '4+':
        return 4.0
    return float(baths)


def get_beds_from_choices(beds):
    if beds == '5+':
        return 5
    return int(beds)
