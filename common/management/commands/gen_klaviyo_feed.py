import json

import psycopg2
from django.conf import settings
from ofirio_common.states_constants import states_from_short
from ofirio_common.enums import PropClass2

from common.utils import get_is_test_condition, get_pg_connection
from common.base_urlgen_command import BaseUrlgenCommand
from common.klaviyo.feed import build_feed_item


class Command(BaseUrlgenCommand):
    '''
    Creates json files ('feeds') for klaviyo. Each state has sales and rent feeds
    '''
    buf_size = 1024 * 16
    chunk_size = 1000
    klaviyo_dir = settings.BASE_DIR / 'data' / 'klaviyo'

    def _handle(self, *args, **options):
        self.conn = get_pg_connection()
        for state_id in states_from_short:
            sections = ('buy', 'rent', )
            if settings.INVEST_ENABLED:
                sections += ('invest',)
            for section in sections:
                feed = self.make_feed(state_id, section)
                if not feed:
                    continue
                path = self.klaviyo_dir / f'klaviyo-{state_id}-{section}.json'
                with open(path, 'w') as f:
                    json.dump(feed, f, separators=(',', ':'))
                    print('done', path)
        self.conn.close()

    def get_properties(self, state_id, section):
        ''' get all properties from prop_cache for specified state and prop class '''
        if section == 'invest':
            prop_class = 'sales'
            invest_condition = "and params ->> 'has_invest_view' = 'true'"
        elif section == 'buy':
            invest_condition = ''
            prop_class = 'sales'
        else:
            invest_condition = ''
            prop_class = 'rent'
        query = f'''
            select c.prop_id,
                   c.address ->> 'line' address_line,
                   c.address ->> 'city' address_city,
                   c.address ->> 'state_code' address_state_code,
                   c.address ->> 'zip' address_zip,
                   c.list_date,
                   c.status,
                   c.data -> 'price' price,
                   c.data -> 'beds' beds,
                   c.data -> 'cleaned_prop_type' prop_type,
                   c.data -> 'cap_rate' cap_rate,
                   c.data -> 'predicted_rent' predicted_rent,
                   c.data -> 'estimated_mortgage' estimated_mortgage,
                   c.badges badges,
                   c.params params,
                   p.photos -> 0 image
            from prop_cache c
            join prop_photos p on c.real_prop_id = p.prop_id
            where prop_class = %(prop_class)s
              and state_id = %(state_id)s
              and status in ('for_sale', 'for_rent')
              {get_is_test_condition(table_alias='c')}
              {invest_condition}
            order by prop_id
        '''
        with self.conn.cursor(
                name='cursor_for_feed',
                cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.itersize = self.chunk_size
            cursor.execute(query, {'state_id': state_id, 'prop_class': prop_class})
            while chunk := cursor.fetchmany(self.chunk_size):
                yield chunk
        self.conn.commit()

    def make_feed(self, state_id, section):
        '''
        generates list of feed items (dicts)
        '''
        print('=======', state_id, section, '========')
        feed = []
        i = 0
        for chunk in self.get_properties(state_id, section):
            print(f'chunk #{i}')
            urls = self.convert_to_urls(chunk)
            items = [build_feed_item(prop, url, section) for prop, url in zip(chunk, urls)]
            feed.extend(items)
            i += 1
        if len(feed):
            print(f'{state_id}: converted {len(feed)} properties')
        return feed
