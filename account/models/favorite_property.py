from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from common.models import BaseModel
from api_property.enums import PropClass

User = get_user_model()


class FavoriteProperty(BaseModel):
    class Meta:
        verbose_name = 'favorite property'
        verbose_name_plural = 'favorite properties'
        indexes = [
            models.Index(fields=['prop_id', 'user']),
            models.Index(fields=['user']),
        ]

    # common fields
    prop_id = models.CharField(max_length=21)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    added_time = models.DateTimeField(default=timezone.now)
    photo1 = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255)
    price = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=32, default='', null=False, blank=True)
    beds = models.FloatField(null=True, blank=True)
    baths = models.FloatField(null=True, blank=True)
    building_size = models.IntegerField(null=True, blank=True)
    prop_class = models.CharField(max_length=20, null=True, default=PropClass.INVEST,
                                  choices=PropClass.choices)

    # sale fields
    cash_on_cash = models.FloatField(null=True, blank=True)
    cap_rate = models.FloatField(null=True, blank=True)
    total_return = models.FloatField(null=True, blank=True)
    estimated_rent = models.FloatField(null=True, blank=True)
    apr_rate = models.FloatField(null=True, blank=True)
    prop_taxes = models.FloatField(null=True, blank=True)
    estimated_mortgage = models.FloatField(null=True, blank=True)

    # rent fields
    parking = models.BooleanField(null=True, blank=True)
    pet_friendly = models.BooleanField(null=True, blank=True)
    laundry = models.BooleanField(null=True, blank=True)
    furnished = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f'{self.user} - {self.prop_id}'
