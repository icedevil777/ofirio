from datetime import timedelta

from django.db import models
from django.utils import timezone

from common.models import BaseModel


class RestorePasswordCheckManager(models.Manager):

    def find_active(self, restore_code):
        """
        Find last fresh Restore Check object for a corresponding code
        """
        return super().filter(
            restore_code__exact=restore_code, used=False,
            created_time__gte=(timezone.now() - timedelta(hours=1)),
        ).first()


class RestorePasswordCheck(BaseModel):
    email = models.EmailField()
    restore_code = models.CharField(max_length=32)
    created_time = models.DateTimeField(default=timezone.now, blank=True)
    used = models.BooleanField(default=False)

    objects = RestorePasswordCheckManager()

    def __str__(self):
        used = 'used' if self.used else 'not used'
        return f'{self.email}, {used}'
