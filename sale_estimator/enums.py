from django.db import models


class PropertyType3(models.TextChoices):
    CONDO_APT           = 'condo-apt',    'Cond & Apts'
    HOUSE_DUPLEX        = 'house-duplex', 'Single Family'
    TOWNHOUSE            = 'townhouse',    'Townhome'



class Beds(models.TextChoices):
    ZERO        = '0', 'Studio'
    ONE         = '1', '1'
    TWO         = '2', '2'
    THREE       = '3', '3'
    FOUR        = '4', '4'
    FIVE_PLUS   = '5+', '5+'


class Baths(models.TextChoices):
    ONE         = '1', '1'
    ONE_AND_HALF = '1.5', '1.5'
    TWO         = '2', '2'
    TWO_AND_HALF = '2.5', '2.5'
    THREE       = '3', '3'
    THREE_AND_HALF = '3.5', '3.5'
    FOUR_PLUS   = '4+', '4+'
