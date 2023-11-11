from django.contrib.auth import get_user_model

from api_property.management.prop_notification import BaseSimilarNotification


User = get_user_model()


class Command(BaseSimilarNotification):
    prefix = 'Favorite '

    def get_props_subscribed(self, user, prop_class):
        return user.favoriteproperty_set.filter(prop_class=prop_class)

    def get_users(self):
        return User.objects.filter(is_active=True,
                                   emailsettings__favorites_match_notification=True)
