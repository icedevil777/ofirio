from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from account.constants import ANON_LIMITS
from account.enums import AccessType
from account.utils import is_premium
from common.models import BaseModel
from common.utils import get_ip_address


User = get_user_model()


class AccessEventManager(models.Manager):

    def remember_access(self, request, access_type, query):
        """
        Create only events needed to correctly restrict user access later.
        Use this instead of create()
        """
        limit_reached = self.is_limit_reached(request, access_type)
        same_recent_events = self.get_same_recent_events(request, access_type, query)
        if not limit_reached and not same_recent_events:
            if request.user.is_authenticated:
                if not is_premium(request.user):
                    return self.create(user=request.user, access_type=access_type, query=query)
            else:
                ip_address = get_ip_address(request)
                return self.create(ip_address=ip_address, access_type=access_type, query=query)

    def get_same_recent_events(self, request, access_type, query):
        """
        Return recent access events with the same type
        for the same user with the same query
        """
        threshold = timezone.now() - timedelta(hours=24)
        if request.user.is_authenticated:
            events = self.filter(
                user=request.user, access_type=access_type, query=query,
                created_at__gte=threshold,
            )
        else:
            ip_address = get_ip_address(request)
            events = self.filter(
                ip_address=ip_address, access_type=access_type, query=query,
                created_at__gte=threshold,
            )
        return events

    def is_limit_reached(self, request, access_type):
        """Tell if limit is reached for a given user and access type"""
        if request.user.is_authenticated:
            if is_premium(request.user):
                return
            else:
                access_limit = ANON_LIMITS[access_type]
                access_count = self.filter(user=request.user, access_type=access_type).count()
        else:
            access_limit = ANON_LIMITS.get(access_type, 0)
            ip_address = get_ip_address(request)
            access_count = self.filter(ip_address=ip_address, access_type=access_type).count()
        return access_count >= access_limit

    def get_limits_left(self, request):
        """Return dict with structure {access_type: times_left} for a user"""
        left = {}
        if request.user.is_authenticated:
            if not is_premium(request.user):
                for access_type, limit in ANON_LIMITS.items():
                    count = self.filter(user=request.user, access_type=access_type).count()
                    left[access_type] = limit - count
        else:
            ip_address = get_ip_address(request)
            for access_type, limit in ANON_LIMITS.items():
                count = self.filter(ip_address=ip_address, access_type=access_type).count()
                left[access_type] = limit - count
        return left


class AccessEvent(BaseModel):
    """
    Remember some users events to be able to limit them based on that
    """
    objects = AccessEventManager()

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=100, null=True, blank=True)
    access_type = models.CharField(max_length=100, choices=AccessType.choices)
    query = models.JSONField()  # values came from client in request

    def __str__(self):
        return f'{self.access_type} of {self.user}'
