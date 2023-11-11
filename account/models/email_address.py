import datetime

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone

import common.tasks as tasks
from common.constants import FRONTEND_URLS
from common.models import BaseModel
from common.utils import generate_random_hex_str, get_absolute_url


User = get_user_model()


class EmailAddress(BaseModel):
    """Handle email verification status"""

    class Meta:
        verbose_name = 'email address'
        verbose_name_plural = 'email addresses'

    sent_at = models.DateTimeField(null=True, blank=True)
    code = models.CharField(max_length=32, default=generate_random_hex_str, null=True, blank=True)
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)

    @property
    def email(self):
        return self.user.email

    def generate_new_code(self):
        self.code = generate_random_hex_str()
        self.save()

    def get_verification_url(self):
        """
        API verification URL
        """
        url = reverse('account:verify_email', kwargs={'code': self.code})
        absolute_url = get_absolute_url(url)
        return absolute_url

    def get_frontend_verification_url(self):
        """
        Frontend verification URL
        """
        url = FRONTEND_URLS.email_verification.format(code=self.code)
        absolute_url = get_absolute_url(url)
        return absolute_url

    def unverify(self, force=False):
        if not self.verified and not force:
            raise RuntimeError('Email is not verified')
        self.verified = False
        self.generate_new_code()

    @property
    def is_code_expired(self):
        # no requirement for this, so hardcoded something temporary
        expire_time = datetime.timedelta(days=7)

        if self.sent_at:
            expiration_date = self.sent_at + expire_time
            return expiration_date <= timezone.now()

    def __str__(self):
        status = 'verified' if self.verified else 'not verified'
        return f'{self.email} ({status})'

    def verify(self, force=False):
        if force:
            self.user.verified = True
            self.verified = True
            # Trial period starts when the user gets verified
            tasks.track_user_status_changed.delay(self.user.id)

        else:
            if self.verified:
                raise RuntimeError('Email already verified')
            elif self.is_code_expired:
                raise RuntimeError('Code expired')
            else:
                self.user.verified = True
                self.verified = True
                tasks.track_user_status_changed.delay(self.user.id)

        self.user.save()
        self.save()
