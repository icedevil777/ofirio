from django.db import models

from common.models import BaseModel


class ContactUs(BaseModel):
    class Meta:
        verbose_name = 'contact us'
        verbose_name_plural = 'contact us objects'

    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField(max_length=4096)
