import datetime

from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

import account.models
from account.common import phone_regex
from account.constants import USER_WARNINGS
from common.models import BaseModel


# Based on https://tech.serhatteker.com/post/2020-01/email-as-username-django/

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        account.models.EmailAddress.objects.create(user=user)
        account.models.EmailSettings.objects.create(user=user)
        account.models.GoodDealSettings.objects.create(user=user)

        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser, BaseModel):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)

    phone = models.CharField(validators=[phone_regex], max_length=16, blank=True)
    verified = models.BooleanField(default=False)
    accepted_terms_of_use = models.BooleanField(default=True)
    password_changed_at = models.DateTimeField(default=timezone.now)
    is_team = models.BooleanField(default=False)

    # If a user logged in by a social at least once, these fields contain internal user id
    fb_user_id = models.CharField(max_length=31, default='', null=False, blank=True)
    google_user_id = models.CharField(max_length=31, default='', null=False, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    @property
    def warnings(self):
        warnings = []
        if not self.accepted_terms_of_use:
            warnings.append(USER_WARNINGS.terms_of_use_not_accepted)
        if self.password_changed_at < timezone.now() - datetime.timedelta(days=90):
            warnings.append(USER_WARNINGS.password_change_required)
        return warnings

    @property
    def email_address(self):
        return self.emailaddress_set.first()

    @property
    def last_restore_password_check(self):
        model_class = account.models.RestorePasswordCheck
        checks = model_class.objects.filter(email=self.email).order_by('created_time')
        return checks.last()

    def save(self, *args, **kwargs):
        if self._password:  # new password has been set
            self.password_changed_at = timezone.now()
        super().save(*args, **kwargs)
