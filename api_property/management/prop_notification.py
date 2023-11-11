import sys
import random
from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connections
from ofirio_common.enums import PropClass2

from api_property.common.common import get_pg_connection
from api_property.common.errors import NoPropertyError
from api_property.common.recommendations import get_similar
from api_property.enums import PropClass, PropertyNotificationTopic
from api_property.models import PropertyNotified, PropertyUpdateModel
from common.klaviyo import util as klaviyo
from common.management import OfirioCommand


User = get_user_model()

PROP_CLASS_CONVERT_MAP = {
    PropClass.BUY: PropClass2.SALES,
    PropClass.INVEST: PropClass2.SALES,
    PropClass.RENT: PropClass2.RENT,
}


class BasePropNotification(OfirioCommand):
    """
    Base class for a script that read properties and notify users about them.
    You need to define in a subclass:
    - topic
    - prefix - to use in log messages and event naming
    - get_props()
    - get_users()
    """
    min_count = 4
    max_count = 8
    topic = None
    prefix = ''

    def get_props(self, user, prop_class, sent_ids):
        """
        Gather all the props potentially suitable for user notification.
        Have to return 2 lists: main and related properties
        """
        raise NotImplementedError

    def get_users(self):
        """
        Must provide queryset of users who enabled the notifications
        """
        raise NotImplementedError

    def process_prop_class_for_user(self, user, prop_class):
        sent_notifications = PropertyNotified.objects.filter(prop_class=prop_class,
                                                             user=user).values('prop_id')
        sent_ids = list({s['prop_id'] for s in sent_notifications})

        main, related = self.get_props(user, prop_class, sent_ids)
        self.log(f'Found {len(related)} {self.prefix}{prop_class.title()} '
                 f'{self.topic.title()} props')

        if len(related) >= self.min_count:
            random.shuffle(related)
            related = related[:self.max_count]

            self.log(f'Notifying about props: {related}')
            klaviyo.track_properties_notification(user.email, main, related, prop_class,
                                                  self.topic, prefix=self.prefix)
            for prop_id in related:
                PropertyNotified.objects.create(user=user, prop_id=prop_id, prop_class=prop_class,
                                                topic=self.topic)

    def handle(self, *args, **options):
        """
        For each user gather props to send, send them with klaviyo,
        and remember them using PropertyNotified model
        """
        users = self.get_users()
        total = users.count()

        for i, user in enumerate(users):
            self.log(f'Processing User(pk={user.pk}) ({i+1}/{total})')

            prop_classes = (PropClass.BUY,)
            if settings.INVEST_ENABLED:
                prop_classes += (PropClass.INVEST,)
            # OT-2902: rent currently disabled
            for prop_class in prop_classes:
                self.process_prop_class_for_user(user, prop_class)


class BaseSimilarNotification(BasePropNotification):
    topic = PropertyNotificationTopic.SIMILAR

    def get_props(self, user, prop_class, sent_ids):
        """
        Gather all the props similar to those user added to Favorites
        """
        cursor = get_pg_connection().cursor()
        main, related = [], []

        for sim_ntf in self.get_props_subscribed(user, prop_class):
            try:
                for prop in get_similar(cursor, sim_ntf.prop_id, prop_class, sent_ids):
                    related.append(prop['prop_id'])
            except NoPropertyError:
                pass
        return main, related

    def get_props_subscribed(self, user, prop_class):
        """
        Return queryset of properties, which user subscribed to.
        Similar properties are being searched based on them.
        """
        raise NotImplementedError


class BasePropHistoryNotification(BasePropNotification):
    """
    Scan prop_cache for properties that users subscribed to,
    and send Klaviyo events if updated price or status detected
    """
    command_name = sys.argv[1]
    topic = PropertyNotificationTopic.PROP_HISTORY
    event_counter = 0

    def read_prop_cache(self, prop_ids, prop_class):
        if not prop_ids:
            return {}

        props = []
        sql = f'''
            SELECT prop_id, status, (data->>'price')::numeric
            FROM prop_cache
            WHERE prop_id in %(prop_ids)s AND
                  prop_class = '{PROP_CLASS_CONVERT_MAP[prop_class]}'
        '''
        with connections['prop_db'].cursor() as cursor:
            cursor.execute(sql, {'prop_ids': tuple(prop_ids)})
            for fetched_prop in cursor.fetchall():
                props.append(dict(zip(('prop_id', 'status', 'price'), fetched_prop)))

        return {p['prop_id']: p for p in props}

    def _notify(self, user, prop, related, prop_class, subtopic, old_val, new_val, **kwargs):
        self.log(f'{subtopic.title()} for {prop_class.title()} {self.prefix}prop {prop.prop_id} '
                 f'changed from "{old_val}" to "{new_val}". Notifying')

        related = [p['prop_id'] for p in related]
        klaviyo.track_properties_notification(
            user.email,
            [prop.prop_id],
            related,
            prop_class,
            self.topic,
            subtopic,
            prefix=self.prefix,
            event_id=kwargs.get('event_id')
        )

    def get_props_subscribed(self, user, prop_class):
        """
        Read and return all the properties user subscribed for
        in format {prop_id: prop}
        """
        return {p.prop_id: p for p in
                PropertyUpdateModel.objects.filter(prop_class=prop_class, user=user)}

    def get_related(self, user, prop_id, prop_class):
        return []

    def process_prop_class_for_user(self, user, prop_class):
        """
        Read new data about user properties, notify if changed, and remember the new data
        """
        props_subscribed = self.get_props_subscribed(user, prop_class)
        started_for_user_at = datetime.now().timestamp()

        for prop_id, prop in self.read_prop_cache(list(props_subscribed), prop_class).items():
            prop_subscribed = props_subscribed[prop_id]
            related = self.get_related(user, prop_id, prop_class)

            if prop['status'] != prop_subscribed.status:
                self._notify(
                    user,
                    prop_subscribed,
                    related,
                    prop_class,
                    'status',
                    prop_subscribed.status,
                    prop['status'],
                    event_id=f'{self.event_counter}.{int(started_for_user_at)}.{self.command_name}.{settings.PROJECT_DOMAIN}'
                )
                self.event_counter += 1

            if prop['price'] < (prop_subscribed.price or 0):
                self._notify(
                    user,
                    prop_subscribed,
                    related,
                    prop_class,
                    'price',
                    prop_subscribed.status,
                    prop['price'],
                    event_id=f'{self.event_counter}.{int(started_for_user_at)}.{self.command_name}.{settings.PROJECT_DOMAIN}'
                )
                self.event_counter += 1

            prop_subscribed.status = prop['status']
            prop_subscribed.price = int(prop['price'])
            prop_subscribed.save()
