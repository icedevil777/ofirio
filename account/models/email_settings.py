from django.contrib.auth import get_user_model
from django.db import models

from common.models import BaseModel


User = get_user_model()


class EmailSettings(BaseModel):
    class Meta:
        verbose_name_plural = 'email settingses'

    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=True)

    good_deals = models.BooleanField(default=False)
    similars = models.BooleanField(default=False)
    prop_updates = models.BooleanField(default=False)
    #  props that will be pushed into prop history updates script
    favorites = models.BooleanField(default=False)
    #  props that will be pushed into prop simialrs script
    favorites_match_notification = models.BooleanField(default=False)

    tips_and_guides = models.BooleanField(default=True)
    market_reports_and_updates = models.BooleanField(default=True)
    tool_updates = models.BooleanField(default=True)
    partner_offers_and_deals = models.BooleanField(default=True)
    properties_you_may_like = models.BooleanField(default=True)

    def __str__(self):
        return str(self.user)
