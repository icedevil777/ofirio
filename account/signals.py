from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

import common.tasks as tasks
from account.models import EmailSettings, FavoriteProperty, GoodDealSettings
from api_property.models import SimilarPropertyNotificationModel, PropertyUpdateModel


@receiver(pre_save, sender=FavoriteProperty)
def pre_favorite_save(sender, instance, **kwargs):
    """
    If user adds fav props and there were no prev favs,
    enable similar and history notifications for fav
    """
    if FavoriteProperty.objects.count() == 0:
        settings = instance.user.emailsettings_set.first()
        settings.favorites = True
        settings.favorites_match_notification = True
        settings.save()


@receiver(post_save, sender=FavoriteProperty)
def post_favorite_save(sender, instance, **kwargs):
    if kwargs['created']:
        tasks.track_favorites.delay(instance.user.id, instance.user.email)
        tasks.track_add_favorite(instance.pk)


@receiver(post_delete, sender=FavoriteProperty)
def post_favorite_delete(sender, instance, **kwargs):
    tasks.track_favorites.delay(instance.user.id, instance.user.email)


@receiver((post_save, post_delete), sender=EmailSettings)
def post_email_settings_save(sender, instance, **kwargs):
    tasks.track_email_settings.delay(instance.user.id)


@receiver(post_save, sender=GoodDealSettings)
def post_good_deal_settings_save(sender, instance, **kwargs):
    tasks.track_good_deal_settings.delay(instance.user.id)


@receiver((post_save, post_delete), sender=SimilarPropertyNotificationModel)
def post_similar_notification_save(sender, instance, **kwargs):
    tasks.track_similars.delay(instance.user.id, instance.user.email)


@receiver((post_save, post_delete), sender=PropertyUpdateModel)
def post_prop_updates_save(sender, instance, **kwargs):
    tasks.track_prop_updates.delay(instance.user.id, instance.user.email)
