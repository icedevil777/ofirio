from django.contrib.auth import get_user_model
from django.conf import settings

from account.models import GoodDealSettings
from api_property.common.common import get_pg_connection
from api_property.constants import ACTIVE_STATUS_MAP
from api_property.enums import PropClass, PropertyNotificationTopic
from api_property.management.prop_notification import BasePropNotification, PROP_CLASS_CONVERT_MAP


User = get_user_model()

PROP_CLASS_ENABLED_MAP = {
    PropClass.BUY: 'buy_enabled',
    PropClass.RENT: 'rent_enabled',
    PropClass.INVEST: 'invest_enabled',
}
MIN_PRICE_MAP = {
    PropClass.BUY: 'buy_min_price',
    PropClass.INVEST: 'invest_min_price',
    PropClass.RENT: 'rent_min_price',
}
MAX_PRICE_MAP = {
    PropClass.BUY: 'buy_max_price',
    PropClass.INVEST: 'invest_max_price',
    PropClass.RENT: 'rent_max_price',
}


class Command(BasePropNotification):
    topic = PropertyNotificationTopic.GOOD_DEAL

    def _query_for_props(self, prop_class, sent_ids, gd_settings, city):
        """
        Read prop_ids from prop_cache
        """
        props = []
        not_in_sent = 'prop_id NOT IN %(sent)s AND ' if sent_ids else ''
        prop_type_select = "(data->>'cleaned_prop_type') = %(prop_type)s AND "
        where_prop_type = prop_type_select if gd_settings.prop_type else ''

        sql = f'''
            SELECT prop_id FROM prop_cache
            WHERE {not_in_sent}
                  {where_prop_type}
                  badges LIKE %(badges)s AND
                  status = '{ACTIVE_STATUS_MAP[prop_class]}' AND
                  prop_class = '{PROP_CLASS_CONVERT_MAP[prop_class]}' AND
                  (data->>'baths')::numeric >= %(baths_min)s AND
                  (data->>'beds')::numeric >= %(beds_min)s AND
                  (data->>'price')::numeric >= %(min_price)s AND
                  (data->>'price')::numeric <= %(max_price)s AND
                  (address->>'city_url') = %(city)s AND
                  (address->>'state_code') = %(state_id)s
        '''
        with get_pg_connection().cursor() as cursor:
            params = {
                'sent': tuple(sent_ids),
                'badges': f'%good_deal_{prop_class}%',
                'baths_min': gd_settings.baths_min or 0,
                'beds_min': gd_settings.beds_min or 0,
                'min_price': getattr(gd_settings, MIN_PRICE_MAP[prop_class]),
                'max_price': getattr(gd_settings, MAX_PRICE_MAP[prop_class]),
                'prop_type': gd_settings.prop_type,
                'city': city.city,
                'state_id': city.state_id.upper(),
            }
            cursor.execute(sql, params)
            props = [p[0] for p in cursor.fetchall()]

        return props

    def get_users(self):
        users = User.objects.filter(is_active=True, emailsettings__good_deals=True)
        return users

    def get_props(self, user, prop_class, sent_ids):
        """
        Gather all the 'good deal' props according to user settings
        """
        main, related = [], []

        if not settings.INVEST_ENABLED and prop_class == PropClass.INVEST:
            return main, related
        # OT-2902: rent currently disabled
        if prop_class == PropClass.RENT:
            return main, related

        gd_settings = GoodDealSettings.objects.get(user=user)
        if getattr(gd_settings, PROP_CLASS_ENABLED_MAP[prop_class]):
            self.log(f'{prop_class.title()} is enabled')

            for city in gd_settings.cities.all():
                city_props = self._query_for_props(prop_class, sent_ids, gd_settings, city)
                related.extend(city_props)

        return main, related
