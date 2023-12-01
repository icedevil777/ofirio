from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from api_property.enums import PropClass, PropertyNotificationTopic
from common.models import BaseModel

User = get_user_model()


class ContactAgent(BaseModel):
    user = models.ManyToManyField(User, null=True, related_name='leads')
    order_number = models.CharField(max_length=255, unique=True, null=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=255)
    request = models.TextField(max_length=4096)
    prop_id = models.CharField(max_length=21)
    prop_address = models.CharField(max_length=255)
    url = models.CharField(max_length=255, null=True)
    price = models.FloatField(null=True)
    prop_class = models.CharField(max_length=8, choices=PropClass.choices, null=True)
    move_in_date = models.DateField(null=True)


class PropCity(BaseModel):
    city = models.CharField(max_length=32)
    county = models.CharField(max_length=32)
    state_id = models.CharField(max_length=3)
    label = models.CharField(max_length=255)

    def __str__(self):
        return self.label


class SimilarPropertyNotificationModel(BaseModel):
    class Meta:
        verbose_name = 'Similar Property Notification'

    prop_id = models.CharField(max_length=21)
    prop_class = models.CharField(max_length=6, choices=PropClass.choices)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='similar_props',
                             on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user} - {self.prop_id}'


class PropertyUpdateModel(BaseModel):
    class Meta:
        verbose_name = 'Property Updates Notification'

    prop_id = models.CharField(max_length=21)
    prop_class = models.CharField(max_length=6, choices=PropClass.choices)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='props_updates',
                             on_delete=models.CASCADE)
    price = models.IntegerField(default=0, null=False, blank=False)
    status = models.CharField(max_length=32, default='', null=False, blank=True)

    def __str__(self):
        return f'{self.user} - {self.prop_id}'


class PropertyNotified(BaseModel):
    """
    To remember, what properties a user has been already notified about
    """
    prop_id = models.CharField(max_length=21)
    prop_class = models.CharField(max_length=6, choices=PropClass.choices)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='props_notified',
                             on_delete=models.CASCADE)
    topic = models.CharField(max_length=32, choices=PropertyNotificationTopic.choices)


class Building(models.Model):
    """
    The model exists in `prop_db` (not `default`) and is managed by playground
    """
    building_id = models.CharField(primary_key=True, max_length=128)
    photos = models.JSONField()

    class Meta:
        db_table = 'buildings'
        managed = True
