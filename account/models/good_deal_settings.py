from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from api_property.enums import PropClass
from api_property.models import PropCity
from common.models import BaseModel
from search.enums import PropType3


User = get_user_model()


class GoodDealSettings(BaseModel):
    """
    To remember what exactly good deals user wants to receive
    """
    class Meta:
        verbose_name_plural = 'good deal settingses'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cities = models.ManyToManyField(PropCity)
    prop_type = models.CharField(max_length=20, choices=PropType3.choices, null=True, blank=True)
    rent_min_price = models.IntegerField(default=200, null=True, blank=True)
    rent_max_price = models.IntegerField(default=20_000, null=True, blank=True)
    buy_min_price = models.IntegerField(default=10_000, null=True, blank=True)
    buy_max_price = models.IntegerField(default=10_000_000, null=True, blank=True)
    invest_min_price = models.IntegerField(default=10_000, null=True, blank=True)
    invest_max_price = models.IntegerField(default=10_000_000, null=True, blank=True)
    rent_enabled = models.BooleanField(default=False)
    buy_enabled = models.BooleanField(default=False)
    invest_enabled = models.BooleanField(default=False)
    beds_min = models.IntegerField(null=True, blank=True)
    baths_min = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return str(self.user)
