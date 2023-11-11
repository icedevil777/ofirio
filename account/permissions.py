from rest_framework import permissions
from rest_framework import status

from account.enums import UserAccessStatus
from account.models import AccessEvent
from account.utils import get_access_status


class RequestsLimit(permissions.BasePermission):
    """
    Permission to restrict access for nonpaid and anon users
    """
    code = status.HTTP_403_FORBIDDEN

    def _get_same_recent_events(self, request, view):
        serializer_class = view.get_serializer_class()
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            same_recent_events = AccessEvent.objects.get_same_recent_events(
                request, view.access_type, serializer.validated_data)
            return same_recent_events

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            status = get_access_status(request.user)
            if status == UserAccessStatus.PREMIUM:
                return True
            elif not AccessEvent.objects.is_limit_reached(request, view.access_type):
                return True
            elif self._get_same_recent_events(request, view):
                return True
            return False

        else:
            if not AccessEvent.objects.is_limit_reached(request, view.access_type):
                return True
            elif self._get_same_recent_events(request, view):
                return True
            return False
