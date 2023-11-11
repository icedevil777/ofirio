from django.contrib.auth import get_user_model

from api_property.management.prop_notification import BasePropHistoryNotification
from api_property.models import PropertyUpdateModel


User = get_user_model()


class Command(BasePropHistoryNotification):
    """
    Scan prop_cache for properties that users subscribed to,
    and send Klaviyo events if updated price or status detected
    """
    def get_users(self):
        return User.objects.filter(is_active=True, emailsettings__prop_updates=True)

    def get_props_subscribed(self, user, prop_class):
        """
        Read and return all the properties user subscribed for
        in format {prop_id: prop}
        """
        return {p.prop_id: p for p in
                PropertyUpdateModel.objects.filter(prop_class=prop_class, user=user)}
