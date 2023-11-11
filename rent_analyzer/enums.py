from django.db import models


class SearchType(models.TextChoices):
    ADDRESS     = 'address', 'Address'
    ZIP         = 'zip', 'Zip'
    CITY        = 'city', 'City'


class Distance(models.TextChoices):
    AUTO            = 'auto', 'Auto'
    POINT_1         = 0.1, '0.10 mi'
    POINT_2         = 0.2, '0.20 mi'
    POINT_33        = 0.33, '0.33 mi'
    POINT_5         = 0.50, '0.50 mi'
    POINT_75        = 0.75, '0.75 mi'
    ONE             = 1, '1.00 mi'
    ONE_AND_HALF    = 1.5, '1.50 mi'
    TWO             = 2, '2 mi'
    THREE           = 3, '3 mi'
    FIVE            = 5, '5 mi'
    TEN             = 10, '10 mi'


class Beds(models.TextChoices):
    ANY         = 'any', 'Any'
    ZERO        = '0', 'Studio'
    ONE         = '1', '1'
    TWO         = '2', '2'
    THREE       = '3', '3'
    FOUR        = '4', '4'
    FIVE_PLUS   = '5+', '5+'


class Baths(models.TextChoices):
    ANY         = 'any', 'Any'
    ONE         = '1', '1'
    ONE_AND_HALF = '1.5', '1.5'
    TWO         = '2', '2'
    TWO_AND_HALF = '2.5', '2.5'
    THREE       = '3', '3'
    THREE_AND_HALF = '3.5', '3.5'
    FOUR_PLUS   = '4+', '4+'


class PropertyType(models.TextChoices):
    ANY                 = 'any', 'Any'
    CONDO_APT           = 'condo-apt',    'Cond & Apts'
    HOUSE_DUPLEX        = 'house-duplex', 'Single Family'

class PropertyType3(models.TextChoices):
    ANY                 = 'any', 'Any'
    CONDO_APT           = 'condo-apt',    'Cond & Apts'
    HOUSE_DUPLEX        = 'house-duplex', 'Single Family'
    TOWNHOUSE            = 'townhouse',    'Townhome'


class LookBack(models.TextChoices):
    THREE           = '3', '3 mo'
    SIX             = '6', '6 mo'
    NINE            = '9', '9 mo'
    TWELVE          = '12', '12 mo'
    EIGHTEEN        = '18', '18 mo'
    TWENTY_FOUR     = '24', '24 mo'
    THIRTY_SIX      = '36', '36 mo'
    FOURTY_EIGHT    = '48', '48 mo'
