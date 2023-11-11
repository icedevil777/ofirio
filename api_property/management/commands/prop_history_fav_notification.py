from django.contrib.auth import get_user_model

from api_property.common.common import get_pg_connection
from api_property.common.recommendations import get_similar
from api_property.management.prop_notification import BasePropHistoryNotification
from api_property.models import PropertyNotified


User = get_user_model()


class Command(BasePropHistoryNotification):
    """
    Scan prop_cache for properties that users subscribed to,
    and send Klaviyo events if updated price or status detected
    """
    prefix = 'Favorite '

    def get_users(self):
        return User.objects.filter(is_active=True, emailsettings__favorites=True)

    def get_props_subscribed(self, user, prop_class):
        """
        Read and return all the properties user subscribed for
        in format {prop_id: prop}
        """
        props_subscribed = {}
        if user.emailsettings_set.first().favorites:
            for fav in user.favoriteproperty_set.filter(prop_class=prop_class):
                props_subscribed[fav.prop_id] = fav
        return props_subscribed

    def get_related(self, user, prop_id, prop_class):
        sent_notifications = PropertyNotified.objects.filter(prop_class=prop_class,
                                                             user=user).values('prop_id')
        sent_ids = list({s['prop_id'] for s in sent_notifications})
        related = get_similar(get_pg_connection().cursor(), prop_id, prop_class, sent_ids)
        return related
